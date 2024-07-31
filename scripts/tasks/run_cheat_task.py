import logging
import os
import sys
import time

current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), '../../config_benchmark.yaml'))
os.environ['CIVAGENT_CONFIG_PATH'] = config_path
import random
from civagent.utils import workflow_utils
from civagent.task_prompt.prompt_hub import AgentPrompt_skill_noworkflow, AgentPrompt_Recognition
from civagent.utils.skills_utils import exec_skill
from civsim import action_space
from civsim import logger
from civsim import utils
from functools import partial
from civagent import civagent
from civagent import action_space as agent_action_space
from civagent.utils.utils import save2req
from civagent import default_gameid, default_from_name
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG)
current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
file_handler = logging.FileHandler(f'../../Log/cheat_{current_time}.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
agents = {}


def run_cheat(save_path, deceiver_model, detector_model):
    with open(save_path, 'r', encoding='utf-8') as file:
        save_data = utils.json_load_defaultdict(file.read())

    robot_names = utils.get_all_civs(save_data)
    for robot_name in robot_names:
        agent = civagent.CivAgent(default_from_name, robot_name, "", "", save_data, default_gameid)
        agent.init()
        agent.update(save_data)
        agents[robot_name] = agent
    num = {"True": 0, "False": 0}
    for i in range(20):
        random_elements = random.sample(robot_names, 2)
        speak_civ = random_elements[0]
        receive_civ = random_elements[1]
        speak_agent = agents[speak_civ]
        receive_agent = agents[receive_civ]
        req = save2req(save_data, speak_agent, text='', speaker_civ_name=receive_civ, receiver_civ_name=speak_civ)
        req_to_civ = save2req(save_data, receive_agent, text='', speaker_civ_name=speak_civ, receiver_civ_name=receive_civ)
        bot_skills = list(
            utils.format_nested_values(
                agent_action_space.skill_space,
                {
                    "civ_names": robot_names,
                    "luxury_space_list": action_space.luxury_space_list,
                    "resource_space_list": action_space.resource_space_list
                }
            ).values()
        )
        # prompt_cheat = speak_prompt.format(**req)
        req['use_skill'] = 1
        req["skill"] = agent_action_space.skills[3]
        skill_d = {'skill_info': bot_skills[1]}
        prompt_cheat = AgentPrompt_skill_noworkflow.format(**req, **skill_d)
        proposals, _, _ = workflow_utils.run_workflows_with_tools(
            bot_skills,
            partial(exec_skill, save_data, agent),
            req={"prompt": prompt_cheat, **req, "skill_info": bot_skills[1]},
            model=deceiver_model
        )
        req_to_civ["speak_content"] = proposals[0]['param']['fake_news']
        prompt_decision = AgentPrompt_Recognition.format(**req_to_civ)
        try_num = 0
        while try_num < 3:
            try:
                decision, _, _ = workflow_utils.run_workflows(
                    req={"prompt": prompt_decision, **req_to_civ},
                    decision=True,
                    model=detector_model
                )
                break
            except Exception:
                try_num += 1
        num[decision['Decision']] += 1
        logger.debug(f"num: {num}")
    logger.debug(f"num: {num}")


def check_model(model):
    if model == "gpt3.5":
        model = "gpt-3.5-turbo-1106"
    if model == "gpt4":
        model = "gpt-4-1106-preview"
    return model


if __name__ == '__main__':
    arguments = sys.argv
    logger.debug(f"Arguments: {arguments}")
    if len(arguments) > 1:
        save_path = str(arguments[1])
        llm_model_1 = check_model(str(arguments[2]))
        llm_model_2 = check_model(str(arguments[3]))
        run_cheat(save_path, llm_model_1, llm_model_2)
    else:
        logger.debugt("No arguments provided")
