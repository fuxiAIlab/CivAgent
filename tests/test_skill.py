import json
import os

import yaml

import civsim.simulator.simulator as simulator
from civagent.skills import reply_declarefrienship, reply_trades_from_skills, use_skills
from civsim import utils

default_skill_data = {
    "skills": {},
    "skill_num": {},
    "tech": {},
    "production": {},
    "turns": 0,
}


def test_skill():
    simulator.init_jvm()
    path = os.path.join("..", "scripts", "reproductions", "Autosave-China-60")
    config_path = os.path.join("..", "tests", "test_config.yaml")
    with open(path, "r") as f:
        save_data = f.read()
        save_data_json = json.loads(save_data)
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    for key in config:
        config_data = config[key]
        use_skills(save_data, "china", config_data, default_skill_data)
        save_data_json = utils.trade_offer(save_data_json, "aztecs", "china", {"Ivory": 1}, {"Gold": 20})
        save_data = json.dumps(save_data_json)
        reply_trades_from_skills(save_data, "china", "aztecs", config_data)
        reply_declarefrienship(save_data, "china", "aztecs", config_data)
    assert True
