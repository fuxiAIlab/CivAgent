import traceback

import jpype
from jpype import JPackage, JString, getDefaultJVMPath, startJVM
import os
import ujson as json
from civsim import utils
from civsim import logger

cwd_old = os.getcwd()
current_dir = os.path.dirname(os.path.abspath(__file__))
UncivGame = None
# GameInfo = JPackage('com.unciv.logic').GameInfo
UncivFiles = None
GameSettings = None
DiplomacyAutomation = None
DiplomacyFunctions = None
TradeLogic = None
TradeEvaluation = None
HeadTowardsEnemyCityAutomation = None
NextTurnAutomation = None
Paths = None
Files = None
IOException = None
uncivGame = None
# uncivGame.Current = None
gameSettings = None
uncivFiles = None


def returnGameInfo(filepath):
    content = None
    try:
        path = Paths.get(filepath)
        content = Files.readString(path)
    except IOException as e:
        logger.exception("An error occurred: ", exc_info=True)
    return content


def getGameInfo(filepath, return_dict=False):
    if isinstance(filepath, str):
        game_info = returnGameInfo(filepath)
    elif return_dict:
        game_info = filepath
    else:
        game_info = JString(json.dumps(filepath))
    return game_info


def init_jvm():
    if jpype.isJVMStarted():
        logger.debug("JVM already started")
        return
    jar_filename = "Unciv.jar"
    jar_path = os.path.join(current_dir, "..", "..", "resources", jar_filename)
    startJVM(getDefaultJVMPath(), "-Djava.class.path=%s" % jar_path)
    global UncivGame, UncivFiles, GameSettings, DiplomacyAutomation
    global DiplomacyFunctions, TradeLogic, TradeEvaluation, HeadTowardsEnemyCityAutomation
    global NextTurnAutomation, Paths, Files, IOException, uncivGame, gameSettings, uncivFiles
    UncivGame = JPackage('com.unciv').UncivGame
    UncivFiles = JPackage('com.unciv.logic.files').UncivFilesNoGdx
    GameSettings = JPackage('com.unciv.models.metadata').GameSettings
    DiplomacyAutomation = JPackage('com.unciv.logic.automation.civilization').DiplomacyAutomation
    DiplomacyFunctions = JPackage('com.unciv.logic.civilization.diplomacy').DiplomacyFunctions
    TradeLogic = JPackage('com.unciv.logic.trade').TradeLogic
    TradeEvaluation = JPackage('com.unciv.logic.trade').TradeEvaluation
    HeadTowardsEnemyCityAutomation = JPackage('com.unciv.logic.automation.unit').HeadTowardsEnemyCityAutomation
    NextTurnAutomation = JPackage('com.unciv.logic.automation.civilization').NextTurnAutomation
    Paths = JPackage('java.nio.file').Paths
    Files = JPackage('java.nio.file').Files
    IOException = JPackage('java.io').IOException
    uncivGame = UncivGame()
    uncivGame.Current = uncivGame
    gameSettings = GameSettings()
    uncivFiles = UncivFiles()
    uncivGame.settings = gameSettings


def close_jvm():
    jpype.shutdownJVM()
    return


def get_gameInfoFromString(gameinfo):
    os.chdir(os.path.join(current_dir, ".."))
    game = uncivFiles.gameInfoFromString_civsim(gameinfo)
    os.chdir(cwd_old)
    return game


def wantsToSignDeclarationOfFrienship(gameinfo, civ_name_1, civ_name_2):
    """
       Assessing whether our civilization can sign a declaration of friendship with the target civilization.
       Parameters:
           gameinfo: String
               Representing game information.
           civ_name_1: String
               The name of our civilization. Active party.
           civ_name_2: String
               The name of the target civilization. Passive party.
       Returns:
            String: A JSON string containing the result and reason for being able to sign a declaration of friendship.
       Example:
            wantsToSignDeclarationOfFrienship(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
   """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToSignDeclarationOfFrienship_civsim(civ1, civ2)
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(key)
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(key)
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def wantsToOpenBorders(gameinfo, civ_name_1, civ_name_2):
    """
        Retrieves whether a civilization wants to open borders with another civilization.
        Parameters:
            gameinfo: String
               Representing game information.
            civ_name_1: String
               The name of our civilization. Active party.
            civ_name_2: String
               The name of the target civilization. Passive party.
        Returns:
            String: A JSON string containing the result and reason for wanting to open borders
        Example:
            wantsToOpenBorders(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToOpenBorders_civsim(civ1, civ2)
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(key)
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(key)
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def wantsToSignDefensivePact(gameinfo, civ_name_1, civ_name_2):
    """
       Assessing whether our civilization can sign a defensive pact with the target civilization.
       Parameters:
           gameinfo: String
               Representing game information.
           civ_name_1: String
               The name of our civilization. Active party.
           civ_name_2: String
               The name of the target civilization. Passive party.
       Returns:
            String: A JSON string containing the result and reason for being able to sign defensive pact.
       Example:
             wantsToSignDefensivePact(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
   """

    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToSignDefensivePact_civsim(civ1, civ2)
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(str(key))
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def hasAtLeastMotivationToAttack(gameinfo, civ_name_1, civ_name_2, motivation=10):
    """
        Assessing whether a civilization has a motivation level above a certain value to determine whether to issue a declaration of peace or declare war.
        Parameters:
            gameinfo: String
                Representing game information.
            civ_name_1: String
                The name of our civilization. Active party.
            civ_name_2: String
                The name of the target civilization. Passive party.
            motivation: Int
                The minimum motivation level for the attack.The default threshold for initiating war is 20, and the threshold for peace is 10.
        Returns:
            String: A JSON string containing the result and reason for whether to attack or pursue peace.
        Example:
            hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20) => {"result": "false", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.hasAtLeastMotivationToAttack_civsim(civ1, civ2, motivation)
    # python_reason = [str(item) for item in reason.getSecond()]
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(str(key))
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    # pair_dict : {"result": xxx, "reason": {'consent':[],'reject':[] }}
    json_data = json.dumps(pair_dict)
    return json_data


def canSignResearchAgreementsWith(gameinfo, civ_name_1, civ_name_2):
    """
        Assessing whether our civilization can sign a research agreement with the target civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ_name_1: String
                The name of our civilization. Active party.
            civ_name_2: String
                The name of the target civilization. Passive party.
        Returns:
            String: A JSON string containing the result and reason for being able to sign research agreements
        Example:
            canSignResearchAgreementsWith(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    diplomacy_functions = DiplomacyFunctions(civ1)
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = diplomacy_functions.canSignResearchAgreementsWith_civsim(civ2)
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(str(key))
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def getTradeAcceptability(gameinfo, civ_name_1, civ_name_2):
    """
        Our civilization needs to respond to the trade request initiated by the target civilization
        Parameters:
            gameinfo: String
                Representing game information.
            civ_name_1: String
                The name of our civilization. The responding party to the treaty
            civ_name_2: String
                The name of the target civilization. The party initiating the treaty
        Returns:
            String: A JSON string containing the response result to the trade request, as well as the reasons.
        Example:
            replyTrades(gameinfo, rome, greece) => {"result": "false", "reason": "I need more resources"}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    trade_requests = civ2.getTradeRequests()
    iterator = trade_requests.iterator()
    while iterator.hasNext():
        trade_requests = iterator.next()
        if utils.fix_civ_name(civ_name_1) == game.getCivilization(trade_requests.requestingCiv).getCivName():
            trade_logic = TradeLogic(civ1, civ2)
            trade_logic.getCurrentTrade().set(trade_requests.trade)
            iterator.remove()
            trade_evaluation = TradeEvaluation()
            reason = trade_evaluation.isTradeAcceptable_civsim(trade_logic.getCurrentTrade(), civ1, civ2)
            python_reason = {'consent': [], 'reject': []}
            for key in reason.getSecond()['consent']:
                python_reason['consent'].append(str(key))
            for key in reason.getSecond()['reject']:
                python_reason['reject'].append(str(key))
            pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
            json_data = json.dumps(pair_dict)
            return json_data
    return json.dumps({"result": 'false', "reason": "No trade requests found"})

def hasAtLeastMotivationToAttackScore(gameinfo, civ_name_1, civ_name_2, motivation):
    """
        Retrieves the score indicating whether a civilization has at least a certain motivation level to attack another civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ_name_1: String
                The name of our civilization. Active party.
            civ_name_2: String
                The name of the target civilization. Passive ization.
        motivation: Int
            The minimum motivation level for the attack.The default threshold for initiating war is 20, and the threshold for peace is 10.
        Returns:
            String: String representation of the score indicating the motivation to attack
        Example:
            hasAtLeastMotivationToAttackScore(gameinfo, rome, greece, 20) => "true"
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    result = DiplomacyAutomation.INSTANCE.hasAtLeastMotivationToAttack(civ1, civ2, motivation)
    return str(result)


def getEnemyCitiesByPriority(gameinfo, civ_name_1, id):
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
            getEnemyCitiesByPriority(gameinfo, rome, 1) => "(1, 2)"
    """
    try:
        game = get_gameInfoFromString(gameinfo)
        uncivGame.setGameInfo(game)
        uncivGame.Current = uncivGame
        civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
        unit = NextTurnAutomation.INSTANCE.getunits(civ1, int(id))
        city_position = HeadTowardsEnemyCityAutomation.INSTANCE.getEnemyCities(unit)
        return str(city_position)
    except Exception as e:
        logger.error(f"Error in getEnemyCitiesByPriority: {e} {traceback.format_exc()}")
        return str("None")


def predicted(gameinfo, turns, diplomacy_flag, workerAuto):
    """
        This function processes game information and returns predictions based on the parameters.
        Parameters:
            gameinfo: String
                String representing game information
            turns: Int
                The number of predicted returns
            diplomacy_flag: Bool
                Flag for diplomacy status
            workerAuto: Bool
                Flag for worker automation
        Returns:
            Dict: A dictionary representation of the predicted game state
        Example:
            predicted(gameinfo, 5, True, True) => savegame
    """
    if gameinfo is not None:
        gameinfo = getGameInfo(gameinfo)
        game = get_gameInfoFromString(gameinfo)
        uncivGame.setGameInfo(game)
        uncivGame.Current = uncivGame
        game.nextTenTurn(turns, diplomacy_flag, workerAuto, False)
        savegame = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(savegame))


def getTechToResarchAvailable(gameinfo, civ1_name):
    """
        Retrieves available technologies for research for a given civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ1_name: String
                The name of our civilization.
        Returns:
            String: String representation of available technologies for research
        Example:
            getTechToResarchAvailable(gameinfo, rome) => "['Agriculture', 'Animal Husbandry', 'Writing']"
    """
    gameinfo = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(gameinfo)
    uncivGame.Current = uncivGame
    civ1 = gameinfo.getCivilization(utils.fix_civ_name(civ1_name))
    tech = NextTurnAutomation.INSTANCE.getGroupedResearchableTechsAsString(civ1)
    tech = str(tech)
    return tech


def getProductionToBuildAvailable(gameinfo, civ1_name):
    """
        Retrieves available production options for a given civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ1_name: String
                The name of our civilization.
        Returns:
            String: String representation of available production options
        Example:
            getProductionToBuildAvailable(gameinfo, rome) => "['Monument', 'Granary', 'Shrine']"
    """
    gameinfo = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(gameinfo)
    uncivGame.Current = uncivGame
    civ1 = gameinfo.getCivilization(utils.fix_civ_name(civ1_name))
    building = NextTurnAutomation.INSTANCE.getAllProductionToBuild_available(civ1)
    building = str(building)
    return building


def chooseTechToResarch(gameinfo, civ1_name):
    """
        Chooses a technology to research for a given civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ1_name: String
                The name of our civilization.
        Returns:
            String: A JSON string containing the chosen technology to research
        Example:
            chooseTechToResarch(gameinfo, rome) => {"result": "Masonry"}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ1_name))
    result = NextTurnAutomation.INSTANCE.chooseTechToResearch_civsim(civ1)
    pair_dict = {"result": str(result)}
    json_data = json.dumps(pair_dict)
    return json_data


def chooseNextConstruction(gameinfo, civ1_name, city_name):
    """
        Chooses the next construction for a specific city within a civilization.
        Parameters:
            gameinfo: String
                Representing game information.
            civ1_name: String
                The name of our civilization.
            city_name: String
                This is the name of a city belonging to our civilization.
        Returns:
            String: A JSON string containing the chosen construction for the city
        Example:
            chooseNextConstruction(gameinfo, rome, rome) => {"result": "worker"}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ1_name))
    city = civ1.getCity(city_name)
    building = city.chooseNextConstruction_civsim()
    pair_dict = {"result": str(building)}
    json_data = json.dumps(pair_dict)
    return json_data


def run_getEnemyCitiesByPriority(filepath, civ_name_1, id):
    game_info = getGameInfo(filepath)
    json_data = getEnemyCitiesByPriority(game_info, civ_name_1, id)
    return json_data


def run(filepath, turns, diplomacy_flag, workerAuto, http_automation=False):
    game_info = getGameInfo(filepath)

    def predicted(gameinfo):
        if gameinfo is not None:
            game = get_gameInfoFromString(gameinfo)
            uncivGame.setGameInfo(game)
            uncivGame.Current = uncivGame
            game.nextTenTurn(turns, diplomacy_flag, workerAuto, http_automation)
            gameinfo = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(gameinfo))

    gameinfo_after10 = predicted(game_info)
    return gameinfo_after10


def run_hasAtLeastMotivationToAttackScore(filepath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filepath)
    json_data = hasAtLeastMotivationToAttackScore(game_info, civ_name_1, civ_name_2, 20)
    return json_data


def run_wantsToOpenBorders(filepath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filepath)
    json_data = wantsToOpenBorders(game_info, civ_name_1, civ_name_2)
    return json_data


def run_wanwantsToSignDeclarationOfFrienship(filepath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filepath)
    json_data = wantsToSignDeclarationOfFrienship(game_info, civ_name_1, civ_name_2)
    return json_data


def run_wantsToSignDefensivePact(filepath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filepath)
    json_data = wantsToSignDefensivePact(game_info, civ_name_1, civ_name_2)
    return json_data


def run_hasAtLeastMotivationToAttack(filepath, civ_name_1, civ_name_2, atlesat=10):
    game_info = getGameInfo(filepath)
    json_data = hasAtLeastMotivationToAttack(game_info, civ_name_1, civ_name_2, atlesat)
    return json_data


def run_canSignResearchAgreementsWith(filepath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filepath)
    json_data = canSignResearchAgreementsWith(game_info, civ_name_1, civ_name_2)
    return json_data


def run_getTradeAcceptability(filepath, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict):
    game_info = getGameInfo(filepath, return_dict=True)
    # todo check: Does it take effect when put into the save file or as a treaty pending decision?
    game_info = utils.trade_offer(game_info, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict)
    json_data = getTradeAcceptability(game_info, civ_name_1, civ_name_2)
    return json_data


if __name__ == '__main__':
    init_jvm()
    run("Autosave-China-60", 20, False, True, False)
    print(run_hasAtLeastMotivationToAttack('Autosave-China-60', 'China', 'Aztecs'))
    print(run_canSignResearchAgreementsWith('Autosave-China-60', 'China', 'Aztecs'))
    close_jvm()
