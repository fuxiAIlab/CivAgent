import json
import logging
import os
import time
import yaml
current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), '..', 'scripts', 'tasks', 'config.yaml'))
os.environ['CIVAGENT_CONFIG_PATH'] = config_path
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import civsim.simulator.simulator as simulator
from civagent.skills import reply_trades_from_skills, use_skills, reply_declarfrienship
from civagent.utils.skills_utils import get_skills
from civsim import logger
simulator.init_jvm()
app = Flask(__name__)
skills = {}
skill_num = {}
tech = {}
production = {}
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG)
current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
file_handler = logging.FileHandler(f'../Log/flask_{current_time}.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

with open(config_path, 'r') as file:
    config_data = yaml.safe_load(file)

use_ai = 'civagent'
# use_ai = 'native_unciv'


def get_canSignResearchAgreementsWith(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves whether a civilization can sign research agreements with another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for being able to sign research agreements
    '''
    if use_ai == 'civagent':
        return get_skills(
            "research_agreement", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.get_canSignResearchAgreementsWith(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise


def get_wantsToSignDefensivePact(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves whether a civilization wants to sign a defensive pact with another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for wanting to sign a defensive pact
    '''
    if use_ai == 'civagent':
        return get_skills(
            "form_ally", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.get_wantsToSignDefensivePact(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise

def get_hasAtLeastMotivationToAttack(gameinfo, civ_name_1, civ_name_2, motivation=20):
    '''
        Retrieves whether a civilization has at least a certain motivation level to attack another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        at_least: The minimum motivation level for the attack
        Returns:
        json_data: A JSON string containing the result and reason for having at least a certain motivation to attack
    '''
    if use_ai == 'civagent':
        key = "seek_peace" if motivation < 20 else "declare_war"
        return get_skills(
            key, civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.get_hasAtLeastMotivationToAttack(
            gameinfo, civ_name_1, civ_name_2, motivation
        )
    else:
        # todo write your custom ai
        raise


def get_wantsToSignDeclarationOfFrienship(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves whether a civilization wants to sign a declaration of friendship with another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for the declaration of friendship
    '''
    if use_ai == 'civagent':
        return get_skills(
            "change_closeness", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.get_wantsToSignDeclarationOfFrienship(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise


def chooseTechToResarch(gameinfo, civ_name_1, civ_name_2):
    '''
        Chooses a technology to research for a given civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        Returns:
        json_data: A JSON string containing the chosen technology to research
    '''
    if use_ai == 'civagent':
        return get_skills(
            "choose_technology", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.chooseTechToResarch(
            gameinfo, civ_name_1
        )
    else:
        # todo write your custom
        raise


def chooseNextConstruction(gameinfo, civ_name_1, civ_name_2):
    '''
        Chooses the next construction for a specific city within a civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        city_name: Name of the city
        Returns:
        json_data: A JSON string containing the chosen construction for the city
    '''
    if use_ai == 'civagent':
        return get_skills(
            "production_priority", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return simulator.chooseNextConstruction(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise

def get_commonenemy(gameinfo, civ_name_1, civ_name_2):
    '''
        Initiates a joint attack against a common enemy.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result of the joint attack initiation
    '''
    if use_ai == 'civagent':
        return get_skills(
            "common_enemy", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return json.dumps({'result': 'false'})
    else:
        # todo write your custom ai
        raise


def get_buyluxury(gameinfo, civ_name_1, civ_name_2):
    '''
        Initiates a trade for luxury goods between two civilizations.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result of the luxury goods trade initiation
    '''
    if use_ai == 'civagent':
        return get_skills(
            "common_ally", civ_name_1, civ_name_2,
            skills, skill_num, tech, production
        )
    elif use_ai == 'native_unciv':
        return json.dumps({'result': 'false'})
    else:
        # todo write your custom ai
        raise


def reply_trades(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves the trade acceptability between two civilizations.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for the trade acceptability
    '''
    if use_ai == 'civagent':
        return reply_trades_from_skills(
            gameinfo, civ_name_1, civ_name_2, config_data
        )
    elif use_ai == 'native_unciv':
        return simulator.get_getTradeAcceptability(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise

def get_getEnemyCitiesByPriority(gameinfo, civ_name_1, id):
    '''
       Retrieves enemy cities by priority for a given civilization and unit ID.
       Args:
       gameinfo: String representing game information
       civ_name_1: Name of the civilization
       id: ID of the unit
       Returns:
       str: String representation of the positions of enemy cities by priority（x,y）
    '''
    if use_ai == 'civagent':
        return simulator.get_getEnemyCitiesByPriority(
            gameinfo, civ_name_1, id
        )
    elif use_ai == 'native_unciv':
        return simulator.get_getEnemyCitiesByPriority(
            gameinfo, civ_name_1, id
        )
    else:
        # todo write your custom ai
        raise


def replyDeclarFrienship(gameinfo, civ_name_1, civ_name_2):
    '''
        Responds to a declaration of friendship between two civilizations.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the response to the declaration of friendship
        '''
    if use_ai == 'civagent':
        return reply_declarfrienship(
            gameinfo, civ_name_1, civ_name_2, config_data
        )
    elif use_ai == 'native_unciv':
        return simulator.get_wantsToSignDeclarationOfFrienship(
            gameinfo, civ_name_1, civ_name_2
        )
    else:
        # todo write your custom ai
        raise


@app.route('/decision', methods=['POST'])
def decision():
    data = request.json
    # if "skill" in data:
    if data["skill"] == "research_agreement":
        result = get_canSignResearchAgreementsWith(data["gameinfo"], data["civ1"], data["civ2"])
    elif data["skill"] == "form_ally":
        result = get_wantsToSignDefensivePact(data["gameinfo"], data["civ1"], data["civ2"])
    elif data["skill"] == "declare_war":
        result = get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 20)
    elif data["skill"] == "change_closeness":
        result = get_wantsToSignDeclarationOfFrienship(data["gameinfo"], data["civ1"], data["civ2"])
    elif data["skill"] == "choose_technology":
        result = chooseTechToResarch(data['gameinfo'], data["civ1"], data["civ2"])
    elif data["skill"] == "production_priority":
        result = chooseNextConstruction(data['gameinfo'], data["civ1"], data["civ2"])
    elif data["skill"] == "seek_peace":
        result = get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 10)
    elif data["skill"] == 'common_enemy':
        result = get_commonenemy(data["gameinfo"], data["civ1"], data["civ2"])
    elif data["skill"] == 'buy_luxury':
        result = get_buyluxury(data["gameinfo"], data["civ1"], data["civ2"])
    elif data["skill"] == 'open_borders':
        result = get_skills(data["skill"], data["civ1"], data["civ2"], skills, skill_num, tech, production)
    else:
        assert False, f'Invalid skill: {data["skill"]}'
    # else:
    #     result = get_skills(data["skill"], data["civ1"], data["civ2"], skills, skill_num, tech, production)
    return result


@app.route('/get_early_decision', methods=['POST'])
def getEarlyDecision():
    data = request.json
    result = use_skills(
        data["gameinfo"], data["civ1"], skills,
        skill_num, tech, production, config_data
    )
    return result


@app.route('/reply_trade', methods=['POST'])
def replyTrades():
    data = request.json
    result = reply_trades(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/wantsToDeclarationOfFrienship', methods=['POST'])
def wantsToDeclarationOfFrienship():
    data = request.json
    result = replyDeclarFrienship(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/getEnemyCitiesByPriority', methods=['POST'])
def getEnemyCitiesByPriority():
    data = request.json
    result =get_getEnemyCitiesByPriority(data["gameinfo"], data["civ1"], data["id"])
    return result


http_server = WSGIServer(('127.0.0.1', 2337), app)
http_server.serve_forever()
