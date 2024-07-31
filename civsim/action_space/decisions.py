from functools import partial
from civsim.action_space import gm_command
from civsim.simulator import simulator

decision_reason_space = {
    'ask_for_object_yes': ['He is much stronger than me'],
    'ask_for_object_no': ['I am not afraid of him', 'I am too far away from him'],
    'change_closeness_up': ['He has persuaded me, we have common interests'],
    'change_closeness_down': ['His words do not convince me'],
    'change_closeness_nochange': ['Not enough to change the diplomatic level'],
    'chat_continue': [''],
    'chat_close': [''],
    'nonsense_close': ['Not interested in what he has to say'],
    # 'force_surrender_resist': ['I am stubborn', 'The international situation will be in my favor'],
    # 'force_surrender_surrender': ['He is too powerful', 'I think he will treat me well as a vassal'],
    'form_ally_yes': ['Together we prosper', 'We face a common threat'],
    'form_ally_no': ['He is not my best choice for an ally', 'He is too weak', 'He is not strong enough', 'I am too far away from him'],
    'friendly_statement_yes': ['He is my friend'],
    'friendly_statement_no': ['Our relationship is not so good'],
    'mutual_defense_yes': ['Together we prosper', 'We face a common threat'],
    'mutual_defense_no': ['He is not my best choice', 'He is too weak', 'He is not strong enough', 'I am too far away from him', 'Our relationship is not so good'],
    'open_border_yes': ['He has also opened borders to me', 'I feel his goodwill', 'We are too far away from each other, no threat to each other', 'I know he just needs to pass through'],
    'open_border_no': ['I feel threatened by him', 'His reputation is not good', 'Our relationship is not so good'],
    'propose_trade_yes': ['This trade is fair', 'We have a good relationship'],
    'propose_trade_no': ['This trade is unfair', 'Our relationship is not so good'],
    'research_agreement_yes': ['This is very helpful to me', 'I feel his goodwill'],
    'research_agreement_no': ['I feel threatened by him, I do not want to help him', 'Our relationship is not so good'],
    'seek_peace_yes': ['He is really stubborn', 'There are no permanent enemies', 'I admit my defeat'],
    'seek_peace_no': ['I will win in the end', 'I am only temporarily at a disadvantage', 'The battle has just begun']
}

identity_fn = lambda x: x
identity_partial_fn = lambda *args: identity_fn

decision_space = {
    # Peace status + threat - Demand items or become a vassal
    'ask_for_object': {
        "decisions": {"yes": "Agree to demand", "no": "Disagree to demand"},
        # todo Integrate various tradable items
        "param": gm_command.gm_command_space['ask_for_object']['param'],
        "func": lambda decision: gm_command.gm_command_space['ask_for_object']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Flattery
    'change_closeness': {
        "decisions": {"yes": "Increase diplomatic relations", 'no': "Do not change diplomatic level"},
        # todo Need to add GM commands: Condemnation, relationship downgrade; Display relationship on the interface.
        "param": [],
        "func": lambda decision: identity_partial_fn,
    },
    # Alliance
    'form_ally': {
        "decisions": {"yes": "Agree to form an alliance", "no": "Disagree to form an alliance"},
        "param": gm_command.gm_command_space['form_ally']['param'],
        "func": lambda decision: gm_command.gm_command_space['form_ally']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Friendly statement
    'friendly_statement': {
        "decisions": {"yes": "Agree to make a friendly statement", "no": "Disagree to make a friendly statement"},
        "param": gm_command.gm_command_space['friendly_statement']['param'],
        "func": lambda decision: gm_command.gm_command_space['friendly_statement']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Mutual defense
    'mutual_defense': {
        "decisions": {"yes": "Agree to a mutual defense pact", "no": "Disagree to a mutual defense pact"},
        "param": gm_command.gm_command_space['form_mutual_defense']['param'],
        "func": lambda decision: gm_command.gm_command_space['form_mutual_defense']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Open borders
    'open_border': {
        "decisions": {"yes": "Agree to open borders", "no": "Disagree to open borders"},
        "param": gm_command.gm_command_space['open_borders']['param'],
        "func": lambda decision: gm_command.gm_command_space['open_borders']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Difference from ask_for_object is that there is no threat, pure trade
    'propose_trade': {
        "decisions": {"yes": "Agree to trade", "no": "Disagree to trade"},
        "param": gm_command.gm_command_space['propose_trade']['param'],
        "func": lambda decision: gm_command.gm_command_space['propose_trade']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Common trade
    'propose_common_trade': {
        "decisions": {"yes": "Agree to trade", "no": "Disagree to trade"},
        "param": gm_command.gm_command_space['propose_common_trade']['param'],
        "func": lambda decision: gm_command.gm_command_space['propose_common_trade']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Research cooperation agreement
    'research_agreement': {
        "decisions": {"yes": "Agree to research cooperation", "no": "Disagree to research cooperation"},
        "param": gm_command.gm_command_space['research_agreement']['param'],
        "func": lambda decision: gm_command.gm_command_space['research_agreement']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # At war
    'seek_peace': {
        "decisions": {"yes": "Agree to a peace treaty", "no": "Disagree to a peace treaty"},
        "param": gm_command.gm_command_space['seek_peace']['param'],
        "func": lambda decision: gm_command.gm_command_space['seek_peace']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Persuade to deal with a common enemy
    "common_enemy": {
        "decisions": {"yes": "Agree with the notion of a common enemy", "no": "Disagree with the notion of a common enemy"},
        # todo change param
        "param": gm_command.gm_command_space['declare_war']['param'],
        "func": lambda decision: gm_command.gm_command_space['declare_war']['func'] if decision == 'yes' else identity_partial_fn,
    },
    "declare_war": {
        # todo
        "decisions": {"yes": "Declare war"},
        "param": gm_command.gm_command_space['declare_war']['param'],
        "func": lambda decision: gm_command.gm_command_space['declare_war']['func'],
    },
    "chat": {
        "decisions": {"continue": "Continue conversation", "close": "End conversation"},
    },
    # Nonsense Prompt
    "nonsense": {
        "decisions": {"close": "End conversation"},
    },
    # Buy luxury goods
    'buy_luxury': {
        "decisions": {"yes": "Agree to research cooperation", "no": "Disagree to research cooperation"},
        "param": gm_command.gm_command_space['research_agreement']['param'],
        "func": lambda decision: gm_command.gm_command_space['research_agreement']['func'] if decision == 'yes' else identity_partial_fn,
    },
    # Deceive with false information
    'cheat': {
        "decisions": {"yes": "Agree that the information is true", "no": "Disagree that the information is true"},
        "param": [],
        "func": lambda decision: identity_partial_fn,
    },
}

decision_reason_simulate_space = {
    # todo It's easy to confuse.
    'ask_for_object_yes': {
        "reason": ["ask_for_object_yes_satisfied_with_value"],
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            simulator.run_getTradeAcceptability,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        )
    },

    'ask_for_object_no': {
        "reason": ["ask_for_object_no_too_many_cities_to_trade", "ask_for_object_no_value_diminishes",
                   "ask_for_object_no_unforgivable_relationship", "ask_for_object_no_defense_treaty_not_close",
                   "ask_for_object_no_value_greatly_diminished", "ask_for_object_no_hostile_relationship",
                   "ask_for_object_yes_satisfied_with_no_value"],
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            simulator.run_getTradeAcceptability,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        )
    },
    'change_closeness_up': {
        "reason": ["friendly_statement_yes_strong", "friendly_statement_yes_good",
                   "friendly_statement_yes_make_more_friends"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wanwantsToSignDeclarationOfFrienship,
            civ_name_1=civ_name_1, civ_name_2=civ_name_2)
    },
    'change_closeness_down': {
        "reason": ['friendly_statement_no_disadvantage', 'friendly_statement_no_worse',
                   'friendly_statement_no_made_too_many_friends', 'friendly_statement_no_too_many_friendly_forces',
                   'friendly_statement_no_met_few_civilizations'],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wanwantsToSignDeclarationOfFrienship,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'change_closeness_nochange': {
        "reason": [],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wanwantsToSignDeclarationOfFrienship,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },

    'form_ally_yes': {
        "reason": ["mutual_defense_yes_good", "mutual_defense_yes_strong"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToSignDefensivePact,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'form_ally_no': {
        "reason": ["mutual_defense_no_no_good_relationship", "mutual_defense_no_not_get_along_with_my_friends",
                   "mutual_defense_no_not_as_good_as_me", "mutual_defense_no_defensive_pact_drawn_into_battles",
                   "mutual_defense_no_signed_enough", "mutual_defense_no_worse"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToSignDefensivePact,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'friendly_statement_yes': {
        "reason": ["friendly_statement_yes_strong", "friendly_statement_yes_good",
                   "friendly_statement_yes_make_more_friends"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wanwantsToSignDeclarationOfFrienship,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'friendly_statement_no': {
        "reason": ['friendly_statement_no_disadvantage', 'friendly_statement_no_worse',
                   'friendly_statement_no_made_too_many_friends', 'friendly_statement_no_too_many_friendly_forces',
                   'friendly_statement_no_met_few_civilizations'],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wanwantsToSignDeclarationOfFrienship,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'mutual_defense_yes': {
        "reason": ["mutual_defense_yes_good", "mutual_defense_yes_strong"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToSignDefensivePact,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'mutual_defense_no': {
        "reason": ["mutual_defense_no_no_good_relationship", "mutual_defense_no_not_get_along_with_my_friends",
                   "mutual_defense_no_not_as_good_as_me", "mutual_defense_no_defensive_pact_drawn_into_battles",
                   "mutual_defense_no_signed_enough", "mutual_defense_no_worse"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToSignDefensivePact,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'open_border_yes': {
        "reason": ["open_border_yes_good_relationship", "open_border_yes_not_at_war_with_my_friends",
                   "open_border_yes_not_go_to_war"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToOpenBorders,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'open_border_no': {
        "reason": ["open_border_no_no_good_relationship", "open_border_no_not_accept_war_with_friends",
                   "open_border_no_can_attack_not_open_border"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_wantsToOpenBorders,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'propose_trade_yes': {
        "reason": ["ask_for_object_yes_satisfied_with_value"],
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            simulator.run_getTradeAcceptability,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        )
    },
    'propose_trade_no': {
        "reason": ["ask_for_object_no_too_many_cities_to_trade", "ask_for_object_no_value_diminishes",
                   "ask_for_object_no_unforgivable_relationship", "ask_for_object_no_defense_treaty_not_close",
                   "ask_for_object_no_value_greatly_diminished", "ask_for_object_no_hostile_relationship"],
        "param": ["civ_name_1", "civ_name_2", "civ1_resource_dict", "civ2_resource_dict"],
        "func": lambda civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict: partial(
            simulator.run_getTradeAcceptability,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2,
            civ1_resource_dict=civ1_resource_dict,
            civ2_resource_dict=civ2_resource_dict
        )
    },
    'research_agreement_yes': {
        "reason": ["research_agreement_yes_can_initiate_research_agreements",
                   "research_agreement_yes_can_all_pay_for_it"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_canSignResearchAgreementsWith,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'research_agreement_no': {
        "reason": ["research_agreement_no_not_major_city", "research_agreement_no_didnt_study_properties",
                   "research_agreement_no_nothing_to_study", "research_agreement_no_partner_not_major_city",
                   "research_agreement_no_partner_didnt_study_properties",
                   "research_agreement_no_partner_nothing_to_study", "research_agreement_no_cant_afford_to_pay",
                   "research_agreement_no_partner_cant_afford_to_pay"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_canSignResearchAgreementsWith,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'seek_peace_yes': {
        "reason": ["motivation_to_attack_no_too_far", "motivation_to_attack_no_much_better_than_us",
                   "motivation_to_attack_no_sacrifice_heavy", "motivation_to_attack_no_far_away_cities",
                   "motivation_to_attack_no_signed_research_agreement", "motivation_to_attack_no_declared_friendship",
                   "motivation_to_attack_no_allies", "motivation_to_attack_no_do_business",
                   "motivation_to_attack_no_just_city_states", "motivation_to_attack_no_confederate_city"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_hasAtLeastMotivationToAttack,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },
    'seek_peace_no': {
        "reason": ["motivation_to_attack_yes_military_force_overwhelmed_opposite_side",
                   "motivation_to_attack_yes_far_more_military_power", "motivation_to_attack_yes_more_military_power",
                   "motivation_to_attack_yes_military_strength_slightly_stronger",
                   "motivation_to_attack_yes_relationship_unforgivable",
                   "motivation_to_attack_yes_hostile_relationship", "motivation_to_attack_yes_they_were_alone",
                   "motivation_to_attack_yes_cant_let_other_side_win", "motivation_to_attack_yes_no_way_to_get_there"],
        "param": ["civ_name_1", "civ_name_2"],
        "func": lambda civ_name_1, civ_name_2: partial(
            simulator.run_hasAtLeastMotivationToAttack,
            civ_name_1=civ_name_1,
            civ_name_2=civ_name_2
        )
    },

}

# todo Modify it in the game code: 'they'->'you'
decision_reasons = {
    "friendly_statement_no_disadvantage": "To our disadvantage",
    "friendly_statement_yes_strong": "You are very strong",
    "friendly_statement_yes_good": "You are very good",
    "friendly_statement_no_worse": "You're so much worse than me",
    "friendly_statement_yes_make_more_friends": "Need to make more friends",
    "friendly_statement_no_made_too_many_friends": "I've made too many friends",
    "friendly_statement_no_too_many_friendly_forces": "There are too many friendly forces",
    "friendly_statement_no_met_few_civilizations": "I've met so few civilizations now",
    "open_border_no_no_good_relationship": "We don't have a good relationship",
    "mutual_defense_no_no_good_relationship": "We don't have a good relationship",
    "open_border_no_not_accept_war_with_friends": "Don't accept if you are at war with our friends, you might use our land to attack them",
    "open_border_no_can_attack_not_open_border": "We can attack it, so we don't have to open the border",
    "open_border_yes_good_relationship": "We have a good relationship",
    "open_border_yes_not_at_war_with_my_friends": "You're not at war with my friends",
    "open_border_yes_not_go_to_war": "We don't have to go to war",
    "mutual_defense_yes_good": "You are very good",
    "mutual_defense_yes_strong": "You are very strong",
    "mutual_defense_no_worse": "You're so much worse than me",
    "mutual_defense_no_not_get_along_with_my_friends": "You don't get along with my friends",
    "mutual_defense_no_not_as_good_as_me": "You're not as good as me",
    "mutual_defense_no_defensive_pact_drawn_into_battles": "If we have a defensive pact with another civ then we would get drawn into their battles as well",
    "mutual_defense_no_signed_enough": "I think I signed enough",
    "motivation_to_attack_no_too_far": "Be too far",
    "motivation_to_attack_no_much_better_than_us": "It's so much better than us",
    "motivation_to_attack_no_sacrifice_heavy": "Our sacrifice will be heavy",
    "motivation_to_attack_yes_military_force_overwhelmed_opposite_side": "Our military force completely overwhelmed the opposite side",
    "motivation_to_attack_yes_far_more_military_power": "We have far more military power than the other side",
    "motivation_to_attack_yes_more_military_power": "We have more military power than the other side",
    "motivation_to_attack_yes_military_strength_slightly_stronger": "Our military strength is slightly stronger than the opposite side",
    "motivation_to_attack_no_far_away_cities": "Far away cities",
    "motivation_to_attack_no_signed_research_agreement": "We signed a research agreement",
    "motivation_to_attack_no_declared_friendship": "We declared our friendship",
    "motivation_to_attack_yes_relationship_unforgivable": "Our relationship is unforgivable",
    "motivation_to_attack_yes_hostile_relationship": "We have a hostile relationship",
    "motivation_to_attack_no_allies": "We are Allies",
    "motivation_to_attack_no_do_business": "We do business",
    "motivation_to_attack_yes_they_were_alone": "You were alone",
    "motivation_to_attack_no_just_city_states": "You're just city-states",
    "motivation_to_attack_no_confederate_city": "It's a confederate city",
    "motivation_to_attack_yes_cant_let_other_side_win": "We can't let the other side win",
    "motivation_to_attack_yes_no_way_to_get_there": "There's no way to get there",
    "research_agreement_no_not_major_city": "We're not a major city",
    "research_agreement_no_didnt_study_properties": "We didn't study the properties",
    "research_agreement_no_nothing_to_study": "We don't have anything to study",
    "research_agreement_no_partner_not_major_city": "You're not a major city",
    "research_agreement_no_partner_didnt_study_properties": "You didn't study the properties",
    "research_agreement_no_partner_nothing_to_study": "Your don't have anything to study",
    "research_agreement_no_cant_afford_to_pay": "We can't afford to pay",
    "research_agreement_no_partner_cant_afford_to_pay": "You can't afford to pay",
    "research_agreement_yes_can_initiate_research_agreements": "We can initiate research agreements and have things to study",
    "research_agreement_yes_can_all_pay_for_it": "We can all pay for it",
    "ask_for_object_no_too_many_cities_to_trade": "There are too many cities to trade",
    "ask_for_object_no_value_diminishes": "The value of the resources we provide diminishes in your eyes",
    "ask_for_object_no_unforgivable_relationship": "We have an unforgivable relationship",
    "ask_for_object_no_hostile_relationship": "We have a hostile relationship",
    "ask_for_object_no_value_greatly_diminished": "The value of the resources we provide is greatly diminished in your eyes",
    "ask_for_object_no_defense_treaty_not_close": "We propose a defense treaty, but it's not close",
    "ask_for_object_yes_satisfied_with_value": "We are satisfied with the value your offer",
    "ask_for_object_yes_satisfied_with_no_value": "We are not satisfied with the value your offer"
}
