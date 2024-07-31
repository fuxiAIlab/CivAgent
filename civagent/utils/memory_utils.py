import collections
import ujson as json
import os
from dataclasses import dataclass
from typing import Optional, List, Union
from dataclasses import dataclass, asdict
from civagent import logger


@dataclass
class ChatMemory:
    msgType: str
    isGroup: int
    channelId: str
    uuid: str
    userId: str
    sessionId: str
    addTime: str
    fromBot: str
    fromCiv: str
    toBot: str
    toCiv: str
    notify: str
    gameId: str
    debugInfo: Optional[Union[str, dict]]


class Memory:
    def __init__(self, user_id, game_id, filter_id=''):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chat_file_dir = os.path.join(current_dir, '../../deployment/data')
        self.chat_file = os.path.normpath(os.path.join(chat_file_dir, str(game_id) + '.txt'))
        self.filter_id = filter_id
        self.game_id = game_id

    @staticmethod
    def persist_user_data(user_data, data_directory="../../data/"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.join(current_dir, data_directory)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        for user_id, data in user_data.items():
            file_path = os.path.join(data_directory, f"{user_id}.txt")
            if os.path.exists(file_path):
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write(json.dumps(data, ensure_ascii=False) + '\n')
            else:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(json.dumps(data, ensure_ascii=False) + '\n')

    @staticmethod
    def read_last_n_lines_with_json_loads(file_path, game_id, num=10):
        tmp = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # todo efficiency
                lines = [line for line in lines if game_id in line]
                last_10_lines = lines[-num:]
                for line in last_10_lines:
                    try:
                        json_data = json.loads(line)
                        tmp.append(ChatMemory(**json_data))
                    except Exception as e:
                        logger.exception(f'error in read_last_n_lines_with_json_loads for {line}', exc_info=True)
                        pass
        return tmp

    def get_chat_memory(self, filter_id=''):
        filter_id = self.filter_id if len(filter_id) < 1 else filter_id
        # todo efficiency of tail
        chats = self.read_last_n_lines_with_json_loads(self.chat_file, self.game_id, num=5)
        if len(filter_id) > 0:
            # todo supoort group chat
            chats = [chat for chat in chats if filter_id in chat.fromCiv or filter_id in chat.toCiv]
        return chats

    @staticmethod
    def chat2dialogue(chat_history: List[ChatMemory], default_civ=''):
        tmp = []
        for chat in chat_history:
            chat_d = asdict(chat)
            chat_d['notify'] = chat.notify.split('\n')[0]
            tmp.append(
                chat_d
            )
        return tmp

    @staticmethod
    def get_event_memory(game_info, civ_ind):
        # todo notificationsLog Persistence x['civilizations'][1]['notificationsLog'][-1]['notifications']
        # {
        # 'category': 'Diplomacy', 'text': '[Cape Town] assigned you a new quest: [Bully City State].',
        # 'actions': [{'DiplomacyAction': {'otherCivName': 'Cape Town'}}],
        # 'icons': ['Cape Town', 'OtherIcons/Quest']
        # }
        notifications = game_info['civilizations'][civ_ind].get('notifications', [])
        notificationsLog = game_info['civilizations'][civ_ind].get('notificationsLog', [])
        turns_value = game_info.get('turns', 0)
        if isinstance(turns_value, collections.defaultdict):
            turns = 1
        else:
            turns = int(game_info.get('turns', 0))
        history_events = [(int(x.get('turn', 0)), x.get('notifications', {})) for x in notificationsLog]
        events = [(turns, notifications)] + history_events
        tmp = []
        for turn, event_list in events:
            for event in event_list:
                if (event.get('category', '') == 'Diplomacy'
                        and 'encountered' not in event['text']
                        and 'a new quest' not in event['text']):
                    # todo Further enhance the detailed information within notifications, replacing 'you'
                    tmp.append({"turns": int(turn), "type": event.get('category', ''), "text": event['text']})
                if event.get('category', '') == 'Trade' and 'denied' not in event['text']:
                    tmp.append({"turns": int(turn), "type": event.get('category', ''), "text": event['text']})
                # if event.get('category', '') == 'War' and 'attacked' not in event['text'] and 'can bombard' not in event['text']:
                #     tmp.append({"turns":int(turn), "type":event.get('category', ''), "text":event['text']})
                # todo Whose soldiers
                # {'category': 'War', 'text': 'An enemy [Trebuchet] ([-0] HP) has attacked our [Rifleman] ([-4] HP)', 'icons': ['Trebuchet', 'OtherIcons/Pillage', 'Rifleman'], 'actions': [{'LocationAction': {'location': {'x': -2, 'y': 2}}}, {'LocationAction': {'location': {'x': -2, 'y': 4}}}]}
                # if event.get('category', '') == 'War' and 'attacked' in event['text']:
                #     pattern = r'\[(-?\d+)\] HP'
                #     matches = re.findall(pattern, event['text'])
                #     tmp.append({"turn":turn, "text":f""})
        return tmp


default_chat_memory = ChatMemory(
    msgType="0",
    isGroup=0,
    channelId="0",
    uuid="0",
    userId="0",
    sessionId="0",
    addTime="2024-01-01 11:11:11",
    fromBot="",
    fromCiv="",
    toBot="",
    toCiv="",
    notify="",
    gameId="0",
    debugInfo={}
)
