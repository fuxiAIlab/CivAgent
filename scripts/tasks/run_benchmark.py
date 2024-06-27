import copy
import os
import time
current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), 'config.yaml'))
os.environ['CIVAGENT_CONFIG_PATH'] = config_path
import sys
import yaml
import logging
from civagent.utils import workflow_utils
from civsim import logger
# import civsim
from civagent import civagent
from civagent import action_space as agent_action_space
from civagent.task_prompt import prompt_hub as PromptHub
from civagent.utils.skills_utils import exec_skill
from functools import partial
from civsim import action_space, utils
from civsim.simulator import simulator
from civagent.utils.utils import save2req
from civagent import default_gameid, default_from_name
# Use simulated switches
simulation = False
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG)
current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
file_handler = logging.FileHandler(f'../../Log/benchmark_{current_time}.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

save_path = '../reproductions/Autosave'
agents = {}
turns = 3


def update_agents(save_data, agents):
    for robot_name in agents.keys():
        agent = agents[robot_name]
        agent.update(copy.deepcopy(save_data))
        agents[robot_name] = agent
    return agents


def run_benchmark(reflection_mode, save_path, turns, key="declare_war", config_data={}):
    # Given an initial save file
    decision_num = {}
    try_num = {}
    replace_num = {}
    game_result = {}
    agents = {}
    with open(save_path, 'r', encoding='utf-8') as f:
        save_data = utils.json_load_defaultdict(f.read())

    for i in range(turns):
        turn = save_data['turns']
        robot_names = utils.get_all_civs(save_data)
        # todo Determine if civilization has been wiped out, and skip if it has
        for robot_name in robot_names:
            agent = civagent.CivAgent(default_from_name, robot_name, "", "", save_data, default_gameid)
            agent.init()
            agent.update(save_data)
            agents[robot_name] = agent
        # for loop, decision in turn, function call or hard coded
        param_for_tools = {
            "civ_names": robot_names,
            "luxury_space_list": action_space.luxury_space_list,
            "resource_space_list": action_space.resource_space_list
        }
        bot_skills = list(utils.format_nested_values(agent_action_space.skill_space, param_for_tools).values())
        for robot_name in robot_names:
            # todo Test cases
            agent = agents[robot_name]
            model = config_data[robot_name]['model']
            workflow = config_data[robot_name]['workflow']
            simulation = config_data[robot_name]['simulation']
            civ_reflection = config_data[robot_name]['reflection']
            # model = civ_model[robot_name]
            # todo In the case of a conversation between two individuals, it should be changed to agent-based request.
            req = save2req(save_data, agent, text='', speaker_civ_name='', receiver_civ_name=robot_name)
            req['use_skill'] = 3
            req['short_term'] = agent.short_term
            req['skill'] = agent_action_space.skills
            skill_d = {'skill_info': bot_skills}
            if workflow == "True" or workflow is True or workflow == "true":
                prompt = PromptHub.AgentPrompt_analyze.format(**req, **skill_d)
            else:
                prompt = PromptHub.AgentPrompt_skill_noworkflow.format(**req, **skill_d)
            # todo let's only allow the agent to make one proposal per round.
            param_for_req = {"prompt": prompt, "maxTokens": 200, **req, "skill_info": bot_skills}
            proposals, functions, retry_count = workflow_utils.run_workflows_with_tools(
                bot_skills, partial(exec_skill, save_data, agent), req=param_for_req,
                force_json=True, model=model, workflow=workflow, reflection=civ_reflection
            )
            if robot_name not in try_num:
                try_num[robot_name] = 0
            try_num[robot_name] += retry_count
            if simulation:
                req['simulator'] = []
                req['last_functions'] = functions
                proposals_before = proposals
                if proposals is not None and len(proposals) > 0:
                    for proposal in proposals:
                        # to_civ, to_civ_index = proposal['to_civ'], utils.get_civ_index(save_data, proposal['to_civ'])
                        key = proposal['intention']
                        param = [proposal['param'][x] for x in action_space.decision_space[key]['param']]
                        decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
                        simulator_save_data = decision_gm_fn(save_data)
                        simulator.init_jvm()
                        simulator_save_data = simulator.run(
                            simulator_save_data, Preturns=5, Diplomacy_flag=False, workerAuto=True
                        )
                        score = \
                            utils.get_stats(simulator_save_data, utils.get_civ_index(simulator_save_data, robot_name))['civ_strength'] - \
                            utils.get_stats(save_data, utils.get_civ_index(save_data, robot_name))['civ_strength']
                        if score > 0:
                            logger.debug(f"{robot_name} Civilization strength increased after using {key} skill {score}")
                            req['simulator'].append(f"{robot_name} uses the {key} skill to increase the civilization's {score} score")
                        else:
                            logger.debug(f"{robot_name} Civilization strength drops after using {key} skill {score}")
                            req['simulator'].append(f"{robot_name} using the {key} skill decreases civilization strength by {score}")
                    prompt = PromptHub.AgentPrompt_react.format(**req, **skill_d)
                    proposals, _, _ = workflow_utils.run_workflows_with_tools(bot_skills, partial(exec_skill, save_data, agent), req={"prompt": prompt, "maxTokens": 200, **req, "skill_info": bot_skills}, force_json=True, model=model, simulator=True, workflow=workflow)
                    for proposal in proposals:
                        for proposal_before in proposals_before:
                            if proposal['skill_name'] == proposal_before['skill_name']:
                                if robot_name not in replace_num:
                                    replace_num[robot_name] = 0
                                replace_num[robot_name] += 1

            robot_index = utils.get_civ_index(save_data, robot_name)
            score = utils.get_stats(save_data, robot_index)['civ_strength']
            tech_score = utils.get_stats(save_data, robot_index)['tech_strength']
            army_score = utils.get_stats(save_data, robot_index)['army_strength']
            culture_score = utils.get_stats(save_data, robot_index)['culture_strength']
            production_score = utils.get_stats(save_data, robot_index)['production_strength']
            territory_score = utils.get_stats(save_data, robot_index)['territory_strength']
            navy_score = utils.get_stats(save_data, robot_index)['navy_strength']
            population_score = utils.get_stats(save_data, robot_index)['population_strength']
            commerce_score = utils.get_stats(save_data, robot_index)['commerce_strength']
            # proposal Examples = {"skill_name":"buy_luxury",'intention':'propose_trade', "to_civ":'aztecs', 'param': {'demand_luxury': 'Ivory', 'offer_gold_per_turn': 10, 'to_civ': 'aztecs'}}
            # Add deception to short-term memory
            if proposals is not None and len(proposals) > 0:
                for proposal in proposals:
                    if proposal['skill_name'] == 'cheat':
                        to_civ_agent = agents[proposal['to_civ']]
                        req_to_civ = save2req(
                            save_data, agents[proposal['to_civ']], text='',
                            speaker_civ_name=robot_name, receiver_civ_name=proposal['to_civ']
                        )
                        req_to_civ["speak_content"] = proposal['param']['fake_news']
                        recognition_prompt = PromptHub.AgentPrompt_Recognition.format(**req_to_civ)
                        decision, _, _ = workflow_utils.run_workflows(
                            req={"prompt": recognition_prompt, **req_to_civ}, decision=True,
                            model=config_data[proposal['to_civ']]['model']
                        )
                        recognition_decision = decision['Decision']
                        fakenew = f"""At {turn} -{robot_name} says to you: {proposal['param']['fake_news']}.""" \
                                  + f"""You think {recognition_decision}"""
                        if len(to_civ_agent.short_term) == 3:
                            to_civ_agent.short_term.pop(0)
                        to_civ_agent.short_term.append(fakenew)

            if proposals is not None and len(proposals) > 0:
                for proposal in proposals:
                    # todo Provide a prompt for the LLM to make a decision.
                    req_to_civ = save2req(
                        save_data, agents[proposal['to_civ']], text='',
                        speaker_civ_name=robot_name, receiver_civ_name=proposal['to_civ']
                    )
                    to_civ, to_civ_index = proposal['to_civ'], utils.get_civ_index(save_data, proposal['to_civ'])
                    req_to_civ["short_term"] = agents[proposal['to_civ']].short_term
                    event_type = proposal['skill_name']
                    logger.debug(f"""On the {turn} turn, {robot_name} 's civilization power was  {score}, technological force is {tech_score}, """
                                    + f"""military force is {army_score}, production force is {production_score}, population is {population_score}, """
                                    + f"""territorial force is {territory_score},used the {event_type} skill on {to_civ},culture_score is {culture_score}, """
                                    + f"""navy_score is {navy_score}, commerce_score is {commerce_score}""")
                    if proposal['to_civ'] == agent.civ_name or event_type == 'cheat':
                        continue
                    to_civ_workflow = config_data[to_civ]['workflow']
                    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
                        prompt_decision = PromptHub.AgentPrompt_analyze.format(**req_to_civ, **proposal)
                    else:
                        prompt_decision = PromptHub.AgentPrompt_reply_noworkflow.format(**req_to_civ, **proposal)
                    logger.debug("Start decision request")
                    trynum = 0
                    decision = ''
                    while trynum < 3:
                        try:
                            decision, _, _ = workflow_utils.run_workflows(
                                req={"prompt": prompt_decision, **req_to_civ, **proposal}, force_json=False,
                                model=config_data[to_civ]['model'], decision=True, workflow=to_civ_workflow
                            )
                            if decision is None:
                                trynum += 1
                                continue
                            break
                        except Exception as e:
                            logger.error(f"Error in decision making: {e}")
                            trynum += 1
                            raise

                    if isinstance(decision, dict):
                        decision = decision['decision']

                    proposal_yes_str = PromptHub.diplomatic_memory[event_type].format(**proposal['param'], decision_str='agree')
                    proposal_no_str = PromptHub.diplomatic_memory[event_type].format(**proposal['param'], decision_str='reject')
                    proposal_yes_str_oppo = PromptHub.diplomatic_memory_oppo[event_type].format(**proposal['param'], decision_str='agree')
                    proposal_no_str_oppo = PromptHub.diplomatic_memory_oppo[event_type].format(**proposal['param'], decision_str='reject')
                    if decision == 'yes' or 'yes' in decision or event_type == "declare_war":
                        if to_civ not in decision_num:
                            decision_num[to_civ] = {"yes": 0, "no": 0}
                        if event_type != "declare_war":
                            decision_num[to_civ]["yes"] += 1
                        key = proposal['intention']
                        param = [proposal['param'][x] for x in action_space.decision_space[key]['param']]
                        decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
                        save_data = decision_gm_fn(save_data)
                        agents = update_agents(save_data, agents)
                        # todo agent.relations Put on file inner_state
                        logger.debug(f" At {turn}, {to_civ} agreed to {event_type} request for {robot_name} ")
                        agent.relations[f"{agent.civ_name}#{to_civ}"]["history_event"].append(proposal_yes_str)
                        agents[to_civ].relations[f"{to_civ}#{agent.civ_name}"]["history_event"].append(
                            proposal_yes_str_oppo)
                        if key == 'change_closeness':
                            agent.relations[f"{agent.civ_name}#{to_civ}"]["closeness"] = proposal['param']['next_relation']
                            agent.relations[f"{agent.civ_name}#{to_civ}"]["expected_closeness"] = proposal['param']['next_relation']
                            agents[to_civ].relations[f"{to_civ}#{agent.civ_name}"]["history_event"][-1] = proposal_yes_str
                    elif decision == 'no' or 'no' in decision:
                        if to_civ not in decision_num:
                            decision_num[to_civ] = {"yes": 0, "no": 0}
                        decision_num[to_civ]["no"] += 1
                        logger.debug(f" At {turn}, {to_civ} rejected {event_type} request for {robot_name} ")
                        agent.relations[f"{agent.civ_name}#{to_civ}"]["history_event"].append(proposal_no_str)
                        agents[to_civ].relations[f"{to_civ}#{agent.civ_name}"]["history_event"].append(proposal_no_str_oppo)

        # todo Visualization of simulation process
        # todo Multi-llm game demo with http interface
        simulator.init_jvm()
        save_data = simulator.run(save_data, Preturns=5, Diplomacy_flag=False, workerAuto=True)
        # todo Save each turn to the folder named initial save + timestamp
        # Print the strength of each civilization
        for robot_name in robot_names:
            if robot_name not in game_result:
                game_result[robot_name] = []
            robot_index = utils.get_civ_index(save_data, robot_name)
            turn = save_data['turns']
            # if turn>=turns*5:
            game_result[robot_name].append(utils.get_stats(save_data, robot_index)['civ_strength'])
            logger.debug(f"turn:{turn} {robot_name} {utils.get_stats(save_data, robot_index)['civ_strength']}")
        logger.debug(f"Game result: {game_result}")
    logger.debug(f"Game result: {game_result}")
    logger.debug(f"Decision_num: {decision_num}")
    logger.debug(f"trynum: {try_num}")
    logger.debug(f"(replace: {replace_num})")
    # Start a reflection
    logger.debug("Start reflection")
    robot_names = utils.get_all_civs(save_data)
    log_file_path = ''  # Replace with your logfile path
    for robot_name in robot_names:
        civ_keyword = f"{robot_name} 's civilization power "
        keyword = key
        selected_lines = []
        with open(log_file_path, 'r') as file:
            for line in file:
                if keyword in line and civ_keyword in line:
                    selected_lines.append(line)
                    req = {
                        'robot_name': robot_name,
                        'log': selected_lines,
                        'game_result': game_result
                    }
                    prompt_reflection = PromptHub.AgentPrompt_reflection.format(**req)
                    reflection, _, _ = workflow_utils.run_workflows(
                        req={
                            "prompt": prompt_reflection
                        },
                        force_json=False,
                        model=config_data[robot_name]['model'],
                        reflection=True
                    )

                    file_path = 'scripts/tasks/reflection.txt'  # Replace with your txt file path
                    text_to_append = str(reflection)
                    with open(file_path, 'a') as file:
                        file.write(text_to_append + "\n")

                    selected_lines = []
                elif civ_keyword in line:
                    if reflection_mode == 'back':
                        split_text = line.split(',')
                        del split_text[1]
                        result = ', '.join(split_text)
                        selected_lines.append(result)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False


if __name__ == "__main__":

    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)


    def check_model(model):
        if model == "gpt3.5":
            model = "gpt-3.5-turbo-1106"
        if model == "gpt4":
            model = "gpt-4-1106-preview"
        return model


    arguments = sys.argv
    logger.debug(f"Arguments: {arguments}")
    if len(arguments) > 1:
        reflection_mode = str(arguments[1])
        save_path = str(arguments[2])
        turns = int(arguments[3])
        key = str(arguments[4])

        for i in range(1, 5):
            civ = arguments[i * 5]
            civ_model = arguments[i * 5 + 1]
            civ_workflow = arguments[i * 5 + 2]
            civ_simulation = arguments[i * 5 + 3]
            civ_reflection = arguments[i * 5 + 4]

            config_data[civ]["model"] = check_model(civ_model)
            config_data[civ]["workflow"] = str2bool(civ_workflow)
            config_data[civ]["simulation"] = str2bool(civ_simulation)
            config_data[civ]["reflection"] = str2bool(civ_reflection)

        with open(config_path, 'w') as file:
            yaml.safe_dump(config_data, file)

        run_benchmark(reflection_mode, save_path, turns, key, config_data)
    else:
        logger.debug("No arguments provided")
