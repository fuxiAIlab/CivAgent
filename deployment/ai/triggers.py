import re
from datetime import datetime

from civagent.utils import memory_utils
from civagent.utils.prompt_utils import event_trigger_make
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


def trigger_declare_war(event_data, gameid):
    gameid2info = mq.get("gameid2info_" + gameid, {})
    assert isinstance(gameid2info, dict), f"{gameid2info} is not a dict"
    text = event_data["event"]
    pattern = r"\b(?:" + "|".join(ChatManager.robot_names) + r")\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    attack_civ_name, attacked_civ_name = matches[0].lower(), matches[1].lower()
    # Imitate player dialogue to enable proactive conversation by the agent.
    if attack_civ_name == gameid2info.get("player_civ", ""):
        trigger_text = event_trigger_make("declare_war_event", gameid2info)
    elif attacked_civ_name == gameid2info.get("player_civ", ""):
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
                "event": event["text"],
            }
            mq.xadd(gameid, msg)
