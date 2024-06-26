import jpype
from jpype import JPackage, JString, getDefaultJVMPath, startJVM
import os
import json
from civsim import utils

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


def returnGameInfo(filePath):
    content = None
    try:
        path = Paths.get(filePath)
        content = Files.readString(path)
    except IOException as e:
        e.printStackTrace()
    return content


def getGameInfo(filePath, return_dict=False):
    if isinstance(filePath, str):
        game_info = returnGameInfo(filePath)
    elif return_dict:
        game_info = filePath
    else:
        game_info = JString(json.dumps(filePath))
    return game_info


def init_jvm():
    if jpype.isJVMStarted():
        print("JVM already started")
        return
    jar_filename = "Unciv.jar"
    jar_path = os.path.join(current_dir, "..", "resources", jar_filename)
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
    # json_data = json.dumps(pair_dict)
    return pair_dict


def get_wantsToOpenBorders(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves whether a civilization wants to open borders with another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for wanting to open borders
    '''
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
    # json_data = json.dumps(pair_dict)
    return pair_dict


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
    # json_data = json.dumps(pair_dict)
    return pair_dict


def get_hasAtLeastMotivationToAttack(gameinfo, civ_name_1, civ_name_2, atlesat=10):
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
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.hasAtLeastMotivationToAttack_civsim(civ1, civ2, atlesat)
    # python_reason = [str(item) for item in reason.getSecond()]
    python_reason = {'consent': [], 'reject': []}
    for key in reason.getSecond()['consent']:
        python_reason['consent'].append(str(key))
    for key in reason.getSecond()['reject']:
        python_reason['reject'].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    # pair_dict : {"result": xxx, "reason": {'consent':[],'reject':[] }}
    # json_data = json.dumps(pair_dict)
    return pair_dict


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
    # json_data = json.dumps(pair_dict)
    return pair_dict


def get_getTradeAcceptability(gameinfo, civ_name_1, civ_name_2):
    '''
        Retrieves the trade acceptability between two civilizations.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for the trade acceptability
    '''
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
            # json_data = json.dumps(pair_dict)
            return pair_dict


def get_hasAtLeastMotivationToAttackScore(gameinfo, civ_name_1, civ_name_2, atlesat):
    '''
        Retrieves the score indicating whether a civilization has at least a certain motivation level to attack another civilization.
        Args:
        gameinfo: String representing game information
        civ_name_1: Name of the first civilization
        civ_name_2: Name of the second civilization
        at_least: The minimum motivation level for the attack
        Returns:
        str: String representation of the score indicating the motivation to attack
    '''
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.hasAtLeastMotivationToAttack(civ1, civ2, atlesat)
    return str(reason)


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
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    unit = NextTurnAutomation.INSTANCE.getunits(civ1, int(id))
    city_position = HeadTowardsEnemyCityAutomation.INSTANCE.getEnemyCities(unit)
    return str(city_position)


def predicted(gameinfo, Preturns, Diplomacy_flag, workerAuto):
    '''
        This function processes game information and returns predictions based on the parameters.
        Args:
        gameinfo: String representing game information
        Preturns: The number of predicted returns
        Diplomacy_flag: Flag for diplomacy status
        workerAuto: Flag for worker automation
        Returns:
        dict: A dictionary representation of the predicted game state
        '''
    if gameinfo is not None:
        gameinfo = getGameInfo(gameinfo)
        game = get_gameInfoFromString(gameinfo)
        uncivGame.setGameInfo(game)
        uncivGame.Current = uncivGame
        game.nextTenTurn(Preturns, Diplomacy_flag, workerAuto, False)
        savegame = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(savegame))


def getTechToResarch_available(gameinfo, civ1_name):
    '''
        Retrieves available technologies for research for a given civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        Returns:
        str: String representation of available technologies for research
    '''
    gameinfo = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(gameinfo)
    uncivGame.Current = uncivGame
    civ1 = gameinfo.getCivilization(civ1_name)
    tech = NextTurnAutomation.INSTANCE.getGroupedResearchableTechsAsString(civ1)
    tech = str(tech)
    return tech


def getProductionToBuild_available(gameinfo, civ1_name):
    '''
        Retrieves available production options for a given civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        Returns:
        str: String representation of available production options
    '''
    gameinfo = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(gameinfo)
    uncivGame.Current = uncivGame
    civ1 = gameinfo.getCivilization(civ1_name)
    building = NextTurnAutomation.INSTANCE.getAllProductionToBuild_available(civ1)
    building = str(building)
    return building


def chooseTechToResarch(gameinfo, civ1_name):
    '''
        Chooses a technology to research for a given civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        Returns:
        str: JSON string containing the chosen technology to research
    '''
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(civ1_name)
    result = NextTurnAutomation.INSTANCE.chooseTechToResearch_civsim(civ1)
    pair_dict = {"result": str(result)}
    json_data = json.dumps(pair_dict)
    return json_data


def chooseNextConstruction(gameinfo, civ1_name, city_name):
    '''
        Chooses the next construction for a specific city within a civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the civilization
        city_name: Name of the city
        Returns:
        str: JSON string containing the chosen construction for the city
    '''
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(civ1_name)
    city = civ1.getCity(city_name)
    building = city.chooseNextConstruction_civsim()
    pair_dict = {"result": str(building)}
    json_data = json.dumps(pair_dict)
    return json_data


def run_getEnemyCitiesByPriority(filePath, civ_name_1, id):
    game_info = getGameInfo(filePath)
    json_data = get_getEnemyCitiesByPriority(game_info, civ_name_1, id)
    return json_data


def run(filePath, Preturns, Diplomacy_flag, workerAuto, http_automation=False):
    game_info = getGameInfo(filePath)

    def predicted(gameinfo):
        if gameinfo is not None:
            game = get_gameInfoFromString(gameinfo)
            uncivGame.setGameInfo(game)
            uncivGame.Current = uncivGame
            game.nextTenTurn(Preturns, Diplomacy_flag, workerAuto, http_automation)
            gameinfo = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(gameinfo))

    gameinfo_after10 = predicted(game_info)
    return gameinfo_after10


def run_hasAtLeastMotivationToAttackScore(filePath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filePath)
    json_data = get_hasAtLeastMotivationToAttackScore(game_info, civ_name_1, civ_name_2, 20)
    return json_data


def run_wantsToOpenBorders(filePath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filePath)
    json_data = get_wantsToOpenBorders(game_info, civ_name_1, civ_name_2)
    return json_data


def run_wanwantsToSignDeclarationOfFrienship(filePath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filePath)
    json_data = get_wantsToSignDeclarationOfFrienship(game_info, civ_name_1, civ_name_2)
    return json_data


def run_wantsToSignDefensivePact(filePath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filePath)
    json_data = get_wantsToSignDefensivePact(game_info, civ_name_1, civ_name_2)
    return json_data


def run_hasAtLeastMotivationToAttack(filePath, civ_name_1, civ_name_2, atlesat=10):
    game_info = getGameInfo(filePath)
    json_data = get_hasAtLeastMotivationToAttack(game_info, civ_name_1, civ_name_2, atlesat)
    return json_data


def run_canSignResearchAgreementsWith(filePath, civ_name_1, civ_name_2):
    game_info = getGameInfo(filePath)
    json_data = get_canSignResearchAgreementsWith(game_info, civ_name_1, civ_name_2)
    return json_data


def run_getTradeAcceptability(filePath, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict):
    game_info = getGameInfo(filePath, return_dict=True)
    # todo Does it take effect when put into the archive or as a treaty pending decision?
    game_info = utils.trade_offer(game_info, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict)
    json_data = get_getTradeAcceptability(game_info, civ_name_1, civ_name_2)
    return json_data


if __name__ == '__main__':
    init_jvm()
    run("Autosave-China-60", 20, False, True, False)
    print(run_hasAtLeastMotivationToAttack('Autosave-China-60', 'China', 'Aztecs'))
    print(run_canSignResearchAgreementsWith('Autosave-China-60', 'China', 'Aztecs'))
    close_jvm()
