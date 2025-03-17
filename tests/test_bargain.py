import os

import civsim.simulator.simulator as simulator
from civagent.civagent import CivAgent
from civagent.utils.utils import save2req
from civsim.utils import json_load_defaultdict

default_from_name = "player"
default_gameid = "aa9092fe-61fb-4554-8102-d77d5c689851"


def test_civagent():
    simulator.init_jvm()
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    with open(path, "r") as f:
        save_data = f.read()
    gameinfo = json_load_defaultdict(save_data)
    agent = CivAgent(default_from_name, "china", "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    req = save2req(gameinfo, agent, text="", speaker_civ_name="", receiver_civ_name="china")
    border_info = agent.get_resource_border(req, gameinfo)
    req["identify_result"] = {
        "offer": [{"category": "Luxury", "item": "Silver", "amount": "Any"}],
        "demand": [{"category": "Gold", "item": "Gold", "amount": "100"}],
    }
    req["border_info"] = {"Gold": -153}
    bottom_line = agent.get_trade_bottom_line(req, gameinfo, "seller")
    print({"border_info": border_info, "bottom_line": bottom_line})
    simulator.close_jvm()
    assert True
