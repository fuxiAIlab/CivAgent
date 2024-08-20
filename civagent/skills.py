import copy
from functools import partial
from typing import Any, Dict, List, Tuple

import ujson as json

from civagent import action_space as agent_action_space
from civagent import default_from_name, default_gameid
from civagent.civagent import CivAgent
from civagent.utils import workflow_utils
from civagent.utils.prompt_utils import prompt_make
from civagent.utils.skills_utils import exec_skill
from civagent.utils.utils import save2req
from civsim import action_space, logger, utils
from civsim.simulator.simulator import (
    getProductionToBuildAvailable,
    getTechToResearchAvailable,
    predicted,
)
from civsim.utils import fix_civ_name, get_civ_index, json_load_defaultdict


def simulation_score(
    gameinfo: Dict[str, Any],
    robot_name: str,
    key: str,
    param: List,
) -> float:
    decision_gm_fn = action_space.decision_space[key]["func"]("yes")(*param)
    simulator_save_data = decision_gm_fn(gameinfo)
    simulator_save_data = predicted(
        simulator_save_data,
        turns=10,
        diplomacy_flag=False,
        worker_auto=True,
    )
    civ_ind = utils.get_civ_index(simulator_save_data, robot_name)
    civ_strength = utils.get_stats(simulator_save_data, civ_ind)["civ_strength"]
    civ_strength_2 = utils.get_stats(gameinfo, utils.get_civ_index(gameinfo, robot_name))["civ_strength"]
    score = civ_strength - civ_strength_2
    return score


def choose_tech(
    gameinfo_str: str,
    civ_name: str,
    model: str,
    req: Dict[str, Any],
) -> Dict[str, Any]:
    req["available_tech"] = getTechToResearchAvailable(gameinfo_str, civ_name)
    tech_prompt, llm_config = prompt_make("agent_choose_tech", context_dict={**req})
    req["llm_config"] = llm_config
    tech_decision, _, _ = workflow_utils.run_workflows(
        req={**req, "prompt": tech_prompt},
        model=model,
        force_json=False,
        is_reply=True,
        workflow=False,
    )
    return tech_decision


def choose_production(
    gameinfo_str: str,
    civ_name: str,
    model: str,
    req: Dict[str, Any],
) -> Dict[str, Any]:
    req["available_production"] = getProductionToBuildAvailable(gameinfo_str, civ_name)
    production_prompt, llm_config = prompt_make("agent_choose_production", context_dict={**req})
    req["llm_config"] = llm_config
    production_decision, _, _ = workflow_utils.run_workflows(
        req={**req, "prompt": production_prompt},
        model=model,
        force_json=False,
        is_reply=True,
        workflow=False,
    )
    return production_decision


def extract_trades_info(
    trade_info: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    their_offers: dict = {"theirOffers": []}
    our_offers: dict = {"ourOffers": []}
    civ1_resource_dict: dict = {}
    civ2_resource_dict: dict = {}
    for standard_our_offer in trade_info[0]["trade"].get("ourOffers", {}):
        our_offer = copy.deepcopy(standard_our_offer)
        civ1_resource_dict[our_offer["name"]] = our_offer.get("amount", "Any")
        our_offer["amount"] = our_offer.get("amount", 1)
        if our_offer.get("type", "") == "WarDeclaration":
            our_offers["ourOffers"].append(f'attack {our_offer["name"]}')
            civ1_resource_dict["DeclareWar_" + our_offer["name"]] = "Any"
            del civ1_resource_dict[our_offer["name"]]
        elif our_offer.get("type", "") == "Gold_Per_Turn":
            our_offers["ourOffers"].append(f'{our_offer["amount"]} gold each round')
        else:
            our_offers["ourOffers"].append(f'{our_offer["amount"]} {our_offer["name"]}')

    for standard_their_offer in trade_info[0]["trade"].get("theirOffers", {}):
        their_offer = copy.deepcopy(standard_their_offer)
        civ2_resource_dict[their_offer["name"]] = their_offer.get("amount", "Any")
        their_offer["amount"] = their_offer.get("amount", 1)
        if their_offer.get("type", "") == "WarDeclaration":
            their_offers["theirOffers"].append(f'attack {their_offer["name"]}')
            civ2_resource_dict["DeclareWar_" + their_offer["name"]] = "Any"
            del civ2_resource_dict[their_offer["name"]]
        elif their_offer.get("type", "") == "Gold_Per_Turn":
            their_offers["theirOffers"].append(f'{their_offer["amount"]} gold each round')
        else:
            their_offers["theirOffers"].append(f'{their_offer["amount"]} {their_offer["name"]}')
    return our_offers, their_offers, civ1_resource_dict, civ2_resource_dict


def use_skills(
    gameinfo_str: str,
    civ_name: str,
    config_data: Dict[str, Any],
    game_skill_data: Dict[str, Any],
) -> Tuple[str, Dict[str, Any]]:
    gameinfo = json_load_defaultdict(gameinfo_str)
    turn = gameinfo.get("turns", 0)
    game_skill_data["turns"] = turn
    robot_names = utils.get_all_civs(gameinfo)
    bot_skills = list(
        utils.format_nested_values(
            agent_action_space.skill_space,
            {
                "civ_names": robot_names,
                "luxury_space_list": action_space.luxury_space_list,
                "resource_space_list": action_space.resource_space_list,
            },
        ).values()
    )
    robot_name = civ_name.lower()
    # speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    req = save2req(gameinfo, agent, text="", speaker_civ_name="", receiver_civ_name=robot_name)
    req["use_skill"] = 3
    req["short_term"] = agent.short_term
    req["skill"] = agent_action_space.skills
    skill_d = {"skill_info": bot_skills}
    model = config_data[robot_name]["model"] if req.get("llm_model", "") == "" else req["llm_model"]
    workflow = config_data[robot_name]["workflow"]
    simulation = config_data[robot_name]["simulation"]
    civ_reflection = config_data[robot_name]["reflection"]
    if workflow == "True" or workflow is True or workflow == "true":
        prompt, llm_config = prompt_make("agent_analyze", context_dict={**req, **skill_d})
    else:
        prompt, llm_config = prompt_make("agent_skill_noworkflow", context_dict={**req, **skill_d})
    req["maxTokens"] = 200
    req["skill_info"] = bot_skills
    req["llm_config"] = llm_config
    req["llm_config"]["skill_info"] = bot_skills
    proposals, functions, retry_count = workflow_utils.run_workflows_with_tools(
        req["skill_info"],
        partial(exec_skill, gameinfo, agent),
        req={**req, "prompt": prompt},
        force_json=True,
        model=model,
        workflow=workflow,
        reflection=civ_reflection,
    )
    if "last_plans" in req:
        agent.last_plans = req["last_plans"]
    if civ_name in game_skill_data["skills"]:
        acc = game_skill_data["skill_num"][civ_name] / req["use_skill"] * 100
        logger.debug(f" In turn {turn - 1}, {civ_name} skill usage is {acc}%")
        logger.debug(f" During turn {turn - 1}, {game_skill_data['skills'][civ_name]} these skills were not used ")
    game_skill_data["skills"][civ_name] = []
    game_skill_data["skill_num"][civ_name] = 0

    if simulation:
        req["simulator"] = []
        req["last_functions"] = functions
        if proposals is not None and len(proposals) > 0:
            for proposal in proposals:
                key = proposal["intention"]
                param = [proposal["param"][x] for x in action_space.decision_space[key]["param"]]
                score = simulation_score(gameinfo, robot_name, key, param)
                if score > 0:
                    logger.debug(f"{robot_name} Civilization strength increased after using {key} skill {score}")
                    req["simulator"].append(
                        f"{robot_name} uses the {key} skill to increase the civilization's {score} score"
                    )
                else:
                    logger.debug(f"{robot_name} Civilization strength drops after using {key} skill {score}")
                    req["simulator"].append(
                        f"{robot_name} using the {key} skill decreases civilization strength by {score}"
                    )
            prompt, llm_config = prompt_make("agent_react", context_dict={**req})
            req["llm_config"] = llm_config
            req["llm_config"]["skill_info"] = bot_skills
            proposals, _, _ = workflow_utils.run_workflows_with_tools(
                req["skill_info"],
                partial(exec_skill, gameinfo, agent),
                req={**req, "prompt": prompt},
                force_json=True,
                model=model,
                simulator=True,
                workflow=workflow,
            )
    for proposal in proposals:
        conversation_prompt, llm_config = prompt_make(
            "agent_conversation", context_dict={**req, **{"proposal": proposal}}
        )
        req["llm_config"] = llm_config
        dialogue, _, _ = workflow_utils.run_workflows(
            req={**req, "prompt": conversation_prompt},
            model=model,
            force_json=False,
            is_reply=True,
            workflow=False,
        )
        dialogue = dialogue["dialogue"]
        proposal["dialogue"] = dialogue
        game_skill_data["skills"][civ_name].append(proposal)

    tech_decision = choose_tech(gameinfo_str, civ_name, model, req)
    logger.debug(f"{robot_name} choose tech {tech_decision}")
    production_decision = choose_production(gameinfo_str, civ_name, model, req)
    logger.debug(f"{robot_name} choose production {production_decision}")

    if tech_decision is not None:
        assert isinstance(tech_decision, dict)
        game_skill_data["tech"][robot_name] = tech_decision.get("decision", "")

    game_skill_data["production"][robot_name] = {}
    production_decision_result = production_decision.get("decision", {})

    if production_decision_result is not None:
        for city_name in production_decision_result:
            # The AntiAircraft Gun cannot be built in the early stages of the game
            if production_decision_result[city_name] != "AntiAircraft Gun":
                game_skill_data["production"][robot_name][city_name.lower()] = production_decision_result[city_name]
    pair_dict = {"result": "success"}
    result = json.dumps(pair_dict)
    return result, game_skill_data


def reply_trades_from_skills(gameinfo_str: str, civ1_name: str, civ2_name: str, config_data: Dict[str, Any]) -> str:
    gameinfo = json_load_defaultdict(gameinfo_str)
    ind_1 = get_civ_index(gameinfo, civ1_name)
    civ2_name = fix_civ_name(civ2_name)
    civ1_name = fix_civ_name(civ1_name)
    turn = gameinfo.get("turns", 0)
    trade = "Use {theirOffers} in exchange for our {ourOffers}"
    trade_info = copy.deepcopy(gameinfo["civilizations"][ind_1]["tradeRequests"])
    logger.info(f"Getting a transaction request {civ1_name} - {civ2_name}: {trade_info}")

    our_offers, their_offers, civ1_resource_dict, civ2_resource_dict = extract_trades_info(trade_info)

    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text="", speaker_civ_name=speaker, receiver_civ_name=robot_name)

    req["short_term"] = agent.short_term
    req["simulation_result"] = []
    if config_data[civ1_name.lower()]["simulation"]:
        logger.info(f"civ1_resource_dict :{civ1_resource_dict}, civ2_resource_dict :{civ2_resource_dict}")
        param = [civ1_name, civ2_name, civ1_resource_dict, civ2_resource_dict]
        score = simulation_score(gameinfo, robot_name, "propose_common_trade", param)
        if score > 0:
            logger.debug(f"After {civ1_name} agreed to the request, the civilization power was increased by {score}")
            req["simulation_result"].append(
                f"After {civ1_name} agreed to the request, the civilization power was increased by {score}"
            )
        else:
            logger.debug(f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}")
            req["simulation_result"].append(
                f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}"
            )

    proposal = {
        "param": {"civ_name": speaker},
        "skill_name": trade.format(**their_offers, **our_offers),
    }
    model = config_data[robot_name]["model"] if req.get("llm_model", "") == "" else req["llm_model"]
    to_civ_workflow = config_data[robot_name]["workflow"]
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision, llm_config = prompt_make("agent_analyze", context_dict={**req, **proposal})
    else:
        prompt_decision, llm_config = prompt_make("agent_reply_noworkflow", context_dict={**req, **proposal})
    req["llm_config"] = llm_config
    decision, _, _ = workflow_utils.run_workflows(
        req={**req, **proposal, "prompt": prompt_decision},
        model=model,
        force_json=False,
        is_reply=True,
        workflow=to_civ_workflow,
    )
    if isinstance(decision, dict):
        decision = decision["decision"]
    assert isinstance(decision, str)
    if decision == "yes":
        logger.debug(
            f"""On the {turn} turn, {civ1_name} agrees to {civ2_name}'s """
            + f"""{trade.format(**their_offers, **our_offers)} request --success"""
        )
    else:
        logger.debug(
            f"""On the {turn} turn, {civ1_name} denies {civ2_name}'s  """
            + f"""{trade.format(**their_offers, **our_offers)} request --fail"""
        )
    req["decision_result"] = decision
    req["civ1_resource_dict"] = civ1_resource_dict
    req["civ2_resource_dict"] = civ2_resource_dict
    req["decision_reason"] = utils.get_decision_reason(
        decision, "propose_common_trade", req, gameinfo, use_random=False
    )
    # response
    prompt_str, prompt_config = prompt_make("propose_trade", req)
    response, _, actual_prompt = workflow_utils.run_workflows(
        {
            "prompt": prompt_str,
            "llm_config": prompt_config,
        },
        force_json=False,
    )
    logger.info(f"response: {response}")
    pair_dict = {"result": decision, "response": response}
    result = json.dumps(pair_dict)
    return result


def reply_declarefrienship(gameinfo_str: str, civ1_name: str, civ2_name: str, config_data: Dict[str, Any]) -> str:
    gameinfo = json_load_defaultdict(gameinfo_str)
    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    proposal = {
        "param": {"civ_name": speaker},
        "skill_name": "Want to make a declaration of friendship with you",
    }
    req = save2req(gameinfo, agent, text="", speaker_civ_name=speaker, receiver_civ_name=robot_name)
    req["short_term"] = agent.short_term
    req["simulation_result"] = []
    if config_data[civ1_name.lower()]["simulation"]:
        param = [civ1_name, civ2_name]
        score = simulation_score(gameinfo, robot_name, "friendly_statement", param)
        if score > 0:
            logger.debug(f"After {civ1_name} agreed to the request, the civilization power was increased by {score}")
            req["simulation_result"].append(
                f"After {civ1_name} agreed to the request, the civilization power was increased by {score}"
            )
        else:
            logger.debug(f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}")
            req["simulation_result"].append(
                f"After {civ1_name} agreed to the request, the civilization power was reduced  by {score}"
            )

    model = config_data[robot_name]["model"] if req.get("llm_model", "") == "" else req["llm_model"]
    to_civ_workflow = config_data[robot_name]["workflow"]
    if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
        prompt_decision, llm_config = prompt_make("agent_analyze", context_dict={**req, **proposal})
    else:
        prompt_decision, llm_config = prompt_make("agent_reply_noworkflow", context_dict={**req, **proposal})
    req["llm_config"] = llm_config
    decision, _, _ = workflow_utils.run_workflows(
        req={**req, **proposal, "prompt": prompt_decision},
        model=model,
        force_json=False,
        is_reply=True,
        workflow=to_civ_workflow,
    )
    if isinstance(decision, dict):
        decision = decision["decision"]
    pair_dict = {"result": decision}
    result = json.dumps(pair_dict)
    return result
