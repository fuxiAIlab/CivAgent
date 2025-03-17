import json
import os

import yaml

import civsim.simulator.simulator as simulator
from civagent.skills import make_skill_decision

default_skill_data = {
    "skills": {},
    "skill_num": {},
    "tech": {},
    "production": {},
    "turns": 0,
}


def test_skill():
    simulator.init_jvm()
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    config_path = os.path.join("..", "tests", "test_config.yaml")
    with open(path, "r") as f:
        save_data = f.read()
        save_data_json = json.loads(save_data)
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    for key in config:
        config_data = config[key]
        config_data.update({"skill_usage_count": 5})
        make_skill_decision(save_data_json, "china", config_data, default_skill_data)


test_skill()
