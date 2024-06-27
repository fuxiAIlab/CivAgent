import json
from functools import partial
from civagent.civagent import CivAgent
from civagent.task_prompt.prompt_hub import AgentPrompt_react, AgentPrompt_chooseTech, AgentPrompt_chooseProduction, \
    AgentPrompt_analyze, AgentPrompt_reply_noworkflow, AgentPrompt_skill_noworkflow
from civsim.simulator.simulator import predicted, getTechToResarch_available, getProductionToBuild_available
from civsim.utils import json_load_defaultdict, get_civ_index, fix_civ_name
from civagent.utils import workflow_utils
from civagent import default_gameid, default_from_name
from civagent.utils.skills_utils import exec_skill
from civagent.utils.utils import save2req
from civagent import action_space as agent_action_space
import collections
from civsim import action_space, utils, logger


def use_skills(gameinfo, civ_name, skills, skill_num, tech, production, config_data):
    gameinfo_copy = gameinfo
    gameinfo = json_load_defaultdict(gameinfo)
    turn = gameinfo['turns']
    if isinstance(turn, collections.defaultdict):
        turn = 1
    else:
        turn = int(turn)
    robot_names = utils.get_all_civs(gameinfo)
    bot_skills = list(utils.format_nested_values(
        agent_action_space.skill_space,
        {
            "civ_names": robot_names,
            "luxury_space_list": action_space.luxury_space_list,
            "resource_space_list": action_space.resource_space_list
        }
    ).values())
    robot_name = civ_name.lower()
    # speaker = civ2_name.lower()
    agent = CivAgent(
        default_from_name, robot_name, "", "", gameinfo, default_gameid
    )
    agent.init()
    agent.update(gameinfo)
    req = save2req(
        gameinfo, agent, text='', speaker_civ_name='', receiver_civ_name=robot_name
    )
    req['use_skill'] = 3
    req['short_term'] = agent.short_term
    req['skill'] = agent_action_space.skills
    skill_d = {'skill_info': bot_skills}
    model = config_data[robot_name]['model']
    workflow = config_data[robot_name]['workflow']
    simulation = config_data[robot_name]['simulation']
    civ_reflection = config_data[robot_name]['reflection']
    if workflow == "True" or workflow is True or workflow == "true":
        prompt = AgentPrompt_analyze.format(**req, **skill_d)
    else:
        prompt = AgentPrompt_skill_noworkflow.format(**req, **skill_d)
    proposals, functions, retry_count = workflow_utils.run_workflows_with_tools(
        bot_skills, partial(exec_skill, gameinfo, agent),
        req={"prompt": prompt, "maxTokens": 200, **req, "skill_info": bot_skills},
        force_json=True, model=model, workflow=workflow, reflection=civ_reflection
    )
    if civ_name in skills:
        acc = skill_num[civ_name] / req['use_skill'] * 100
        logger.debug(
            f" In turn {turn - 1}, {civ_name} skill usage is {acc}%"
        )
        logger.debug(
            f" During turn {turn - 1}, {skills[civ_name]} these skills were not used "
        )
    skills[civ_name] = []
    skill_num[civ_name] = 0

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
                    logger.debug(
                        f"{robot_name} Civilization strength increased after using {key} skill {score}"
                    )
                    req['simulator'].append(
                        f"{robot_name} uses the {key} skill to increase the civilization's {score} score"
                    )
                else:
                    logger.debug(
                        f"{robot_name} Civilization strength drops after using {key} skill {score}"
                    )
                    req['simulator'].append(
                        f"{robot_name} using the {key} skill decreases civilization strength by {score}"
                    )
            prompt = AgentPrompt_react.format(**req, **skill_d)
            proposals, _, _ = workflow_utils.run_workflows_with_tools(
                skills, partial(exec_skill, gameinfo, agent),
                req={"prompt": prompt, "maxTokens": 200, **req, "skill_info": bot_skills},
                force_json=True, model=model, simulator=True, workflow=workflow
            )
    for proposal in proposals:
        skills[civ_name].append(proposal)

    req['available_tech'] = getTechToResarch_available(gameinfo_copy, civ_name)
    req['available_production'] = getProductionToBuild_available(gameinfo_copy, civ_name)
    tech_prompt = AgentPrompt_chooseTech.format(**req)
    production_prompt = AgentPrompt_chooseProduction.format(**req)

    tech_decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": tech_prompt, **req},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.debug(f"{robot_name} choose tech {tech_decision}")
    production_decision, _, _ = workflow_utils.run_workflows(
        req={"prompt": production_prompt, **req},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.debug(f"{robot_name} choose production {production_decision}")
    tech[robot_name] = tech_decision["decision"]
    production[robot_name] = {}
    if production_decision is not None:
        for city_name in production_decision:
            production[robot_name][city_name] = production_decision[city_name]
    pair_dict = {'result': 'sueccess'}
    json_data = json.dumps(pair_dict)
    return json_data


def reply_trades_from_skills(gameinfo, civ1_name, civ2_name, config_data):
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
    agent = CivAgent(
        default_from_name, robot_name, "", "", gameinfo, default_gameid
    )
    agent.init()
    agent.update(gameinfo)

    req = save2req(
        gameinfo, agent, text='', speaker_civ_name=speaker, receiver_civ_name=robot_name
    )
    req['short_term'] = agent.short_term
    proposal = {
        'param': {'civ_name': speaker},
        'skill_name': trade.format(**their_offers, **our_offers)
    }
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
        logger.debug(
            f"""On the {turn} turn, {civ1_name} agrees to {civ2_name}'s """
            + f"""{trade.format(**their_offers, **our_offers)} request --success"""
        )
    else:
        logger.debug(
            f"""On the {turn} turn, {civ1_name} denies {civ2_name}'s  """
            + f"""{trade.format(**their_offers, **our_offers)} request --fail"""
        )
    pair_dict = {"result": decision}
    json_data = json.dumps(pair_dict)
    return json_data


def reply_declarfrienship(gameinfo, civ1_name, civ2_name, config_data):
    gameinfo = json_load_defaultdict(gameinfo)
    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(
        default_from_name, robot_name, "", "", gameinfo, default_gameid
    )
    agent.init()
    agent.update(gameinfo)
    proposal = {
        'param': {'civ_name': speaker},
        'skill_name': 'Want to make a declaration of friendship with you'
    }
    req = save2req(
        gameinfo, agent, text='', speaker_civ_name=speaker, receiver_civ_name=robot_name
    )
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
