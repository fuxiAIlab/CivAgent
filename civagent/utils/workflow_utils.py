import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import ujson as json
from llama_index.core.base.llms.types import ChatResponse

from civagent import logger
from civagent.config import config_data
from civagent.utils.skills_utils import SkillException
from civagent.workflow import (
    reply,
    reply_workflow,
    simulator_workflow,
    skill_workflow_no_reflection,
    skill_workflow_with_reflection,
)


def run_workflows(
    req: Dict[str, Any],
    model: str = "",
    force_json: bool = True,
    is_reply: bool = False,
    reflection: bool = False,
    simulator: bool = False,
    workflow: bool = False,
) -> Tuple[Optional[Union[str, Dict, List[Dict]]], Optional[ChatResponse], str]:
    if model == "" or model is None:
        model = config_data["LLM"]["default_model"]
    if workflow:
        if is_reply:
            response = reply_workflow(req, model)
        elif reflection:
            response = skill_workflow_with_reflection(req, model)
        elif simulator:
            response = simulator_workflow(req, model)
        else:
            response = skill_workflow_no_reflection(req, model)
    else:
        # There is a simple version without a predefined workflow, allowing developers to design their own.
        response = reply(req, model)
    try:
        if response is None:
            logger.error(
                f"""LLM response is None: force_json={force_json}
                decision={is_reply} reflection={reflection}
                simulator={simulator} workflow={workflow}""".replace("\n", "")
            )
            return None, response, req["prompt"]
        result = response.message.content.replace("json", "").replace("\n", "").replace("```", "").replace("-", "")
        # if reflection and not workflow:
        #     return result, response, req['prompt']
        result = json.loads(result)
        return result, response, req["prompt"]
    except json.JSONDecodeError:
        if force_json:
            logger.exception(f"JSONDecodeError in llm_server: {response}", exc_info=True)
            raise
        return result, response, req["prompt"]
    except Exception:
        raise


def run_workflows_with_tools(
    tools: List[str],
    exec_fn: Callable[[str, Any], Any],
    req: Dict[str, Any],
    model: str = "gpt-3.5-turbo-1106",
    force_json: bool = True,
    simulator: bool = False,
    workflow: bool = False,
    reflection: bool = False,
) -> Tuple[Optional[List[Any]], Union[Dict, List[Dict]], int]:
    # tools has been put in req
    retry_count = 0
    error_message = []
    results, functions, actual_prompt = None, None, ""
    while retry_count < 3:
        try:
            if "error_message" not in req:
                req["error_message"] = []
            functions, response, actual_prompt = run_workflows(
                req,
                model,
                force_json,
                is_reply=False,
                simulator=simulator,
                workflow=workflow,
                reflection=reflection,
            )
            results = []
            llm_reply = {"role": "assistant", "context": functions}
            req["error_message"].append(llm_reply)
            assert isinstance(functions, (dict, list))
            for function in functions["functions"]:
                assert isinstance(function, dict)
                name = function["function"]["name"]
                param = function["function"]["arguments"]
                result = exec_fn(name, param)
                if result is not None:
                    results.append(result)
            break
        except SkillException as e:
            retry_count += 1
            error_reply = {"role": "user", "content": str(e)}
            req["error_message"].append(error_reply)
            error_message.append(str(e))
            logger.exception(f"SkillException in llm_server_with_tools: {e}", exc_info=True)
        except Exception as e:
            retry_count += 1
            error_reply = {"role": "user", "content": str(e)}
            req["error_message"].append(error_reply)
            error_message.append(traceback.format_exc())
            logger.exception(f"Exception in llm_server_with_tools: {e}", exc_info=True)
    return results, functions, retry_count
