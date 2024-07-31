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


def check_turns(data, gameid):
    gameid2info = mq.get('gameid2info_' + gameid, {})
    turns = gameid2info.get('turns', 0)
    robot_names = gameid2info.get('civ_robots', [])
    player_civ = gameid2info['player_civ'][0]
    if data['civ1'].lower() == player_civ.lower():
        return False
    if 'barbarians' in robot_names:
        robot_names.remove('barbarians')
    robot_nums = len(robot_names)
    robot_index = [x.lower() for x in robot_names].index(data['civ1'].lower())
    if turns % robot_nums != robot_index or turns < config_data['use_skills_turns']:
        return False
    return True


@app.route('/healthz')
def healthz():
    return 'OK', 200


@app.route('/decision', methods=['POST'])
def decision():
    global logger
    data = request.json
    gameinfo = json_load_defaultdict(data["gameinfo"])
    civ_name = data['civ1'].lower()
    civ_name_2 = data['civ2'].lower()
    gameid = utils.check_and_bind_gameid(gameinfo['gameId'])
    logger = logger.bind(**{"game_id": gameid})
    default_skill_data = {'skills': {}, 'skill_num': {}, 'tech': {}, 'production': {}, 'turns': 0}
    game_skill_data = mq.get(f'multiplayer_{gameid}_{civ_name}_skill_data', default_skill_data)
    if data["skill"] == "research_agreement":
        result, game_skill_data = canSignResearchAgreementsWith(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "form_ally":
        result, game_skill_data = wantsToSignDefensivePact(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "declare_war":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data, 20
        )
    elif data["skill"] == "change_closeness":
        result, game_skill_data = wantsToSignDeclarationOfFrienship(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "choose_technology":
        result, game_skill_data = chooseTechToResarch(
            data['gameinfo'], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "production_priority":
        result, game_skill_data = chooseNextConstruction(
            data['gameinfo'], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "seek_peace":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data, 10
        )
    elif data["skill"] == 'common_enemy':
        result, game_skill_data = commonEnemy(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == 'buy_luxury':
        result, game_skill_data = buyLuxury(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == 'open_borders':
        result, game_skill_data = get_skills(
            data["skill"], civ_name, civ_name_2, game_skill_data
        )
    else:
        assert False, f'Invalid skill: {data["skill"]}'
    logger.debug(f"{data['skill']} decision on {game_skill_data['turns']} turn of {data['civ1']}: {result}")
    mq.set(f'multiplayer_{gameid}_{civ_name}_skill_data', json.dumps(game_skill_data))
    return result


@app.route('/get_early_decision', methods=['POST'])
def getEarlyDecision():
    global logger
    data = request.json
    save_data = json_load_defaultdict(data["gameinfo"])
    civ_name = data["civ1"].lower()
    # todo no save_data at the first turn
    turns = int(save_data.get('turns', 0))
    gameid = utils.check_and_bind_gameid(save_data['gameId'])
    logger = logger.bind(**{"game_id": gameid})
    if not check_turns(data, gameid):
        return json.dumps({'result': ''})
    is_async = data.get('is_async', 0)
    game_info = mq.get('gameid2info_' + gameid, {})
    player_civ = game_info['player_civ'][0]
    default_skill_data = {'skills': {}, 'skill_num': {}, 'tech': {}, 'production': {}, 'turns': 0}
    game_skill_data = mq.get(
        f'multiplayer_{gameid}_{civ_name}_skill_data',
        default_skill_data
    )
    if not is_async:
        from civagent.utils.memory_utils import Memory
        player_civ_ind = utils.get_civ_index(save_data, player_civ)
        event_history = Memory.get_event_memory(save_data, player_civ_ind)
        war_events = [event for event in event_history
                      if int(event.get('turns', 0)) >= turns
                      and 'declared war' in event.get('text', '')]
        if int(game_skill_data['turns']) >= int(save_data['turns']) and len(war_events) < 1:
            logger.info(f"{civ_name} use_async in getEarlyDecision: {game_skill_data}")
            game_skill_data = game_skill_data
        else:
            result, game_skill_data = use_skills(
                data["gameinfo"], civ_name, config_data, game_skill_data
            )
            logger.debug(f"{civ_name} war_events of {player_civ_ind}: {war_events}")
            logger.info(f"{civ_name} getEarlyDecision without use_async: {game_skill_data}")
            mq.set(f'multiplayer_{gameid}_{civ_name}_skill_data', json.dumps(game_skill_data))
        for skill in game_skill_data['skills'][civ_name]:
            if skill['to_civ'].lower() == player_civ.lower():
                ChatManager.send_msg_by_http(
                    gameid,
                    skill['dialogue'],
                    civ_name,
                    skill['to_civ'].lower(),
                    0
                )
        pair_dict = {'result': 'success'}
        return json.dumps(pair_dict)
    else:
        assert int(game_skill_data['turns']) < turns, \
            f"{civ_name} turns: {game_skill_data['turns']}, {turns}"
        result, game_skill_data = use_skills(
            data["gameinfo"], civ_name, config_data, game_skill_data
        )
        logger.info(f"{civ_name} getEarlyDecision async: {game_skill_data}")
        mq.set(f'multiplayer_{gameid}_{civ_name}_skill_data', json.dumps(game_skill_data))
    return result


@app.route('/reply_trade', methods=['POST'])
def replyTrade():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    civ_name_2 = data["civ2"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])['gameId']
    logger = logger.bind(**{"game_id": gameid})
    gameid2info = mq.get('gameid2info_' + gameid, {})
    player_civ = gameid2info['player_civ'][0]
    result = replyTrades(data["gameinfo"], civ_name, civ_name_2)
    if civ_name_2 == player_civ.lower():
        ChatManager.send_msg_by_http(
            gameid,
            json.loads(result)['response'],
            civ_name,
            civ_name_2,
            0
        )
    return result


@app.route('/wantsToDeclarationOfFrienship', methods=['POST'])
def wantsToDeclarationOfFrienship():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    civ_name_2 = data["civ2"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])['gameId']
    logger = logger.bind(**{"game_id": gameid})
    result = replyDeclarFrienship(data["gameinfo"], civ_name, civ_name_2)
    return result


@app.route('/getEnemyCitiesByPriority', methods=['POST'])
def getEnemyCitiesByPriority():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])['gameId']
    logger = logger.bind(**{"game_id": gameid})
    result = getOursEnemyCitiesByPriority(data["gameinfo"], civ_name, data["id"])
    return result


@app.route('/event_trigger', methods=['POST'])
def replyEventTrigger():
    global logger
    data = request.json
    gameid = utils.check_and_bind_gameid(data['gameId'])
    logger = logger.bind(**{"game_id": gameid})
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
                    "turns": turns,
                    "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event": event["text"]
                }
                mq.xadd(gameid, msg)
        if config_data.get("use_async_agent", 0):
            msg = {
                "game_id": gameid,
                "type": "get_early_decision_async",
                "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "turns": turns,
                "event": ""
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
