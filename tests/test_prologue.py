import os

from civagent.templates.prompt_utils import generate_prompt
from civagent.utils import workflow_utils
from civsim import utils
from civsim.utils import json_load_defaultdict

default_from_name = "test"
default_gameid = "aa9092fe-61fb-4554-8102-d77d5c689851"


def test_prologue():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    with open(path, "r") as f:
        save_data = f.read()
    gameinfo = json_load_defaultdict(save_data)
    # agent = CivAgent(default_from_name, "china", "", "", gameinfo, default_gameid)
    # agent.init()
    # agent.update(gameinfo)
    # req = save2req(gameinfo, agent, text="", speaker_civ_name="rome", receiver_civ_name="china")

    civ_names = utils.get_all_civs(gameinfo)
    other_civs = [civ for civ in civ_names if civ != "china"]
    civ_count = len(other_civs)
    response = workflow_utils.run(generate_prompt("prologue", {"civ_count": civ_count}))
    assert len(other_civs) == len(response["prologue"])
    prologue = dict(zip(other_civs, response["prologue"]))

    print(prologue)


test_prologue()
