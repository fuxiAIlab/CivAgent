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
import civagent.task_prompt.prompt_hub as PromptHub
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
        # print(prompt)
        return {"output": prompt}


def skill_workflow(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)
    base_path = os.path.dirname(__file__)
    reflection_path = os.path.abspath(os.path.join(base_path, "..", "scripts", "tasks", "reflection.txt"))
    if not os.path.exists(reflection_path):
        open(reflection_path, 'a').close()
    try:
        documents = SimpleDirectoryReader(input_files=[reflection_path]).load_data()
    except Exception as e:
        documents = None
        logger.error("Error loading document: ", e)

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
            logger.error("Error loading index: ", e)
            # If the index fails to load, it's probably because the index doesn't exist or is corrupted
            # recreate the index and save
            index = VectorStoreIndex.from_documents(documents)
            index.set_index_id("vector_index")
            index.storage_context.persist("./storage")
    retriever = index.as_retriever(similarity_top_k=2)
    summarizer = TreeSummarize(llm=llm)
    plans_comnponent = Component(req=req, prompt=PromptHub.AgentPrompt_Plans, input_key="analysis")
    decision_component = ComponentRetriever(req=req,
                                            prompt=PromptHub.AgentPrompt_skill_Decision,
                                            input_key="plans",
                                            retriever="retriever")
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Plans_llm": llm,
        "Plans_prompt": plans_comnponent,
        "Decison_llm": llm,
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

    response = workflow.run(input=req['prompt'])
    return response


def skill_workflow_noreflection(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)

    plans_comnponent = Component(req=req, prompt=PromptHub.AgentPrompt_Plans, input_key="analysis")
    decision_component = Component(req=req, prompt=PromptHub.AgentPrompt_skill_Decision_noreflection, input_key="plans")
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Plans_llm": llm,
        "Plans_prompt": plans_comnponent,
        "Decison_llm": llm,
        "Decison_prompt": decision_component,
    })

    workflow.add_link("Analyze_prompt", "Analyze_llm")
    workflow.add_link("Analyze_llm", "Plans_prompt", dest_key="analysis")
    workflow.add_link("Plans_prompt", "Plans_llm")
    workflow.add_link("Plans_llm", "Decison_prompt", dest_key="plans")
    workflow.add_link("Decison_prompt", "Decison_llm")

    response = workflow.run(input=req['prompt'])
    return response


def reply_workflow(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)

    simulation_component = Component(req=req, prompt=PromptHub.AgentPrompt_reply_simulation, input_key="analysis")
    evaluation_component = Component(req=req, prompt=PromptHub.AgentPrompt_reply_evaluation, input_key="simulation")
    decision_component = Component(req=req, prompt=PromptHub.AgentPrompt_reply, input_key="evaluation")
    workflow.add_modules({
        "Analyze_llm": llm,
        "Analyze_prompt": InputComponent(),
        "Simulation_llm": llm,
        "Simulation_prompt": simulation_component,
        "Evaluation_llm": llm,
        "Evaluation_prompt": evaluation_component,
        "Reply_llm": llm,
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
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def simulator_workflow(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def reply(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response


def skill(req, model):
    llm = CustomOllama(model=model, format="json", force_json=True)
    workflow = QueryPipeline(verbose=True)
    workflow.add_modules({
        "llm": llm,
        "prompt": InputComponent()
    })
    workflow.add_link("prompt", "llm")
    response = workflow.run(input=req['prompt'])
    return response
