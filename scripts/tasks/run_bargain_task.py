import json
import logging
import os
import sys
current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), 'config.yaml'))
os.environ['CIVAGENT_CONFIG_PATH'] = config_path
import re
import time
from civsim import logger
from civsim import utils
from civsim.simulator import simulator
from civagent.civagent import CivAgent
from civagent.utils.utils import default_req
from civagent.utils.memory_utils import Memory
from civagent.utils.utils import save2req
from civsim.utils import default_chat_memory
import copy
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG)
current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
file_handler = logging.FileHandler(f'../../Log/bargin_{current_time}.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_chat(from_civ, to_civ, game_id, text):
    memo = copy.deepcopy(default_chat_memory)
    memo['from'] = from_civ
    memo['from_civ'] = from_civ
    memo['to'] = to_civ
    memo['to_civ'] = to_civ
    memo['game_id'] = game_id
    memo['notify'] = text
    memo['addtime'] = time.strftime("%Y-%m-%d %H:%M:%S")
    return memo


def save_chat(user_id, chat_data):
    Memory.persist_user_data({user_id: chat_data})


def get_req_buyer(buy_civ, seller_civ):
    req = copy.deepcopy(default_req)
    req['civ_name'] = buy_civ
    req['speaker_persona']['civ_name'] = seller_civ
    req['receiver_persona']['civ_name'] = buy_civ

    return req


def get_req_seller(buy_civ, seller_civ):
    req = copy.deepcopy(default_req)
    req['civ_name'] = seller_civ
    req['speaker_persona']['civ_name'] = buy_civ
    req['receiver_persona']['civ_name'] = seller_civ
    return req


def reply(agent, bargain_role, req, save_data, text, only_line=False):
    req['utterance'] = text
    req['bargain_role'] = bargain_role
    civ1_resource_dict, civ2_resource_dict, identify_result, _ = agent.extract_trades('propose_trade', req, model='gpt-3.5-turbo-1106')
    req['identify_result'] = identify_result
    # todo Change to buyer_resource_dict
    req['civ1_resource_dict'] = civ1_resource_dict
    req['civ2_resource_dict'] = civ2_resource_dict
    # req['intention'] = 'trade_bargain'
    # req['bargain_result'] = 'continue'
    req['bargain_cnt'] = 0

    if 'bottom_line' not in req:
        req['border_info'] = agent.get_resource_border(req, save_data)['border_info']
        bottom_line = agent.get_trade_bottom_line(req, save_data, bargain_role=bargain_role)
        req['bottom_line'] = bottom_line
        if only_line:
            return bottom_line, identify_result, req['border_info']
    response, actual_prompt = agent.bargain(req, save_data, model=agent.default_llm)
    return response


def check_model(model):
    if model == "gpt3.5":
        model = "gpt-3.5-turbo-1106"
    if model == "gpt4":
        model = "gpt-4-1106-preview"
    return model


def check_bargain_result(chat, response):
    chat_matches = re.findall(r'\b\d+\b', chat)
    response_matches = re.findall(r'\b\d+\b', response)
    if chat_matches and response_matches:
        chat_numbers = [int(match) for match in chat_matches]
        response_numbers = [int(match) for match in response_matches]
        chat_max_number = max(chat_numbers)
        response_max_number = max(response_numbers)
        if abs(response_max_number - chat_max_number) < 5:
            return True, response_max_number
    return False, 0


if __name__ == '__main__':
    arguments = sys.argv
    # arguments = 'none ../reproductions/Autosave-China-60 rome gpt3.5 china gpt3.5'.split(' ')
    logger.debug(f"Arguments: {arguments}")
    if len(arguments) > 1:
        save_path = str(arguments[1])
        buyer_civ = str(arguments[2]).lower()
        buyer_model = check_model(str(arguments[3]))
        seller_civ = str(arguments[4]).lower()
        seller_model = check_model(str(arguments[5]))
    else:
        logger.debug("No arguments provided")
        exit(0)
    result = {buyer_civ: 0, seller_civ: 0}
    success_num = 0
    for i in range(10):
        ts = time.strftime("%Y%m%d%H%M%S")
        user_id = 'test_bargain%s' % ts
        game_id = ts
        with open(save_path, 'r', encoding='utf-8') as file:
            save_data = json.load(file)
        civs = utils.get_all_civs(save_data)
        civ_resources = utils.get_all_resources(save_data)

        simulator.init_jvm()
        # user_id, civ_name, nicknames, character, game_info
        agent_buyer = CivAgent(user_id, buyer_civ, "", "", save_data, default_llm=buyer_model)
        agent_buyer.init()
        agent_buyer.update(save_data)
        agent_seller = CivAgent(user_id, seller_civ, "", "", save_data, default_llm=seller_model)
        agent_seller.init()
        agent_seller.update(save_data)
        # req_buyer = get_req_buyer(buyer_civ, seller_civ)

        # req_seller = get_req_seller(buyer_civ, seller_civ)

        current_file = os.path.abspath(__file__)
        current_directory = '../'  # os.path.dirname(current_file)

        initial_sentence = "Can I give you 50 gold in exchange for 2 luxury gems?"
        text = initial_sentence
        # todo memory
        req_buyer = save2req(save_data, agent_buyer, text, seller_civ, buyer_civ)
        buyer_line, buyer_identify_result, buyer_border_info = reply(agent_buyer, 'buyer', req_buyer, save_data, text, only_line=True)
        Market_price_top = int(buyer_line['bottom_line'][0].get('amount', 0)) * 1.2
        Market_price_bottom = int(buyer_identify_result['offer'][0].get('amount', 0)) * 0.8

        req_seller = save2req(save_data, agent_seller, text, buyer_civ, seller_civ)
        seller_line, seller_identify_result, seller_border_info = reply(agent_seller, 'seller', req_seller, save_data, text, only_line=True)

        for j in range(5):

            chat_data = get_chat(buyer_civ, seller_civ, game_id, text=text)
            save_chat(user_id, chat_data)
            req_seller = save2req(save_data, agent_seller, text, buyer_civ, seller_civ)
            req_seller['Market_price_top'] = Market_price_top
            req_seller['Market_price_bottom'] = Market_price_bottom
            req_seller['border_info'] = seller_border_info
            req_seller['bottom_line'] = seller_line
            response = reply(agent_seller, 'seller', req_seller, save_data, text)
            check_result, Price = check_bargain_result(chat_data['notify'], response['response'])
            if response.get('bargain_result', "").lower() == 'yes' or check_result:
                logger.debug('Trade successful')
                result[seller_civ] = ((abs(Price - Market_price_bottom) / abs(Market_price_top - Market_price_bottom)) + result[seller_civ] * success_num) / (success_num + 1)
                result[buyer_civ] = ((abs(Market_price_top - Price) / abs(Market_price_top - Market_price_bottom)) + result[buyer_civ] * success_num) / (success_num + 1)
                success_num += 1
                break
            elif response.get('bargain_result', "").lower() == 'no':
                logger.debug('Trade failed')
                break
            else:
                req_seller['bargain_cnt'] += 1
                req_seller = {**req_seller, **response}
                text = response['response']
            chat_data = get_chat(seller_civ, buyer_civ, game_id, text=text)
            save_chat(user_id, chat_data)
            req_buyer = save2req(save_data, agent_buyer, text, seller_civ, buyer_civ)
            req_buyer['Market_price_top'] = Market_price_top
            req_buyer['Market_price_bottom'] = Market_price_bottom
            req_buyer['border_info'] = buyer_border_info
            req_buyer['bottom_line'] = buyer_line
            response = reply(agent_buyer, 'buyer', req_buyer, save_data, text)
            check_result, Price = check_bargain_result(chat_data['notify'], response['response'])
            if response.get('bargain_result', "").lower() == 'yes' or check_result:
                logger.debug('Trade successful')
                result[seller_civ] = ((abs(Price - Market_price_bottom) / abs(Market_price_top - Market_price_bottom)) + result[seller_civ] * success_num) / (success_num + 1)
                result[buyer_civ] = ((abs(Market_price_top - Price) / abs(Market_price_top - Market_price_bottom)) + result[buyer_civ] * success_num) / (success_num + 1)
                success_num += 1
                break
            elif response.get('bargain_result', "").lower() == 'no':
                logger.debug('Trade failed')
                break
            else:
                req_buyer['bargain_cnt'] += 1
                req_buyer = {**req_buyer, **response}
                text = response['response']
        logger.debug(success_num)
        logger.debug(result)
    logger.debug(success_num)
    logger.debug(result)
simulator.close_jvm()
