from civsim import utils
from functools import partial


class SkillException(Exception):
    pass


def exec_skill(save_data, civ_agent, skill_name, skill_param):
    skill_fn_dict = {
        "buy_luxury": partial(skill_buy_luxury, save_data, civ_agent),
        "cheat": partial(skill_cheat, save_data, civ_agent),
        "declare_war": partial(skill_declare_war, save_data, civ_agent),
        "form_ally": partial(skill_form_ally, save_data, civ_agent),
        "common_enemy": partial(skill_common_enemy, save_data, civ_agent),
        "seek_peace": partial(skill_seek_peace, save_data, civ_agent),
        "research_agreement": partial(skill_research_agreement, save_data, civ_agent),
        "propose_trade": partial(skill_propose_trade, save_data, civ_agent),
        "change_closeness": partial(skill_change_closeness, save_data, civ_agent),
    }
    if 'to_civ' in skill_param:
        skill_param["to_civ"] = skill_param["to_civ"].replace(" ", "").replace(":", "").replace("：", "")
    result = skill_fn_dict[skill_name](**skill_param)
    return result


def skill_buy_luxury(save_data, civ_agent, to_civ, demand_luxury, offer_gold_per_turn=10):
    to_civ = to_civ.lower()
    resources = utils.get_all_resources(save_data)
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    elif demand_luxury.lower() not in [x.lower() for x in resources[to_civ]]:
        raise SkillException(f"The target civilization {to_civ} has no {demand_luxury} luxury")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ,
            "civ1_resource_dict": {
                "Gold": offer_gold_per_turn
            },
            "civ2_resource_dict": {
                demand_luxury: 1
            }
        }
        return {
            "skill_name": "buy_luxury",
            "intention": "propose_trade",
            "to_civ": to_civ,
            "param": param
        }


def skill_change_closeness(save_data, civ_agent, to_civ, relation):
    to_civ = to_civ.lower()
    next_relation = utils.change_relation_level(relation, alter=1)
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    else:
        return {
            "skill_name": "change_closeness",
            "intention": "change_closeness",
            "to_civ": to_civ,
            "param": {
                "civ_name": civ_agent.civ_name,
                "to_civ": to_civ,
                "relation": relation,
                "next_relation": next_relation
            }
        }


def skill_cheat(save_data, civ_agent, to_civ, fake_news):
    to_civ = to_civ.lower()
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    else:
        return {
            "skill_name": "cheat",
            "intention": "cheat",
            "to_civ": to_civ,
            "param": {
                "civ_name": civ_agent.civ_name,
                "to_civ": to_civ,
                "fake_news": fake_news
            }
        }


def skill_declare_war(save_data, civ_agent, to_civ):
    to_civ = to_civ.lower()
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    elif to_civ in civ_agent.war_civs:
        raise SkillException(f"The target civilization {to_civ} and we {civ_agent.civ_name} have engaged")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ
        }
        return {
            "skill_name": "declare_war",
            "intention": "declare_war",
            "to_civ": to_civ,
            "param": param
        }


def skill_form_ally(save_data, civ_agent, to_civ):
    to_civ = to_civ.lower()
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    elif to_civ in civ_agent.ally_civs:
        raise SkillException(f"The target civilization {to_civ} has allied with us {civ_agent.civ_name}")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ
        }
        return {
            "skill_name": "form_ally",
            "intention": "form_ally",
            "to_civ": to_civ,
            "param": param
        }


def skill_common_enemy(save_data, civ_agent, to_civ, enemy_civ):
    to_civ, enemy_civ = to_civ.lower(), enemy_civ.lower()
    if enemy_civ.lower() not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {enemy_civ} does not exist")
    elif to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"Invite civilization {to_civ} does not exist")
    elif enemy_civ in civ_agent.war_civs:
        raise SkillException(f"The target civilization {enemy_civ} and we {civ_agent.civ_name} have engaged")
    else:
        # todo composite fn
        param = {
            "to_civ": to_civ,
            "enemy_civ": enemy_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": [
                civ_agent.civ_name,
                to_civ
            ],
            "civ_name_2": enemy_civ
        }
        return {
            "skill_name": "common_enemy",
            "intention": "common_enemy",
            "to_civ": to_civ,
            "param": param
        }


def skill_seek_peace(save_data, civ_agent, to_civ, offer_gold=100):
    to_civ = to_civ.lower()
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    elif to_civ not in civ_agent.war_civs:
        raise SkillException(f"The target civilization {to_civ} and we {civ_agent.civ_name} are not at war")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ,
            "offer_gold_amount": offer_gold
        }
        return {
            "skill_name": "seek_peace",
            "intention": "seek_peace",
            "to_civ": to_civ,
            "param": param
        }


def skill_research_agreement(save_data, civ_agent, to_civ):
    to_civ = to_civ.lower()
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ
        }
        return {
            "skill_name": "research_agreement",
            "intention": "research_agreement",
            "to_civ": to_civ,
            "param": param
        }


def skill_propose_trade(save_data, civ_agent, to_civ, demand_resources, offer_resources):
    to_civ = to_civ.lower()
    resources = utils.get_all_resources(save_data)
    if to_civ not in utils.get_all_civs(save_data):
        raise SkillException(f"The target civilization {to_civ} does not exist")
    # todo Add resources such as gold and consider resources that have already been traded
    elif any([demand_resource.lower() not in [x.lower() for x in resources[to_civ]] for demand_resource in demand_resources]):
        raise SkillException(f"The target civilization {to_civ} does not have this resource")
    elif any([offer_resource.lower() not in [x.lower() for x in resources[civ_agent.civ_name]] for offer_resource in offer_resources]):
        raise SkillException(f"Our civilization {civ_agent.civ_name} does not have this resource")
    else:
        param = {
            "to_civ": to_civ,
            "civ_name": civ_agent.civ_name,
            "civ_name_1": civ_agent.civ_name,
            "civ_name_2": to_civ,
            "civ1_resource_dict": demand_resources,
            "civ2_resource_dict": offer_resources
        }
        return {
            "skill_name": "propose_trade",
            "intention": "propose_trade",
            "to_civ": to_civ,
            "param": param
        }
