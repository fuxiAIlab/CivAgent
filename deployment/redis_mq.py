from pathlib import Path
from typing import Any, Awaitable, Dict, List, Optional, Union

import redis
import ujson as json

from civagent.config import config_data
from civsim import logger

host: str = config_data["Redis"]["host"]
port: int = config_data["Redis"]["port"]
db: int = config_data["Redis"]["db"]
password: str = config_data["Redis"]["password"]


class RedisStreamMQ:
    def __init__(self, host: str = host, port: int = port, db: int = db) -> None:
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)
        # AOF persist
        self.redis.config_set("appendonly", "yes")
        self.default_group_name = "my_group"
        self.default_consumer_name = "my_consumer"

        # RDB persistence
        self.redis.config_set("save", "900 1")
        self.redis.config_set("save", "300 10")
        self.redis.config_set("save", "60 10000")

    def xadd(self, id_: str, message: Dict[str, Union[str, int]]) -> str:
        stream_name = f"stream_{id_}"
        message_id = self.redis.xadd(stream_name, message)
        return message_id

    def xread(self, id_: str, last_id: str = "$", block: int = 1, count: int = None) -> Any:
        stream_name = f"stream_{id_}"
        value = self.redis.xread({stream_name: last_id}, block=block, count=count)
        res = self.decode_if_bytes(value)
        return res[0] if len(res) == 1 else res

    def set(self, key: str, value: Any, expiration_time: int = 0) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)
        if expiration_time > 0:
            self.redis.setex(key, value=value, time=expiration_time)
        else:
            self.redis.set(key, value)

    def get(self, key: str, default_value: Any = "") -> Any:
        value = self.redis.get(key)
        if value is not None:
            value = self.decode_if_bytes(value)
            if "{" in value:
                try:
                    value = json.loads(value)
                except Exception as e:
                    logger.exception(f"redis_mq {e}, {value}", exc_info=True)
            return value
        else:
            return default_value

    def xread_multi(self, streams: List[str], last_id: str = "$", block: Optional[int] = 60) -> Any:
        streams = dict([(x, last_id) for x in streams])
        value = self.redis.xread(streams, block=block)
        return self.decode_if_bytes(value)

    def decode_if_bytes(self, value: Union[Awaitable, Any]) -> Union[Awaitable, str, dict, list, tuple]:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        elif isinstance(value, dict):
            return {self.decode_if_bytes(k): self.decode_if_bytes(v) for k, v in value.items()}
        elif isinstance(value, list) or isinstance(value, tuple):
            return [self.decode_if_bytes(k) for k in value]
        else:
            return value

    def xreadgroup(
        self, group_name: str, consumer_name: str, user_id: str
    ) -> Union[Dict[bytes, bytes], List[Dict[bytes, bytes]]]:
        stream_name = f"stream_{user_id}"
        return self.redis.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1)

    def extract_message_id(self, messages: List[Union[bytes, List[bytes]]]) -> List[int]:
        if len(messages) > 0:
            return [x[0] for x in messages[1]]
        else:
            return []

    def xack(self, user_id: str, group_name: str, message_id: str) -> int:
        stream_name = f"stream_{user_id}"
        return self.redis.xack(stream_name, group_name, message_id)

    def xdel(self, user_id: str, message_ids: Union[str, List[str]]) -> int:
        stream_name = f"stream_{user_id}"
        if isinstance(message_ids, list) and len(message_ids) > 0:
            return self.redis.xdel(stream_name, *message_ids)
        else:
            return self.redis.xdel(stream_name, message_ids)

    def get_all_stream_names(self) -> List[str]:
        streams = self.redis.keys("stream_*")
        return self.decode_if_bytes(streams)

    def get_unconsumed_streams(self, block: Optional[int] = None) -> Any:
        streams = self.get_all_stream_names()
        if block is not None and int(block) > 0:
            return self.xread_multi(streams, last_id="$", block=block)
        else:
            return self.xread_multi(streams, last_id="0", block=block)

    def serialize_message(self, user_id: str, message_id: str, message: Dict[str, Union[str, int]]) -> None:
        directory = Path(f"./serialized_messages/{user_id}")
        directory.mkdir(parents=True, exist_ok=True)

        # Choose your serialization format here, for instance, JSON.
        file_path = directory / f"{message_id}.json"
        with open(file_path, "w") as file:
            json.dump(message, file)
