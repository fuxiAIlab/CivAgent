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
    """
        Assessing whether our civilization can sign a research agreement with the target civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of being able to sign research agreements.
            if use_ai == 'native_unciv':
                String: A JSON string containing the result and reason for being able to sign research agreements
        Example:
            if use_ai == 'civagent':
                get_canSignResearchAgreementsWith(gameinfo, rome, greece) => {"result": "false"}
            if use_ai == 'native_unciv':
                get_canSignResearchAgreementsWith(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
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
    """
        Assessing whether our civilization can sign a defensive pact with the target civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of being able to sign defensive pact.
            if use_ai == 'native_unciv':
                String: A JSON string containing the result and reason for being able to sign defensive pact.
        Example:
            if use_ai == 'civagent':
                get_wantsToSignDefensivePact(gameinfo, rome, greece) => {"result": "false"}
            if use_ai == 'native_unciv':
                get_wantsToSignDefensivePact(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
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
    """
        Assessing whether a civilization has a motivation level above a certain value to determine whether to issue a declaration of peace or declare war.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        motivation: Int
            The minimum motivation level for the attack.The default threshold for initiating war is 20, and the threshold for peace is 10.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of whether to attack or pursue peace.
            if use_ai == 'native_unciv':
                String: A JSON string containing the result and reason for whether to attack or pursue peace.
        Example:
            if use_ai == 'civagent':
                get_hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20) => {"result": "true"}
            if use_ai == 'native_unciv':
                get_hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20) => {"result": "false", "reason": "Rome has a high level of trust with Greece."}
    """
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
    """
        Assessing whether our civilization can sign a declaration of friendship with the target civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of being able to sign a declaration of friendship.
            if use_ai == 'native_unciv':
                String: A JSON string containing the result and reason for being able to sign a declaration of friendship.
        Example:
            if use_ai == 'civagent':
                get_wantsToSignDeclarationOfFrienship(gameinfo, rome, greece) => {"result": "false"}
            if use_ai == 'native_unciv':
                get_wantsToSignDeclarationOfFrienship(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
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
    """
        Chooses a technology to research for a given civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is a redundant parameter, the same as civ_name_1, the name of our civilization.
        Returns:
            String: A JSON string containing the chosen technology to research
        Example:
            chooseTechToResarch(gameinfo, rome, rome) => {"result": "Masonry"}
    """
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
    """
        Chooses the next construction for a specific city within a civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is the name of a city belonging to our civilization.
        Returns:
            String: A JSON string containing the chosen construction for the city
        Example:
            chooseNextConstruction(gameinfo, rome, rome) => {"result": "worker"}
    """
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
    """
        Our civilization is considering whether to invite other civilizations to launch a joint attack against another civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is a redundant parameter, the same as civ_name_1, the name of our civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string including the decision to launch a joint attack, cooperative civilizations, and the target civilization for the attack.
            if use_ai == 'native_unciv':
                String: It's not part of the original game logic, so we default to returning false.
        Example:
            if use_ai == 'civagent':
                get_commonenemy(gameinfo, rome, rome) => {"result": "false", "to_civ": "greece", "enemy_civ": "egypt"}
            if use_ai == 'native_unciv':
                get_commonenemy(gameinfo, rome, rome) => {"result": "false"}
    """
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
    """
        Our civilization is making a luxury goods request to the target civilization.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of luxury goods trade request, amount of gold required, and the luxury goods involved.
            if use_ai == 'native_unciv':
                String: It's not part of the original game logic, so we default to returning false.
        Example:
            if use_ai == 'civagent':
                get_buyluxury(gameinfo, rome, greece) => {"result": "false", "gold": 100, "luxury": "silk"}
            if use_ai == 'native_unciv':
                get_buyluxury(gameinfo, rome, greece) => {"result": "false"}
    """
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
    """
        Our civilization needs to respond to the trade request initiated by the target civilization
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the response result to the trade request.
            if use_ai == 'native_unciv':
                String: A JSON string containing the response result to the trade request, as well as the reasons.
        Example:
            if use_ai == 'civagent':
                reply_trades(gameinfo, rome, greece) => {"result": "yes"}
            if use_ai == 'native_unciv':
                reply_trades(gameinfo, rome, greece) => {"result": "yes", "reason": "I need more resources"}
    """
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
    """
        For our civilization's units, assess the priority of the enemy city and return its coordinates.
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        id: String
            ID of the unit
       Returns:
            String: The returned information is the coordinates of the city in the format (x, y).
        Example:
            get_getEnemyCitiesByPriority(gameinfo, rome, 1) => "(1, 2)"
    """
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
    """
        Our civilization needs to respond to the declaration of friendship initiated by the target civilization
        Parameters:
        gameinfo: String
            Representing game information.
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            The name of the target civilization.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the response to the declaration of friendship.
            if use_ai == 'native_unciv':
                String: A JSON string containing the response and reason to the declaration of friendship.
        Example:
            if use_ai == 'civagent':
                replyDeclarFrienship(gameinfo, rome, greece) => {"result": "yes"}
            if use_ai == 'native_unciv':
                replyDeclarFrienship(gameinfo, rome, greece) => {"result": "yes", "reason":"Rome has a high level of trust with Greece"}
    """
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
    result = get_getEnemyCitiesByPriority(data["gameinfo"], data["civ1"], data["id"])
    return result


http_server = WSGIServer(('127.0.0.1', 2337), app)
http_server.serve_forever()
