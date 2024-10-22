import os

from civagent.civagent import CivAgent
from civagent.utils.utils import save2req
from civsim.utils import json_load_defaultdict

default_from_name = "player"
default_gameid = "aa9092fe-61fb-4554-8102-d77d5c689851"


def test_civagent():
    path = os.path.join("..", "scripts", "reproductions", "Autosave-China-60")
    with open(path, "r") as f:
        save_data = f.read()
    gameinfo = json_load_defaultdict(save_data)
    agent = CivAgent(default_from_name, "china", "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    save2req(gameinfo, agent, text="", speaker_civ_name="", receiver_civ_name="china")
    assert True
