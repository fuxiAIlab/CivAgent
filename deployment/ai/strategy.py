from typing import Any, Dict, Tuple

import ujson as json

from civagent.config import config_data
from civagent.skills import reply_declarefrienship, reply_trades_from_skills
from civagent.utils.skills_utils import get_skills
from civsim.simulator import simulator as simulator

use_ai = config_data["use_ai"]


def canSignResearchAgreementsWith(
    gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict
) -> Tuple[str, Dict[str, Any]]:
    """
    Assessing whether our civilization can sign a research agreement with the target civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization. Active party.
        civ_name_2: String
            The name of the target civilization. Passive party.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the result of being able to sign research agreements.
        if use_ai == 'native_unciv':
            String: A JSON string containing the result and reason for being able to sign research agreements
    Example:
        if use_ai == 'civagent':
            canSignResearchAgreementsWith(gameinfo, rome, greece) => {"result": "false"}
        if use_ai == 'native_unciv':
            canSignResearchAgreementsWith(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    if use_ai == "civagent":
        return get_skills("research_agreement", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return (
            simulator.canSignResearchAgreementsWith(gameinfo, civ_name_1, civ_name_2),
            {},
        )
    else:
        # todo write your custom ai
        raise


def wantsToSignDefensivePact(
    gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict
) -> Tuple[str, Dict[str, Any]]:
    """
    Assessing whether our civilization can sign a defensive pact with the target civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization. Active party.
        civ_name_2: String
            The name of the target civilization. Passive party.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the result of being able to sign defensive pact.
        if use_ai == 'native_unciv':
            String: A JSON string containing the result and reason for being able to sign defensive pact.
    Example:
        if use_ai == 'civagent':
            wantsToSignDefensivePact(gameinfo, rome, greece) => {"result": "false"}
        if use_ai == 'native_unciv':
            wantsToSignDefensivePact(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    if use_ai == "civagent":
        return get_skills("form_ally", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return simulator.wantsToSignDefensivePact(gameinfo, civ_name_1, civ_name_2), {}
    else:
        # todo write your custom ai
        raise


def hasAtLeastMotivationToAttack(
    gameinfo: str,
    civ_name_1: str,
    civ_name_2: str,
    game_skill_data: Dict,
    motivation: int = 20,
) -> Tuple[str, Dict[str, Any]]:
    """
    Assessing whether a civilization has a motivation level above a certain value to determine whether to issue a declaration of peace or declare war.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization. Active party.
        civ_name_2: String
            The name of the target civilization. Passive party.
        game_skill_data: Dict
            A dictionary containing game skill data.
        motivation: Int
            The minimum motivation level for the attack.The default threshold for initiating war is 20, and the threshold for peace is 10.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the result of whether to attack or pursue peace.
        if use_ai == 'native_unciv':
            String: A JSON string containing the result and reason for whether to attack or pursue peace.
    Example:
        if use_ai == 'civagent':
            hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20) => {"result": "true"}
        if use_ai == 'native_unciv':
            hasAtLeastMotivationToAttack(gameinfo, rome, greece, 20) => {"result": "false", "reason": "Rome has a high level of trust with Greece."}
    """
    if use_ai == "civagent":
        key = "seek_peace" if motivation < 20 else "declare_war"
        return get_skills(key, civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return (
            simulator.hasAtLeastMotivationToAttack(gameinfo, civ_name_1, civ_name_2, motivation),
            {},
        )
    else:
        # todo write your custom ai
        raise


def wantsToSignDeclarationOfFriendship(
    gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict
) -> Tuple[str, Dict[str, Any]]:
    """
    Assessing whether our civilization can sign a declaration of friendship with the target civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization. Active party.
        civ_name_2: String
            The name of the target civilization. Passive party.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the result of being able to sign a declaration of friendship.
        if use_ai == 'native_unciv':
            String: A JSON string containing the result and reason for being able to sign a declaration of friendship.
    Example:
        if use_ai == 'civagent':
            wantsToSignDeclarationOfFriendship(gameinfo, rome, greece) => {"result": "false"}
        if use_ai == 'native_unciv':
            wantsToSignDeclarationOfFriendship(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    if use_ai == "civagent":
        return get_skills("change_closeness", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return (
            simulator.wantsToSignDeclarationOfFriendship(gameinfo, civ_name_1, civ_name_2),
            {},
        )
    else:
        # todo write your custom ai
        raise


def chooseTechToResearch(
    gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict
) -> Tuple[str, Dict[str, Any]]:
    """
    Chooses a technology to research for a given civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is a redundant parameter, the same as civ_name_1, the name of our civilization.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        String: A JSON string containing the chosen technology to research
    Example:
        chooseTechToResearch(gameinfo, rome, rome) => {"result": "Masonry"}
    """
    if use_ai == "civagent":
        return get_skills("choose_technology", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return simulator.chooseTechToResearch(gameinfo, civ_name_1), {}
    else:
        # todo write your custom
        raise


def chooseNextConstruction(
    gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict
) -> Tuple[str, Dict[str, Any]]:
    """
    Chooses the next construction for a specific city within a civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is the name of a city belonging to our civilization.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        String: A JSON string containing the chosen construction for the city
    Example:
        chooseNextConstruction(gameinfo, rome, rome) => {"result": "worker"}
    """
    if use_ai == "civagent":
        return get_skills("production_priority", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        return simulator.chooseNextConstruction(gameinfo, civ_name_1, civ_name_2), {}
    else:
        # todo write your custom ai
        raise


def commonEnemy(gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict) -> Tuple[str, Dict[str, Any]]:
    """
    Our civilization is considering whether to invite other civilizations to launch a joint attack against another civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization.
        civ_name_2: String
            This is a redundant parameter, set the same as civ_name_1, the name of our civilization.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string including the decision to launch a joint attack, cooperative civilizations, and the target civilization for the attack.
        if use_ai == 'native_unciv':
            String: It's not part of the original game logic, so we default to returning false.
    Example:
        if use_ai == 'civagent':
            commonEnemy(gameinfo, rome, rome) => {"result": "false", "to_civ": "greece", "enemy_civ": "egypt"}
        if use_ai == 'native_unciv':
            commonEnemy(gameinfo, rome, rome) => {"result": "false"}
    """
    if use_ai == "civagent":
        return get_skills("common_enemy", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        # not implement in native unciv
        return json.dumps({"result": "false"}), {}
    else:
        # todo write your custom ai
        raise


def buyLuxury(gameinfo: str, civ_name_1: str, civ_name_2: str, game_skill_data: Dict) -> Tuple[str, Dict[str, Any]]:
    """
    Our civilization is making a luxury goods request to the target civilization.
    Parameters:
        gameinfo: String
            If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
            Otherwise, it is represented as a gameid (Unique identifier of the game).
        civ_name_1: String
            The name of our civilization. Active party.
        civ_name_2: String
            The name of the target civilization. Passive party.
        game_skill_data: Dict
            A dictionary containing game skill data.
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the result of luxury goods trade request, amount of gold required, and the luxury goods involved.
        if use_ai == 'native_unciv':
            String: It's not part of the original game logic, so we default to returning false.
    Example:
        if use_ai == 'civagent':
            buyLuxury(gameinfo, rome, greece) => {"result": "false", "gold": 100, "luxury": "silk"}, "luxury" => ['Ivory', 'Citrus', 'Furs', 'Silk', 'Dyes', 'Copper', 'Salt', 'Silver', 'Stone', 'Gems', 'Truffles', 'Spices', 'Marble', 'Sugar', 'Whales', 'Porcelain', 'Crab', 'Pearls', 'Cotton', 'Jewelry', 'Incense', 'Wine']
        if use_ai == 'native_unciv':
            buyLuxury(gameinfo, rome, greece) => {"result": "false"}
    """
    if use_ai == "civagent":
        return get_skills("buy_luxury", civ_name_1, civ_name_2, game_skill_data)
    elif use_ai == "native_unciv":
        # not implement in native unciv
        return json.dumps({"result": "false"}), {}
    else:
        # todo write your custom ai
        raise


def replyTrades(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
    """
    Our civilization needs to respond to the trade request initiated by the target civilization
    Parameters:
        gameinfo: String
            Representing game save information.
        civ_name_1: String
            The name of our civilization. The responding party to the treaty
        civ_name_2: String
            The name of the target civilization. The party initiating the treaty
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the response result to the trade request.
        if use_ai == 'native_unciv':
            String: A JSON string containing the response result to the trade request, as well as the reasons.
    Example:
        if use_ai == 'civagent':
            replyTrades(gameinfo, rome, greece) => {"result": "yes"}
        if use_ai == 'native_unciv':
            replyTrades(gameinfo, rome, greece) => {"result": "yes", "reason": "I need more resources"}
    """
    if use_ai == "civagent":
        return reply_trades_from_skills(gameinfo, civ_name_1, civ_name_2, config_data)
    elif use_ai == "native_unciv":
        return simulator.getTradeAcceptability(gameinfo, civ_name_1, civ_name_2)
    else:
        # todo write your custom ai
        raise


def getOursEnemyCitiesByPriority(gameinfo: str, civ_name_1: str, unit_id: str) -> str:
    """
     For our civilization's units, assess the priority of the enemy city and return its coordinates.
     Parameters:
         gameinfo: String
             Representing game save information.
         civ_name_1: String
             The name of our civilization.
         unit_id: String
             ID of the unit
    Returns:
         String: The returned information is the coordinates of the city in the format (x, y).
     Example:
         getEnemyCitiesByPriority(gameinfo, rome, 1) => "(1, 2)"
    """
    if use_ai == "civagent":
        return simulator.getEnemyCitiesByPriority(gameinfo, civ_name_1, unit_id)
    elif use_ai == "native_unciv":
        return simulator.getEnemyCitiesByPriority(gameinfo, civ_name_1, unit_id)
    else:
        # todo write your custom ai
        raise


def replyDeclareFriendship(gameinfo: str, civ_name_1: str, civ_name_2: str) -> str:
    """
    Our civilization needs to respond to the declaration of friendship initiated by the target civilization
    Parameters:
        gameinfo: String
            Representing game save information.
        civ_name_1: String
            The name of our civilization. The responding party to the treaty
        civ_name_2: String
            The name of the target civilization. The party initiating the treaty
    Returns:
        if use_ai == 'civagent':
            String: A JSON string containing the response to the declaration of friendship.
        if use_ai == 'native_unciv':
            String: A JSON string containing the response and reason to the declaration of friendship.
    Example:
        if use_ai == 'civagent':
            replyDeclareFriendship(gameinfo, rome, greece) => {"result": "yes"}
        if use_ai == 'native_unciv':
            replyDeclareFriendship(gameinfo, rome, greece) => {"result": "yes", "reason":"Rome has a high level of trust with Greece"}
    """
    if use_ai == "civagent":
        return reply_declarefrienship(gameinfo, civ_name_1, civ_name_2, config_data)
    elif use_ai == "native_unciv":
        return simulator.wantsToSignDeclarationOfFriendship(gameinfo, civ_name_1, civ_name_2)
    else:
        # todo write your custom ai
        raise
