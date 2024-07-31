import ujson as json
from functools import partial
from civagent.civagent import CivAgent
from civagent.utils.prompt_utils import prompt_make
from civsim.simulator.simulator import predicted, getTechToResarchAvailable, getProductionToBuildAvailable
from civsim.utils import json_load_defaultdict, get_civ_index, fix_civ_name
from civagent.utils import workflow_utils
from civagent import default_gameid, default_from_name
from civagent.utils.skills_utils import exec_skill
from civagent.utils.utils import save2req
from civagent import action_space as agent_action_space
import collections
from civsim import action_space, utils, logger


def use_skills(gameinfo, civ_name, config_data, game_skill_data):
    gameinfo_copy = gameinfo
    gameinfo = json_load_defaultdict(gameinfo)
    turn = gameinfo['turns']
    if isinstance(turn, collections.defaultdict):
        turn = 1
    else:
        turn = int(turn)
    game_skill_data['turns'] = turn
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
    model = config_data[robot_name]['model'] if req.get('llm_model', '') == '' else req['llm_model']
    workflow = config_data[robot_name]['workflow']
    simulation = config_data[robot_name]['simulation']
    civ_reflection = config_data[robot_name]['reflection']
    if workflow == "True" or workflow is True or workflow == "true":
        prompt, llm_config = prompt_make('agent_analyze', context_dict={**req, **skill_d})
    else:
        prompt, llm_config = prompt_make('agent_skill_noworkflow', context_dict={**req, **skill_d})
    req["maxTokens"] = 200
    req["skill_info"] = bot_skills
    req['llm_config'] = llm_config
    req['llm_config']['skill_info'] = bot_skills
    proposals, functions, retry_count = workflow_utils.run_workflows_with_tools(
        bot_skills, partial(exec_skill, gameinfo, agent),
        req={**req, 'prompt': prompt},
        force_json=True, model=model,
        workflow=workflow, reflection=civ_reflection
    )
    if 'last_plans' in req:
        agent.last_plans = req['last_plans']
    if civ_name in game_skill_data['skills']:
        acc = game_skill_data['skill_num'][civ_name] / req['use_skill'] * 100
        logger.debug(
            f" In turn {turn - 1}, {civ_name} skill usage is {acc}%"
        )
        logger.debug(
            f" During turn {turn - 1}, {game_skill_data['skills'][civ_name]} these skills were not used "
        )
    game_skill_data['skills'][civ_name] = []
    game_skill_data['skill_num'][civ_name] = 0

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
            prompt, llm_config = prompt_make('agent_react', context_dict={**req})
            req['llm_config'] = llm_config
            proposals, _, _ = workflow_utils.run_workflows_with_tools(
                game_skill_data['skills'],
                partial(exec_skill, gameinfo, agent),
                req={**req, 'prompt': prompt},
                force_json=True, model=model,
                simulator=True, workflow=workflow
            )
    for proposal in proposals:
        conversation_prompt, llm_config = prompt_make(
            'agent_conversation', context_dict={**req, **{'proposal': proposal}}
        )
        req['llm_config'] = llm_config
        dialogue, _, _ = workflow_utils.run_workflows(
            req={**req, "prompt": conversation_prompt},
            model=model, force_json=False, decision=True, workflow=False
        )
        dialogue = dialogue['dialogue']
        proposal['dialogue'] = dialogue
        game_skill_data['skills'][civ_name].append(proposal)
    req['available_tech'] = getTechToResarchAvailable(gameinfo_copy, civ_name)
    req['available_production'] = getProductionToBuildAvailable(gameinfo_copy, civ_name)
    tech_prompt, llm_config = prompt_make('agent_choose_tech', context_dict={**req})
    req['llm_config'] = llm_config
    tech_decision, _, _ = workflow_utils.run_workflows(
        req={**req, "prompt": tech_prompt},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.debug(f"{robot_name} choose tech {tech_decision}")

    production_prompt, llm_config = prompt_make('agent_choose_production', context_dict={**req})
    req['llm_config'] = llm_config
    production_decision, _, _ = workflow_utils.run_workflows(
        req={**req, "prompt": production_prompt},
        model=model, force_json=False, decision=True, workflow=False
    )
    logger.debug(f"{robot_name} choose production {production_decision}")
    if tech_decision is not None:
        if 'decision' in tech_decision:
            game_skill_data['tech'][robot_name.capitalize()] = tech_decision['decision']
        elif 'Decision' in tech_decision:
            game_skill_data['tech'][robot_name.capitalize()] = tech_decision['Decision']
    game_skill_data['production'][robot_name.capitalize()] = {}
    if production_decision is not None:
        for city_name in production_decision:
            if production_decision[city_name] != 'AntiAircraft Gun':
                game_skill_data['production'][robot_name.capitalize()][city_name] = production_decision[city_name]
    pair_dict = {'result': 'sueccess'}
    result = json.dumps(pair_dict)
    return result, game_skill_data


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
    their_offers = {'theirOffers': []}
    our_offers = {'ourOffers': []}
    civ1_resource_dict = {}
    civ2_resource_dict = {}
    trade = 'Use {theirOffers} in exchange for our {ourOffers}'
    standard_dicts = [
        json.loads(json.dumps(item, default=lambda x: dict(x)))
        for item in gameinfo['civilizations'][ind_1]['tradeRequests']
    ]

    for our_offer in standard_dicts[0]['trade']['ourOffers']:
        civ1_resource_dict[our_offer['name']] = our_offer.get('amount', 'Any')
        our_offer['amount'] = our_offer.get('amount', 'one')
        if our_offer['type'] == 'WarDeclaration':
            our_offers['ourOffers'].append(f'attack {our_offer["name"]}')
        elif our_offer['type'] == 'Gold_Per_Turn':
            our_offers['ourOffers'].append(f'{our_offer["amount"]} gold each round')
        else:
            our_offers['ourOffers'].append(f'{our_offer["amount"]} {our_offer["name"]}')

    for their_offer in standard_dicts[0]['trade']['theirOffers']:
        civ2_resource_dict[their_offer['name']] = their_offer.get('amount', 'Any')
        their_offer['amount'] = their_offer.get('amount', 'one')
        if their_offer['type'] == 'WarDeclaration':
            their_offers['theirOffers'].append(f'attack {their_offer["name"]}')
        elif their_offer['type'] == 'Gold_Per_Turn':
            their_offers['theirOffers'].append(f'{their_offer["amount"]} gold each round')
        else:
            their_offers['theirOffers'].append(f'{their_offer["amount"]} {their_offer["name"]}')

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
    req['simulation_result'] = []
    if config_data[civ1_name.lower()]['simulation']:
        param = {
            'civ_name_1': civ1_name,
            'civ_name_2': civ2_name,
            'civ1_resource_dict': civ1_resource_dict,
            'civ2_resource_dict': civ2_resource_dict,
        }
        decision_gm_fn = action_space.decision_space['propose_common_trade']['func']('yes')(*param)
        simulator_save_data = decision_gm_fn(gameinfo)

        simulator_save_data = predicted(
            simulator_save_data, Preturns=10, Diplomacy_flag=False, workerAuto=True
        )
        civ_ind = utils.get_civ_index(simulator_save_data, civ1_name.lower())
        score = utils.get_stats(simulator_save_data, civ_ind)['civ_strength'] - \
                utils.get_stats(gameinfo, utils.get_civ_index(gameinfo, civ1_name))['civ_strength']

        if score > 0:
            logger.debug(
                f"After {civ1_name} agreed to the request, the civilization power was increased by {score}"
            )
            req['simulation_result'].append(
                f"After {civ1_name} agreed to the request, the civilization power was increased by {score}"
            )
        else:
            logger.debug(
                f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}"
            )
            req['simulation_result'].append(
                f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}"
            )

    proposal = {
        'param': {'civ_name': speaker},
        'skill_name': trade.format(**their_offers, **our_offers)
    }
    model = config_data[robot_name]['model'] if req.get('llm_model', '') == '' else req['llm_model']
    to_civ_workflow = config_data[robot_name]['workflow']
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision, llm_config = prompt_make('agent_analyze', context_dict={**req, **proposal})
    else:
        prompt_decision, llm_config = prompt_make('agent_reply_noworkflow', context_dict={**req, **proposal})
    req['llm_config'] = llm_config
    decision, _, _ = workflow_utils.run_workflows(
        req={**req, **proposal, "prompt": prompt_decision},
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
    result = json.dumps(pair_dict)
    return result


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
    model = config_data[robot_name]['model'] if req.get('llm_model', '') == '' else req['llm_model']
    to_civ_workflow = config_data[robot_name]['workflow']
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision, llm_config = prompt_make('agent_analyze', context_dict={**req, **proposal})
    else:
        prompt_decision, llm_config = prompt_make('agent_reply_noworkflow', context_dict={**req, **proposal})
    req['llm_config'] = llm_config
    decision, _, _ = workflow_utils.run_workflows(
        req={**req, **proposal, "prompt": prompt_decision},
        model=model, force_json=False, decision=True, workflow=to_civ_workflow
    )
    if isinstance(decision, dict):
        decision = decision['decision']
    pair_dict = {"result": decision}
    result = json.dumps(pair_dict)
    return result
