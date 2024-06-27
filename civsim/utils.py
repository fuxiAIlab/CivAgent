import os
import gzip
import json as json
from base64 import b64decode, b64encode
import datetime
from collections import defaultdict
import re
import numpy as np
import random
from civagent.action_space import intention_space
from civsim import action_space
from civsim.simulator import simulator
import traceback
from functools import partial
from civsim import logger

default_chat_memory = {
    "msgType": "0",
    "addtime": "2024-01-01 11:11:11",
    "robotIds": "",
    "sessionType": "0",
    "from": "",
    "from_civ": "",
    "to": "",
    "to_civ": "",
    "sessionId": "0",
    "uuid": "0",
    "notify": "",
    "game_id": "0",
    "debug_info": {}
}


def format_nested_values(prompt, d):
    for key, value in prompt.items():
        if isinstance(value, dict):
            format_nested_values(value, d)
        elif isinstance(value, str) and "{" in value:
            tmp = value.format(**d).replace("'", '"')
            try:
                prompt[key] = json.loads(tmp)
            except json.JSONDecodeError as e:
                logger.error(f"Error in format_nested_values: {e}")
                prompt[key] = tmp
    return prompt


def get_defaultdict(d):
    default_dict = defaultdict(lambda: defaultdict(dict), d)
    return default_dict


tree = lambda: defaultdict(tree)


def json_load_defaultdict(data):
    if isinstance(data, str) or isinstance(data, bytes):
        return json.loads(data, object_pairs_hook=partial(defaultdict, lambda: tree()))
    else:
        return json.load(data, object_pairs_hook=partial(defaultdict, lambda: tree()))


def is_gameid(text):
    text = text.strip()
    pattern = r'\b[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\b'
    result = re.findall(pattern, text)
    if len(result) > 0 and len(result[0]) == 36:
        return result[0]
    return ''


def get_filename_without_extension(path):
    filename = os.path.basename(path)  # Retrieve the filename (including the extension) from the path.
    filename_without_extension = os.path.splitext(filename)[0]  # Separate the filename and the extension, and take the filename part.
    return filename_without_extension


def get_latest_savefile(filepath):
    try:
        with open(filepath, 'rb') as file:
            binary_data = file.read()
            decompressed_data = gzip.decompress(b64decode(binary_data))
            return json_load_defaultdict(decompressed_data)
    except (IOError, gzip.BadGzipFile, TypeError) as e:
        logger.warning(f"Error: {e}")
        return None


def set_latest_savefile(filepath, data):
    try:
        compressed_data = gzip.compress(json.dumps(data).encode('utf-8'))
        encoded_data = b64encode(compressed_data).decode('utf-8')

        with open(filepath, 'wb') as file:
            file.write(encoded_data.encode('utf-8'))

        return True
    except (IOError, TypeError) as e:
        logger.warning(f"Error: {e}")
        return False


def time_diff_in_minutes(timestamp):
    timestamp = int(float(timestamp))
    current_time = datetime.datetime.now().timestamp() * 1000
    difference = current_time - timestamp
    difference_in_minutes = difference / (1000 * 60)
    return difference_in_minutes


def contains_chinese(text):
    return bool(re.search('[\u4e00-\u9fff]', text))


def is_start_with_chinese_or_number(text):
    pattern = re.compile(r'^[\u4e00-\u9fff\d]')
    return bool(pattern.match(text))


# todo civ_name Use uniform capitalization
def get_civ_name(save_data, civ_index=None):
    civ_index = get_civ_index(save_data) if civ_index is None else civ_index
    civs = save_data.get('civilizations', [])
    if len(civs) > civ_index:
        return civs[civ_index].get('civName', '').lower()
    else:
        logger.debug(f"utils.——_civ_name get illegal civ_index {civ_index} of civs {civs}")
        return None


def fix_civ_name(civ_name):
    return civ_name.capitalize()


def get_civ_index(save_data, civ_name=''):
    # Safely return the index of the civilization or a default value
    assert isinstance(save_data, dict), type(save_data)
    civs = save_data.get('civilizations', [])
    if civ_name and len(civ_name) > 1:
        return [x['civName'].lower() for x in civs].index(civ_name.lower())
    elif civ_name == '':
        res = [index for index, d in enumerate(civs) if "playerType" in d and d["playerType"] == "Human"]
        if res and len(res) > 0:
            return res[0]
        else:
            return 1
        # return [index for index, d in enumerate(civs) if "playerType" in d and d["playerType"] == "Human"][0]
    else:
        logger.debug(
            f"utils.get_civ_index get civ_name: {civ_name}, civ_names:{[x['civName'].lower() for x in civs]}"
        )
        return None


def add_gold(save_data, civ_name='', gold_num=10000):
    ind = get_civ_index(save_data, civ_name)
    if ind is not None:
        # Safely access nested dictionary keys and add gold
        save_data['civilizations'][ind].setdefault('gold', 0)
        save_data['civilizations'][ind]['gold'] += gold_num
    return save_data


def construct_instant(save_data, civ_name=''):
    ind = get_civ_index(save_data, civ_name)
    if ind is not None:
        # Safely iterate through cities and constructions
        for city in save_data['civilizations'][ind].get('cities', []):
            in_progress = city.get('cityConstructions', {}).get('inProgressConstructions', {})
            for item in in_progress:
                in_progress[item] += 100
    return save_data


def technology_instant(save_data, civ_name=''):
    ind = get_civ_index(save_data, civ_name)
    if ind is not None:
        # Safely access techs in progress and add progress points
        techs = save_data['civilizations'][ind].get('tech', {}).get('techsInProgress', {})
        for tech in techs:
            techs[tech] += 1000
    return save_data


# Only the city-state has the concept of alliance, so the game can only be reflected in the goodwill \ peace \ friendship statement \ defense agreement
def form_ally(save_data, civ_name_1, civ_name_2):
    save_data = open_borders(save_data, civ_name_1, civ_name_2)
    save_data = research_agreement(save_data, civ_name_1, civ_name_2)
    save_data = form_mutual_defense(save_data, civ_name_1, civ_name_2)
    return save_data


# "trades":[{"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Research Agreement","type":"Treaty","amount":201,"duration":7}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Research Agreement","type":"Treaty","amount":201,"duration":6}]},{"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Open Borders","type":"Agreement","duration":25}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Open Borders","type":"Agreement","duration":25}]}]
def open_borders(save_data, civ_name_1, civ_name_2, duration=50):
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    trades = diplomacy_info.get('trades', [])
    trade_names = [item['name'] for d in trades for offer in d.values() for item in offer]
    if 'Open Borders' not in trade_names and len(diplomacy_info) > 0:
        open_borders_offer = {
            "theirOffers": [
                {
                    "class": "com.unciv.logic.trade.TradeOffer", "name": "Open Borders", "type": "Agreement",
                    "duration": duration
                }],
            "ourOffers": [
                {
                    "class": "com.unciv.logic.trade.TradeOffer", "name": "Open Borders", "type": "Agreement",
                    "duration": duration
                }]
        }
        if len(trades) > 0:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'].append(open_borders_offer)
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'].append(open_borders_offer)
        else:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = [open_borders_offer]
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'] = [open_borders_offer]
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "[{}] opens borders to {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        if 'notifications' in save_data['civilizations'][1]:
            [notifications.append(y) for y in save_data['civilizations'][1]['notifications']]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


# "trades":[{"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Research Agreement","type":"Treaty","amount":201,"duration":7}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Research Agreement","type":"Treaty","amount":201,"duration":6}]},{"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Open Borders","type":"Agreement","duration":25}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Open Borders","type":"Agreement","duration":25}]}]
def research_agreement(save_data, civ_name_1, civ_name_2):
    ind_player = get_civ_index(save_data)
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    trades = diplomacy_info.get('trades', [])
    trade_names = [item['name'] for d in trades for offer in d.values() for item in offer]
    if 'Research Agreement' not in trade_names and len(diplomacy_info) > 0:
        research_agreement_offer = {
            "theirOffers": [{
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Research Agreement",
                "type": "Treaty",
                "amount": 201,
                "duration": 25
            }],
            "ourOffers": [{
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Research Agreement",
                "type": "Treaty",
                "amount": 201,
                "duration": 25
            }]
        }
        if 'trades' not in save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = []
        if 'trades' not in save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]:
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'] = []
        if len(trades) > 0:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'].append(research_agreement_offer)
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'].append(research_agreement_offer)
        else:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = [research_agreement_offer]
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'] = [research_agreement_offer]
        if ('flagsCountdown' not in save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]
                or 'flagsCountdown' not in save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]):
            return save_data
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['flagsCountdown']["ResearchAgreement"] = 25
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['flagsCountdown']["ResearchAgreement"] = 25
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "[{}] has signed a Research Agreement with {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


def form_mutual_defense(save_data, civ_name_1, civ_name_2, duration=20):
    ind_player = get_civ_index(save_data)
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    trades = diplomacy_info.get('trades', [])
    trade_names = [item['name'] for d in trades for offer in d.values() for item in offer]
    if 'Defensive Pact' not in trade_names and len(diplomacy_info) > 0:
        mutual_defense_offer = {
            "theirOffers": [{
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Defensive Pact",
                "type": "Treaty", "duration": duration
            }],
            "ourOffers": [{
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Defensive Pact",
                "type": "Treaty",
                "duration": duration
            }]
        }
        if len(trades) > 0:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'].append(mutual_defense_offer)
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'].append(mutual_defense_offer)
        else:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = [mutual_defense_offer]
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'] = [mutual_defense_offer]
        if ('flagsCountdown' not in save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]
                or 'flagsCountdown' not in save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]):
            return save_data
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['flagsCountdown']["DefensivePact"] = duration
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['flagsCountdown']["DefensivePact"] = duration
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['diplomaticStatus'] = 'DefensivePact'
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['diplomaticStatus'] = 'DefensivePact'
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "[{}] has signed a mutual defense Agreement with {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


# luxury_resource(save_data, Roma, Mongolia,{"Ivory":2,"Furs":1,"Iron":2},{"Gold per turn":60,"Gems":1,"Oil":3})
def add_luxury_resource(save_data, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict):
    ind_player = get_civ_index(save_data)
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    trades = diplomacy_info.get('trades', [])
    # trade_names = [item['name'] for d in trades for offer in d.values() for item in offer]
    # if 'Luxury_Resource' not in trade_names:
    # luxury_resource_offer = {"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Salt","type":"Luxury_Resource","duration":24},{"class":"com.unciv.logic.trade.TradeOffer","name":"Mongolia","type":"WarDeclaration"}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Gold Ore","type":"Luxury_Resource","duration":24},{"class":"com.unciv.logic.trade.TradeOffer","name":"Gold per turn","type":"Gold_Per_Turn","amount":74,"duration":24}]}
    civ1_luxury_resource_offer = {}
    civ2_luxury_resource_offer = {}
    if civ1_resource_dict:
        civ1_luxury_resource_offer['ourOffers'] = []
        civ2_luxury_resource_offer['theirOffers'] = []
    if civ2_resource_dict:
        civ1_luxury_resource_offer['theirOffers'] = []
        civ2_luxury_resource_offer['ourOffers'] = []

    for key, value in civ1_resource_dict.items():
        if value == 'Any':
            value = 1
        if key.capitalize() in action_space.luxury_space:
            civ1_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key.capitalize(),
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key.capitalize(),
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
        # todo Add 'Gold per turn' to identification
        # todo Add key=='Gold' to be case-insensitive
        elif key == 'Gold' or key == 'gold' or key == 'GOLD':
            civ1_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
        elif key == 'Gold per turn':
            civ1_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
        elif key in action_space.resource_space:
            civ1_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
        else:
            # todo Add assert error logging
            assert False, f"Unexpected resource key: {key}"
            pass

    for key, value in civ2_resource_dict.items():
        if value == 'Any':
            value = 1
        if key in action_space.luxury_space or key.capitalize() in action_space.luxury_space:
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key.capitalize(),
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
            civ1_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key.capitalize(),
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
        elif key == 'Gold' or key == 'gold' or key == 'GOLD':
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
            civ1_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
        elif key == 'Gold per turn':
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
            civ1_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
        elif key in action_space.resource_space:
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
            civ1_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
        else:
            assert False, f"Unexpected resource key: {key}"
            pass
    if len(diplomacy_info) > 0:
        if len(trades) > 0:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'].append(civ1_luxury_resource_offer)
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'].append(civ2_luxury_resource_offer)
        else:
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = [civ1_luxury_resource_offer]
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['trades'] = [civ2_luxury_resource_offer]
        notifications = []
        # todo Increase transaction content
        notifications.append({
            "category": "Trade",
            "text": "[{}]  has successfully completed business with {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][ind_player]['notifications'] = notifications
    return save_data


def trade_offer(save_data, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict):
    # ind_player = get_civ_index(save_data)
    # ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    # civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_2]
    trades = diplomacy_info.get('tradeRequests', [])
    # trade_names = [item['name'] for d in trades for offer in d.values() for item in offer]
    # if 'Luxury_Resource' not in trade_names:
    # luxury_resource_offer = {"theirOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Salt","type":"Luxury_Resource","duration":24},{"class":"com.unciv.logic.trade.TradeOffer","name":"Mongolia","type":"WarDeclaration"}],"ourOffers":[{"class":"com.unciv.logic.trade.TradeOffer","name":"Gold Ore","type":"Luxury_Resource","duration":24},{"class":"com.unciv.logic.trade.TradeOffer","name":"Gold per turn","type":"Gold_Per_Turn","amount":74,"duration":24}]}
    # "tradeRequests": [{"requestingCiv": "Rome", "trade": {"theirOffers": [
    #     {"class": "com.unciv.logic.trade.TradeOffer", "name": "Copper", "type": "Luxury_Resource", "duration": 25}],
    #                                                       "ourOffers": [{"class": "com.unciv.logic.trade.TradeOffer",
    #                                                                      "name": "Incense", "type": "Luxury_Resource",
    #                                                                      "duration": 25}]}}]
    # civ1_luxury_resource_offer = {}
    civ2_luxury_resource_offer = {}
    if civ1_resource_dict:
        # civ1_luxury_resource_offer['ourOffers'] = []
        civ2_luxury_resource_offer['theirOffers'] = []
    if civ2_resource_dict:
        # civ1_luxury_resource_offer['theirOffers'] = []
        civ2_luxury_resource_offer['ourOffers'] = []

    for key, value in civ1_resource_dict.items():
        if value == 'Any':
            value = 1
        if key in action_space.luxury_space:
            # todo processing Any
            # civ1_luxury_resource_offer['ourOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": key, "type": "Luxury_Resource", "amount": value,
            #      "duration": 24})
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
        # todo
        elif key == 'Gold' or key == 'gold' or key == 'GOLD':
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
        elif key == 'Gold per turn':
            # civ1_luxury_resource_offer['ourOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": "Gold per turn", "type": "Gold_Per_Turn",
            #      "amount": value, "duration": 24})
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
        elif key in action_space.resource_space:
            # todo processing Any
            # civ1_luxury_resource_offer['ourOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": key, "type": "Strategic_Resource",
            #      "amount": value, "duration": 25})
            civ2_luxury_resource_offer['theirOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
    for key, value in civ2_resource_dict.items():
        if value == 'Any':
            value = 1
        if key in action_space.luxury_space:
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Luxury_Resource",
                "amount": int(value),
                "duration": 24
            })
            # civ1_luxury_resource_offer['theirOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": key, "type": "Luxury_Resource", "amount": value,
            #      "duration": 24})
        elif key == 'Gold' or key == 'gold' or key == 'GOLD':
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold",
                "amount": int(value)
            })
        elif key == 'Gold per turn':
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": "Gold per turn",
                "type": "Gold_Per_Turn",
                "amount": int(value),
                "duration": 24
            })
            # civ1_luxury_resource_offer['theirOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": "Gold per turn", "type": "Gold_Per_Turn",
            #      "amount": value, "duration": 24})
        elif key in action_space.resource_space:
            civ2_luxury_resource_offer['ourOffers'].append({
                "class": "com.unciv.logic.trade.TradeOffer",
                "name": key,
                "type": "Strategic_Resource",
                "amount": int(value),
                "duration": 25
            })
            # civ1_luxury_resource_offer['theirOffers'].append(
            #     {"class": "com.unciv.logic.trade.TradeOffer", "name": key, "type": "Strategic_Resource",
            #      "amount": value, "duration": 25})
    civ2_luxury_resource_offer = {k: v for k, v in civ2_luxury_resource_offer.items() if v != []}
    civ2_offer = {"requestingCiv": civ_name_1, "trade": civ2_luxury_resource_offer}
    if len(diplomacy_info) > 0:
        if len(trades) > 0:
            # save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'].append(civ1_luxury_resource_offer)
            save_data['civilizations'][ind_2]['tradeRequests'].append(civ2_offer)
        else:
            # save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['trades'] = [civ1_luxury_resource_offer]
            save_data['civilizations'][ind_2]['tradeRequests'] = [civ2_offer]
        # notifications = []
        # notifications.append({"category": "Trade",
        #                       "text": "[{}]  has successfully completed business with {}!".format(civ_name_1,
        #                                                                                           civ_name_2),
        #                       "icons": ["OtherIcons/Pillage", "England"]})
        # [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        # save_data['civilizations'][1]['notifications'] = notifications
    return save_data


# "diplomaticModifiers":{"SharedEnemy":5}
# {"DeclarationOfFriendship":35,"YearsOfPeace":28,"SharedEnemy":5,"OpenBorders":14.125,"DefensivePact":8,"DeclaredFriendshipWithOurAllies":5}
# def change_closeness(save_data, civ_name_1, civ_name_2):
#     pass


# todo Not developed yet
# {"DeclarationOfFriendship":35,"YearsOfPeace":28,"SharedEnemy":5,"OpenBorders":14.125,"DefensivePact":8,"DeclaredFriendshipWithOurAllies":5}
def friendly_statement(save_data, civ_name_1, civ_name_2):
    ind_player = get_civ_index(save_data)
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    if len(diplomacy_info) > 0 and (diplomacy_info.get('diplomaticStatus', '') != 'Peace'):
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['diplomaticStatus'] = 'Peace'
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['diplomaticStatus'] = 'Peace'
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['flagsCountdown'] = {}
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['flagsCountdown'] = {}
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "[{}] announce friendly statement with {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


# "England":{"otherCivName":"England","diplomaticStatus":"Peace","flagsCountdown":{"Bullied":6},"diplomaticModifiers":{"YearsOfPeace":17},"influence":-6}
def make_peace(save_data, civ_name_1, civ_name_2):
    ind_player = get_civ_index(save_data)
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
    if len(diplomacy_info) > 0 and (diplomacy_info.get('diplomaticStatus', '') != 'Peace'):
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['diplomaticStatus'] = 'Peace'
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['diplomaticStatus'] = 'Peace'
        save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['flagsCountdown'] = {}
        save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['flagsCountdown'] = {}
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "[{}] has restored peace with {}!".format(civ_name_1, civ_name_2),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


def declare_war(save_data, civ_name_1, civ_name_2):
    def declare_war_fn(save_data, civ_name_1, civ_name_2):
        ind_player = get_civ_index(save_data)
        ind_1 = get_civ_index(save_data, civ_name_1)
        ind_2 = get_civ_index(save_data, civ_name_2)
        civ_name_1 = fix_civ_name(civ_name_1)
        civ_name_2 = fix_civ_name(civ_name_2)
        diplomacy_info = save_data['civilizations'][ind_1].get('diplomacy', {}).get(civ_name_2, {})
        if len(diplomacy_info) > 0 and diplomacy_info.get('diplomaticStatus', '') == 'Peace':
            del save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['diplomaticStatus']
            del save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['diplomaticStatus']
            save_data['civilizations'][ind_1]['diplomacy'][civ_name_2]['flagsCountdown'] = {'DeclinedPeace': 10, 'DeclaredWar': 10}
            save_data['civilizations'][ind_2]['diplomacy'][civ_name_1]['flagsCountdown'] = {'DeclinedPeace': 10, 'DeclaredWar': 10}
            notifications = []
            notifications.append({
                "category": "Diplomacy",
                "text": "[{}] has declared war on {}!".format(civ_name_1, civ_name_2),
                "icons": ["OtherIcons/Pillage", "England"]
            })
            [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
            save_data['civilizations'][1]['notifications'] = notifications

    if isinstance(civ_name_1, list) or isinstance(civ_name_1, tuple):
        for civ in civ_name_1:
            declare_war_fn(save_data, civ, civ_name_2)
    else:
        declare_war_fn(save_data, civ_name_1, civ_name_2)
    return save_data


def get_all_citys(save_data, civ_name=''):
    tmp = []
    if civ_name is None or len(civ_name) <= 1:
        for civ in save_data['civilizations']:
            for i, city in enumerate(civ.get('cities', [])):
                if 'location' in city:
                    tmp.append((civ['civName'], i, city['location']))
    else:
        ind = get_civ_index(save_data, civ_name)
        civ = save_data['civilizations'][ind]
        for i, city in enumerate(civ.get('cities', [])):
            if 'location' in city:
                tmp.append((civ['civName'], i, city['location']))
    return tmp


def find_closest_location(location_list, target_location):
    min_distance = np.inf  # The initial minimum distance is set to infinity
    closest_index = -1
    for index, location in enumerate(location_list):
        # Compute the Euclidean distance between locations
        distance = np.linalg.norm(np.array(location) - np.array(target_location))
        if distance < min_distance:
            min_distance = distance
            closest_index = index
    return closest_index


def annex_city(save_data, civ_name_1, civ_name_2='', city_name=''):
    ind_player = get_civ_index(save_data)
    civ_name_1 = fix_civ_name(civ_name_1)
    civ_name_2 = fix_civ_name(civ_name_2)
    city_name = fix_civ_name(city_name)
    if len(save_data) <= 1:
        return save_data
    ind_1 = get_civ_index(save_data, civ_name_1)
    ind_2 = get_civ_index(save_data, civ_name_2)
    city_ind = None
    if len(civ_name_2) >= 1 and len(city_name) >= 1:
        # Find the city corresponding to civ_name_2
        civ = save_data['civilizations'][ind_2]
        for j, city in enumerate(civ.get('cities', [])):
            if city.get('name', '').lower() == city_name.lower():
                city_ind = j

    if len(civ_name_2) >= 1 and len(city_name) <= 1:
        # The nearest city in civ_name_2
        civ2_citys = get_all_citys(save_data, civ_name_2)
        civ2_citys_locations = [list(x[-1].values()) for x in civ2_citys]
        civ1_location = list(save_data['civilizations'][ind_1]['cities'][0]['location'].values())
        city_ind = find_closest_location(civ2_citys_locations, civ1_location)

    if city_ind is not None:
        city = save_data['civilizations'][ind_2]['cities'][city_ind]
        citys = save_data['civilizations'][ind_2]['cities']
        save_data['civilizations'][ind_2]['cities'] = citys[:city_ind] + citys[city_ind + 1:]
        save_data['civilizations'][ind_1]['cities'] += [city]
        notifications = []
        notifications.append({
            "category": "Diplomacy",
            "text": "city [{}] of {} is annexed by {}!".format(city_name, civ_name_2, civ_name_1),
            "icons": ["OtherIcons/Pillage", "England"]
        })
        [notifications.append(y) for y in save_data['civilizations'][ind_player].get('notifications', [])]
        save_data['civilizations'][1]['notifications'] = notifications
    return save_data


def get_proximity(save_data, first_civ_index, second_civ_name):
    proximity = save_data["civilizations"][first_civ_index].get("proximity", {"second_civ_name": 'Far'})
    return proximity.get(second_civ_name, '')


# Get the statistical panel data for the country
# Integral contrast value, {' S ': civilization,' N ': population,' C ': food production, "P" : capacity,' G ': money,' T ': territory,' F ': military power,' H ': happy,' W ': science and technology,' A ': cultural}
def get_stats(save_data, civ_ind):
    default_stats_history = {
        "A": 0,
        "W": 0,
        "F": 0,
        "S": 0,
        "T": 0,
        "N": 0,
        "P": 0,
        "G": 0,
    }
    stats = save_data["civilizations"][civ_ind].get("statsHistory", {"0": default_stats_history})
    last_key = list(stats.keys())[-1]
    last_stat = stats[last_key]
    return {
        "culture_strength": last_stat['A'],
        "tech_strength": last_stat['W'],
        "army_strength": last_stat['F'],
        "navy_strength": last_stat['F'],
        "civ_strength": last_stat['S'],
        "territory_strength": last_stat['T'],
        "population_strength": last_stat['N'],
        "production_strength": last_stat['P'],
        "commerce_strength": last_stat['G'],
    }


def get_all_civs(save_data):
    civs = save_data['civilizations']
    return [x['civName'].lower() for x in civs if x['civName'] != 'Barbarians']


def change_relation_level(relation, alter=0):
    relation_values = dict([(relation.name, i) for i, relation in enumerate(action_space.RelationSpace)])
    current_value = relation_values[relation.upper()]
    new_value = current_value + alter
    # Ensure the new_value stays within the range of the enumeration
    new_value = max(0, min(new_value, 7))
    # Find the corresponding key for the new_value
    new_relation = [key for key, value in relation_values.items() if value == new_value][0]
    return new_relation.upper()


def get_all_resources(save_data):
    civs = save_data['civilizations']
    resources = dict([(x['civName'].lower(), x['resourcehash']) for x in civs if x['civName'] != 'Barbarians'])
    return {k: {kk: vv for kk, vv in v.items() if int(vv) > 0} for k, v in resources.items()}


def get_relation(save_data, first_civ_ind, second_civ_name):
    relation_score = 0
    relations = save_data['civilizations'][first_civ_ind].get("diplomacy", {}).get(second_civ_name, {}).get('diplomaticModifiers', {})
    for relation in relations:
        relation_score += relations[relation]
    # todo diplomaticModifiers embodiment
    return relation_score


def get_diplomatic_status(save_data, first_civ_ind, second_civ_name):
    second_civ_name = fix_civ_name(second_civ_name)
    # todo The default diplomacy {'otherCivName': 'Greece', 'diplomaticStatus': 'Peace', 'diplomaticModifiers': {'YearsOfPeace': 0.5}}
    diplomacy = save_data['civilizations'][first_civ_ind].get("diplomacy", {}).get(second_civ_name, {})
    # logger.warning(f"utils.get_diplomatic_status {first_civ_ind} {second_civ_name} {diplomacy}")
    if len(diplomacy) > 0:
        # todo ally
        if 'diplomaticStatus' not in diplomacy:
            return 'War'
        else:
            return 'Peace'
    else:
        return 'Peace'


def intention_correct(intention_task_reply):
    assert isinstance(intention_task_reply, dict), type(intention_task_reply)
    raw_intention, intention_degree, intention, response = "", "", "", ""
    intention_str = intention_task_reply.get('intention', 'chat')
    for k in intention_space:
        if k in intention_str:
            raw_intention = k
    raw_intention = "nonsense" if len(raw_intention) < 1 else raw_intention
    # todo No Chinese
    # pattern = r"degree.{0,4}weak"
    intention_degree = intention_task_reply.get('degree', 'weak')
    if raw_intention in ("open_border", "nonsense"):
        intention = raw_intention
        intention_degree = 'strong'
    elif intention_degree == "weak":
        intention = "chat"
    else:
        intention = raw_intention
    response = intention_task_reply.get('reply', '')
    return {
        "raw_intention": raw_intention,
        "intention_degree": intention_degree,
        "intention": intention,
        "response": response
    }


def get_decision_result(intention, req, save_data={}, use_random=True):
    # decision_gm_fn = None
    key = intention
    if not use_random:
        if intention in action_space.decision_space and "func" in action_space.decision_space[key]:
            try:
                # todo Diplomacy_flag True?
                simulator_res_old = simulator.run(save_data, Preturns=20, Diplomacy_flag=True, workerAuto=False)
                simulator_res_old_stat = get_stats(simulator_res_old, get_civ_index(simulator_res_old, req['civ_name']))
                param = [req[x] for x in action_space.decision_space[key]['param']]
                # todo gm_fn Support for composition
                decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
                save_data_new = decision_gm_fn(save_data)
                simulator_res_new = simulator.run(save_data_new, Preturns=20, Diplomacy_flag=True, workerAuto=False)
                simulator_res_new_stat = get_stats(simulator_res_new, get_civ_index(simulator_res_new, req['civ_name']))
                # todo In addition to 'yes' and 'no'
                if simulator_res_new_stat['civ_strength'] > simulator_res_old_stat['civ_strength']:
                    return 'yes', action_space.decision_space[intention]['decisions']['yes'], decision_gm_fn
                else:
                    return 'no', action_space.decision_space[intention]['decisions']['no'], None
            except Exception as e:
                logger.error(f"""error in cget_decision_result {key}, {req}, {e}""")
                logger.exception(f"""error in cget_decision_result {key}, {req}, {traceback.format_exc()}""")
    decisions = action_space.decision_space[intention]['decisions']
    decision_result_raw = random.choice(list(decisions.keys()))
    param = [req[x] for x in action_space.decision_space[key]['param']]
    if decision_result_raw in ('no', 'nochange'):
        decision_gm_fn = None
    else:
        decision_gm_fn = action_space.decision_space[key]['func'](decision_result_raw)(*param)
    # decision_gm_fn = None if decision_result_raw in ('no', 'nochange') else decision_gm_fn
    return decision_result_raw, decisions[decision_result_raw], decision_gm_fn


def get_decision_reason(decision, intention, req, save_data={}, use_random=True):
    if not use_random:
        key = f"{intention}_{decision}"
        if key in action_space.decision_reason_simulate_space:
            try:
                param = [req[x] for x in action_space.decision_reason_simulate_space[key]['param']]
                result = action_space.decision_reason_simulate_space[key]['func'](*param)(save_data)
                # todo Reasons for Chinese translation
                if result is not None and isinstance(result, dict):
                    # todo deal with reason score
                    # {'result': False, 'reason': {'consent': ['-195'], 'reject': ["We don't have a good relationship", "You're not as good as me", 'If you have a defensive pact with another civ then we would get drawn into thier battles as well', 'I think I signed enough', '-195']}}
                    consent_reasons = result['reason']['consent']
                    reject_reasons = result['reason']['reject']
                else:
                    consent_reasons, reject_reasons = [], []
                # todo re-decision by reasons
                reasons = consent_reasons if decision == 'yes' else reject_reasons
                if len(reasons) > 0:
                    return ','.join(reasons[:2])
                else:
                    # todo No reason or a random reason?
                    logger.debug('0 reason in get_decision_reason', key, result)
                    return ''
            except Exception as e:
                logger.error(f"""error in get_decision_reason {key}, {req}, {e}""")
                logger.warning('error in get_decision_reason', key, req, traceback.format_exc())
    decision_reasons = action_space.decision_reason_space.get(intention + '_' + decision, [''])
    return ','.join([random.choice(decision_reasons)])


def extract_quotes_text(input_string):
    if isinstance(input_string, str):
        matches = re.findall(r'"(.*?)"|“(.*?)”|\'(.*?)\'', input_string)
        if not matches:
            return input_string
        longest_match = max(matches, key=lambda x: max(len(s) for s in x))
        return max(longest_match, key=len)
    else:
        return input_string
