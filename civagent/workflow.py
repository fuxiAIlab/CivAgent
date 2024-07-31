from llama_index.core.base.query_pipeline.query import CustomQueryComponent
from llama_index.core.query_pipeline import QueryPipeline, InputComponent
from llama_index.core.response_synthesizers import TreeSummarize
from typing import Any, Dict
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
import os
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core import SimpleDirectoryReader
from llama_index.core.bridge.pydantic import Field
from civagent.utils.ollama_utils import CustomOllama
from civagent.utils.prompt_utils import prompt_make
from civsim import logger

Settings.embed_model = OllamaEmbedding("mistral")


class Component(CustomQueryComponent):
    req: Dict = Field(..., description="OpenAI LLM")
    prompt: str = Field(..., description="OpenAI LLM")
    input_key: str = Field(..., description="input")

    def _validate_component_inputs(
            self, _input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # NOTE: this is OPTIONAL but we show you here how to do validation as an example
        return _input

    @property
    def _input_keys(self) -> set:
        return {self.input_key}

    @property
    def _output_keys(self) -> set:
        return {"output"}

    def _run_component(self, **kwargs) -> Dict[str, Any]:
        """Run the component."""
        prompt = self.prompt.format(**kwargs, **self.req)
        return {"output": prompt}


class ComponentRetriever(CustomQueryComponent):
    req: Dict = Field(..., description="OpenAI LLM")
    prompt: str = Field(..., description="OpenAI LLM")
    input_key: str = Field(..., description="input")
    retriever: str = Field(..., description="input")

    def _validate_component_inputs(
            self, _input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # NOTE: this is OPTIONAL but we show you here how to do validation as an example
        return _input

    @property
    def _input_keys(self) -> set:
        return {self.input_key, self.retriever}

    @property
    def _output_keys(self) -> set:
        return {"output"}

    def _run_component(self, **kwargs) -> Dict[str, Any]:
        """Run the component."""
        # self.req["retriever"] = retriever
        prompt = self.prompt.format(**kwargs, **self.req)
        return {"output": prompt}


def skill_workflow(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    base_path = os.path.dirname(__file__)
    reflection_path = os.path.abspath(os.path.join(base_path, "..", "data", "deployment", "reflection.txt"))
    if not os.path.exists(reflection_path):
        open(reflection_path, 'a').close()
    try:
        documents = SimpleDirectoryReader(input_files=[reflection_path]).load_data()
    except Exception as e:
        documents = None
        logger.exception(f"Error loading document: {e}", exc_info=True)

    if not os.path.exists("storage"):
        # If the storage directory doesn't exist, create index and save
        index = VectorStoreIndex.from_documents(documents)
        index.set_index_id("vector_index")
        index.storage_context.persist("./storage")
    else:
        # If the store directory exists, try to load the index from the store
        try:
            storage_context = StorageContext.from_defaults(persist_dir="storage")
            index = load_index_from_storage(storage_context, index_id="vector_index")
        except Exception as e:
            logger.exception(f"Error loading index: {e}", exc_info=True)
            # If the index fails to load, it's probably because the index doesn't exist or is corrupted
            # recreate the index and save
            index = VectorStoreIndex.from_documents(documents)
            index.set_index_id("vector_index")
            index.storage_context.persist("./storage")
    retriever = index.as_retriever(similarity_top_k=2)
    summarizer = TreeSummarize(llm=llm)
    plans_prompt, llm_config = prompt_make(
        'agent_plans', context_dict={'language': req['language']}
    )
    plan_llm = CustomOllama(
        model=model, format="json", force_json=True, api_key=api_key, llm_config=llm_config
    )
    decision_prompt, llm_config = prompt_make(
        'agent_skill_decision', context_dict={'language': req['language']}
    )
    decision_llm = CustomOllama(
        model=model, format="json", force_json=True, api_key=api_key, llm_config=llm_config
    )
    plans_comnponent = Component(
        req=req, prompt=plans_prompt, input_key="analysis"
    )
    decision_component = ComponentRetriever(
        req=req, prompt=decision_prompt, input_key="plans", retriever="retriever"
    )
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Plans_llm": plan_llm,
        "Plans_prompt": plans_comnponent,
        "Decison_llm": decision_llm,
        "Decison_prompt": decision_component,
        "retriever": retriever,
        "summarizer": summarizer,
    })

    workflow.add_link("Analyze_prompt", "Analyze_llm")
    workflow.add_link("Analyze_llm", "Plans_prompt", dest_key="analysis")
    workflow.add_link("Plans_prompt", "Plans_llm")
    workflow.add_link("Plans_llm", "retriever")
    workflow.add_link("retriever", "summarizer", dest_key="nodes")
    workflow.add_link("Plans_llm", "summarizer", dest_key="query_str")
    workflow.add_link("summarizer", "Decison_prompt", dest_key="retriever")
    workflow.add_link("Plans_llm", "Decison_prompt", dest_key="plans")
    workflow.add_link("Decison_prompt", "Decison_llm")

    response, intermediates = workflow.run_with_intermediates(input=req['prompt'])
    req['last_plans'] = intermediates["Plans_llm"].outputs['output']
    return response


def skill_workflow_noreflection(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    plans_prompt, llm_config = prompt_make(
        'agent_plans', context_dict={'language': req['language']}
    )
    plan_llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=llm_config
    )
    decision_prompt, llm_config = prompt_make(
        'agent_skill_decision_noreflection',
        context_dict={'language': req['language']}
    )
    decision_llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=llm_config
    )
    # plans_prompt, _ = prompt_make('agent_plans', context_dict={'language': req['language']})
    # decision_prompt, _ = prompt_make('agent_skill_decision_noreflection', context_dict={'language': req['language']})
    plans_comnponent = Component(
        req=req, prompt=plans_prompt, input_key="analysis"
    )
    decision_component = Component(
        req=req, prompt=decision_prompt, input_key="plans"
    )
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Plans_llm": plan_llm,
        "Plans_prompt": plans_comnponent,
        "Decison_llm": decision_llm,
        "Decison_prompt": decision_component,
    })

    workflow.add_link("Analyze_prompt", "Analyze_llm")
    workflow.add_link("Analyze_llm", "Plans_prompt", dest_key="analysis")
    workflow.add_link("Plans_prompt", "Plans_llm")
    workflow.add_link("Plans_llm", "Decison_prompt", dest_key="plans")
    workflow.add_link("Decison_prompt", "Decison_llm")

    response, intermediates = workflow.run_with_intermediates(input=req['prompt'])
    req['last_plans'] = intermediates["Plans_llm"].outputs['output']
    return response


def reply_workflow(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    simulation_prompt, llm_config = prompt_make(
        'agent_reply_simulation',
        context_dict={'language': req['language']}
    )
    simulation_llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=llm_config
    )
    evaluation_prompt, llm_config = prompt_make(
        'agent_reply_evaluation',
        context_dict={'language': req['language']}
    )
    evaluation_llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=llm_config
    )
    decision_prompt, llm_config = prompt_make(
        'agent_reply',
        context_dict={'language': req['language']}
    )
    decision_llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=llm_config
    )
    simulation_component = Component(
        req=req, prompt=simulation_prompt, input_key="analysis"
    )
    evaluation_component = Component(
        req=req, prompt=evaluation_prompt, input_key="simulation"
    )
    decision_component = Component(
        req=req, prompt=decision_prompt, input_key="evaluation"
    )
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Simulation_llm": simulation_llm,
        "Simulation_prompt": simulation_component,
        "Evaluation_llm": evaluation_llm,
        "Evaluation_prompt": evaluation_component,
        "Reply_llm": decision_llm,
        "Reply_prompt": decision_component,

    })

    workflow.add_link("Analyze_prompt", "Analyze_llm")
    workflow.add_link("Analyze_llm", "Simulation_prompt", dest_key="analysis")
    workflow.add_link("Simulation_prompt", "Simulation_llm")
    workflow.add_link("Simulation_llm", "Evaluation_prompt", dest_key="simulation")
    workflow.add_link("Evaluation_prompt", "Evaluation_llm")
    workflow.add_link("Evaluation_llm", "Reply_prompt", dest_key="evaluation")
    workflow.add_link("Reply_prompt", "Reply_llm")

    response = workflow.run(input=req['prompt'])
    return response


def reflection_workflow(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def simulator_workflow(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def reply(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def skill(req, model):
    api_key = req.get('llm_api_key', '')
    llm = CustomOllama(
        model=model, format="json", force_json=True,
        api_key=api_key, llm_config=req.get('llm_config', {})
    )
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response
