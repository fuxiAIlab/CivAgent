from datetime import datetime
from deployment.chatbot.civchatbot import CivChatbot, ChatMessage
from deployment.redis_mq import RedisStreamMQ
import requests
import ujson as json
from civsim import logger
from requests.exceptions import HTTPError
bot_app_secret={
    'guanliyuan': '',
    'rome': '',
    'aztecs': '',
    'greece': '',
    'egypt': ''
}

bot_access_token = {
    'guanliyuan': '',
    'rome': '',
    'aztecs': '',
    'greece': '',
    'egypt': ''
}
feishubot2id = {
    'guanliyuan': '',
    'rome': '',
    'aztecs': '',
    'greece': '',
    'egypt': ''
}
id2feishubot = {v: k for k, v in feishubot2id.items()}
mq = RedisStreamMQ()
default_receiver = 'on_84994289930916a87a5cbe6eb88f063a'


# mq.set("feishu_wjw",default_receiver)

class FeishuChatbot(CivChatbot):
    admin_name = 'guanliyuan'

    def __init__(self, robot_name):
        super().__init__()
        self.name = str(robot_name)
        self.tenant_access_token = bot_access_token[robot_name]
        self.channel_id = ""
        self.team_id = ""
        self.last_session_id = ""
        self.last_uuid = ""

    def update_access_token(self):
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        payload = json.dumps({
            "app_id": feishubot2id[self.name],
            "app_secret": bot_app_secret[self.name]
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        tenant_access_token = response.json()['tenant_access_token']
        self.tenant_access_token = tenant_access_token
        bot_access_token[self.name] = tenant_access_token

    def send_msg(self, text, receiver):
        params = {"receive_id_type": "union_id"}
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        msg = text
        retries = 2
        for _ in range(retries):
            try:
                msgContent = {
                    "text": msg,
                }
                payload = json.dumps({
                    "content": json.dumps(msgContent),
                    "msg_type": "text",
                    "receive_id": receiver,
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.tenant_access_token
                }
                response = requests.request("POST", url, params=params, headers=headers, data=payload)
                if response.status_code == 200 and response.json()["code"] == 0:
                    pass
                elif response.json()['code'] == 99991663:
                    self.update_access_token()
                else:
                    assert False, f"status_code not in (200, 42002): {response.content}"
                return self.get_chatmessage(receiver, text, is_group=0)
            except HTTPError as e:
                logger.exception(f'An HTTP error occurred: {e.response.text}', exc_info=True)
            except Exception as e:
                logger.exception(f'An error occurred:', exc_info=True)
        return

    def send_group_msg(self, text, team_id):
        params = {"receive_id_type": "chat_id"}
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        msg = text
        retries = 2
        for _ in range(retries):
            try:
                msgContent = {
                    "text": msg,
                }
                payload = json.dumps({
                    "content": json.dumps(msgContent),
                    "msg_type": "text",
                    "receive_id": team_id,
                })

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.tenant_access_token
                }

                response = requests.request("POST", url, params=params, headers=headers, data=payload)
                if response.status_code == 200 and response.json()["code"] == 0:
                    pass
                elif response.json()['code'] == 99991663:
                    self.update_access_token()
                else:
                    assert False, f"status_code not in (200, 42002): {response.content}"
                return self.get_chatmessage(team_id, text, is_group=1)
            except HTTPError as e:
                logger.exception(f'An HTTP error occurred: {e.response.text}', exc_info=True)
            except Exception as e:
                logger.exception(f'An error occurred:', exc_info=True)
        return

    @staticmethod
    def convert_to_chatmessage(msg):
        return ChatMessage(
            msgType='feishu',
            isGroup=0,
            channelId="",
            uuid=msg['header']['event_id'],
            sessionId=msg['event']['message']['chat_id'],
            addTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fromBot=msg['event']['sender']['sender_id']['union_id'],
            toBot=id2feishubot[msg['header']['app_id']],
            notify=json.loads(msg['event']['message']['content'])['text']
        )

        pass

    def get_chatmessage(self, receiver, text, is_group):
        return ChatMessage(
            msgType='feishu',
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
        url = "https://open.feishu.cn/open-apis/im/v1/chats?set_bot_manager=true&user_id_type=union_id"
        # user_id_list = [mq.get(user_id) for user_id in robot_names]
        user_id_list = [robot_names[0]]
        payload = json.dumps({
            "avatar": "default-avatar_44ae0ca3-e140-494b-956f-78091e348435",
            "chat_mode": "group",
            "chat_type": "private",
            "edit_permission": "all_members",
            "group_message_type": "chat",
            "hide_member_count_setting": "all_members",
            "join_message_visibility": "all_members",
            "leave_message_visibility": "all_members",
            "membership_approval": "no_approval_required",
            "name": team_name,
            "restricted_mode_setting": {
                "download_has_permission_setting": "all_members",
                "message_has_permission_setting": "all_members",
                "screenshot_has_permission_setting": "all_members",
                "status": False
            },
            "urgent_setting": "all_members",
            "user_id_list": user_id_list,
            "video_conference_setting": "all_members"
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.tenant_access_token
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        team_id = response.json()['data']['chat_id']
        self.team_invite(team_id, robot_names[1:], is_robot=True)
        self.team_id = team_id
        return team_id

    def team_invite(self, team_id, uids, is_robot=True):
        if is_robot:
            url = f"https://open.feishu.cn/open-apis/im/v1/chats/{team_id}/members?member_id_type=app_id"
        else:
            url = f"https://open.feishu.cn/open-apis/im/v1/chats/{team_id}/members?member_id_type=open_id"
        if is_robot:
            uids_id = [feishubot2id[uid] for uid in uids if uid != 'barbarians']
        else:
            uids_id = [mq.get('feishu' + uid) for uid in uids]
        payload = json.dumps({
            "id_list": uids_id
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.tenant_access_token
        }

        requests.request("POST", url, headers=headers, data=payload)
