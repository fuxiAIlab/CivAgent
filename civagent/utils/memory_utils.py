import collections
import json as json
import os
from civagent import logger


class Memory:
    def __init__(self, user_id, game_id, filter_id=''):
        # todo Remove hard coding
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chat_file_dir = os.path.join(current_dir, '../../data')
        self.chat_file = os.path.normpath(os.path.join(chat_file_dir, str(user_id) + '.txt'))
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
                        tmp.append(json_data)
                    except Exception as e:
                        logger.warning('read_last_n_lines_with_json_loads', line, e)
                        pass
        return tmp

    def get_chat_memory(self, filter_id=''):
        filter_id = self.filter_id if len(filter_id) < 1 else filter_id
        # todo tail efficiency
        # {"msgType": "1", "addtime": "2024-01-18 17:44:44", "sessionType": "1", "from": "2eff4204@app.robot.popo.com", "to": "wangkai02@corp.netease.com", "sessionId": "wangkai02@corp.netease.com", "uuid": "8930dbe0-5bc0-4614-a5e2-6927c07c488e", "notify": "我不想再继续闲聊下去了，我们应该专注于我们各自的文明发展和外交关系。\n debug模式:{'raw_intention': 'chat', 'intention': 'chat', 'decision_result': '结束对话', 'decision_reason': '', 'response': '我不想再继续闲聊下去了，我们应该专注于我们各自的文明发展和外交关系。'}", "eventType": "IM_P2P_TO_ROBOT_MSG", "game_id": "4cc3e9a1-1146-4d29-8a0a-ccb21b5996bc"}
        chats = self.read_last_n_lines_with_json_loads(self.chat_file, self.game_id, num=5)
        if len(filter_id) > 0:
            chats = [x for x in chats if filter_id in x.get("from_civ", "") or filter_id in x.get("to_civ", "")]
        return chats

    @staticmethod
    def chat2dialogue(chat_history, default_civ=''):
        #  dialogue_history:
        #    - type: "dialogue"
        #      intention: "open_border"
        #      speaker_civ: "Japan"
        #      speaker_id: "555"
        #      content: "我欲远征英格兰，可否借道？"
        tmp = []
        for chat in chat_history:
            try:
                tmp.append({
                    "type": "dialogue",
                    "debug_info": chat.get('debug_info', {}),
                    "speaker_civ": chat["from_civ"],
                    "speaker_id": "",
                    "receiver_civ": chat["to_civ"],
                    "content": chat["notify"].split('\n')[0]
                })
            except Exception as e:
                logger.warning('chat2dialogue', chat, e)
                tmp.append({
                    "type": "dialogue",
                    "debug_info": chat.get('debug_info', {}),
                    "speaker_civ": chat["from_civ"] if len(chat["from_civ"]) > 1 else default_civ,
                    "speaker_id": "",
                    "receiver_civ": chat["to_civ"] if len(chat["to_civ"]) > 1 else default_civ,
                    "content": chat["notify"].split('\n')[0]
                })
        return tmp

    @staticmethod
    def get_event_memory(game_info, civ_ind):
        # todo notificationsLog Persistence x['civilizations'][1]['notificationsLog'][-1]['notifications']
        # {'category': 'Diplomacy', 'text': '[Cape Town] assigned you a new quest: [Bully City State].', 'actions': [{'DiplomacyAction': {'otherCivName': 'Cape Town'}}], 'icons': ['Cape Town', 'OtherIcons/Quest']}
        notifications = game_info['civilizations'][civ_ind].get('notifications', [])
        notificationsLog = game_info['civilizations'][civ_ind].get('notificationsLog', [])
        turns_value = game_info.get('turns', 0)
        if isinstance(turns_value, collections.defaultdict):
            turns = 1
        else:
            turns = int(game_info.get('turns', 0))
        events = [(turns, notifications)] + [(int(x.get('turn', 0)), x.get('notifications', {})) for x in
                                             notificationsLog]
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
                # todo duplicate removal
                # if event.get('category', '') == 'War' and 'attacked' not in event['text'] and 'can bombard' not in event['text']:
                #     tmp.append({"turns":int(turn), "type":event.get('category', ''), "text":event['text']})
                # todo Whose soldiers
                # {'category': 'War', 'text': 'An enemy [Trebuchet] ([-0] HP) has attacked our [Rifleman] ([-4] HP)', 'icons': ['Trebuchet', 'OtherIcons/Pillage', 'Rifleman'], 'actions': [{'LocationAction': {'location': {'x': -2, 'y': 2}}}, {'LocationAction': {'location': {'x': -2, 'y': 4}}}]}
                # if event.get('category', '') == 'War' and 'attacked' in event['text']:
                #     pattern = r'\[(-?\d+)\] HP'
                #     matches = re.findall(pattern, event['text'])
                #     tmp.append({"turn":turn, "text":f""})
        return tmp
