import copy

from civsim import utils

# civ2robot = {
#     "wu": "sunquan",
#     "shu": "guanyu",
#     # todo
#     "wei": "caocao",
#     'guanliyuan': 'guanliyuan',
#     'mongolia': 'mongolia',
#     'china': 'china',
#     'rome': 'rome',
#     'aztecs': 'aztecs',
#     'greece': 'greece',
#     'egypt': 'egypt'
# }
#
# robot2civ = dict([(v, k) for k, v in civ2robot.items()])

default_req = {
    "test_id": "",
    "uuid": "",
    "civ_name": "",
    "round": 0,
    "dev_setting": {
        "model_name": "gpt-3.5-turbo-instruct"
    },
    "speaker_persona": {
        "npc_id": "",
        "civ_name": "",
        "language_style": "",
        "culture_strength": 0,
        "tech_strength": 0,
        "army_strength": 0,
        "navy_strength": 0
    },
    "receiver_persona": {
        "npc_id": "",
        "civ_name": "",
        "language_style": "",
        "culture_strength": 0,
        "tech_strength": 0,
        "army_strength": 0,
        "navy_strength": 0
    },
    "utterance": "",
    "relation": {
        "closeness": "",
        "diplomacy": "",
        "proximity": "",
        "army_proximity": ""
    }
}


# todo There should be no robot concept, it's all in req
def save2req(save_data, agent, text, speaker_civ_name, receiver_civ_name):
    # todo Not necessarily a player
    req = default_req
    civ_names = utils.get_all_civs(save_data)
    speaker_ind = utils.get_civ_index(save_data, speaker_civ_name)
    # receiver_civ_name = robot2civ[robot_name]
    receiver_ind = utils.get_civ_index(save_data, receiver_civ_name)
    # When testing, avoid speaking and receiver being the same, temporary handle
    if speaker_ind == receiver_ind:
        speaker_ind = (speaker_ind + 1) % len(civ_names)
    speaker_civ_name = utils.get_civ_name(save_data, speaker_ind)
    # todo Remove the robot
    chat_history = agent.memory.get_chat_memory(receiver_civ_name)
    dialogue_history = agent.memory.chat2dialogue(chat_history, speaker_civ_name)
    event_history = agent.memory.get_event_memory(save_data, receiver_ind)
    tmp_req = copy.copy(req)
    tmp_req['round'] = save_data.get('turns', 0)
    if 'event_history' in tmp_req:
        tmp_req['event_history'].extend(event_history)
    else:
        tmp_req['event_history'] = event_history
    if 'dialogue_history' in tmp_req:
        # todo why
        tmp_req['dialogue_history'].extend(dialogue_history)
    else:
        tmp_req['dialogue_history'] = dialogue_history
    tmp_req['utterance'] = text
    # todo Output relation positioning in the game
    tmp_req['relation']['closeness'] = agent.relations[f"{receiver_civ_name}#{speaker_civ_name}"]["closeness"]
    # todo add mapping to chinese
    tmp_req['relation']['diplomatic_status'] = agent.relations[f"{receiver_civ_name}#{speaker_civ_name}"]["diplomatic_status"]
    tmp_req['relation']['proximity'] = agent.relations[f"{receiver_civ_name}#{speaker_civ_name}"]["proximity"]
    # todo Position of the army
    tmp_req['relation']['army_proximity'] = agent.relations[f"{receiver_civ_name}#{speaker_civ_name}"]["army_proximity"]
    tmp_req['civ_name'] = receiver_civ_name
    # todo civ_name_2 -> civ_name_oppo
    tmp_req['civ_name_1'] = receiver_civ_name
    tmp_req['civ_name_2'] = speaker_civ_name
    tmp_req['speaker_persona']['civ_name'] = speaker_civ_name
    speaker_civ_stats = agent.oppo_agent[speaker_civ_name].strengths_info
    tmp_req['speaker_persona'] = {**tmp_req['speaker_persona'], **speaker_civ_stats}
    tmp_req['receiver_persona']['civ_name'] = receiver_civ_name
    receiver_civ_stats = agent.strengths_info
    tmp_req['receiver_persona'] = {**tmp_req['receiver_persona'], **receiver_civ_stats}
    # agent_profile
    tmp_req['civ_names'] = ','.join(agent.civ_names)
    tmp_req['war_civs'] = ','.join(agent.war_civs)
    tmp_req['is_at_war'] = True if speaker_civ_name in agent.war_civs else False
    tmp_req['friend_civs'] = ','.join(agent.friend_civs)
    tmp_req['potential_enemy_civs'] = ','.join(agent.potential_enemy_civs)
    tmp_req['potential_friend_civs'] = ','.join(agent.potential_friend_civs)
    # strongest_civs
    all_civ_stats = [(civ_name, agent.oppo_agent[civ_name].strengths_info) for civ_name in agent.civ_names if civ_name in agent.oppo_agent]
    all_civ_armys = [(k, float(v['army_strength'])) for k, v in all_civ_stats]
    top_two_armies = sorted(all_civ_armys, key=lambda x: x[1], reverse=True)[:2]
    tail_two_armies = sorted(all_civ_armys, key=lambda x: x[1], reverse=False)[:2]
    tmp_req['strongest_civs'] = ','.join([k for k, v in top_two_armies])
    tmp_req['weakest_civs'] = ','.join([k for k, v in tail_two_armies])
    tmp_req['relation']['tech_strength_compare'] = prompt_elem_mapping(
        [tmp_req['receiver_persona']['tech_strength'],
         tmp_req['speaker_persona']['tech_strength']],
        'strength'
    )
    tmp_req['relation']['culture_strength_compare'] = prompt_elem_mapping(
        [tmp_req['receiver_persona']['culture_strength'],
         tmp_req['speaker_persona']['culture_strength']],
        'strength'
    )
    tmp_req['relation']['army_strength_compare'] = prompt_elem_mapping(
        [tmp_req['receiver_persona']['army_strength'],
         tmp_req['speaker_persona']['army_strength']],
        'strength'
    )
    tmp_req['relation']['civ_strength_compare'] = prompt_elem_mapping(
        [tmp_req['receiver_persona']['civ_strength'],
         tmp_req['speaker_persona']['civ_strength']],
        'strength'
    )
    tmp_req['objective'] = ','.join(agent.objective)
    return tmp_req


def prompt_elem_mapping(info, type=''):
    if type == 'strength':
        if float(info[0]) > float(info[1]) * 2:
            return 'much stronger than'
        if float(info[0]) > float(info[1]) * 1.5:
            return 'stronger than'
        if float(info[0]) > float(info[1]) * 1.2:
            return 'slightly stronger than'
        if float(info[0]) > float(info[1]) * 0.85:
            return 'not better than'
        if float(info[0]) > float(info[1]) * 0.75:
            return 'slightly weaker than'
        if float(info[0]) > float(info[1]) * 0.5:
            return 'weaker than'
        if float(info[0]) > float(info[1]) * 0.0:
            return 'much weaker than'
    return ''
