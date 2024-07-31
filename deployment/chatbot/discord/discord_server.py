import multiprocessing
from datetime import datetime
from dataclasses import asdict
import requests
import discord
from discord.ext import commands
from civagent.config import config_data
from deployment.redis_mq import RedisStreamMQ
from deployment.chatbot.civchatbot import ChatMessage
from deployment.chatbot.discord.discord_chatbot import BotToken, discord_robot2id

mq = RedisStreamMQ()

discord_id2robot = {v: k for k, v in discord_robot2id.items()}
voice_connections = {}
receiver_default = '1194848561465143408'
url = config_data['chat_server']['url'] + 'open-apis/fuxi-unciv/MsgPushDiscord'


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.robot_name = None
        self.receive_user_id = None
        self.receive_channel_id = None

    def run(self, robot_name, receive_user_id=None):
        self.robot_name = robot_name
        token = BotToken[self.robot_name]
        self.receive_user_id = receive_user_id
        super().run(token)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    # < Message id = 1196296650461827132
    # channel = < TextChannel
    #             id = 1194463544666755207
    #             name = ''
    #             position = 0
    #             nsfw = False
    #             news = False
    #             category_id = 1194463544666755205 >
    #  type = < MessageType.default: 0 >
    #  author = < Member id = 1168578437653467139
    #             name = 'acon12_48357'
    #             global_name = 'Acon12'
    #             bot = False
    #             nick = None
    #              guild = < Guild id = 1194463544666755204
    #                           name = 'Unciv_Bot'
    #                           shard_id = 0
    #                           chunked = True
    #                           member_count = 11
    #                           member >>
    # flags = < MessageFlags value = 0 >>
    @commands.Cog.listener()
    async def on_message(self, message):
        # the bot should not reply to itself
        if message.author == self.user:
            return
        discord_channel_key = 'discord_channel_' + str(message.author.id) + '_' + self.robot_name + '_private'
        receive_channel_id = mq.get(discord_channel_key)

        # discord.DMChannel means private channel
        if ((self.user in message.mentions and isinstance(message.channel, discord.DMChannel))
                or str(message.channel.id) == str(receive_channel_id)):
            # only use user_id rather than user_name
            channel_msg = 'discord_channel_' + str(message.author.id) + '_' + self.robot_name + '_private'
            mq.set(channel_msg, message.channel.id)
            user_message = message.clean_content.strip().split(' ')[-1]
            # Group chat: please refer to the create_team function of discord_chatbot.
            data = ChatMessage(
                msgType='discord',
                isGroup=0,
                channelId=str(message.channel.id),
                uuid=str(message.id),
                sessionId=str(message.author.id),
                addTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fromBot=str(message.author.id),
                toBot=self.robot_name,
                notify=user_message
            )
            requests.post(url, json=asdict(data))


bot = DiscordBot()


def mongolia_run():
    bot.run("mongolia")


def china_run():
    bot.run("china")


def rome_run():
    bot.run("rome")


def aztek_run():
    bot.run("aztecs")


def greek_run():
    bot.run("greece")


def egypt_run():
    bot.run("egypt")


def guangliyuan():
    bot.run("Unciv_Bot")


if __name__ == "__main__":
    # process1 = multiprocessing.Process(target=sunrun)
    # process2 = multiprocessing.Process(target=guanyurun)
    process3 = multiprocessing.Process(target=guangliyuan)
    process4 = multiprocessing.Process(target=mongolia_run)
    process5 = multiprocessing.Process(target=china_run)
    process6 = multiprocessing.Process(target=rome_run)
    process7 = multiprocessing.Process(target=aztek_run)
    process8 = multiprocessing.Process(target=greek_run)
    process9 = multiprocessing.Process(target=egypt_run)

    # process1.start()
    # process2.start()
    process3.start()
    process4.start()
    process5.start()
    process6.start()
    process7.start()
    process8.start()
    process9.start()
