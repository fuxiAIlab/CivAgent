from datetime import time, datetime
from deployment.chatbot.civchatbot import ChatMessage, CivChatbot
import requests
# import discord
# from discord.ext import commands
# from discord.ext.commands import bot
# import multiprocessing
from civsim import logger
from deployment.redis_mq import RedisStreamMQ
import time

mq = RedisStreamMQ()

BotToken = {
    # "sunquan": "",
    # "guanyu": "",
    'Unciv_Bot': '',
    # 'guanliyuan': '',
    'mongolia': '',
    'china': '',
    'rome': '',
    'aztecs': '',
    'greece': '',
    'egypt': ''
}

discord_robot2id = {
    # "sunquan": '',
    # "guanyu": '',
    'Unciv_Bot': '',
    'mongolia': '',
    'china': '',
    'rome': '',
    'aztecs': '',
    'greece': '',
    'egypt': ''
}
discord_id2robot = {v: k for k, v in discord_robot2id.items()}
voice_connections = {}
default_guild_id = 1194463544666755204

class DiscordChatbot(CivChatbot):
    admin_name = 'guanliyuan'

    def __init__(self, robot_name):
        super().__init__()
        self.name = str(robot_name)
        self.id = discord_robot2id[self.name]
        self.appKey = BotToken
        assert self.name in self.appKey.keys(), f"robot_name:{robot_name}"
        self.channel_id = ""
        self.last_session_id = ""
        self.last_uuid = ""
        self.team_id = ""
        # self.receiver_default = receiver_default

    def send_group_msg(self, text, team_id=None):
        team_id = self.team_id if team_id is None else team_id
        self.team_id = team_id
        self._send_msg(text, "", team_id)
        return self.get_chatmessage(team_id, text, is_group=1)

    def send_msg(self, text, receiver):
        if self.channel_id is None or len(self.channel_id) < 1:
            self.channel_id = self.create_private(receiver)
        self._send_msg(text, "", self.channel_id)
        return self.get_chatmessage(receiver, text, is_group=0)

    def _send_msg(self, text, receiver, channel_id):
        url = f'https://discord.com/api/v8/channels/{channel_id}/messages'
        retries = 4
        for _ in range(retries):
            try:
                receiver_token = BotToken[self.name]
                # print(receiver_token)
                headers = {
                    "Authorization": "Bot" + ' ' + f"{receiver_token}",
                    "Content-Type": "application/json"
                }

                data = {
                    "content": text
                }

                return requests.post(url, headers=headers, json=data, timeout=15)
                # print(response.json())
            except Exception as e:
                logger.exception(f'An error occurred: {e}', exc_info=True)
                pass
        return 0

    def get_receiver(self, receiver, default_receiver):
        if 'private' in str(receiver):
            receiver = int(receiver[:-8])
        if 'private' in str(default_receiver):
            default_receiver = int(default_receiver[:-8])
        return receiver, default_receiver

    def add_private(self, receiver):
        return str(receiver) + '_private'

    @staticmethod
    def convert_to_chatmessage(msg):
        return ChatMessage(
            **msg
        )

    def get_chatmessage(self, receiver, text, is_group):
        return ChatMessage(
            msgType='discord',
            isGroup=is_group,
            channelId=self.channel_id,
            uuid=self.last_uuid,
            sessionId=self.last_session_id,
            addTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fromBot=self.name,
            toBot=receiver,
            notify=text
        )

    def create_team(self, team_name, robot_names):
        url = f"https://discord.com/api/v10/guilds/{default_guild_id }/channels"
        retries = 2
        for _ in range(retries):
            try:

                bot_token = BotToken['Unciv_Bot']
                headers = {
                    "Authorization": f"Bot {bot_token}",
                    "Content-Type": "application/json"
                }

                data = {
                    'name': team_name,
                    'type': 0,  # text channel
                    'position': 1,  # position of channel
                    'permission_overwrites': [
                        {
                            'id': default_guild_id,
                            'type': 0,  # set member type
                            'deny': 1024
                        },
                        {
                            'id': int(discord_id2robot['Unciv_Bot']),
                            'type': 1,  # set member type
                            'allow': 1024,
                            'deny': 0
                        }
                    ],  # new channel permission overwrites
                    # 'topic': 'This is a private text channel.',
                    'nsfw': False,
                    'rate_limit_per_user': 0
                }
                player_id = 0
                for robot_name in robot_names:
                    if str(robot_name) == 'barbarians':
                        continue
                    if str(robot_name) in discord_robot2id:
                        user_id = discord_robot2id[robot_name]
                    else:
                        # human player
                        user_id = int(robot_name)
                        player_id = user_id
                    data['permission_overwrites'].append({
                        'id': user_id,
                        'type': 1,  # set user type
                        'allow': 1024,
                        'deny': 0
                    })
                response = requests.post(
                    url, headers=headers, json=data
                )
                channel_id = response.json()['id']
                self.team_id = channel_id
                return channel_id
            except Exception as e:
                logger.exception(f'error when create_team in discord : {e}', exc_info=True)
                pass
            time.sleep(1)
        return 0

    def create_private(self, receiver):
        target_user_id = receiver
        bot_token = BotToken[self.name]
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }
        create_dm_url = "https://discord.com/api/users/@me/channels"
        create_dm_payload = {
            "recipient_id": target_user_id
        }
        create_dm_response = requests.post(create_dm_url, headers=headers, json=create_dm_payload)
        private_id = create_dm_response.json()['id']
        channel_msg = 'discord_channel_' + str(receiver) + '_' + self.name + '_private'
        mq.set(channel_msg, private_id)
        return private_id
