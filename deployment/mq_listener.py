import ujson as json
import asyncio
import aiohttp
import time
import traceback
import requests
from datetime import datetime
import logging
from civsim import logger
from deployment.chatbot.chatmanager import ChatManager
from deployment.redis_mq import RedisStreamMQ
from civagent.config import config_data

mq = RedisStreamMQ()
gameid_civ_lock = {}


async def make_async_request(url, data):
    async with aiohttp.ClientSession() as session:
        headers = {'Content-Type': 'application/json'}
        try:
            async with session.post(url, data=json.dumps(data), headers=headers, timeout=15) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Error for {data}: {response.status} - {response.reason}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Error for {data}: {e}")
            return None

async def main():
    global gameid_civ_lock
    global mq
    while True:
        msgss = mq.get_unconsumed_streams()
        msgss = [(msgs[0], x) for msgs in msgss for x in msgs[1]]
        for msgs in msgss:
            # msgs: (key, (message_id, data))
            gameid = msgs[0][7:]
            msg_d = msgs[1][1]
            civ = msg_d.get('toBot', '')
            gameid_civ = gameid+ '_' + civ
            if gameid_civ in gameid_civ_lock and int(time.time()) - gameid_civ_lock[gameid_civ] < 20:
                continue
            elif len(gameid_civ_lock)>=10:
                logger.debug(f'msg not process since len(gameid_civ_lock)>=10: {msgs}')
                break
            elif msg_d.get('type', 'chat') == 'chat' and civ not in ChatManager.robot_names:
                logger.debug(f'msg not process since not to robot: {msgs}')
                message_ids = msgs[1][0]
                mq.xdel(gameid, message_ids)
                logger.debug(f"xdel {gameid_civ} {message_ids} {msg_d}.")
                break
            else:
                logger.debug(f'msg: {msgs}')
                gameid_civ_lock[gameid_civ] = int(time.time())
                # todo concat multi msgs
                # d = json.loads(msgs[1][1])
                data = {
                    'type': msg_d.get('type', 'chat'),
                    'gameId': gameid,
                    'addTime': msg_d.get('addTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'toBot': civ,
                    'data': msg_d
                }
                try:
                    if data['type'] == 'chat':
                        url = config_data['ai_server']['url'] + 'reply_free_chat'
                        response = await make_async_request(url, data)
                    else:
                        url = config_data['ai_server']['url'] + 'event_trigger'
                        response = await make_async_request(url, data)
                    if response is not None:
                        message_ids = msgs[1][0]
                        mq.xdel(gameid, message_ids)
                        logger.debug(f"xdel after reply {gameid_civ} {message_ids} {data['data']}.")
                        del gameid_civ_lock[gameid_civ]
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f'error {e} {traceback.format_exc()}.')
        await asyncio.sleep(2)


async def run_multiple_main():
    tasks = []
    for i in range(3):
        task = asyncio.create_task(main())
        tasks.append(task)
    await asyncio.gather(*tasks)


asyncio.run(run_multiple_main())
