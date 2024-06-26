import os
import yaml
current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), '..', 'scripts', 'tasks', 'config.yaml'))
os.environ['CIVAGENT_CONFIG_PATH'] = config_path
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import civsim.simulator.simulator as simulator
from civagent.tools import decision, get_wantsToDeclarationOfFrienship, use_tools, get_tools
simulator.init_jvm()
app = Flask(__name__)
tools = {}
tool_num = {}
tech = {}
production = {}
with open(config_path, 'r') as file:
    config_data = yaml.safe_load(file)


@app.route('/wantsToSignDefensivePact', methods=['POST'])
def wantsToSignDefensivePact():
    data = request.json
    result = simulator.get_wantsToSignDefensivePact(data['gameinfo'], data["civ1"], data["civ2"])
    return result


@app.route('/get_tools', methods=['POST'])
def gettools():
    data = request.json
    if "skill" in data:
        if data["skill"] == "research_agreement":
            result = simulator.get_canSignResearchAgreementsWith(data["gameinfo"], data["civ1"], data["civ2"])
        elif data["skill"] == "form_ally":
            result = simulator.get_wantsToSignDefensivePact(data["gameinfo"], data["civ1"], data["civ2"])
        elif data["skill"] == "declare_war":
            result = simulator.get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 20)
        elif data["skill"] == "change_closeness":
            result = simulator.get_wantsToSignDeclarationOfFrienship(data["gameinfo"], data["civ1"], data["civ2"])
        elif data["skill"] == "choose_technology":
            result = simulator.chooseTechToResarch(data['gameinfo'], data["civ1"])
        elif data["skill"] == "production_priority":
            result = simulator.chooseNextConstruction(data['gameinfo'], data["civ1"], data["civ2"])
        elif data["skill"] == "speek_peace":
            result = simulator.get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 10)
        else:
            assert False, f'Invalid skill: {data["skill"]}'
    else:
        result = get_tools(data['gameinfo'], data["civ1"], data["civ2"], tools, tool_num, tech, production)
    return result


@app.route('/use_tools', methods=['POST'])
def usetools():
    data = request.json
    result = use_tools(data["gameinfo"], data["civ1"], tools, tool_num, tech, production, config_data)
    return result


@app.route('/wantsToSignDeclarationOfFrienship', methods=['POST'])
def wantsToSignDeclarationOfFrienship():
    data = request.json
    result = simulator.get_wantsToSignDeclarationOfFrienship(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/wantsToDeclarationOfFrienship', methods=['POST'])
def wantsToDeclarationOfFrienship():
    data = request.json
    result = get_wantsToDeclarationOfFrienship(data["gameinfo"], data["civ1"], data["civ2"], config_data)
    return result


@app.route('/wantsToOpenBorders', methods=['POST'])
def wantsToOpenBorders():
    data = request.json
    result = simulator.get_wantsToOpenBorders(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/hasAtLeastMotivationToAttack', methods=['POST'])
def hasAtLeastMotivationToAttack():
    data = request.json
    result = simulator.get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 10)
    return result


@app.route('/canSignResearchAgreementsWith', methods=['POST'])
def canSignResearchAgreementsWith():
    data = request.json
    result = simulator.get_canSignResearchAgreementsWith(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/Decision', methods=['POST'])
def getTradeAcceptability():
    data = request.json
    if "skill" in data and data["skill"] == "trade":
        result = simulator.get_getTradeAcceptability(data["gameinfo"], data["civ1"], data["civ2"])
    else:
        result = decision(data["gameinfo"], data["civ1"], data["civ2"], config_data)
    return result


@app.route('/hasAtLeastMotivationToAttackCity', methods=['POST'])
def hasAtLeastMotivationToAttackCity():
    data = request.json
    result = simulator.get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"])
    return result


@app.route('/hasAtLeastMotivationToAttackScore', methods=['POST'])
def hasAtLeastMotivationToAttackScore():
    data = request.json
    result = simulator.get_hasAtLeastMotivationToAttackScore(data["gameinfo"], data["civ1"], data["civ2"], 20)
    return result


@app.route('/offerPeaceTreaty', methods=['POST'])
def offerPeaceTreaty():
    data = request.json
    result = simulator.get_hasAtLeastMotivationToAttack(data["gameinfo"], data["civ1"], data["civ2"], 10)
    return result


@app.route('/getEnemyCitiesByPriority', methods=['POST'])
def getEnemyCitiesByPriority():
    data = request.json
    result = simulator.get_getEnemyCitiesByPriority(data["gameinfo"], data["civ1"], data["id"])
    return result


http_server = WSGIServer(('127.0.0.1', 2337), app)
http_server.serve_forever()
