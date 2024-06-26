import json
import os
from functools import partial
import yaml
from civagent.civagent import CivAgent
from civagent.task_prompt.prompt_hub import AgentPrompt_react, AgentPrompt_chooseTech, AgentPrompt_chooseProduction, \
    AgentPrompt_analyze, AgentPrompt_reply_noworkflow, AgentPrompt_skill_noworkflow
from civsim.simulator.simulator import predicted, getTechToResarch_available, getProductionToBuild_available
from civsim.utils import json_load_defaultdict, get_civ_index, fix_civ_name
from civagent.utils import workflow_utils
from civagent import default_gameid, default_from_name
import civagent
from civagent.utils.skills_utils import exec_skill
from civagent.utils.utils import save2req
import civagent.skills
import collections
from civsim import action_space, utils, logger


def use_tools(gameinfo, civ_name, tools, tool_num, tech, production, config_data):
    gameinfo_copy = gameinfo
    gameinfo = json_load_defaultdict(gameinfo)
    turn = gameinfo['turns']
    if isinstance(turn, collections.defaultdict):
        turn = 1
    else:
        turn = int(turn)
    robot_names = utils.get_all_civs(gameinfo)
    bot_tools = list(utils.format_nested_values(
        civagent.skills.skill_space,
        {
            "civ_names": robot_names,
            "luxury_space_list": action_space.luxury_space_list,
            "resource_space_list": action_space.resource_space_list
        }
    ).values())
    robot_name = civ_name.lower()
    # speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    req = save2req(gameinfo, agent, text='', speaker_civ_name='', receiver_civ_name=robot_name)
    req['use_tool'] = 3
    req['short_term'] = agent.short_term
    req['skill'] = civagent.skills.skills
    tool = {'tool': bot_tools}
    model = config_data[robot_name]['model']
    workflow = config_data[robot_name]['workflow']
    simulation = config_data[robot_name]['simulation']
    civ_reflection = config_data[robot_name]['reflection']
    if workflow == "True" or workflow is True or workflow == "true":
        prompt = AgentPrompt_analyze.format(**req, **tool)
    else:
        prompt = AgentPrompt_skill_noworkflow.format(**req, **tool)
    proposals, functions, retry_count = workflow_utils.run_workflows_with_tools(
        bot_tools, partial(exec_skill, gameinfo, agent),
        req={"prompt": prompt, "maxTokens": 200, **req, "tool": bot_tools},
        force_json=True, model=model, workflow=workflow, reflection=civ_reflection
    )
    if civ_name in tools:
        acc = tool_num[civ_name] / req['use_tool'] * 100
        logger.warning(f" In turn {turn - 1}, {civ_name} skill usage is {acc}%")
        logger.warning(f" During turn {turn - 1},{tools[civ_name]} these skills were not used ")
    tools[civ_name] = []
    tool_num[civ_name] = 0

    if simulation:
        req['simulator'] = []
        req['last_functions'] = functions
        # proposals_before = proposals
        if proposals is not None and len(proposals) > 0:
            for proposal in proposals:
                # to_civ, to_civ_index = proposal['to_civ'], utils.get_civ_index(save_data, proposal['to_civ'])
                key = proposal['intention']
                param = [proposal['param'][x] for x in action_space.decision_space[key]['param']]
                decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
                simulator_save_data = decision_gm_fn(gameinfo)
                # simulator.init_jvm()
                # simulator_save_data = simulator.run(simulator_save_data, Preturns=5, Diplomacy_flag=False,
                #                                     workerAuto=True)
                simulator_save_data = predicted(
                    simulator_save_data, Preturns=10, Diplomacy_flag=False, workerAuto=True
                )
                civ_ind = utils.get_civ_index(simulator_save_data, robot_name)
                score = utils.get_stats(simulator_save_data, civ_ind)['civ_strength'] - \
                        utils.get_stats(gameinfo, utils.get_civ_index(gameinfo, robot_name))['civ_strength']
                if score > 0:
                    logger.info(f"{robot_name} Civilization strength increased after using {key} skill {score}")
                    req['simulator'].append(
                        f"{robot_name} uses the {key} skill to increase the civilization's {score} score"
                    )
                else:
                    logger.info(
                        f"{robot_name} Civilization strength drops after using {key} skill {score}"
                    )
                    req['simulator'].append(
                        f"{robot_name} using the {key} skill decreases civilization strength by {score}"
                    )
            prompt = AgentPrompt_react.format(**req, **tool)
            proposals, _, _ = workflow_utils.run_workflows_with_tools(
                tools, partial(exec_skill, gameinfo, agent),
                req={"prompt": prompt, "maxTokens": 200, **req, "tool": tools},
                force_json=True, model=model, simulator=True, workflow=workflow
            )
    for proposal in proposals:
        tools[civ_name].append(proposal)

    req['available_tech'] = getTechToResarch_available(gameinfo_copy, civ_name)
    req['available_production'] = getProductionToBuild_available(gameinfo_copy, civ_name)
    tech_prompt = AgentPrompt_chooseTech.format(**req)
    production_prompt = AgentPrompt_chooseProduction.format(**req)

    tech_decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": tech_prompt, **req},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.warning(f"{robot_name} choose tech {tech_decision}")
    production_decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": production_prompt, **req},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.warning(f"{robot_name} choose production {production_decision}")
    tech[robot_name] = tech_decision["decision"]
    production[robot_name] = {}
    if production_decision is not None:
        for city_name in production_decision:
            production[robot_name][city_name] = production_decision[city_name]
    pair_dict = {'result': 'sueccess'}
    json_data = json.dumps(pair_dict)
    return json_data


def get_wantsToDeclarationOfFrienship(gameinfo, civ1_name, civ2_name, config_data):
    gameinfo = json_load_defaultdict(gameinfo)

    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    proposal = {'param': {'civ_name': speaker}, 'skill_name': 'Want to make a declaration of friendship with you'}
    req = save2req(gameinfo, agent, text='', speaker_civ_name=speaker, receiver_civ_name=robot_name)
    req['short_term'] = agent.short_term
    model = config_data[robot_name]['model']
    to_civ_workflow = config_data[robot_name]['workflow']
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision = AgentPrompt_analyze.format(**req, **proposal)
    else:
        prompt_decision = AgentPrompt_reply_noworkflow.format(**req, **proposal)
    decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": prompt_decision, **req, **proposal},
        model=model, force_json=False, decision=True, workflow=to_civ_workflow
    )
    if isinstance(decision, dict):
        decision = decision['decision']
    pair_dict = {"result": decision}
    json_data = json.dumps(pair_dict)
    return json_data


def decision(gameinfo, civ1_name, civ2_name, config_data):
    gameinfo = json_load_defaultdict(gameinfo)
    ind_1 = get_civ_index(gameinfo, civ1_name)
    civ2_name = fix_civ_name(civ2_name)
    civ1_name = fix_civ_name(civ1_name)
    turn = gameinfo['turns']
    if isinstance(turn, collections.defaultdict):
        turn = 1
    else:
        turn = int(turn)
    their_offers = {}
    our_offers = {}
    standard_dicts = [
        json.loads(json.dumps(item, default=lambda x: dict(x)))
        for item in gameinfo['civilizations'][ind_1]['tradeRequests']
    ]
    if 'theirOffers' in standard_dicts[0]['trade']:
        their_offers = {'theirOffers': standard_dicts[0]['trade']['theirOffers'][0]}
    if 'ourOffers' in standard_dicts[0]['trade']:
        our_offers = {'ourOffers': standard_dicts[0]['trade']['ourOffers'][0]}

    if our_offers['ourOffers']['type'] == 'WarDeclaration':
        trade = 'Invite us to attack {ourOffers[name]}'
    elif their_offers['theirOffers']['type'] == 'Gold_Per_Turn':
        trade = 'Exchange {theirOffers[amount]} gold for our {ourOffers[name]} each round'
    else:
        trade = 'Use {theirOffers[name]} in exchange for our {ourOffers[name]}'
    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text='', speaker_civ_name=speaker, receiver_civ_name=robot_name)
    req['short_term'] = agent.short_term
    proposal = {'param': {'civ_name': speaker}, 'skill_name': trade.format(**their_offers, **our_offers)}
    model = config_data[robot_name]['model']
    to_civ_workflow = config_data[robot_name]['workflow']
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision = AgentPrompt_analyze.format(**req, **proposal)
    else:
        prompt_decision = AgentPrompt_reply_noworkflow.format(**req, **proposal)
    decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": prompt_decision, **req, **proposal},
        model=model, force_json=False, decision=True, workflow=to_civ_workflow
    )
    if isinstance(decision, dict):
        decision = decision['decision']
    if decision == 'yes':
        logger.warning(
            f"""On the {turn} turn, {civ1_name} agrees to {civ2_name}'s 
            {trade.format(**their_offers, **our_offers)} request --success"""
        )
    else:
        logger.warning(
            f"""On the {turn} turn, {civ1_name} denies {civ2_name}'s 
            {trade.format(**their_offers, **our_offers)} request --fail"""
        )
    pair_dict = {"result": decision}
    json_data = json.dumps(pair_dict)
    return json_data


def get_tools(skill, civ1_name, civ2_name, tools, tool_num, tech, production):
    if skill == "speek_peace":
        skill = "seek_peace"
    if skill == 'buy_luxury':
        json_data = get_tools_buy_luxury(skill, civ1_name, civ2_name, tools, tool_num)
    elif skill == 'common_enemy':
        json_data = get_tools_common_enemy(skill, civ1_name, tools, tool_num)
    elif skill == 'production_priority':
        if civ1_name not in production:
            pair_dict = {'result': ''}
            json_data = json.dumps(pair_dict)
        else:
            if civ2_name not in production[civ1_name]:
                pair_dict = {'result': ''}
                json_data = json.dumps(pair_dict)
            else:
                pair_dict = {'result': production[civ1_name][civ2_name]}
                json_data = json.dumps(pair_dict)
    elif skill == 'choose_technology':
        if civ1_name not in tech:
            pair_dict = {'result': ''}
            json_data = json.dumps(pair_dict)
        else:
            pair_dict = {'result': tech[civ1_name]}
            json_data = json.dumps(pair_dict)
    else:
        civ_name = fix_civ_name(civ1_name)
        if civ_name not in tools:
            tools[civ_name] = []
        if civ_name not in tool_num:
            tool_num[civ_name] = 0
        for tool in tools[civ_name]:
            if skill == tool['skill_name'] and civ2_name.lower() == tool['to_civ']:
                pair_dict = {'result': 'true'}
                json_data = json.dumps(pair_dict)
                logger.warning(f"{civ1_name} uses the {skill} skill --success on {civ2_name}")
                tools[civ_name].remove(tool)
                tool_num[civ_name] += 1
                return json_data
        pair_dict = {'result': 'false'}
        json_data = json.dumps(pair_dict)
    return json_data


def get_tools_buy_luxury(skill, civ1_name, civ2_name, tools, tool_num):
    civ_name = fix_civ_name(civ1_name)
    if civ_name not in tools:
        tools[civ_name] = []
    if civ_name not in tool_num:
        tool_num[civ_name] = 0
    for tool in tools[civ_name]:
        if skill == tool['skill_name'] and civ2_name.lower() == tool['to_civ']:
            pair_dict = {'result': 'true', 'gold': tool['param']['civ1_resource_dict']['Gold'],
                         'luxury': next(iter(tool['param']['civ1_resource_dict']))}
            json_data = json.dumps(pair_dict)
            logger.warning(f"{civ1_name} uses the {skill} skill --success on {civ2_name}")
            tool_num[civ_name] += 1
            return json_data
    pair_dict = {'result': 'false'}
    json_data = json.dumps(pair_dict)
    return json_data


def get_tools_common_enemy(skill, civ1_name, tools, tool_num):
    civ_name = fix_civ_name(civ1_name)
    if civ_name not in tools:
        tools[civ_name] = []
    if civ_name not in tool_num:
        tool_num[civ_name] = 0
    for tool in tools[civ_name]:
        if skill == tool['skill_name']:
            pair_dict = {'result': 'true', 'to_civ': tool['to_civ'].capitalize(),
                         'enemy_civ': tool['param']['enemy_civ'].capitalize()}
            json_data = json.dumps(pair_dict)
            logger.warning(
                f"""{civ1_name} uses the {skill} skill to invite {tool['to_civ']} 
                to attack {tool['param']['enemy_civ']}--success"""
            )
            tool_num[civ_name] += 1
            return json_data
    pair_dict = {'result': 'false'}
    json_data = json.dumps(pair_dict)
    return json_data
