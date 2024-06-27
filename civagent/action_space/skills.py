from civsim.action_space.relations import RelationSpace

skills = [
    "Buy luxury goods from other countries",
    "Declare war on other countries ",
    "Make alliances with other countries",
    "Sharing real or fake intelligence with other countries",
    "Adjust the orientation of foreign relations with other countries",
    "Invite other countries to attack third parties",
    "Sign scientific research agreements with other countries"
]

skill_space = {
    'buy_luxury': {
        "type": "function",
        "function": {
            "name": "buy_luxury",
            "description": "Buy luxury goods from other countries when happiness is below zero ",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                    "demand_luxury": {"type": "string", "description": "Luxuries needed", "enum": "{luxury_space_list}"},
                    "offer_gold_per_turn": {"type": "integer", "description": "The amount of gold to pay per turn", "default": 10},
                },
                "required": ["to_civ", "demand_luxury", "offer_gold_per_turn"],
            },
            "example": "buy_luxury(to_civ='America', demand_luxury='Ivory', offer_gold_per_turn=10)",
        }
    },
    # Disinformation Deception
    'cheat': {
        "type": "function",
        "function": {
            "name": "cheat",
            "description": "Sharing intelligence, true or false, with other countries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                    "fake_news": {"type": "string", "description": "False information"},
                },
                "required": ["to_civ", "fake_news"],
            },
            "example": "cheat(to_civ='America', fake_news='America is going to attack you')",
        }
    },
    # Reflect on credibility
    # todo Should it also be made into a function?
    'change_closeness': {
        "type": "function",
        "function": {
            "name": "change_closeness",
            "description": "We will adjust the orientation of our diplomatic relations with other countries",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                    "relation": {"type": "string", "description": "Current relation location",
                                 "enum": [relation.name for relation in RelationSpace]},
                },
                "required": ["to_civ", "relation"],
            },
            "example": "change_closeness(to_civ='America')",
        }
    },
    # declare_war
    'declare_war': {
        "type": "function",
        "function": {
            "name": "declare_war",
            "description": "Declare war on other countries",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                },
                "required": ["to_civ"],
            },
            "example": "declare_war(to_civ='America')",
        }
    },
    # form_ally
    'form_ally': {
        "type": "function",
        "function": {
            "name": "form_ally",
            "description": "Make alliances with other countries",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                },
                "required": ["to_civ"],
            },
            "example": "form_ally(to_civ='America')",
        }
    },
    # common_enemy
    'common_enemy': {
        "type": "function",
        "function": {
            "name": "common_enemy",
            "description": "Invite some other country to attack a third country",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "The Civilization of Invitation", "enum": "{civ_names}"},
                    "enemy_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                },
                "required": ["to_civ", "enemy_civ"],
            },
            "example": "common_enemy(to_civ='Rome', enemy_civ='America')",
        }
    },
    # seek_peace
    'seek_peace': {
        "type": "function",
        "function": {
            "name": "seek_peace",
            "description": "Appeal for peace to the belligers",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                    "offer_gold": {"type": "integer", "description": "The number of gold coins offered", "default": 100},
                },
                "required": ["to_civ", "offer_gold"],
            },
            "example": "seek_peace(to_civ='America', offer_gold=100)",
        }
    },

    'research_agreement': {
        "type": "function",
        "function": {
            "name": "research_agreement",
            "description": "Spending 200 gold pieces to sign research agreements with other countries",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_civ": {"type": "string", "description": "Target civilization", "enum": "{civ_names}"},
                },
                "required": ["to_civ"],

            },
            "example": "research_agreement(to_civ='America')",
        }
    },

}
