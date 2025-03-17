import re
import traceback
from datetime import datetime

import ujson as json

from civagent.skills import refection_before_skill_decision
from civagent.utils import memory_utils, workflow_utils
from civagent.utils.prompt_utils import event_trigger_make, generate_prompt
from civsim import logger, utils
from deployment.chatbot.chatmanager import ChatManager
from deployment.redis_mq import RedisStreamMQ

mq = RedisStreamMQ()


def trigger_next_turn(data, gameid):
    turns = int(data.get("turns", 1))
    updated_turns = int(mq.get(f"{gameid}_updated_turns", 0))
    gameid2info = mq.get("gameid2info_" + gameid, {})
    filepath = utils.get_savefile(gameid)
    save_data = utils.get_latest_savefile(filepath)
    civ_ind = utils.get_civ_index(save_data)
    civ_name = utils.get_civ_name(save_data, civ_ind)
    events = memory_utils.Memory.get_event_memory(save_data, civ_ind)
    events = [event for event in events if event["turns"] == turns - 1 and event["turns"] > updated_turns]
    logger.debug(f"events in trigger_next_turn at turns {turns-1}: {events}")
    if len(events) == 0:
        text = event_trigger_make("turn_event_default", {**gameid2info, **{"turns": turns - 1}})
        ChatManager.send_msg_by_http(gameid, text, from_civ="admin", is_group=1)
    else:
        for event in events:
            text = event["text"].replace("your", f"[{utils.fix_civ_name(civ_name)}]")
            text = text.replace("our", f"[{utils.fix_civ_name(civ_name)}]")
            text = event_trigger_make(
                "turn_event",
                {**gameid2info, **{"turns": event["turns"], "text": text}},
            )
            ChatManager.send_msg_by_http(gameid, text, from_civ="admin", is_group=1)
    return events, turns, updated_turns


def trigger_reflection(event_data, gameid):
    civ_name = event_data["event"]["civ_name"].lower()
    savefile_path = utils.get_savefile(gameid)
    save_data = utils.get_latest_savefile(savefile_path)
    inner_state_new = refection_before_skill_decision(save_data, civ_name, gameid)
    mq.set(f"multiplayer_{gameid}_{civ_name}_inner_state", json.dumps(inner_state_new))


def trigger_prologue(event_data, gameid):
    civ_names = event_data["event"]["civ_names"]
    gameid2info = mq.get("gameid2info_" + gameid, {})
    player_civ = gameid2info["player_civ"][0]
    try:
        req = {}
        req["other_civs"] = civ_names
        req["civ_count"] = len(civ_names)
        req["language"] = gameid2info["language"]
        result = workflow_utils.run(generate_prompt("prologue", req))
        prologue = dict(zip(req["other_civs"], result["prologue"]))
        for civ_name, response in prologue.items():
            if response:
                ChatManager.send_msg_by_http(
                    gameid,
                    response,
                    civ_name,
                    player_civ,
                    1,
                    {"bootstrap": 1},
                )
    except Exception as e:
        logger.error(f"error {e} {traceback.format_exc()}.")


def trigger_declare_war(event_data, gameid):
    gameid2info = mq.get("gameid2info_" + gameid, {})
    assert isinstance(gameid2info, dict), f"{gameid2info} is not a dict"
    player_civ = gameid2info.get("player_civ", "")
    text = event_data["event"]["text"]
    pattern = r"\b(?:" + "|".join(ChatManager.robot_names) + r")\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if len(matches) == 2:
        attack_civ_name, attacked_civ_name = matches[0].lower(), matches[1].lower()
    else:
        attack_civ_name, attacked_civ_name = matches[0].lower(), player_civ
    # Imitate player dialogue to enable proactive conversation by the agent.
    if attack_civ_name == player_civ:
        trigger_text = event_trigger_make("declare_war_event", gameid2info)
    elif attacked_civ_name == player_civ:
        trigger_text = event_trigger_make(
            "heard_war_event",
            {**gameid2info, **{"attack_civ_name": attack_civ_name}},
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
            {"bootstrap": 1},
        )


def send_mq_trigger(events, gameid, turns, updated_turns):
    # todo more event trigger
    declare_war_event = [
        event
        for event in events
        if "declare" in event["text"] and event["turns"] == turns - 1 and event["turns"] > updated_turns
    ]
    if len(declare_war_event) > 0:
        for event in declare_war_event:
            msg = {
                "game_id": gameid,
                "type": "declare_war",
                "turns": turns,
                "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": {"text": event["text"]},
            }
            mq.xadd(gameid, msg)
    # say prologue events
    chat_platform = mq.get(f"gameid2platform_{gameid}", "")
    is_prologued = mq.get(f"isprologued_{gameid}", 0)
    if chat_platform and not is_prologued:
        gameid2info = mq.get("gameid2info_" + gameid, {})
        robot_names = gameid2info.get("civ_robots", [])
        msg = {
            "game_id": gameid,
            "toBot": "",
            "type": "prologue",
            "turns": turns,
            "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": {"civ_names": robot_names},
        }
        mq.xadd(gameid, msg)
        mq.set("isprologued_" + gameid, 1)
    # reflection
    if int(turns) % 3 == 2:
        gameid2info = mq.get("gameid2info_" + gameid, {})
        robot_names = gameid2info.get("civ_robots", [])
        for civ_name in robot_names:
            msg = {
                "game_id": gameid,
                "toBot": civ_name,
                "type": "reflection",
                "turns": turns,
                "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": {"civ_name": civ_name},
            }
            mq.xadd(gameid, msg)
