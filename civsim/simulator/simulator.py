import os
from typing import Any, Dict, List, Union

import jpype
import ujson as json
from jpype import JPackage, JString, getDefaultJVMPath, startJVM

from civsim import logger, utils

cwd_old: str = os.getcwd()
current_dir: str = os.path.dirname(os.path.abspath(__file__))
UncivGame: Union[JPackage, None] = None
UncivFiles: Union[JPackage, None] = None
GameSettings: Union[JPackage, None] = None
DiplomacyAutomation: Union[JPackage, None] = None
DiplomacyFunctions: Union[JPackage, None] = None
TradeLogic: Union[JPackage, None] = None
TradeEvaluation: Union[JPackage, None] = None
HeadTowardsEnemyCityAutomation: Union[JPackage, None] = None
NextTurnAutomation: Union[JPackage, None] = None
Paths: Union[JPackage, None] = None
Files: Union[JPackage, None] = None
IOException: Union[JPackage, None] = None
uncivGame: Union[JPackage, None] = None
gameSettings: Union[JPackage, None] = None
uncivFiles: Union[JPackage, None] = None


def returnGameInfo(filepath: str) -> Union[str, None]:
    content: Union[str, None] = None
    try:
        path = Paths.get(filepath)
        content = Files.readString(path)
    except IOException as e:
        logger.exception(f"An error occurred {e}: ", exc_info=True)
    return content


def getGameInfo(filepath: Union[str, dict], return_dict: bool = False) -> Union[str, dict, JString]:
    if isinstance(filepath, str):
        game_info = returnGameInfo(filepath)
        if return_dict:
            game_info = utils.json_load_defaultdict(game_info)
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
    UncivGame = JPackage("com.unciv").UncivGame
    UncivFiles = JPackage("com.unciv.logic.files").UncivFilesNoGdx
    GameSettings = JPackage("com.unciv.models.metadata").GameSettings
    DiplomacyAutomation = JPackage("com.unciv.logic.automation.civilization").DiplomacyAutomation
    DiplomacyFunctions = JPackage("com.unciv.logic.civilization.diplomacy").DiplomacyFunctions
    TradeLogic = JPackage("com.unciv.logic.trade").TradeLogic
    TradeEvaluation = JPackage("com.unciv.logic.trade").TradeEvaluation
    HeadTowardsEnemyCityAutomation = JPackage("com.unciv.logic.automation.unit").HeadTowardsEnemyCityAutomation
    NextTurnAutomation = JPackage("com.unciv.logic.automation.civilization").NextTurnAutomation
    Paths = JPackage("java.nio.file").Paths
    Files = JPackage("java.nio.file").Files
    IOException = JPackage("java.io").IOException
    uncivGame = UncivGame()
    uncivGame.Current = uncivGame
    gameSettings = GameSettings()
    uncivFiles = UncivFiles()
    uncivGame.settings = gameSettings


def close_jvm() -> None:
    jpype.shutdownJVM()
    return


def get_gameInfoFromString(gameinfo: str) -> Union[JPackage, None]:
    os.chdir(os.path.join(current_dir, ".."))
    game = uncivFiles.gameInfoFromString_civsim(gameinfo)
    os.chdir(cwd_old)
    return game


def wantsToSignDeclarationOfFriendship(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
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
         wantsToSignDeclarationOfFriendship(gameinfo, rome, greece)
         =>
         {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToSignDeclarationOfFriendship_civsim(civ1, civ2)
    python_reason = {"consent": [], "reject": []}
    for key in reason.getSecond()["consent"]:
        python_reason["consent"].append(key)
    for key in reason.getSecond()["reject"]:
        python_reason["reject"].append(key)
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def wantsToOpenBorders(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
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
        wantsToOpenBorders(gameinfo, rome, greece)
        =>
        {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToOpenBorders_civsim(civ1, civ2)
    python_reason = {"consent": [], "reject": []}
    for key in reason.getSecond()["consent"]:
        python_reason["consent"].append(key)
    for key in reason.getSecond()["reject"]:
        python_reason["reject"].append(key)
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def wantsToSignDefensivePact(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
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
          wantsToSignDefensivePact(gameinfo, rome, greece)
          =>
          {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """

    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.wantsToSignDefensivePact_civsim(civ1, civ2)
    python_reason = {"consent": [], "reject": []}
    for key in reason.getSecond()["consent"]:
        python_reason["consent"].append(str(key))
    for key in reason.getSecond()["reject"]:
        python_reason["reject"].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def hasAtLeastMotivationToAttack(gameinfo: str, civ_name_1: str, civ_name_2: str, motivation: int = 10) -> str:
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
        hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20)
        =>
        {"result": "false", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = DiplomacyAutomation.INSTANCE.hasAtLeastMotivationToAttack_civsim(civ1, civ2, motivation)
    # python_reason = [str(item) for item in reason.getSecond()]
    python_reason = {"consent": [], "reject": []}
    for key in reason.getSecond()["consent"]:
        python_reason["consent"].append(str(key))
    for key in reason.getSecond()["reject"]:
        python_reason["reject"].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    # pair_dict : {"result": xxx, "reason": {'consent':[],'reject':[] }}
    json_data = json.dumps(pair_dict)
    return json_data


def canSignResearchAgreementsWith(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
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
        canSignResearchAgreementsWith(gameinfo, rome, greece)
        =>
        {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ_name_1))
    diplomacy_functions = DiplomacyFunctions(civ1)
    civ2 = game.getCivilization(utils.fix_civ_name(civ_name_2))
    reason = diplomacy_functions.canSignResearchAgreementsWith_civsim(civ2)
    python_reason = {"consent": [], "reject": []}
    for key in reason.getSecond()["consent"]:
        python_reason["consent"].append(str(key))
    for key in reason.getSecond()["reject"]:
        python_reason["reject"].append(str(key))
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data


def getTradeAcceptability(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
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
        replyTrades(gameinfo, rome, greece)
        =>
        {"result": "false", "reason": "I need more resources"}
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
            python_reason = {"consent": [], "reject": []}
            for key in reason.getSecond()["consent"]:
                python_reason["consent"].append(str(key))
            for key in reason.getSecond()["reject"]:
                python_reason["reject"].append(str(key))
            pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
            json_data = json.dumps(pair_dict)
            return json_data
    return json.dumps({"result": "false", "reason": "No trade requests found"})


def hasAtLeastMotivationToAttackScore(gameinfo: str, civ_name_1: str, civ_name_2: str, motivation: int) -> str:
    """
    Retrieves the score indicating whether a civilization has at least a certain motivation level to attack another civilization.
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


def getEnemyCitiesByPriority(gameinfo: str, civ_name_1: str, unit_id: str) -> str:
    """
     For our civilization's units, assess the priority of the enemy city and return its coordinates.
     Parameters:
         gameinfo: String
             Representing game information.
         civ_name_1: String
             The name of our civilization.
         unit_id: String
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
        unit = NextTurnAutomation.INSTANCE.getunits(civ1, int(unit_id))
        city_position = HeadTowardsEnemyCityAutomation.INSTANCE.getEnemyCities(unit)
        return str(city_position)
    except Exception as e:
        logger.error("Error in getEnemyCitiesByPriority: " + str(e))
        return str("None")


def predicted(gameinfo: str, turns: int, diplomacy_flag: bool, worker_auto: bool) -> Dict:
    """
    This function processes game information and returns predictions based on the parameters.
    Parameters:
        gameinfo: String
            gameinfo is the json string of save file
        turns: Int
            The number of predicted returns
        diplomacy_flag: Bool
            Flag for diplomacy status
        worker_auto: Bool
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
        game.nextTenTurn(turns, diplomacy_flag, worker_auto, False)
        savegame = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(savegame))


def getTechToResearchAvailable(gameinfo: str, civ1_name: str) -> List[str]:
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
        getTechToResearchAvailable(gameinfo, rome) => "['Agriculture', 'Animal Husbandry', 'Writing']"
    """
    gameinfo = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(gameinfo)
    uncivGame.Current = uncivGame
    civ1 = gameinfo.getCivilization(utils.fix_civ_name(civ1_name))
    tech = NextTurnAutomation.INSTANCE.getGroupedResearchableTechsAsString(civ1)
    tech = str(tech).replace("\n", ", ").split(", ")
    return tech


def getProductionToBuildAvailable(gameinfo: str, civ1_name: str) -> str:
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
    buildings = NextTurnAutomation.INSTANCE.getAllProductionToBuild_available(civ1)
    buildings = str(buildings).rstrip("\n").replace(" : ", ": ").split("\n")
    productions = []
    for building_str in buildings:
        idx = building_str.find(": ")
        city = building_str[:idx]
        available_productions = building_str[idx + len(": ") :].split(", ")
        productions.append({"city": city, "available_productions": available_productions})
    return productions


def chooseTechToResearch(gameinfo: str, civ1_name: str) -> str:
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
        chooseTechToResearch(gameinfo, rome) => {"result": "Masonry"}
    """
    game = get_gameInfoFromString(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(utils.fix_civ_name(civ1_name))
    result = NextTurnAutomation.INSTANCE.chooseTechToResearch_civsim(civ1)
    pair_dict = {"result": str(result)}
    json_data = json.dumps(pair_dict)
    return json_data


def chooseNextConstruction(gameinfo: str, civ1_name: str, city_name: str) -> str:
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


def run(
    filepath: Union[str, dict],
    turns: int,
    diplomacy_flag: bool,
    worker_auto: bool,
    http_automation: bool = False,
) -> Dict:
    game_info = getGameInfo(filepath)

    def predicted(gameinfo: str) -> Dict:
        if gameinfo is not None:
            game = get_gameInfoFromString(gameinfo)
            uncivGame.setGameInfo(game)
            uncivGame.Current = uncivGame
            game.nextTenTurn(turns, diplomacy_flag, worker_auto, http_automation)
            gameinfo = uncivFiles.gameInfoToString(game, False, False)
        return json.loads(str(gameinfo))

    gameinfo_after10 = predicted(game_info)
    return gameinfo_after10


def run_hasAtLeastMotivationToAttackScore(filepath: str, civ_name_1: str, civ_name_2: str) -> str:
    game_info = getGameInfo(filepath)
    json_data = hasAtLeastMotivationToAttackScore(game_info, civ_name_1, civ_name_2, 20)
    return json_data


def run_wantsToOpenBorders(filepath: str, civ_name_1: str, civ_name_2: str) -> str:
    game_info = getGameInfo(filepath)
    json_data = wantsToOpenBorders(game_info, civ_name_1, civ_name_2)
    return json_data


def run_wantsToSignDeclarationOfFriendship(filepath: str, civ_name_1: str, civ_name_2: str) -> str:
    game_info = getGameInfo(filepath)
    result = wantsToSignDeclarationOfFriendship(game_info, civ_name_1, civ_name_2)
    return result


def run_wantsToSignDefensivePact(filepath: str, civ_name_1: str, civ_name_2: str) -> str:
    game_info = getGameInfo(filepath)
    result = wantsToSignDefensivePact(game_info, civ_name_1, civ_name_2)
    return result


def run_hasAtLeastMotivationToAttack(filepath: str, civ_name_1: str, civ_name_2: str, atlesat: int = 10) -> str:
    game_info = getGameInfo(filepath)
    result = hasAtLeastMotivationToAttack(game_info, civ_name_1, civ_name_2, atlesat)
    return result


def run_canSignResearchAgreementsWith(filepath: str, civ_name_1: str, civ_name_2: str) -> str:
    game_info = getGameInfo(filepath)
    result = canSignResearchAgreementsWith(game_info, civ_name_1, civ_name_2)
    return result


def run_getTradeAcceptability(
    filepath: str,
    civ_name_1: str,
    civ_name_2: str,
    civ1_resource_dict: Dict[str, Any],
    civ2_resource_dict: Dict[str, Any],
) -> str:
    game_info = getGameInfo(filepath, return_dict=True)
    # todo check: Does it take effect when put into the save file or as a treaty pending decision?
    game_info = utils.trade_offer(game_info, civ_name_1, civ_name_2, civ1_resource_dict, civ2_resource_dict)
    result = getTradeAcceptability(json.dumps(game_info), civ_name_1, civ_name_2)
    return result


if __name__ == "__main__":
    init_jvm()
    run("Autosave-China-60", 20, False, True, False)
    print(run_hasAtLeastMotivationToAttack("Autosave-China-60", "China", "Aztecs"))
    print(run_canSignResearchAgreementsWith("Autosave-China-60", "China", "Aztecs"))
    close_jvm()
