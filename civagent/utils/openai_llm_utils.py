from typing import Any, Dict, Tuple

import instructor
from openai import OpenAI

from civagent.config import config_data

config_api_key: str = config_data["LLM"]["openai_api_key"]


def llm_server(
    payload: Dict[str, Any],
    model: str,
    request_timeout: float,
    llm_config: Dict[str, Any],
    api_key: str = "",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    api_key = config_api_key if api_key == "" else api_key
    if llm_config.get("response_model", None).__name__ == "Use_skills" and "gpt" in model.lower():
        client = OpenAI(base_url=config_data["LLM"]["openai_base_url"], api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=payload["messages"],
            tools=llm_config.get("skill_info", ""),
            tool_choice="auto",
        )
        if "toolCalls" in response.choices[0].message:
            result = response.choices[0].message.toolCalls
        else:
            result = response.choices[0].message.content.replace("'", '"')

        message = {"role": "user", "content": result}
    else:
        client = instructor.from_openai(
            OpenAI(
                base_url=config_data["LLM"]["openai_base_url"],
                api_key=api_key,  # required, but unused
            ),
            mode=instructor.Mode.JSON,
        )

        resp = client.chat.completions.create(
            model=model,
            messages=payload["messages"],
            response_model=llm_config.get("response_model", None),
        )
        if llm_config.get("response_model", None) is None:
            resp = resp.choices[0].message.content
        else:
            resp = resp.model_dump_json()
        message = {"role": "user", "content": resp}
    return message, {}
