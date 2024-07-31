import ujson as json
import redis
from pathlib import Path
from civagent.config import config_data
from civsim import logger

host = config_data['Redis']['host']
port = config_data['Redis']['port']
db = config_data['Redis']['db']
password = config_data['Redis']['password']


class RedisStreamMQ:
    def __init__(self, host=host, port=port, db=db):
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)
        # AOF persist
        self.redis.config_set('appendonly', 'yes')
        self.default_group_name = "my_group"
        self.default_consumer_name = "my_consumer"

        # RDB persistence
        self.redis.config_set('save', '900 1')
        self.redis.config_set('save', '300 10')
        self.redis.config_set('save', '60 10000')

    # not support nested dictionaries.
    def xadd(self, id, message):
        stream_name = f'stream_{id}'
        message_id = self.redis.xadd(stream_name, message)
        # self.serialize_message(user_id, message_id, message)
        return message_id

    def xread(self, id, last_id='$', block=1, count=None):
        stream_name = f'stream_{id}'
        value = self.redis.xread({stream_name: last_id}, block=block, count=count)
        # pending_info = self.redis.xpending(stream_name, self.default_group_name)
        res = self.decode_if_bytes(value)
        return res[0] if len(res) == 1 else res

    def set(self, key, value, expiration_time=None):
        if isinstance(value, dict):
            value = json.dumps(value)
        if expiration_time is not None:
            self.redis.setex(key, value=value, time=expiration_time)
        else:
            self.redis.set(key, value)

    def get(self, key, default_value=''):
        value = self.redis.get(key)
        if value is not None:
            value = self.decode_if_bytes(value)
            if '{' in value:
                try:
                    value = json.loads(value)
                except json.decoder.JSONDecodeError as e:
                    logger.exception(f'redis_mq {e}, {value}', exc_info=True)
            return value
        else:
            return default_value

    # def xread(self, user_id, last_id='$', block=1):
    #     stream_name = f'stream_{user_id}'
    #     # self.redis.xgroup_create(stream_name, self.default_group_name, id='0', mkstream=True)
    #     value = self.redis.xreadgroup(self.default_group_name, self.default_consumer_name, {stream_name: last_id}, block=block, noack=True)
    #     # pending_info = self.redis.xpending(stream_name, self.default_group_name)
    #     return self.decode_if_bytes(value)

    def xread_multi(self, streams, last_id='$', block=60):
        streams = dict([(x, last_id) for x in streams])
        value = self.redis.xread(streams, block=block)
        return self.decode_if_bytes(value)

    def decode_if_bytes(self, value):
        if isinstance(value, bytes):
            return value.decode('utf-8')
        elif isinstance(value, dict):
            return {self.decode_if_bytes(k): self.decode_if_bytes(v) for k, v in value.items()}
        elif isinstance(value, list) or isinstance(value, tuple):
            return [self.decode_if_bytes(k) for k in value]
        else:
            return value

    # def xread_to_dict(self, user_id, last_id='$'):
    #     stream_name = f'stream_{user_id}'
    #     result = self.redis.xread({stream_name: last_id})
    #     data_dict = {stream_name: []}
    #     if result:
    #         for key, value in result[0][1]:
    #             decoded_key = key.decode('utf-8') if isinstance(key, bytes) else key
    #             decoded_value = self.decode_if_bytes(value)
    #             data_dict[stream_name].append({decoded_key: decoded_value})
    #     return data_dict

    def xreadgroup(self, group_name, consumer_name, user_id):
        stream_name = f'stream_{user_id}'
        return self.redis.xreadgroup(group_name, consumer_name, {stream_name: '>'}, count=1)

    def extract_message_id(self, messages):
        if len(messages) > 0:
            return [x[0] for x in messages[1]]
        else:
            return []

    def xack(self, user_id, group_name, message_id):
        stream_name = f'stream_{user_id}'
        return self.redis.xack(stream_name, group_name, message_id)

    def xdel(self, user_id, message_ids):
        stream_name = f'stream_{user_id}'
        if isinstance(message_ids, list) and len(message_ids) > 0:
            return self.redis.xdel(stream_name, *message_ids)
        else:
            return self.redis.xdel(stream_name, message_ids)

    def get_all_stream_names(self):
        streams = self.redis.keys('stream_*')
        return self.decode_if_bytes(streams)

    def get_unconsumed_streams(self, block=None):
        streams = self.get_all_stream_names()
        if block is not None and int(block) > 0:
            return self.xread_multi(streams, last_id='$', block=block)
        else:
            return self.xread_multi(streams, last_id='0', block=block)

    def serialize_message(self, user_id, message_id, message):
        directory = Path(f"./serialized_messages/{user_id}")
        directory.mkdir(parents=True, exist_ok=True)

        # Choose your serialization format here, for instance, JSON.
        file_path = directory / f"{message_id}.json"
        with open(file_path, 'w') as file:
            json.dump(message, file)
