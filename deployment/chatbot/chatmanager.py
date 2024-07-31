import ujson as json
from dataclasses import asdict
from datetime import datetime
import requests
from deployment.chatbot.civchatbot import CivChatbot, ChatMessage
from deployment.chatbot.discord.discord_chatbot import discord_robot2id, DiscordChatbot
# from deployment.chatbot.popo.popo_chatbot import robot2civ, PopoChatbot
from civagent.config import config_data
from civagent.utils.memory_utils import ChatMemory
from civagent import logger
from deployment.redis_mq import RedisStreamMQ
from deployment.chatbot.feishu.feishu_chatbot import FeishuChatbot, feishubot2id

mq = RedisStreamMQ()


class ChatManager:
    admin_names = [
        DiscordChatbot.admin_name,
        FeishuChatbot.admin_name
    ]
    robot_names = (list(feishubot2id.keys())
                   + list(discord_robot2id.keys()))

    def __init__(self, user_id):
        self.user_id = user_id
        self.platforms = ["discord", "feishu"]
        self.chatbots = {}
        self.last_session_id = ""
        self.last_uuid = ""
        self.game_id = ""
        self.game_info = {}
        self.create_chatbots(platform='discord')
        self.create_chatbots(platform='feishu')
        self.update_from_redis(platform='discord')
        self.update_from_redis(platform='feishu')

    def get_teamid(self, platform):
        if platform == 'discord':
            return self.chatbots['discord']['Unciv_Bot'].team_id
        elif platform == 'feishu':
            return self.chatbots['feishu']['guanliyuan'].team_id
        else:
            assert False, f"Unknow platform: {platform}"

    @staticmethod
    def get_teamid_static(game_id, user_id, platform):
        if platform == 'discord':
            return mq.get(f"discord_channel_{user_id}", "")
        elif platform == 'feishu':
            return mq.get(f"feishuteam_{user_id}_{game_id}", "")
        else:
            assert False, f"Unknow platform: {platform}"

    def update_from_redis(self, platform='discord'):
        self.game_id = mq.get(f"userid2gameid_{self.user_id}", "")
        self.game_info = mq.get('gameid2info_' + self.game_id, {})
        if platform == 'discord':
            team_id = self.get_teamid_static(self.game_id, self.user_id, platform)
            for robot_name in discord_robot2id.keys():
                bot: CivChatbot = self.chatbots['discord'][robot_name]
                bot.team_id = team_id
                channel_id = mq.get(
                    f"discord_channel_{self.user_id}_{robot_name}_private", ""
                )
                bot.channel_id = channel_id
        elif platform == 'feishu':
            team_id = self.get_teamid_static(self.game_id, self.user_id, platform)
            bot: CivChatbot = self.chatbots['feishu']['guanliyuan']
            bot.team_id = team_id
        else:
            assert False, f"Unknow platform: {platform}"

    def create_chatbots(self, platform):
        if platform == 'discord':
            self.chatbots['discord'] = {}
            for robot_name in discord_robot2id.keys():
                self.chatbots['discord'][robot_name] = DiscordChatbot(robot_name)
        elif platform == 'feishu':
            self.chatbots['feishu'] = {}
            for robot_name in feishubot2id.keys():
                self.chatbots['feishu'][robot_name] = FeishuChatbot(robot_name)
        else:
            assert False, f"Unknow platform: {platform}"

    def send_msg(self, text, sender, receiver, platform):
        bot: CivChatbot = self.get_chatbot(platform, sender)
        self.update_chatbot(bot)
        if platform == 'discord':
            if bot.channel_id is None or len(bot.channel_id) < 1:
                channel_key = 'discord_channel_' + str(self.user_id) + '_' + sender + '_private'
                bot.channel_id = mq.get(channel_key)
            return bot.send_msg(text, receiver)
        elif platform == 'feishu':
            return bot.send_msg(text, receiver)
        else:
            assert False, f"Unknow platform: {platform}"

    def get_admin_chatbot(self, platform):
        if platform == 'discord':
            return self.chatbots[platform]['Unciv_Bot']
        elif platform == 'feishu':
            return self.chatbots[platform]['guanliyuan']
        else:
            assert False, f"Unknow platform: {platform}"

    def get_chatbot(self, platform, robot_name):
        if robot_name in self.chatbots[platform]:
            return self.chatbots[platform][robot_name]
        else:
            return self.get_admin_chatbot(platform)

    def send_group_msg(self, text, sender, platform, team_id=None):
        team_id = self.get_admin_chatbot(platform).team_id \
            if team_id is None else team_id
        bot: CivChatbot = self.get_chatbot(platform, sender)
        self.update_chatbot(bot)
        return bot.send_group_msg(text, team_id)

    def update_chatbot(self, bot: CivChatbot):
        bot.last_session_id = self.last_session_id
        bot.last_uuid = self.last_uuid

    def convert_to_chatmessage(self, msg, platform):
        if platform == 'discord':
            chatmessage = DiscordChatbot.convert_to_chatmessage(msg)
        elif platform == 'feishu':
            chatmessage = FeishuChatbot.convert_to_chatmessage(msg)
        else:
            assert False, f"Unknow platform: {platform}"
        self.last_uuid = chatmessage.uuid
        self.last_session_id = chatmessage.sessionId
        return chatmessage

    @staticmethod
    def extract_message(msg, platform):
        if platform == 'discord':
            chatmessage = DiscordChatbot.convert_to_chatmessage(msg)
        elif platform == 'feishu':
            chatmessage = FeishuChatbot.convert_to_chatmessage(msg)
        else:
            assert False, f"Unknow platform: {platform}"
        return chatmessage.fromBot, chatmessage.toBot, chatmessage.notify

    def create_team(self, team_name, uids, platform):
        if platform == 'discord':
            bot: CivChatbot = self.chatbots['discord']['Unciv_Bot']
            tid = bot.create_team(team_name, uids)
            mq.set(f"discord_channel_{self.user_id}", tid)
        elif platform == 'feishu':
            bot: CivChatbot = self.chatbots['feishu']['guanliyuan']
            tid = bot.create_team(team_name, uids)
            mq.set(f"feishuteam_{self.user_id}_{self.game_id}", tid)
        else:
            assert False, f"Unknow platform: {platform}"
        return tid

    def get_chatmemory(self, chatmessage: ChatMessage):
        if self.game_info is None or len(self.game_info) < 1:
            self.update_from_redis()
        assert len(self.game_info) > 0, "Game info is empty!"
        player_civ = self.game_info['player_civ']
        is_group = chatmessage.isGroup
        from_civ = chatmessage.fromBot \
            if chatmessage.fromBot in self.robot_names \
            else player_civ[0]
        to_civ = chatmessage.toBot \
            if chatmessage.toBot in self.robot_names or is_group \
            else player_civ[0]
        tmp_d = {
            **asdict(chatmessage),
            "gameId": self.game_id,
            "userId": self.user_id,
            "fromCiv": from_civ,
            "toCiv": to_civ,
            "debugInfo": {}
        }
        chatmemory = ChatMemory(**tmp_d)
        return chatmemory

    @staticmethod
    def get_reply_chatmemory(chatmemory, text, is_group=None):
        return ChatMemory(
            msgType=chatmemory.msgType,
            isGroup=chatmemory.isGroup if is_group is None else is_group,
            channelId=chatmemory.channelId,
            uuid=chatmemory.uuid,
            userId=chatmemory.userId,
            sessionId=chatmemory.sessionId,
            addTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fromBot=chatmemory.toBot,
            fromCiv=chatmemory.toCiv,
            toBot=chatmemory.fromBot,
            toCiv=chatmemory.fromCiv,
            notify=text,
            gameId=chatmemory.gameId,
            debugInfo=chatmemory.debugInfo
        )

    @staticmethod
    def get_chatmemory_by_gameid(game_id, text, from_civ, to_civ, is_group, debug_info={}):
        platform = mq.get(f"gameid2platform_{game_id}", "")
        gameinfo = mq.get('gameid2info_' + game_id, {})
        player_civ = gameinfo['player_civ'][0]
        user_id = mq.get(f"gameid2userid_{game_id}", "")
        # user_id = mq.get(f"civ2userid_{game_id}_{player_civ}", "")
        from_bot = user_id if player_civ == from_civ else from_civ
        to_bot = user_id if player_civ == to_civ else to_civ
        if is_group:
            team_id = ChatManager.get_teamid_static(game_id, user_id, platform)
        else:
            team_id = ""
        return ChatMemory(
            msgType=platform,
            isGroup=is_group,
            channelId="",
            uuid="",
            userId=user_id,
            sessionId="",
            addTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fromBot=from_bot,
            fromCiv=from_civ,
            toBot=team_id if is_group else to_bot,
            toCiv=team_id if is_group else to_civ,
            notify=text,
            gameId=game_id,
            debugInfo=debug_info
        )

    @staticmethod
    def send_msg_by_http(game_id, text, from_civ, to_civ="", is_group=0, debug_info={}):
        chatmemory = asdict(ChatManager.get_chatmemory_by_gameid(
            game_id, text, from_civ, to_civ, is_group, debug_info
        ))
        headers = {'Content-Type': 'application/json'}
        url = config_data['chat_server']['url'] + 'open-apis/fuxi-unciv/SendMsg'
        response = requests.post(url, data=json.dumps(chatmemory), headers=headers)
        logger.debug(f"Send msg by remote http: {response.text}")
        return True
