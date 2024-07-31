from functools import partial
from .. import utils
from . import items

gm_command_space = {
    'gold': {
        "sub_item": ["gold"],
        "param": ["civ_name", "num"],
        "func": lambda civ_name, num: partial(
            utils.add_gold,
            civ_name=civ_name,
            gold_num=num
        )
    },
    'ask_for_object': {
        "sub_item": list({**items.luxury_space, **items.resource_space}.keys()),
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            utils.add_luxury_resource,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        ),
    },
    'propose_trade': {
        "sub_item": list({**items.luxury_space, **items.resource_space}.keys()),
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            utils.add_luxury_resource,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        ),
    },
    'propose_common_trade': {
        "sub_item": list({**items.luxury_space, **items.resource_space}.keys()),
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            utils.add_common_resource(),
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        ),
    },
    'friendly_statement': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.friendly_statement,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'declare_war': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.declare_war,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'open_borders': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.open_borders,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'research_agreement': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.research_agreement,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'form_mutual_defense': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.form_mutual_defense,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'form_ally': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.form_ally,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'seek_peace': {
        "sub_item": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            utils.make_peace,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        ),
    },
    'city': {
        "sub_item": ["city"],
        "param": ["civ_name_1", "civ_name_2", "city_name"],
        "func": lambda civ_name_1, civ_name_2, city_name: partial(
            utils.annex_city,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            city_name=city_name
        ),
    }
}
