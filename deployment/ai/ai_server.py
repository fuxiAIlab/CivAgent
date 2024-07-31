from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from datetime import datetime
import re
from civsim import logger
from civsim import utils
from civsim.utils import json_load_defaultdict
import civsim.simulator.simulator as simulator
from civagent.utils.prompt_utils import envent_trigger_make
from civagent.utils import memory_utils
from civagent.utils.memory_utils import ChatMemory
from civagent.skills import use_skills
from civagent.utils.skills_utils import get_skills
from civagent.config import config_data
from deployment.chatbot.chatmanager import ChatManager
from deployment.ai.strategy import *
from deployment.redis_mq import RedisStreamMQ
from deployment.ai.free_chat import process

mq = RedisStreamMQ()
simulator.init_jvm()
app = Flask(__name__)


def check_turns(data, gameinfo={}, gameid={}):
    if gameinfo == {}:
        gameinfo = json_load_defaultdict(data["gameinfo"])
        gameid = utils.check_and_bind_gameid(gameinfo['gameId'])
    turns = int(mq.get(f"{gameid}_updated_turns", 0))
    gameid2info = mq.get('gameid2info_' + gameid, {})
    robot_names = gameid2info.get('civ_robots', [])
    if 'barbarians' in robot_names:
        robot_names.remove('barbarians')
    robot_nums = len(robot_names)
    robot_index = [x.lower() for x in robot_names].index(data["civ1"].lower())
    logger.debug(f"check_turns: {turns} {robot_nums} {robot_index} {data['civ1']}")
    if turns % robot_nums != robot_index or turns < config_data['use_skills_turns']:
        return False
    return True


@app.route('/healthz')
def healthz():
    return 'OK', 200


@app.route('/decision', methods=['POST'])
def decision():
    data = request.json
    gameinfo = json_load_defaultdict(data["gameinfo"])
    gameid = utils.check_and_bind_gameid(gameinfo['gameId'])
    if not check_turns(data, gameinfo, gameid):
        return jsonify({'result': ''})
    default_skill_data = {'skills': {}, 'skill_num': {}, 'tech': {}, 'production': {}, 'turns': 0}
    game_skill_data = mq.get('multiplayer_' + gameid + '_game_skill_data', default_skill_data)
    if data["skill"] == "research_agreement":
        result, game_skill_data = canSignResearchAgreementsWith(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == "form_ally":
        result, game_skill_data = wantsToSignDefensivePact(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == "declare_war":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data, 20
        )
    elif data["skill"] == "change_closeness":
        result, game_skill_data = wantsToSignDeclarationOfFrienship(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == "choose_technology":
        result, game_skill_data = chooseTechToResarch(
            data['gameinfo'], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == "production_priority":
        result, game_skill_data = chooseNextConstruction(
            data['gameinfo'], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == "seek_peace":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data, 10
        )
    elif data["skill"] == 'common_enemy':
        result, game_skill_data = commonEnemy(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == 'buy_luxury':
        result, game_skill_data = buyLuxury(
            data["gameinfo"], data["civ1"], data["civ2"], game_skill_data
        )
    elif data["skill"] == 'open_borders':
        result, game_skill_data = get_skills(
            data["skill"], data["civ1"], data["civ2"], game_skill_data
        )
    else:
        assert False, f'Invalid skill: {data["skill"]}'
    mq.set('multiplayer_' + gameid + '_game_skill_data', json.dumps(game_skill_data))
    return result


@app.route('/get_early_decision', methods=['POST'])
def getEarlyDecision():
    data = request.json
    gameinfo = json_load_defaultdict(data["gameinfo"])
    gameid = utils.check_and_bind_gameid(gameinfo['gameId'])
    if not check_turns(data, gameinfo, gameid):
        return jsonify({'result': ''})
    player_civ = gameinfo['player_civ']
    default_skill_data = {'skills': {}, 'skill_num': {}, 'tech': {}, 'production': {}, 'turns': 0}
    game_skill_data = mq.get(
        'multiplayer_' + gameid + '_game_skill_data', default_skill_data
    )
    result, game_skill_data = use_skills(
        data["gameinfo"], data["civ1"], config_data, game_skill_data
    )
    logger.info(f"getEarlyDecision: {game_skill_data}")
    mq.set('multiplayer_' + gameid + '_game_skill_data', json.dumps(game_skill_data))
    for skill in game_skill_data['skills'][data["civ1"]]:
        if skill['to_civ'] == player_civ:
            ChatManager.send_msg_by_http(
                gameid,
                skill['dialogue'],
                data["civ1"].lower(),
                skill['to_civ'].lower(),
                0
            )
    return result


@app.route('/reply_trade', methods=['POST'])
def replyTrade():
    data = request.json
    if not check_turns(data):
        return jsonify({'result': ''})
    result = replyTrades(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/wantsToDeclarationOfFrienship', methods=['POST'])
def wantsToDeclarationOfFrienship():
    data = request.json
    if not check_turns(data):
        return jsonify({'result': ''})
    result = replyDeclarFrienship(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/getEnemyCitiesByPriority', methods=['POST'])
def getEnemyCitiesByPriority():
    data = request.json
    if not check_turns(data):
        return jsonify({'result': ''})
    result = getOursEnemyCitiesByPriority(data["gameinfo"], data["civ1"], data["id"])
    return result


@app.route('/event_trigger', methods=['POST'])
def replyEventTrigger():
    data = request.json
    gameid = utils.check_and_bind_gameid(data['gameId'])
    logger.debug(f'event_trigger data: {data}')
    if utils.time_diff_in_minutes(data['addTime']) >= 2:
        logger.debug(f'event_trigger time out: {data}')
        pass
    elif data.get("type", "") == "next_turn":
        # {'game_id': '74ab70cb-4c15-485c-a3ac-d8799f114657', 'type': 'next_turn', 'turns': '1'}
        data = data["data"]
        turns = int(data.get('turns', 1))
        updated_turns = int(mq.get(f"{gameid}_updated_turns", 0))
        user_id = mq.get(f"gameid2userid_{gameid}")
        gameid2info = mq.get('gameid2info_' + gameid, {})
        filepath = utils.get_savefile(gameid)
        save_data = utils.get_latest_savefile(filepath)
        civ_ind = utils.get_civ_index(save_data)
        civ_name = utils.get_civ_name(save_data, civ_ind)
        events = memory_utils.Memory.get_event_memory(save_data, civ_ind)
        events = [event for event in events
                  if event['turns'] == turns - 1 and event['turns'] > updated_turns]
        if len(events) == 0:
            text = envent_trigger_make(
                'turn_event_default',
                {**gameid2info, **{"turns": turns}}
            )
            ChatManager.send_msg_by_http(
                gameid,
                text,
                from_civ="admin",
                is_group=1
            )
        else:
            for event in events:
                text = event["text"].replace('your', f'[{utils.fix_civ_name(civ_name)}]')
                text = text.replace('our', f'[{utils.fix_civ_name(civ_name)}]')
                text = envent_trigger_make(
                    'turn_event',
                    {**gameid2info, **{"turns": event["turns"], "text": text}}
                )
                ChatManager.send_msg_by_http(
                    gameid,
                    text,
                    from_civ="admin",
                    is_group=1
                )
        # todo more event trigger
        # if int(turns) % 10 == 0:
        #     mq.xadd(gameid, {"game_id": gameid, "type": "long_think"})
        declare_war_event = [event for event in events
                             if 'declare' in event['text']
                             and event['turns'] == turns - 1
                             and event['turns'] > updated_turns]
        if len(declare_war_event) > 0:
            for event in declare_war_event:
                msg = {
                    "game_id": gameid,
                    "type": "declare_war",
                    "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event": event["text"]
                }
                mq.xadd(gameid, msg)
        mq.set(f"{gameid}_updated_turns", int(turns) - 1)
    elif data.get("type", "") == "declare_war":
        data = data["data"]
        user_id = mq.get(f"gameid2userid_{gameid}")
        gameinfo = mq.get(f"gameinfo_{gameid}")
        gameid2info = mq.get('gameid2info_' + gameid, {})
        text = data['event']
        pattern = r'\b(?:' + '|'.join(ChatManager.robot_names) + r')\b'
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        attack_civ_name, attacked_civ_name = matches[0].lower(), matches[1].lower()
        # Imitate player dialogue to enable proactive conversation by the agent.
        if attack_civ_name == gameinfo.get('player_civ', ''):
            trigger_text = envent_trigger_make(
                'declare_war_event', gameid2info
            )
        elif attacked_civ_name == gameinfo.get('player_civ', ''):
            trigger_text = envent_trigger_make(
                'heard_war_event',
                {**gameid2info, **{"attack_civ_name": attack_civ_name}}
            )
        else:
            trigger_text = ""
        if trigger_text:
            ChatManager.send_msg_by_http(
                gameid,
                trigger_text,
                attack_civ_name,
                attacked_civ_name,
                0,
                {"bootstrap": 1}
            )
    return 'success'


@app.route('/reply_free_chat', methods=['POST'])
def replyFreeChat():
    data = request.json
    game_id = utils.check_and_bind_gameid(data['gameId'])
    logger.debug(f'reply_free_chat data: {data}')
    if utils.time_diff_in_minutes(data['addTime']) >= 2:
        if data.get("type", "") == "chat":
            chatmemory = ChatMemory(**data['data'])
            gameid2info = mq.get('gameid2info_' + game_id, {})
            ChatManager.send_msg_by_http(
                data['gameId'],
                f'{chatmemory.notify}' + envent_trigger_make('time_out_event', gameid2info),
                from_civ=chatmemory.toCiv,
                to_civ=chatmemory.fromCiv,
                is_group=chatmemory.isGroup
            )
    else:
        process(ChatMemory(**data['data']))
    return 'success'


http_server = WSGIServer(('0.0.0.0', 2335), app)
http_server.serve_forever()
