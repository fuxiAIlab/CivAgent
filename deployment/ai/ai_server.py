from datetime import datetime
from typing import Any, Dict

import ujson as json
from flask import Flask, request
from gevent.pywsgi import WSGIServer

import civsim.simulator.simulator as simulator
from civagent.config import config_data
from civagent.skills import make_skill_decision
from civagent.utils.memory_utils import ChatMemory, Memory
from civagent.utils.prompt_utils import event_trigger_make
from civagent.utils.skills_utils import get_skills
from civsim import logger, utils
from civsim.utils import json_load_defaultdict
from deployment.ai.free_chat import process
from deployment.ai.strategy import (
    buyLuxury,
    canSignResearchAgreementsWith,
    chooseNextConstruction,
    chooseTechToResearch,
    commonEnemy,
    getOursEnemyCitiesByPriority,
    hasAtLeastMotivationToAttack,
    replyDeclareFriendship,
    replyTrades,
    wantsToSignDeclarationOfFriendship,
    wantsToSignDefensivePact,
)
from deployment.ai.triggers import (
    send_mq_trigger,
    trigger_declare_war,
    trigger_next_turn,
    trigger_prologue,
    trigger_reflection,
)
from deployment.chatbot.chatmanager import ChatManager
from deployment.redis_mq import RedisStreamMQ

mq = RedisStreamMQ()
simulator.init_jvm()
app = Flask(__name__)


def check_turns(data: Dict[str, Any], gameid: str) -> bool:
    gameid2info = mq.get("gameid2info_" + gameid, {})
    turns = gameid2info.get("turns", 0)
    robot_names = gameid2info.get("civ_robots", [])
    player_civ = gameid2info["player_civ"][0]
    if data["civ1"].lower() == player_civ.lower():
        return False
    if "barbarians" in robot_names:
        robot_names.remove("barbarians")
    robot_nums = len(robot_names)
    robot_index = [x.lower() for x in robot_names].index(data["civ1"].lower())
    if turns % robot_nums != robot_index or turns < config_data["use_skills_turns"]:
        return False
    return True


@app.route("/healthz")
def healthz():
    return "OK", 200


@app.route("/decision", methods=["POST"])
def decision():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    civ_name_2 = data["civ2"].lower()
    gameinfo = json_load_defaultdict(data["gameinfo"])
    gameid = utils.check_and_bind_gameid(gameinfo["gameId"])
    logger = logger.bind(**{"game_id": gameid})

    default_skill_data = {
        "skills": {},
        "skill_num": {},
        "tech": {},
        "production": {},
        "turns": 0,
    }
    game_skill_data = mq.get(f"multiplayer_{gameid}_{civ_name}_skill_data", default_skill_data)

    if data["skill"] == "research_agreement":
        result, game_skill_data = canSignResearchAgreementsWith(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "form_ally":
        result, game_skill_data = wantsToSignDefensivePact(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "declare_war":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data, 20
        )
    elif data["skill"] == "change_closeness":
        result, game_skill_data = wantsToSignDeclarationOfFriendship(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data
        )
    elif data["skill"] == "choose_technology":
        result, game_skill_data = chooseTechToResearch(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "production_priority":
        result, game_skill_data = chooseNextConstruction(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "seek_peace":
        result, game_skill_data = hasAtLeastMotivationToAttack(
            data["gameinfo"], civ_name, civ_name_2, game_skill_data, 10
        )
    elif data["skill"] == "common_enemy":
        result, game_skill_data = commonEnemy(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "buy_luxury":
        result, game_skill_data = buyLuxury(data["gameinfo"], civ_name, civ_name_2, game_skill_data)
    elif data["skill"] == "open_borders":
        result, game_skill_data = get_skills(data["skill"], civ_name, civ_name_2, game_skill_data)
    else:
        assert False, f'Invalid skill: {data["skill"]}'

    mq.set(f"multiplayer_{gameid}_{civ_name}_skill_data", json.dumps(game_skill_data))
    return result


@app.route("/get_early_decision", methods=["POST"])
def getEarlyDecision():
    global logger
    data = request.json
    if len(data["gameinfo"]) < 2:
        gameid = data["gameid"]
        assert len(gameid) > 1, f"null gameid in getEarlyDecision: {gameid}"
        savefile_path = utils.get_savefile(gameid)
        save_data = utils.get_latest_savefile(savefile_path)
    else:
        save_data = json_load_defaultdict(data["gameinfo"])
    civ_name = data["civ1"].lower()
    # todo no save_data at the first turn
    turns = int(save_data.get("turns", 0))
    gameid = utils.check_and_bind_gameid(save_data["gameId"])
    logger = logger.bind(**{"game_id": gameid})
    if not check_turns(data, gameid):
        return json.dumps({"result": ""})
    is_async = data.get("is_async", 0)
    game_info = mq.get("gameid2info_" + gameid, {})
    player_civ = game_info["player_civ"][0]
    default_skill_data = {
        "skills": {},
        "skill_num": {},
        "tech": {},
        "production": {},
        "turns": 0,
    }
    # {'skills': {'china': [{'skill_name': 'form_ally', 'to_civ': 'rome', 'dialogue': 'Rome, our shared values and mutual respect make us natural allies. Let us unite for a prosperous future.', 'param': {}}, {'skill_name': 'buy_luxury', 'to_civ': 'egypt', 'dialogue': 'Egypt, your fine wines are renowned. Shall we trade for mutual benefit?', 'param': {'demand': {'Wine': 1}, 'offer': {'Gold': 10}}}, {'skill_name': 'common_enemy', 'to_civ': 'aztecs', 'dialogue': "Rome, the Aztecs' growing strength concerns us both. Shall we stand together against this threat?", 'param': {'enemy_civ': 'aztecs'}}]}, 'skill_num': {}, 'tech': {'china': {'china': 'Education'}}, 'production': {'china': {'beijing': 'Library', 'shanghai': 'Library', 'guangzhou': 'Library', 'nanjing': 'Library', 'xian': 'Library', 'chengdu': 'Library', 'hangzhou': 'Library'}}, 'turns': 60}
    game_skill_data = mq.get(f"multiplayer_{gameid}_{civ_name}_skill_data", default_skill_data)
    if not is_async:
        player_civ_ind = utils.get_civ_index(save_data, player_civ)
        event_history = Memory.get_event_memory(save_data, player_civ_ind)
        war_events = [
            event
            for event in event_history
            if int(event.get("turns", 0)) >= turns and "declared war" in event.get("text", "")
        ]
        if int(game_skill_data.get("turns", 0)) >= int(save_data.get("turns", 0)) and len(war_events) < 1:
            logger.info(f"{civ_name} use_async in getEarlyDecision: {game_skill_data}")
            game_skill_data = game_skill_data
        else:
            result, game_skill_data = make_skill_decision(save_data, civ_name, config_data, game_skill_data)
            logger.debug(f"{civ_name} war_events of {player_civ_ind}: {war_events}")
            logger.info(f"{civ_name} getEarlyDecision without use_async: {game_skill_data}")
            mq.set(
                f"multiplayer_{gameid}_{civ_name}_skill_data",
                json.dumps(game_skill_data),
            )
        for skill in game_skill_data["skills"].get(civ_name, []):
            if skill["to_civ"].lower() == player_civ.lower():
                reply = f"{skill['dialogue']}"
                if config_data.get("debug_mode", 0):
                    reply += f"\n\n{skill}"
                debug_info = {"skill_name": skill["skill_name"], "param": skill.get("param", {})}
                ChatManager.send_msg_by_http(gameid, reply, civ_name, skill["to_civ"].lower(), 0, debug_info=debug_info)
                ChatManager.send_msg_by_http(gameid, reply, civ_name, skill["to_civ"].lower(), 1)
            else:
                # todo group chat is just for debugging
                ChatManager.send_msg_by_http(gameid, skill["dialogue"], civ_name, skill["to_civ"].lower(), 1)
        pair_dict = {"result": "success"}
        return json.dumps(pair_dict)
    else:
        assert int(game_skill_data.get("turns", 0)) < turns, f"{civ_name} turns: {game_skill_data['turns']}, {turns}"
        result, game_skill_data = make_skill_decision(save_data, civ_name, config_data, game_skill_data)
        logger.info(f"{civ_name} getEarlyDecision async: {game_skill_data}")
        mq.set(f"multiplayer_{gameid}_{civ_name}_skill_data", json.dumps(game_skill_data))
        return result


@app.route("/reply_trade", methods=["POST"])
def replyTrade():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    civ_name_2 = data["civ2"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])["gameId"]
    logger = logger.bind(**{"game_id": gameid})
    gameid2info = mq.get("gameid2info_" + gameid, {})
    player_civ = gameid2info["player_civ"][0]
    # todo consider skill["dialogue"]
    result = replyTrades(data["gameinfo"], civ_name, civ_name_2)
    result_d = json.loads(result)
    if civ_name_2 == player_civ.lower():
        debug_info = {"result": result_d.get("result", {}), "skill": "reply_trade"}
        ChatManager.send_msg_by_http(gameid, result_d["reason"], civ_name, civ_name_2, 0, debug_info=debug_info)
        ChatManager.send_msg_by_http(gameid, result_d["reason"], civ_name, civ_name_2, 1)
    else:
        ChatManager.send_msg_by_http(gameid, result_d["reason"], civ_name, civ_name_2, 1)
    return result


@app.route("/wantsToDeclarationOfFriendship", methods=["POST"])
def wantsToDeclarationOfFriendship():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    civ_name_2 = data["civ2"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])["gameId"]
    logger = logger.bind(**{"game_id": gameid})
    result = replyDeclareFriendship(data["gameinfo"], civ_name, civ_name_2)
    return result


@app.route("/getEnemyCitiesByPriority", methods=["POST"])
def getEnemyCitiesByPriority():
    global logger
    data = request.json
    civ_name = data["civ1"].lower()
    gameid = json_load_defaultdict(data["gameinfo"])["gameId"]
    logger = logger.bind(**{"game_id": gameid})
    result = getOursEnemyCitiesByPriority(data["gameinfo"], civ_name, data["id"])
    return result


@app.route("/event_trigger", methods=["POST"])
def replyEventTrigger():
    global logger
    data = request.json
    gameid = utils.check_and_bind_gameid(data["gameId"])
    logger = logger.bind(**{"game_id": gameid})
    logger.info(f"event_trigger data: {data}")
    if utils.time_diff_in_minutes(data["addTime"]) >= 2:
        logger.debug(f"event_trigger time out: {data}")
        pass
    elif data.get("type", "") == "next_turn":
        data = data["data"]
        events, turns, updated_turns = trigger_next_turn(data, gameid)
        send_mq_trigger(events, gameid, turns, updated_turns)
        if config_data.get("use_async_agent", 0):
            msg = {
                "game_id": gameid,
                "type": "get_early_decision_async",
                "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "turns": turns,
                "event": "",
            }
            mq.xadd(gameid, msg)
        mq.set(f"{gameid}_updated_turns", int(turns) - 1)
    elif data.get("type", "") == "declare_war":
        trigger_declare_war(data["data"], gameid)
    elif data.get("type", "") == "prologue":
        trigger_prologue(data["data"], gameid)
    elif data.get("type", "") == "reflection":
        trigger_reflection(data["data"], gameid)
    return "success"


@app.route("/reply_free_chat", methods=["POST"])
def replyFreeChat():
    data = request.json
    game_id = utils.check_and_bind_gameid(data["gameId"])
    logger.info(f"reply_free_chat data: {data}")
    if utils.time_diff_in_minutes(data["addTime"]) >= 2:
        if data.get("type", "") == "chat":
            chatmemory = ChatMemory(**data["data"])
            gameid2info = mq.get("gameid2info_" + game_id, {})
            ChatManager.send_msg_by_http(
                data["gameId"],
                f"{chatmemory.notify}" + event_trigger_make("time_out_event", gameid2info),
                from_civ=chatmemory.toCiv,
                to_civ=chatmemory.fromCiv,
                is_group=chatmemory.isGroup,
            )
    else:
        process(ChatMemory(**data["data"]))
    return "success"


http_server = WSGIServer(("0.0.0.0", 2335), app)
http_server.serve_forever()
