import httpx
from httpx import Timeout


def llm_server(payload, model, request_timeout):
    assert model == "gpt-3.5-turbo-1106" or model == "gpt-4-1106-preview", f"model {model} not supported"
    url = ''
    with httpx.Client(timeout=Timeout(request_timeout)) as client:
        response = client.post(
            # url=f"{self.base_url}/api/chat",
            url=url,
            headers={
                'Access-Key': '',
                'Access-Secret': '',
                'projectId': '',
                'Content-Type': 'application/json',
                'Accept-Encoding': 'identity',
            },
            json=payload,
        )
        response.raise_for_status()
        raw = response.json()
        if model == 'gpt-3.5-turbo-1106' or model == "gpt-4-1106-preview":
            message = raw['detail']['choices'][0]['message']
    return message, raw
