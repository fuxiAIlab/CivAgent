import asyncio
import time
import traceback
from datetime import datetime

import aiohttp
import ujson as json

from civagent.config import config_data
from civsim import logger
from deployment.chatbot.chatmanager import ChatManager
from deployment.redis_mq import RedisStreamMQ

mq = RedisStreamMQ()
gameid_civ_lock = {}
# slow request lock
gameid_civ_slow_lock = {}
timeout_max = 60


async def make_async_request(url: str, data: dict, timeout: int = timeout_max) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/json"}
        try:
            async with session.post(url, data=json.dumps(data), headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Error for {url} {str(data)[:100]}: {response.status} - {response.reason}")
                    return ""
        except aiohttp.ClientError as e:
            logger.error(f"Error for {data}: {e}")
            return ""


async def main() -> None:
    global gameid_civ_lock
    global mq
    while True:
        msgss = mq.get_unconsumed_streams()
        msgss = [(msgs[0], x) for msgs in msgss for x in msgs[1]]
        for msgs in msgss:
            # msgs: (key, (message_id, data))
            gameid = msgs[0][7:]
            msg_d: dict = msgs[1][1]
            civ = msg_d.get("toBot", "")
            event_type = msg_d.get("type", "")
            gameid_civ = gameid + "_" + civ + "_" + event_type
            if gameid_civ in gameid_civ_lock and int(time.time()) - gameid_civ_lock[gameid_civ] > timeout_max:
                del gameid_civ_lock[gameid_civ]
            elif len(gameid_civ_lock) >= 10:
                logger.debug(f"msg not process since len(gameid_civ_lock)>=10: {msgs}")
                break
            elif msg_d.get("type", "chat") == "chat" and civ not in ChatManager.robot_names:
                logger.debug(f"msg not process since not to robot: {msgs}")
                message_ids = msgs[1][0]
                mq.xdel(gameid, message_ids)
                logger.debug(f"xdel {gameid_civ} {message_ids} {msg_d}.")
                break
            elif msg_d.get("type", "chat") == "get_early_decision_async" and gameid_civ not in gameid_civ_slow_lock:
                gameid_civ_slow_lock[gameid_civ] = int(time.time())
                # 1s after next_turn event
                await asyncio.sleep(1)
                gameid2info = mq.get("gameid2info_" + gameid, {})
                robot_names = gameid2info.get("civ_robots", [])
                try:
                    for civ_name in robot_names:
                        url = config_data["ai_server"]["url"] + "get_early_decision"
                        data = {
                            "gameid": gameid,
                            # load savefile_path in receiver
                            "gameinfo": "",
                            "civ1": civ_name,
                            "is_async": 1,
                            "turns": msg_d["turns"],
                        }
                        response = await make_async_request(url, data, 120)
                except Exception as e:
                    logger.error(f"error {e} {traceback.format_exc()}.")
                message_ids = msgs[1][0]
                mq.xdel(gameid, message_ids)
                logger.info(f"xdel gameid_civ_slow_lock {gameid_civ} {message_ids} {msg_d}.")
                del gameid_civ_slow_lock[gameid_civ]
                break
            elif msg_d.get("type", "chat") == "get_early_decision_async" and gameid_civ in gameid_civ_slow_lock:
                pass
            elif gameid_civ not in gameid_civ_lock:
                gameid_civ_lock[gameid_civ] = int(time.time())
                logger.debug(f"msg: {msgs}")
                # todo concat multi msgs
                # d = json.loads(msgs[1][1])
                data = {
                    "type": msg_d.get("type", "chat"),
                    "gameId": gameid,
                    "addTime": msg_d.get("addTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "toBot": civ,
                    "data": msg_d,
                }
                try:
                    if data["type"] == "chat":
                        url = config_data["ai_server"]["url"] + "reply_free_chat"
                        response = await make_async_request(url, data)
                    else:
                        url = config_data["ai_server"]["url"] + "event_trigger"
                        response = await make_async_request(url, data)
                    if response is not None and response != "":
                        message_ids = msgs[1][0]
                        mq.xdel(gameid, message_ids)
                        logger.info(f"xdel after reply {gameid_civ} {message_ids} {data['data']}.")
                        del gameid_civ_lock[gameid_civ]
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"mq_listener error in {msgs}: {e} {traceback.format_exc()}.")
                    message_ids = msgs[1][0]
                    mq.xdel(gameid, message_ids)
        await asyncio.sleep(2)


async def run_multiple_main() -> None:
    tasks = []
    for i in range(5):
        task = asyncio.create_task(main())
        tasks.append(task)
    await asyncio.gather(*tasks)


asyncio.run(run_multiple_main())
