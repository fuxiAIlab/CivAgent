import copy
import random
from typing import Any, Dict, List, Tuple, Union

import ujson as json

from civagent import action_space as agent_action_space
from civagent import default_from_name, default_gameid
from civagent.civagent import CivAgent
from civagent.config import config_data
from civagent.utils import workflow_utils
from civagent.utils.prompt_utils import generate_prompt
from civagent.utils.utils import save2req
from civsim import action_space, logger, utils
from civsim.simulator.simulator import (
    getProductionToBuildAvailable,
    getTechToResearchAvailable,
    predicted,
)
from civsim.utils import fix_civ_name, get_civ_index, json_load_defaultdict
from deployment.redis_mq import RedisStreamMQ

# TODO: mq should not be used here.
mq = RedisStreamMQ()


def refection_before_skill_decision(gameinfo: Dict[str, Any], civ_name: str, gameid: str) -> Union[str, Dict[str, Any]]:
    """
    The agent conducts a reflection on the overall game environment to optimize the make_skill_decision.
    """

    robot_name = civ_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text="", speaker_civ_name="", receiver_civ_name=robot_name)
    req["relationship_types"] = [relation.value for relation in action_space.RelationSpace]

    # Get and update the diplomatic skills that have been used.
    diplomatic_records = mq.get(f"diplomatic_records_{gameid}_{robot_name}", {})
    req["diplomatic_records"] = process_diplomatic_records(diplomatic_records)
    req["gameid"] = gameid

    # Reflection workflow
    refection_result = workflow_utils.run(generate_prompt("reflection", req))
    logger.info(f"refection result of {civ_name}: {refection_result}")

    return refection_result


def make_skill_decision(
    gameinfo: Dict[str, Any],
    civ_name: str,
    config_data: Dict[str, Any],
    game_skill_data: Dict[str, Any],
) -> Tuple[str, Dict[str, Any]]:
    """
    The decision - making behaviors of the Agent in each round.
    """

    robot_name = civ_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text="", speaker_civ_name="", receiver_civ_name=robot_name)
    req["skill_usage_count"] = min(config_data["skill_usage_count"], len(req["known_civs"]))
    game_skill_data["turns"] = req["round"]

    # Get the luxury goods and their quantities owned by each civilization.
    all_resources = utils.get_all_resources(gameinfo)
    req["existing_luxury_space"] = []
    for civ, resources in all_resources.items():
        existing_luxury_list = []
        for item, amount in resources.items():
            if item in action_space.luxury_space_list:
                existing_luxury_list.append({"item": item, "amount": amount})
        if existing_luxury_list:
            req["existing_luxury_space"].append({"civ_name": civ, "existing_luxury_list": existing_luxury_list})

    # Get and update the diplomatic skills that have been used.
    diplomatic_records_key = f"diplomatic_records_{gameinfo['gameId']}_{robot_name}"
    diplomatic_records = mq.get(diplomatic_records_key, {})
    logger.info(f"diplomatic_records: {diplomatic_records}")
    req["diplomatic_records"] = process_diplomatic_records(diplomatic_records)

    # Skill workflow
    skills = workflow_utils.run(generate_prompt("skill", req))
    random.shuffle(skills)

    # Get available_skills by checking
    game_skill_data["skills"][robot_name] = check_skill_availability(
        req, skills, robot_name, all_resources, diplomatic_records, diplomatic_records_key
    )

    # Technology and production choose
    gameinfo_str = json.dumps(gameinfo)
    req["available_technologies"] = getTechToResearchAvailable(gameinfo_str, civ_name)
    req["productions"] = getProductionToBuildAvailable(gameinfo_str, civ_name)

    # Technology and production workflow
    item_choose = workflow_utils.run(generate_prompt("development", req))

    # Technology and production save
    technology_choose = item_choose["technology_choose"]
    production_choose = item_choose["production_choose"]
    logger.info(f"{robot_name} choose tech: {technology_choose}")
    logger.info(f"{robot_name} choose production: {production_choose}")
    game_skill_data["tech"][robot_name] = {robot_name: technology_choose}
    game_skill_data["production"][robot_name] = {}

    # Production check
    for city, production in production_choose.items():
        if production != "AntiAircraft Gun":
            game_skill_data["production"][robot_name][city.lower()] = production

    return json.dumps({"result": "success"}), game_skill_data


def check_skill_availability(req, skills, robot_name, all_resources, diplomatic_records, diplomatic_records_key):
    """
    Get available_skills by checking.
    """

    available_skills = []
    for skill in skills:
        logger.info(f"{robot_name} used skill: {skill}")
        skill_target = skill.get("target", "").lower()
        skill_type = skill.get("type", "").lower()
        params = skill.get("params", {})

        # Skill type check
        if skill_type != "chat_to_all" and skill_type not in action_space.decision_space.keys():
            logger.info(f"Skill error, {skill_type} does not exist.")
            continue

        # Skill target check
        if skill_type != "chat_to_all" and skill_target not in req["known_civs"]:
            logger.info(f"Skill error, {skill_target} does not known.")
            continue

        # Skill repeat check
        if not check_repeat(available_skills, skill):
            continue

        # Luxury check
        if skill_type == "buy_luxury" and not check_luxury(all_resources, skill):
            continue

        # Skill usage check and update
        if skill_type in ["research_agreement", "common_enemy", "mutual_defense", "form_ally"]:
            flag, new_records_to_target = check_diplomatic_records(diplomatic_records, skill, req["round"])
            if not flag:
                logger.info(f"{robot_name} have recently used skill {skill_type} on {skill_target}")
                continue
            new_records_to_target.append({"skill_type": skill_type, "round": req["round"]})
            diplomatic_records[skill_target] = new_records_to_target
            mq.set(diplomatic_records_key, diplomatic_records)

        # Reply to the translation
        if req.get("language", "english").lower() == "simplified_chinese":
            robot_name_reply = agent_action_space.civ_name_spaces[robot_name]
            skill_target_reply = agent_action_space.civ_name_spaces[skill_target]
            reply_content = f"{robot_name_reply} (to {skill_target_reply}): {skill['dialogue']}"
        else:
            reply_content = f"{robot_name} (to {skill_target}): {skill['dialogue']}"

        available_skills.append(
            {
                "skill_name": skill_type,
                "to_civ": skill_target,
                "dialogue": reply_content,
                "param": params,
            }
        )

    return available_skills


def check_repeat(available_skills, current_skill):
    skill_target = current_skill.get("target", "").lower()
    skill_type = current_skill.get("type", "").lower()

    if any(skill_type == skill_data["skill_name"] for skill_data in available_skills):
        logger.warning(f"In this round, {skill_type} has been used.")
        return False
    if any(skill_target == skill_data["to_civ"] for skill_data in available_skills):
        logger.warning(f"In this round, {skill_target} has already had a skill used on it.")
        return False

    # In a single turn, Skill A and Skill B will not be used simultaneously
    if skill_type == "chat":
        for skill_data in available_skills:
            if skill_data["skill_name"] == "chat_to_all":
                logger.warning("In this round, chat or chat_to_all has been used.")
                return False
    if skill_type == "chat_to_all":
        for skill_data in available_skills:
            if skill_data["skill_name"] == "chat":
                logger.warning("In this round, chat or chat_to_all has been used.")
                return False
    return True


def check_luxury(all_resources, skill):
    skill_target = skill.get("target", "").lower()
    params = skill.get("params", {})

    if skill_target not in all_resources:
        logger.warning(f"Skill error, {skill_target} does not have any luxury goods.")
        return False
    else:
        for item, amount in params.items():
            if item not in action_space.luxury_space_list:
                logger.warning(f"Skill error, {skill_target} does not have luxury good - {item}.")
                return False
            if amount > all_resources[skill_target][item]:
                logger.warning(
                    f"Skill error, {skill_target} does not have a sufficient quantity of luxury goods. {amount} > {all_resources[skill_target][item]}"
                )
                return False
    return True


def check_diplomatic_records(diplomatic_records, skill, round):
    skill_type = skill.get("type", "").lower()
    skill_target = skill.get("target", "").lower()
    new_records_to_target = []
    flag = True
    for record in diplomatic_records.get(skill_target, []):
        if skill_type == record["skill_type"]:
            if round < record["round"] + config_data["skill_cooldown_turns"]:
                flag = False
                logger.warning(f"Skill error, {skill_target} is still on cooldown.")
            else:
                new_records_to_target.append(record)
    return flag, new_records_to_target


def process_diplomatic_records(diplomatic_records) -> List:
    diplomatic_record_list = []
    for civ, records in diplomatic_records.items():
        diplomatic_record_list.append({"civ_name": civ, "diplomatic_records_to_target": records})
    return diplomatic_record_list


def simulation_evaluate(
    gameinfo: Dict[str, Any],
    robot_name: str,
    key: str,
    param: List,
) -> Tuple[float, float, float]:
    """
    Calculate the score of the Agent after N rounds when using this skill through a game emulator.
    """

    # Get the simulated fuction and data
    decision_gm_fn = action_space.decision_space[key]["func"]("yes")(*param)
    simulator_save_data = decision_gm_fn(gameinfo)

    # Predicted result of simulation
    simulator_save_data = predicted(
        simulator_save_data,
        turns=10,
        diplomacy_flag=False,
        worker_auto=True,
    )

    # Get civ strength
    civ_ind = utils.get_civ_index(simulator_save_data, robot_name)
    civ_strength_new = utils.get_stats(simulator_save_data, civ_ind)["civ_strength"]
    civ_strength_old = utils.get_stats(gameinfo, utils.get_civ_index(gameinfo, robot_name))["civ_strength"]

    # Compute simulated score
    diff = civ_strength_new - civ_strength_old
    mean = (civ_strength_new + civ_strength_old) / 2
    if mean == 0:
        score = 0
    else:
        score = diff / mean

    return civ_strength_new, civ_strength_old, score


def extract_trades_info(
    trade_info: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    their_offers: dict = {"theirOffers": []}
    our_offers: dict = {"ourOffers": []}
    civ1_resource_dict: dict = {}
    civ2_resource_dict: dict = {}

    if not trade_info:
        return their_offers, our_offers, civ1_resource_dict, civ2_resource_dict
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


def reply_trades_from_skills(gameinfo_str: str, civ1_name: str, civ2_name: str, config_data: Dict[str, Any]) -> str:
    """
    Make a reply in relation to transaction - related skills, e.g., including research agreement, common enemy, mutual defense, and so on.
    """

    gameinfo = json_load_defaultdict(gameinfo_str)
    ind_1 = get_civ_index(gameinfo, civ1_name)
    civ2_name = fix_civ_name(civ2_name)
    civ1_name = fix_civ_name(civ1_name)
    turn = gameinfo.get("turns", 0)
    trade = "Use {theirOffers} in exchange for our {ourOffers}"
    trade_info = copy.deepcopy(gameinfo["civilizations"][ind_1]["tradeRequests"])
    logger.info(f"Getting a transaction request {civ1_name} - {civ2_name}: {trade_info}")

    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text="", speaker_civ_name=speaker, receiver_civ_name=robot_name)
    req["short_term"] = agent.short_term

    our_offers, their_offers, civ1_resource_dict, civ2_resource_dict = extract_trades_info(trade_info)

    # Simulation
    req["simulation_result"] = []
    if config_data[robot_name]["simulation"]:
        params = [robot_name, speaker, civ1_resource_dict, civ2_resource_dict]
        logger.info(f"simulated params in reply trade: {params}")

        # Get simulated score
        civ_strength_new, civ_strength_old, score = simulation_evaluate(
            gameinfo, robot_name, "propose_common_trade", params
        )

        if civ_strength_new - civ_strength_old > score:
            decision = "yes"
        elif civ_strength_new - civ_strength_old >= 0:
            # The scores are close, enter the simulation workflow
            req["civ_strength_new"] = civ_strength_new
            req["civ_strength_old"] = civ_strength_old
            req["skill"] = "propose_common_trade"
            response = workflow_utils.run(generate_prompt("simulated_decision", req))
            decision = response["decision_result"].lower()
        else:
            decision = "no"

    if decision == "yes":
        logger.info(
            f"""On the {turn} turn, {civ1_name} agrees to {civ2_name}'s """
            + f"""{trade.format(**their_offers, **our_offers)} request --success"""
        )
    else:
        # The request was denied, delete the most recently used skill.
        key = f"diplomatic_records_{gameinfo['gameId']}_{speaker}"
        diplomatic_records = mq.get(key, {})
        target_records = diplomatic_records.get(robot_name, [])
        if len(target_records) > 0 and target_records[-1]["type"] != "buy_luxury":
            diplomatic_records[robot_name] = diplomatic_records[robot_name][:-1]
            mq.set(key, diplomatic_records)
        logger.info(
            f"""On the {turn} turn, {civ1_name} denies {civ2_name}'s  """
            + f"""{trade.format(**their_offers, **our_offers)} request --fail"""
        )

    req["civ1_resource_dict"] = civ1_resource_dict
    req["civ2_resource_dict"] = civ2_resource_dict
    req["decision_result"] = decision
    req["decision_reason"] = utils.get_decision_reason(
        decision, "propose_common_trade", req, gameinfo, use_random=False
    )

    # Response rewrite baesd on decision_result and decision_reason
    response = workflow_utils.run(generate_prompt("response_rewrite", req))

    if req.get("language", "english").lower() == "simplified_chinese":
        civ1_name_reply = agent_action_space.civ_name_spaces[civ1_name.lower()]
        civ2_name_reply = agent_action_space.civ_name_spaces[civ2_name.lower()]
    reply_content = f"{civ1_name_reply} (to {civ2_name_reply}): {response['reply']}"

    logger.info(f"{civ1_name} response to {civ2_name}: {response['reply']}")

    return json.dumps({"result": decision, "reason": reply_content})


def reply_declarefrienship(gameinfo_str: str, civ1_name: str, civ2_name: str, config_data: Dict[str, Any]) -> str:
    gameinfo = json_load_defaultdict(gameinfo_str)
    robot_name = civ1_name.lower()
    speaker = civ2_name.lower()
    round = gameinfo.get("turns", 0)

    agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)

    req = save2req(gameinfo, agent, text="", speaker_civ_name=speaker, receiver_civ_name=robot_name)
    req["short_term"] = agent.short_term

    req["simulation_result"] = []
    if config_data[robot_name]["simulation"]:
        params = [robot_name, speaker]
        civ_strength_new, civ_strength_old, score = simulation_evaluate(
            gameinfo, robot_name, "propose_common_trade", params
        )

        if civ_strength_new - civ_strength_old > score:
            decision = "yes"
        elif civ_strength_new - civ_strength_old >= 0:
            # The scores are close, enter the simulation workflow
            req["civ_strength_new"] = civ_strength_new
            req["civ_strength_old"] = civ_strength_old
            req["skill"] = "Want to make a declaration of friendship with you"
            response = workflow_utils.run(generate_prompt("simulated_decision", req))
            decision = response["decision_result"].lower()
        else:
            decision = "no"

    if decision == "yes":
        logger.debug(f"On the {round} round, {civ1_name} agreed to {civ2_name}'s request")
    else:
        logger.debug(f"On the {round} round, {civ1_name} disagreed to {civ2_name}'s request")

    return json.dumps({"result": decision})


# def reply_declarefrienship(gameinfo_str: str, civ1_name: str, civ2_name: str, config_data: Dict[str, Any]) -> str:
#     gameinfo = json_load_defaultdict(gameinfo_str)
#     robot_name = civ1_name.lower()
#     speaker = civ2_name.lower()
#     agent = CivAgent(default_from_name, robot_name, "", "", gameinfo, default_gameid)
#     agent.init()
#     agent.update(gameinfo)
#     proposal = {
#         "param": {"civ_name": speaker},
#         "skill_name": "Want to make a declaration of friendship with you",
#     }
#     req = save2req(gameinfo, agent, text="", speaker_civ_name=speaker, receiver_civ_name=robot_name)
#     req["short_term"] = agent.short_term
#     req["simulation_result"] = []
#     if config_data[civ1_name.lower()]["simulation"]:
#         params = [civ1_name, civ2_name]
#         civ_strength_new, civ_strength_old, score = simulation_evaluate(
#             gameinfo, robot_name, "propose_common_trade", params
#         )
#         if civ_strength_new - civ_strength_old > score:
#             logger.debug(f"After {civ1_name} agreed to the request, the civilization power was increased")
#             req["simulation_result"].append(
#                 f"After {civ1_name} agreed to the request, the civilization power was increased"
#             )
#         else:
#             logger.debug(f"After {civ1_name} agreed to the request, the civilization power was reduced")
#             req["simulation_result"].append(
#                 f"After {civ1_name} agreed to the request, the civilization power was reduced"
#             )

#     model = config_data[robot_name]["model"] if req.get("llm_model", "") == "" else req["llm_model"]
#     to_civ_workflow = config_data[robot_name]["workflow"]
#     if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
#         prompt_decision, llm_config = prompt_make("agent_analyze", context_dict={**req, **proposal})
#     else:
#         prompt_decision, llm_config = prompt_make("agent_reply_noworkflow", context_dict={**req, **proposal})
#     req["llm_config"] = llm_config
#     decision, _, _ = workflow_utils.run_workflows(
#         req={**req, **proposal, "prompt": prompt_decision},
#         model=model,
#         force_json=False,
#         is_reply=True,
#         workflow=to_civ_workflow,
#     )
#     if isinstance(decision, dict):
#         decision = decision["decision"]
#     pair_dict = {"result": decision}
#     result = json.dumps(pair_dict)
#     return result
