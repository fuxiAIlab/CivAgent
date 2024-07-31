from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify
import ujson as json
import logging
import traceback
from dataclasses import asdict
from civsim import utils
from civsim import logger
from civagent.utils.memory_utils import Memory
from civagent.utils.prompt_utils import admin_reply_make
# from deployment.chatbot.popo.popo_chatbot import PopoChatbot
from deployment.redis_mq import RedisStreamMQ
from deployment.chatbot.chatmanager import ChatManager

app = Flask(__name__)
mq = RedisStreamMQ()

# todo periodic refresh & use database
chat_managers = {}


def say_hello(
        chat_manager,
        robot_names,
        gameid,
        receiver,
        team_id,
        platform
):
    gameid2info = mq.get('gameid2info_' + gameid, {})
    gameid2info['gameid'] = gameid
    gameid2info['platform'] = platform
    for robot_name in robot_names:
        chat_manager.send_msg(
            text=admin_reply_make('join_game', gameid2info),
            sender=robot_name,
            receiver=receiver,
            platform=platform
        )
        chat_manager.send_group_msg(
            text=admin_reply_make('join_game', gameid2info),
            sender=robot_name,
            # receiver=receiver,
            platform=platform,
            team_id=team_id
        )


def admin_logic(
        chat_manager,
        admin_name,
        from_name,
        text,
        gameinfo,
        perv_gameid,
        platform
):
    gameid = utils.check_and_bind_gameid(text)
    if gameid:
        gameinfo = mq.get(gameid, "")
        # chat_manager.send_msg(
        #     'receive:' + text,
        #     sender=admin_name,
        #     receiver=from_name,
        #     platform=platform
        # )
        gameid2info = mq.get('gameid2info_' + gameid, {})
        gameid2info['gameid'] = gameid
        gameid2info['platform'] = platform
        if gameinfo:
            prev_gameid = chat_manager.game_id
            chat_manager.game_id = gameid
            mq.set(f'gameid2userid_{gameid}', str(from_name))
            chat_manager.send_msg(
                text=admin_reply_make('successful_detection', gameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
            chat_manager.send_msg(
                text=admin_reply_make('gm_intro', gameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
            mq.set(f"userid2gameid_{from_name}", gameid)
            mq.set(f"gameid2platform_{gameid}", platform)
            player_civ = gameinfo.get('player_civ')[0]
            mq.set(f"civ2userid_{gameid}_{player_civ}", from_name)
            civ_robots = gameinfo.get('civ_robots')
            prev_team_id = chat_manager.get_teamid(platform)
            if gameid != prev_gameid or (prev_team_id is None or len(prev_team_id) < 2):
                prev_team_id = chat_manager.create_team(
                    team_name=admin_reply_make('team_name', gameid2info), uids=[from_name, *civ_robots], platform=platform
                )

            say_hello(
                chat_manager, civ_robots, gameid, from_name,
                team_id=prev_team_id, platform=platform
            )
        else:
            chat_manager.send_msg(
                admin_reply_make('failed_detection', gameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
    else:
        pervgameid2info = mq.get('gameid2info_' + perv_gameid, {})
        pervgameid2info['gameid'] = perv_gameid
        pervgameid2info['platform'] = platform
        if gameinfo:
            # If the game has already been started and the gameid is the same
            # Need to determine if it is the most recent first time entering gameid
            chat_manager.send_msg(
                text=admin_reply_make('successful_detection', pervgameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
            chat_manager.send_msg(
                text=admin_reply_make('gm_intro', pervgameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
        else:
            # haven't started the game yet or changed my save
            chat_manager.send_msg(
                text=admin_reply_make('gm_intro', pervgameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )
            chat_manager.send_msg(
                text=admin_reply_make('game_not_launched', pervgameid2info),
                sender=admin_name,
                receiver=from_name,
                platform=platform
            )


def reply(data, admin_name, platform):
    # from_name is user_id; only supports replying to human players now
    from_name, robot_name, text = ChatManager.extract_message(data, platform)
    if from_name not in chat_managers and from_name not in ChatManager.robot_names:
        chat_managers[from_name] = ChatManager(from_name)
    chat_manager: ChatManager = chat_managers[from_name]
    # previous gameid
    perv_gameid = mq.get(f"userid2gameid_{from_name}", "")
    gameinfo = mq.get(perv_gameid, "")
    gameid2info = mq.get('gameid2info_' + perv_gameid, {})
    gameid2info['gameid'] = perv_gameid
    gameid2info['platform'] = platform
    game_exist = True if gameinfo else False

    # previous gameid are not opened
    if not game_exist:
        if robot_name == admin_name:
            admin_logic(chat_manager, admin_name, from_name, text, gameinfo, perv_gameid, platform)
        else:
            chat_manager.send_msg(
                text=admin_reply_make('search_bot', gameid2info),
                sender=robot_name,
                receiver=from_name,
                platform=platform
            )
    else:
        gameid = utils.check_and_bind_gameid(text)
        if robot_name == admin_name and gameid:
            # switch to new gameid
            admin_logic(chat_manager, admin_name, from_name, text, gameinfo, perv_gameid, platform)
        else:
            chat_manager.game_id = perv_gameid if gameinfo else ''
            gameid = chat_manager.game_id
            chatmessage = chat_manager.convert_to_chatmessage(data, platform)
            chatmemory = chat_manager.get_chatmemory(chatmessage)
            chatmemory_d = asdict(chatmemory)
            chatmemory_d['debugInfo'] = json.dumps(chatmemory_d['debugInfo'], ensure_ascii=False)
            mq.xadd(gameid, chatmemory_d)
            Memory.persist_user_data({from_name: chatmemory_d})
            if gameid is not None and len(gameid) > 1:
                Memory.persist_user_data({chat_manager.game_id: chatmemory_d})
            # chat_manager.send_msg(
            #     'receive:' + text,
            #     sender=robot_name,
            #     receiver=from_name,
            #     platform=platform
            # )
            if robot_name == admin_name:
                chat_manager.send_msg(
                    text=admin_reply_make('analysis_gm', gameid2info).replace('\n', '').replace('\t', ''),
                    sender=admin_name,
                    receiver=from_name,
                    platform=platform
                )


@app.route('/healthz')
def healthz():
    return 'OK', 200


@app.route('/open-apis/fuxi-unciv/MsgPushDiscord', methods=['POST'])
def test_msg_push_discord():
    admin_name = 'Unciv_Bot'
    platform = 'discord'
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f'Get request.post {data}.')
            reply(data, admin_name, platform)
        except Exception as e:
            logger.exception(f'error {e}.', exc_info=True)
        return {"success": ""}
    else:
        return {'data': 'Unsupported request method'}


@app.route('/open-apis/fuxi-unciv/MsgPushFeishu', methods=['POST'])
def test_msg_push_feishu():
    admin_name = 'guanliyuan'
    platform = 'feishu'
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.info(f'Get request.post {data}.')
            reply(data, admin_name, platform)
            # return {'challenge':data['challenge']}
        except Exception as e:
            logger.exception(f'error {e}.', exc_info=True)
        return jsonify({"success": True}), 200
    else:
        return {'data': 'Unsupported request method'}


@app.route('/open-apis/fuxi-unciv/SendMsg', methods=['POST'])
def test_send_msg():
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f'Get request.post {data}.')
            user_id, is_group = str(data['userId']), data['isGroup']
            chat_manager: ChatManager = chat_managers[user_id]
            if is_group:
                chatmessage = chat_manager.send_group_msg(
                    data['notify'],
                    sender=data['fromBot'],
                    platform=data['msgType']
                )
            else:
                chatmessage = chat_manager.send_msg(
                    data['notify'],
                    sender=data['fromBot'],
                    receiver=data['toBot'],
                    platform=data['msgType']
                )
            chatmemory = chat_manager.get_chatmemory(chatmessage)
            chatmemory_d = asdict(chatmemory)
            # use debugInfo of request.get_json()
            chatmemory_d['debugInfo'] = json.dumps(data['debugInfo'])
            # do not persist error log
            if len(data['debugInfo']) > 0:
                Memory.persist_user_data({user_id: chatmemory_d})
                game_id = chat_manager.game_id
                if game_id is not None and len(game_id) > 1:
                    Memory.persist_user_data({game_id: chatmemory_d})
                    mq.xadd(game_id, chatmemory_d)
        except Exception as e:
            logger.exception(f'error {e}.', exc_info=True)
        return {"success": ""}
    else:
        return {'data': 'Unsupported request method'}


if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 2337), app)
    http_server.serve_forever()
