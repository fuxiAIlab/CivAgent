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
    def __init__(self):
        self.channel_id: str = ""
        self.team_id: str = ""
        self.last_session_id: str = ""
        self.last_uuid: str = ""

    @abstractmethod
    def send_msg(self, text: str, receiver: str) -> ChatMessage:
        pass

    @abstractmethod
    def send_group_msg(self, text: str, team_id: str) -> ChatMessage:
        pass

    @abstractmethod
    def get_chatmessage(self, text: str, receiver: str, is_group: int) -> ChatMessage:
        pass

    @staticmethod
    def convert_to_chatmessage(msg: dict) -> ChatMessage:
        pass

    @abstractmethod
    def create_team(self, team_name: str, robot_names: list[str]) -> str:
        pass
