import ujson as json
import traceback
from civagent import logger
from civagent.workflow import reply_workflow, skill_workflow, simulator_workflow, skill_workflow_noreflection, \
    reflection_workflow, reply, skill
from civagent.utils.skills_utils import SkillException
from civagent.config import config_data


def run_workflows(
        req,
        model='',
        force_json=True,
        decision=False,
        reflection=False,
        simulator=False,
        workflow=False
):
    if model == '' or model is None:
        model = config_data['LLM']['default_model']
    if decision and workflow:
        response = reply_workflow(req, model)
    elif reflection and workflow:
        response = skill_workflow(req, model)
    elif simulator and workflow:
        response = simulator_workflow(req, model)
    elif workflow:
        response = skill_workflow_noreflection(req, model)
    elif reflection:
        response = reflection_workflow(req, model)
    elif decision:
        response = reply(req, model)
    else:
        response = skill(req, model)
    try:
        if response is None:
            logger.error(
                f'''LLM response is None: force_json={force_json} 
                decision={decision} reflection={reflection} 
                simulator={simulator} workflow={workflow}'''.replace('\n', '')
            )
            return None, response, req['prompt']
        result = (response.message.content.replace("json", "")
                  .replace("\n", "").replace("```", '').replace("-", ''))
        if reflection and not workflow:
            return result, response, req['prompt']
        result = json.loads(result)
        logger.debug(result)
        return result, response, req['prompt']
    except json.JSONDecodeError:
        if force_json:
            logger.exception(f'JSONDecodeError in llm_server: {response}', exc_info=True)
            raise
        return result, response, req['prompt']
    except Exception:
        raise


def run_workflows_with_tools(
        tools,
        exec_fn,
        req,
        model="gpt-3.5-turbo-1106",
        force_json=True,
        simulator=False,
        workflow=False,
        reflection=False
):
    retry_count = 0
    error_message = []
    results, functions, actual_prompt = None, None, ""
    while retry_count < 3:
        try:
            if 'error_message' not in req:
                req['error_message'] = []
            functions, response, actual_prompt = run_workflows(
                req, model, force_json, simulator=simulator, workflow=workflow, reflection=reflection
            )
            results = []
            llm_reply = {"role": "assistant", 'context': functions}
            req['error_message'].append(llm_reply)
            if len(functions) > 1:
                for function in functions:
                    name = function["function"]["name"]
                    param = json.loads(function["function"]["arguments"])
                    result = exec_fn(name, param)
                    if result is not None:
                        results.append(result)
            else:
                num = 1
                for function in functions['functions']:
                    gpt3_key = f"function{num}"
                    if 'function' not in function:
                        name = function["name"]
                        param = function["arguments"]
                        result = exec_fn(name, param)
                        if result is not None:
                            results.append(result)
                    elif gpt3_key in function:
                        name = functions['functions'][function]['name']
                        param = functions['functions'][function]['arguments']
                        result = exec_fn(name, param)
                        if result is not None:
                            results.append(result)
                        num += 1
                    else:
                        name = function["function"]["name"]
                        param = function["function"]["arguments"]
                        result = exec_fn(name, param)
                        if result is not None:
                            results.append(result)
            break
        except SkillException as e:
            retry_count += 1
            error_reply = {'role': 'user', 'content': str(e)}
            req['error_message'].append(error_reply)
            error_message.append(str(e))
            logger.exception(f"SkillException in llm_server_with_tools: {e}", exc_info=True)
        except Exception as e:
            retry_count += 1
            error_reply = {'role': 'user', 'content': str(e)}
            req['error_message'].append(error_reply)
            error_message.append(traceback.format_exc())
            logger.exception(f"Exception in llm_server_with_tools: {e}", exc_info=True)
    return results, functions, retry_count
