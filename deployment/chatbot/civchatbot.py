from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatMessage:
    msgType: str
    isGroup: int
    channelId: str
    uuid: str
    sessionId: str
    addTime: str
    fromBot: str
    toBot: str
    notify: str


class CivChatbot(ABC):
    def __int__(self):
        self.channel_id = ""
        self.team_id = ""
        self.last_session_id = ""
        self.last_uuid = ""

    # @abstractmethod
    # def get_chatmsg(self):
    #     pass

    @abstractmethod
    def send_msg(self, text, receiver) -> ChatMessage:
        pass

    @abstractmethod
    def send_group_msg(self, text, team_id) -> ChatMessage:
        pass

    @abstractmethod
    def get_chatmessage(self, text, receiver, is_group) -> ChatMessage:
        pass

    @staticmethod
    def convert_to_chatmessage(msg) -> ChatMessage:
        pass

    @abstractmethod
    def create_team(self, team_name, robot_names) -> str:
        pass
