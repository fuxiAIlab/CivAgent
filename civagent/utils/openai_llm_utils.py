import json
import os
import yaml
from openai import OpenAI

config_path = os.environ.get('CIVAGENT_CONFIG_PATH')
with open(config_path, 'r') as file:
    config_data = yaml.safe_load(file)
api_key = config_data["LLM"]["openai_api_key"]


def llm_server(payload, model, request_timeout):
    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1/chat")

    response = client.chat.completions.create(
        model=model,
        messages=payload["messages"],
        stream=False
    )
    raw = response.json()
    raw = json.loads(raw)
    message = raw['choices'][0]['message']
    return message, raw
