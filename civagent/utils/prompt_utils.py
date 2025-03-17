import os
from typing import Any, Dict

import chevron

from civsim import logger
from deployment.redis_mq import RedisStreamMQ

# TODO: mq should not be used here.
mq = RedisStreamMQ()


def load_prompt(prompt_type: str, context: Dict[str, Any]):
    prompt_template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "templates",
    )
    with open(os.path.join(prompt_template_path, f"{prompt_type}.mu"), "r") as f:
        prompt = chevron.render(f.read(), context)
    return prompt


def load_inner_state(context):
    inner_state = mq.get(f"multiplayer_{context['gameid']}_{context['civ_name']}_inner_state", {})
    if inner_state == {}:
        inner_state["relationships"] = []
        civ_names = context["civ_names"]
        for civ in civ_names:
            if civ.lower() == context["civ_name"]:
                continue
            inner_state["relationships"].append(
                {
                    "civ_name": civ,
                    "type": "3Neutral",
                    "description": "There is calm between you, and nothing has happened yet.",
                }
            )
    return inner_state


def generate_prompt(prompt_type: str, context: Dict[str, Any]):
    guideline_prompt = load_prompt("guideline", context)
    environment_prompt = load_prompt("environment", context)
    analysis_prompt = load_prompt("analysis", load_inner_state(context))

    prompt = load_prompt(prompt_type, context)

    if prompt_type in [
        "reflection",
        "skill",
        "development",
        "intention_understand",
        "doublecheck_rewrite",
        "simulated_decision",
        "response_rewrite",
        "bargin_seller",
        "bargin_buyer",
    ]:
        complete_prompt = f"{guideline_prompt}\n{environment_prompt}\n{analysis_prompt}\n{prompt}"
    elif prompt_type in ["doublecheck"]:
        complete_prompt = f"{guideline_prompt}\n{prompt}"
    elif prompt_type in ["ask_for_object_identify", "propose_trade_identify", "prologue"]:
        complete_prompt = prompt

    logger.info(f"workflow: {prompt_type}")
    print(complete_prompt)

    if context.get("language", "simplified_chinese").lower() == "simplified_chinese":
        complete_prompt += load_prompt("reply_in_chinese", context)

    return complete_prompt


def response_make(intention: str, context_dict: Dict[str, Any]) -> str:
    if "chinese" in context_dict.get("language", "english").lower():
        from civagent.action_space.reply import (
            INTENTION_RESPONSE_CHINESE as intention_response,
        )
    else:
        from civagent.action_space.reply import INTENTION_RESPONSE as intention_response
    return intention_response[intention]


def admin_reply_make(intention: str, context_dict: Dict[str, Any]) -> str:
    default_language = "chinese" if "discord" not in context_dict.get("platform", "").lower() else "English"
    if "chinese" in context_dict.get("language", default_language).lower():
        from civagent.action_space.reply import ADMIN_REPLY_CHINESE as admin_reply
    else:
        from civagent.action_space.reply import ADMIN_REPLY as admin_reply
    text = str_make(admin_reply[intention], context_dict)
    return text


def event_trigger_make(intention: str, context_dict: Dict[str, Any]) -> str:
    if "chinese" in context_dict.get("language", "english").lower():
        from civagent.action_space.reply import (
            EVENT_TRIGGER_REPLY_CHINESE as event_reply,
        )
    else:
        from civagent.action_space.reply import EVENT_TRIGGER_REPLY as event_reply
    text = str_make(event_reply[intention], context_dict)
    return text


def str_make(T: str, d: Dict[str, Any]) -> str:
    return T.format(**d)


# def doublecheck_make(intention: str, context_dict: Dict[str, Any]) -> str:
#     if "chinese" in context_dict.get("language", "english").lower():
#         import civagent.task_prompt_chinese as task_prompt
#     else:
#         from civagent import task_prompt
#     return task_prompt.Doublecheck_question[intention]


# def intention_doublecheck(intention_result: Dict[str, Any], req: Dict[str, Any]) -> Dict[str, str]:
#     intention = intention_result["intention"]
#     if "offer" in intention_result:
#         offer_extract = []
#         for original_offer in intention_result["offer"]:
#             offer = copy.deepcopy(original_offer)
#             offer["amount"] = offer.get("amount", 1)
#             offer_extract.append(f'{offer["amount"]} {offer["item"]}')
#         intention_result["offer_str"] = ", ".join(offer_extract)
#     if "demand" in intention_result:
#         demand_extract = []
#         for original_demand in intention_result["demand"]:
#             demand = copy.deepcopy(original_demand)
#             demand["amount"] = demand.get("amount", 1)
#             demand_extract.append(f'{demand["amount"]} {demand["item"]}')
#         intention_result["demand_str"] = ", ".join(demand_extract)
#     if intention == "propose_trade" and len(intention_result.get("demand", [])) == 0:
#         intention = "propose_trade_gift"
#     if intention == "propose_trade" and len(intention_result.get("offer", [])) == 0:
#         intention = "ask_for_object"
#     if intention == "ask_for_object" and req.get("is_at_war", False):
#         intention = "ask_for_object_at_war"
#     response = doublecheck_make(intention, req)[0]
#     # todo Format of transfer Are you asking me for [{'category': 'Gold', 'item': 'Gold', 'amount': 100}]?
#     return {"response": str_make(response, intention_result)}
