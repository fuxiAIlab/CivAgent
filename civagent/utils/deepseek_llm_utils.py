import ujson as json
from llama_index.core.base.llms.types import ChatMessage
from openai import OpenAI
from civagent.config import config_data
import instructor

config_api_key = config_data["LLM"]["deepseek_api_key"]


def llm_server(payload, model, request_timeout, llm_config, api_key=''):
    api_key = config_api_key if api_key == '' else api_key
    client = instructor.from_openai(
        OpenAI(
            base_url="https://api.deepseek.com",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON,
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=payload["messages"],
        response_model=llm_config.get("response_model", None),
    )
    if llm_config.get("response_model", None) is None:
        resp = resp.choices[0].message.content
    else:
        resp = resp.model_dump_json()
    message = {
        'role': 'user',
        'content': resp
    }
    return message, {}
