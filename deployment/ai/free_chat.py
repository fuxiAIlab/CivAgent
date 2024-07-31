import ujson as json
import traceback
from civsim import utils
from civsim import logger
from civagent import civagent
from civagent.utils.utils import save2req
from deployment.redis_mq import RedisStreamMQ
from deployment.chatbot.chatmanager import ChatManager
from civagent.utils.memory_utils import ChatMemory
from civagent.utils.prompt_utils import admin_reply_make
from civagent.config import config_data
mq = RedisStreamMQ()


def router(user_input, save_data):
    user_input = user_input.lower()
    if 'gold' in user_input:
        input_parts = user_input.split()
        num = input_parts[1] if len(input_parts) >= 2 else '0'
        civ_name = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.add_gold(save_data, civ_name, int(float(num))), 'add_gold {} success'.format(num)
    elif 'tech' in user_input:
        input_parts = user_input.split()
        civ_name = input_parts[1] if len(input_parts) >= 2 else ''
        return utils.technology_instant(save_data, civ_name), 'add_tech success'
    elif 'build' in user_input:
        input_parts = user_input.split()
        civ_name = input_parts[1] if len(input_parts) >= 2 else ''
        return utils.construct_instant(save_data, civ_name), 'fast_build success'
    elif 'war' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.declare_war(save_data, civ_name_1, civ_name_2), 'declare_war success'
    elif 'border' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.open_borders(save_data, civ_name_1, civ_name_2), 'open_borders success'
    elif 'ally' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.form_ally(save_data, civ_name_1, civ_name_2), 'form_ally success'
    elif 'research' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.research_agreement(save_data, civ_name_1, civ_name_2), 'research_agreement success'
    elif 'defense' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.form_mutual_defense(save_data, civ_name_1, civ_name_2), 'mutual_defense success'
    elif 'peace' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        return utils.make_peace(save_data, civ_name_1, civ_name_2), 'make_peace success'
    elif 'annex' in user_input:
        input_parts = user_input.split()
        civ_name_1 = input_parts[1]
        civ_name_2 = input_parts[2] if len(input_parts) >= 3 else ''
        city_name = input_parts[3] if len(input_parts) >= 4 else ''
        return utils.annex_city(save_data, civ_name_1, civ_name_2, city_name), 'annex_city success'
    else:
        return save_data, 'unknown command'


def gm_commander(gm_text, save_data):
    try:
        save_data, msg = router(gm_text, save_data)
        # print(msg, text)
    except Exception as e:
        logger.exception(f'GM error {e}.', exc_info=True)
        msg = 'error'
    return save_data, msg


def process(data: ChatMemory):
    gameid, from_name = data.gameId, data.fromCiv
    robot_name, text = data.toCiv, data.notify
    assert utils.check_and_bind_gameid(gameid) == gameid, gameid
    game_context = mq.get('gameid2info_'+gameid, {})
    assert isinstance(game_context, dict), f"get {game_context}:{type(game_context)} from {gameid} in redis."

    civ_robots = game_context.get('civ_robots',[''])
    if robot_name not in ChatManager.admin_names and robot_name not in civ_robots:
        ChatManager.send_msg_by_http(
            gameid,
            admin_reply_make('querying_civ', game_context)+f'{civ_robots}。',
            robot_name,
            from_name,
            0
        )
    if game_context:
        is_bootstrap = json.loads(data.debugInfo).get('bootstrap', 0)
        file_path = utils.get_savefile(gameid)
        save_data = utils.get_latest_savefile(file_path)
        save_data_preview = utils.get_latest_savefile(file_path+'_Preview')
        if robot_name in ChatManager.admin_names:
            save_data, msg = gm_commander(text, save_data)
            logger.debug(f'GM command result: {msg}')
            if msg != 'unknown command' and msg != 'error':
                save_data_preview['currentTurnStartTime'] = save_data_preview.get('currentTurnStartTime', 0)+1
                utils.set_latest_savefile(file_path, save_data)
                utils.set_latest_savefile(file_path+'_Preview', save_data_preview)
                ChatManager.send_msg_by_http(
                    gameid,
                    f'{data.notify}!'+admin_reply_make('gm_command_success', game_context),
                    robot_name,
                    from_name,
                    0
                )
            else:
                ChatManager.send_msg_by_http(
                    gameid,
                    f'{data.notify}!'+admin_reply_make('gm_command_error', game_context),
                    robot_name,
                    from_name,
                    0
                )
        else:
            try:
                agent = civagent.CivAgent(
                    from_name, robot_name, "", "", save_data, gameid
                )
                agent.init()
                agent.update(save_data)
                req = save2req(save_data, agent, text, from_name, robot_name)
                logger.info(f'save2req: {req}')
                intention_result, _ = civagent.CivAgent.intention_understanding(
                    req, only_chat=is_bootstrap
                )
                logger.info(f'intention_result: {intention_result}')
                response_debug, _, decision_gm_fn = civagent.CivAgent.response(
                    req, intention_result, save_data, use_random=False
                )
                response = response_debug['response']
                # comment: Require users to initiate transactions instead of directly modifying the save file
                #
                # if decision_gm_fn is not None:
                #     logger.debug(f"decision_gm_fn is not None {response_debug}")
                #     save_data = decision_gm_fn(save_data)
                #     save_data_preview['currentTurnStartTime'] = save_data_preview.get('currentTurnStartTime', 0)+1
                #     utils.set_latest_savefile(file_path, save_data)
                #     utils.set_latest_savefile(file_path+'_Preview', save_data_preview)
                # else:
                #     logger.debug(f"decision_gm_fn is None {response_debug}")
                if config_data.get('debug_mode', 0):
                    text = f'{response}\n\n{response_debug}'
                else:
                    text = f'{response}'
                ChatManager.send_msg_by_http(
                    gameid,
                    text,
                    robot_name,
                    from_name,
                    0,
                    debug_info=response_debug
                )
            except Exception as e:
                logger.exception(f"LLM_error {e}.", exc_info=True)
                ChatManager.send_msg_by_http(
                    gameid,
                    admin_reply_make('LLM_error', game_context),
                    robot_name,
                    from_name,
                    0
                )
    return