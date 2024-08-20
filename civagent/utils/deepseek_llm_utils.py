from typing import Any, Dict, Tuple

import instructor
from openai import OpenAI

from civagent.config import config_data

config_api_key = config_data["LLM"]["deepseek_api_key"]


def llm_server(
    payload: Dict,
    model: str,
    request_timeout: float,
    llm_config: Dict,
    api_key: str = "",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    api_key = config_api_key if api_key == "" else api_key
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
    message = {"role": "user", "content": resp}
    return message, {}
