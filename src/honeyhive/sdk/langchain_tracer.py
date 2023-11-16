"""A Tracer implementation that logs runs to HoneyHive."""
from __future__ import annotations

import copy
import logging
from abc import ABC
import json
import os
import re
import datetime
from enum import Enum
import inspect
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, Optional, Union, List, Tuple, Callable
from datetime import timedelta
import uuid
import requests

from langchain.callbacks.tracers.base import BaseTracer, TracerException
from langchain.callbacks.tracers.schemas import (
    TracerSession,
    Run,
)
from langchain.input import get_colored_text

import traceback

HONEYHIVE_APP_URL = "https://api.honeyhive.ai"
LLM_CHAIN_TYPE = "llm_chain"
AGENT_CHAIN_TYPE = "agent_executor_chain"
ROLE_MAPPING = {"ai": "assistant", "human": "user", "system": "system"}


class HoneyHiveLangChainTracer(BaseTracer, ABC):
    """An implementation of BaseTracer that logs events in a session to the HoneyHive API."""

    _headers: Dict[str, Any] = {"Content-Type": "application/json"}
    _base_url: str = "https://api.honeyhive.ai"
    _env_api_key = os.getenv("HONEYHIVE_API_KEY")

    def __init__(
        self,
        project: str,
        name: Optional[str] = None,
        source: Optional[str] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the HoneyHive tracer."""
        super().__init__()
        if self._env_api_key:
            api_key = self._env_api_key
        elif not api_key:
            raise ValueError(
                "HoneyHive API key is not set! Please set the HONEYHIVE_API_KEY environment variable or pass in the api_key value."
            )

        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

        self.project = project
        self.source = source if source is not None else "langchain"
        self.name = name
        self.user_properties = user_properties

        if api_key is not None:
            self._headers["Authorization"] = "Bearer " + api_key

    def _start_new_session(self):
        self.session_id = str(uuid.uuid4())
        body = {
            "project": self.project,
            "source": self.source,
            "session_id": self.session_id,
            "session_name": self.name,
            "user_properties": self.user_properties,
        }
        requests.post(
            url=f"{self._base_url}/session/start",
            headers=self._headers,
            json=body,
        )

    def _persist_run(self, run: Run) -> None:
        """Persist a run."""
        try:
            logs = self._convert_run_to_logs(run=run)
            if self.project is not None:
                logs[0].project = self.project
            self._post_trace(logs=logs)
        except Exception as error:
            logging.warning(f"Failed to persist run: {error}")
            print(traceback.format_exc())

    def _convert_run_to_logs(
        self, run: Run, parent_log: Optional[Log] = None
    ) -> List[Log]:
        logs: List[Log] = []
        duration = (run.end_time - run.start_time) / timedelta(milliseconds=1)
        metadata = {"langchain_trace_id": str(run.id), **run.extra}
        run_type = run.serialized.get("_type")
        if run.run_type == "chain":
            if run_type == LLM_CHAIN_TYPE:
                child_llm_runs = [
                    child_run
                    for child_run in run.child_runs
                    if child_run.run_type == "llm"
                ]
                run.child_runs = [
                    child_run
                    for child_run in run.child_runs
                    if child_run.run_type != "llm"
                ]
                inputs = {
                    input_: value
                    for input_, value in run.inputs.items()
                    if input_ in run.serialized["prompt"]["input_variables"]
                }
                for llm_run in child_llm_runs:
                    logs += self._convert_llm_run_to_log(
                        llm_run=llm_run,
                        event_name=run.name,
                        inputs=[inputs],
                        prompt_details=run.serialized["prompt"],
                        duration=duration,
                        parent_log=parent_log,
                    )
            elif run_type == AGENT_CHAIN_TYPE:
                logs.append(
                    self._convert_agent_run_to_log(
                        run=run,
                        event_name=run.name,
                        duration=duration,
                        metadata=metadata,
                        parent_log=parent_log,
                    )
                )
            else:
                logs.append(
                    self._convert_generic_chain_run_to_log(
                        run=run,
                        event_name=run.name,
                        duration=duration,
                        metadata=metadata,
                        parent_log=parent_log,
                    )
                )
        elif run.run_type in ["tool", "retriever"]:
            logs.append(
                self._convert_tool_run_to_log(
                    run=run,
                    event_name=run.name,
                    duration=duration,
                    metadata=metadata,
                    parent_log=parent_log,
                )
            )
        elif run.run_type == "llm":
            logs += self._convert_llm_run_to_log(
                llm_run=run,
                event_name=run.name,
                inputs=[self._convert_chain_inputs_to_text(run.inputs)],
                duration=duration,
                parent_log=parent_log,
            )
        else:
            raise NotImplementedError

        if parent_log is not None:
            if parent_log.children is None:
                parent_log.children = logs
            else:
                parent_log.children += logs
        child_runs = sorted(
            run.child_runs,
            key=lambda x: x.execution_order,
        )
        for run in child_runs:
            # Assume the final log at this step is the parent
            _ = self._convert_run_to_logs(
                run=run,
                parent_log=logs[-1],
            )
        return logs

    def _post_trace(self, logs: List[Log]) -> None:
        """Post a trace to the HoneyHive API"""
        self._start_new_session()
        root_log = logs[0].dict()
        root_log['session_id'] = self.session_id
        trace_response = requests.post(
            url=f"{self._base_url}/session/{self.session_id}/traces",
            json={"logs": [root_log]},
            headers=self._headers,
        )
        if trace_response.status_code != 200:
            raise TracerException(
                f"Failed to post trace to HoneyHive with status code {trace_response.status_code}"
            )

    @staticmethod
    def _convert_chain_outputs_to_text(outputs: Dict[str, Any]) -> str:
        """Convert LC dictionary outputs to a string required by the HH API."""
        output = ""
        for key, value in outputs.items():
            # TODO: check are there other data types to deal with
            if isinstance(value, list):
                value = ", ".join([str(v) for v in value])
            output += f"{key}:\n{value}\n"
        return output

    @staticmethod
    def _convert_chain_inputs_to_text(
        inputs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Convert LC list inputs to a string required by the HH API."""
        new_inputs = {}
        for key, value in inputs.items():
            # TODO: check are there other data types to deal with
            if isinstance(value, list):
                value = ", ".join([str(v) for v in value])
            new_inputs[key] = value
        return new_inputs

    @staticmethod
    def _convert_provider_parameters(
        llm_type: str, params: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Convert provider specific parameters to the HH common model parameters.

        Return a tuple of HoneyHive parameters and any parameters not mapped.
        """
        if not params:
            return {}, {}
        params = copy.deepcopy(params)
        # use startswith because LC has patterns 'openai', 'openai-chat' as _llm_types
        # TODO: Don't want to rely on string ops for getting provider,
        #  suggest to have separate 'provider' and 'mode' (complete or chat) instead
        #  of just _llm_type
        if llm_type.startswith("openai"):
            provider = "openai"
            mapping = {
                "model_name": "model",
                "temperature": "temperature",
                "max_tokens": "max_tokens",
                "n": "num_samples",
                "top_p": "top_p",
                "presence_penalty": "presence_penalty",
                "frequency_penalty": "frequency_penalty",
                "stop": "stop",
            }
        elif llm_type == "anthropic":
            provider = "anthropic"
            mapping = {
                "provider": "anthropic",
                "model_name": "model",
                "max_tokens_to_sample": "max_tokens",
                "temperature": "temperature",
                "top_k": "top_k",
                "top_p": "top_p",
                "stop_sequence": "stop",
            }
        else:
            raise NotImplementedError

        mapped_params = {
            hl_param: params.pop(provider_param, None)
            for provider_param, hl_param in mapping.items()
        }
        hl_params = {
            **mapped_params,
            "provider": provider,
        }
        return hl_params, params

    def _convert_agent_run_to_log(
        self,
        run: Run,
        event_name: str,
        duration: float,
        metadata: Dict[str, Any],
        parent_log: Optional[Log],
    ) -> Log:
        """Converts LC agent chain run to HH log."""
        if parent_log is not None:
            parent_id = parent_log.event_id
        else:
            parent_id = None
        config = AgentConfig(
            agent_class=run.serialized["agent"]["_type"],
            tools=[
                ToolConfig(
                    name=tool["name"],
                    description=tool["description"],
                    source=self._get_tool_source_from_function(
                        tool["name"], tool["func"]
                    )
                    if "func" in tool
                    else None,
                )
                for tool in run.serialized["tools"]
            ],
            model_config=self._create_model_config_from_params(
                params=run.serialized["agent"]["llm_chain"]["llm"],
                prompt_details=run.serialized["agent"]["llm_chain"]["prompt"],
            ),
            other=AgentOther(
                max_iterations=run.serialized["max_iterations"],
                stop=run.serialized["early_stopping_method"],
                output_parser=run.serialized["agent"]["output_parser"][
                    "_type"
                ],
            ),
        )
        return Log(
            project=self.project,
            children=None,
            event_name=event_name,
            event_type="chain",
            event_id=str(uuid.uuid4()),
            parent_id=parent_id,
            config=config,
            inputs=self._convert_chain_inputs_to_text(inputs=run.inputs),
            error=run.error,
            outputs={"text": self._convert_chain_outputs_to_text(run.outputs)}
            if run.outputs is not None
            else None,
            start_time=int(run.start_time.timestamp() * 1000000),
            end_time=int(run.end_time.timestamp() * 1000000),
            duration=duration,
            metadata=metadata,
        )

    def _convert_generic_chain_run_to_log(
        self,
        run: Run,
        event_name: str,
        duration: float,
        metadata: Dict[str, Any],
        parent_log: Optional[Log],
    ) -> Log:
        """Converts LC generic chain run to HH log."""
        if parent_log is not None:
            parent_id = parent_log.event_id
        else:
            parent_id = None
        config = Config(name=event_name)
        return Log(
            project=self.project,
            event_name=event_name,
            event_type="generic",
            config=config,
            event_id=str(uuid.uuid4()),
            parent_id=parent_id,
            inputs=self._convert_chain_inputs_to_text(inputs=run.inputs),
            error=run.error,
            children=None,
            outputs={"text": self._convert_chain_outputs_to_text(run.outputs)}
            if run.outputs is not None
            else None,
            end_time=int(run.end_time.timestamp() * 1000000),
            start_time=int(run.start_time.timestamp() * 1000000),
            duration=duration,
            metadata=metadata,
        )

    @staticmethod
    def _get_tool_source_from_function(
        tool_name: str, tool_function: Callable
    ) -> str:
        """Get the source code for a tool function."""
        try:
            return inspect.getsource(tool_function)
        except Exception as _:
            logging.info(f"Failed to get source for tool {tool_name}")

    def _convert_tool_run_to_log(
        self,
        run: Run,
        event_name: str,
        duration: float,
        metadata: Dict[str, Any],
        parent_log: Optional[Log],
    ) -> Log:
        """Converts LC tool chain run to HH log."""
        if parent_log is not None:
            parent_id = parent_log.event_id
        else:
            parent_id = None
        description = (
            run.serialized["description"]
            if run.run_type != "retriever"
            else None
        )
        return Log(
            project=self.project,
            children=None,
            event_name=event_name,
            event_type="tool",
            event_id=str(uuid.uuid4()),
            parent_id=parent_id,
            config=ToolConfig(
                name=event_name,
                description=description,
                source=self._get_tool_source_from_function(
                    event_name, run.serialized["func"]
                )
                if "func" in run.serialized
                else None,
                other=run.extra,
            ),
            inputs=run.inputs,
            outputs={"text": self._convert_chain_outputs_to_text(run.outputs)}
            if run.outputs is not None
            else None,
            error=run.error,
            metadata=metadata,
            end_time=int(run.end_time.timestamp() * 1000000),
            start_time=int(run.start_time.timestamp() * 1000000),
            duration=duration,
        )

    @staticmethod
    def _convert_template_to_hl_syntax(
        template: str, template_format: str
    ) -> str:
        """Converts LC template to HH double curly bracket syntax"""
        if template_format == "f-string":
            # match the f-string syntax with single curly brackets
            pattern = r"{([^{}]+)}"

            # replaces f-string syntax with Jinja2 syntax
            def replace(match):
                return "{{{{ {} }}}}".format(match.group(1))

            return re.sub(pattern, replace, template)
        elif template_format == "jinja2":
            # jinja2 already uses double curly brackets
            return template
        else:
            logging.info(f"Unknown template format: {template_format}")
            return template

    def _create_model_config_from_params(
        self,
        params: Dict[str, Any],
        prompt_details: Optional[Dict[Any]] = None,
    ) -> ModelConfig:
        """Creates HH model configuration from LC parameters."""
        hl_params, other_params = self._convert_provider_parameters(
            llm_type=params.pop("_type"),
            params=params,
        )
        if prompt_details is not None:
            if "messages" in prompt_details:
                return ModelConfig(
                    chat_template=[
                        ChatMessage(
                            content=self._convert_template_to_hl_syntax(
                                template=message["prompt"]["template"],
                                template_format=message["prompt"][
                                    "template_format"
                                ],
                            ),
                            role=ROLE_MAPPING[message["role"]],
                        )
                        for message in prompt_details["messages"]
                    ],
                    endpoints="chat",
                    **hl_params,
                )
            else:
                return ModelConfig(
                    prompt_template=self._convert_template_to_hl_syntax(
                        template=prompt_details["template"],
                        template_format=prompt_details["template_format"],
                    ),
                    endpoint="complete",
                    **hl_params,
                )
        else:
            return ModelConfig(**hl_params)

    def _convert_llm_run_to_log(
        self,
        llm_run: Run,
        event_name: str,
        inputs: List[Dict[str, str]],
        duration: float,
        parent_log: Optional[Log],
        prompt_details: Optional[Dict[Any]] = None,
    ) -> List[Log]:
        if parent_log is not None:
            parent_id = parent_log.event_id
        else:
            parent_id = None
        """Converts LC llm run to HH log."""
        config = self._create_model_config_from_params(
            params=llm_run.extra.pop("invocation_params", {}),
            prompt_details=prompt_details,
        )
        metadata = {"langchain_run_id": str(llm_run.id), **llm_run.extra}
        if "generations" in llm_run.outputs:
            logs = []
            # response.generations is a list (# inputs) of lists (# samples)
            for i, generations in enumerate(llm_run.outputs["generations"]):
                for generation in generations:
                    if "message" in generation:
                        if "content" in generation["message"]:
                            output = generation["message"]["content"]
                        elif (
                            "kwargs" in generation["message"]
                            and "content" in generation["message"]["kwargs"]
                        ):
                            output = generation["message"]["kwargs"]["content"]
                        else:
                            raise NotImplementedError
                    elif "text" in generation:
                        output = generation["text"]
                    else:
                        raise NotImplementedError
                    logs.append(
                        # TODO: add token usage
                        # TODO: chat serialization doesn't include messages array
                        Log(
                            project=self.project,
                            children=None,
                            event_name=event_name,
                            event_type="model",
                            event_id=str(uuid.uuid4()),
                            parent_id=parent_id,
                            config=config,
                            inputs=inputs[i],
                            outputs={"text": output},
                            start_time=int(
                                llm_run.start_time.timestamp() * 1000000
                            ),
                            end_time=int(
                                llm_run.end_time.timestamp() * 1000000
                            ),
                            duration=duration,
                            metadata=metadata,
                        )
                    )
        else:
            logs = [
                Log(
                    project=self.project,
                    children=None,
                    event_name=event_name,
                    event_type="model",
                    event_id=str(uuid.uuid4()),
                    parent_id=parent_id,
                    config=config,
                    inputs=inputs,
                    error=llm_run.error,
                    start_time=int(llm_run.start_time.timestamp() * 1000000),
                    end_time=int(llm_run.end_time.timestamp() * 1000000),
                    duration=duration,
                    metadata=metadata,
                )
            ]
        return logs

    def load_session(self, session_name: str) -> TracerSession:
        """Load a tracing session and set it as the Tracer's session."""
        # LCs session concept is a collection of runs, not required by HH.
        return TracerSession(id=-1)

    def load_default_session(self) -> TracerSession:
        """Load the default tracing session and set it as the Tracer's session."""
        # LCs session concept is a collection of runs, not required by HH.
        return TracerSession(id=-1)


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatMessage(BaseModel):
    role: ChatRole
    content: str
    name: Optional[str] = None


class Config(BaseModel):
    type: str = "generic"
    name: Optional[str] = None
    description: Optional[str] = None


class ModelConfig(Config):
    provider: str = Field(
        title="Model provider",
        description="The company providing the underlying model service.",
    )
    endpoint: Optional[str] = Field(
        title="Provider endpoint",
        description="Which of the providers model endpoints to use. "
        "For example Complete or Edit.",
        default=None,
    )
    model: str = Field(
        title="Model instance used",
        description="What model instance to use for the generation. "
        "e.g. text-davinci-002.",
    )
    prompt_template: Optional[str] = Field(
        title="Prompt template",
        description="Prompt template that will take your specified inputs to form "
        "your final request to the provider model. "
        "Input variables within the prompt template should be specified "
        "with double curly bracket syntax: {{INPUT_NAME}}.",
        default=None,
    )
    chat_template: Optional[List[ChatMessage]] = Field(
        title="Chat template",
        description="Messages prepended to the list of messages sent to the provider. "
        "These messages that will take your specified inputs to form "
        "your final request to the provider model. ",
        default=None,
    )
    temperature: Optional[float] = Field(
        title="Sampling temperature",
        description="What sampling temperature to use when making a generation. "
        "Higher values means the model will be more creative.",
        default=1,
    )
    max_tokens: Optional[int] = Field(
        title="Maximum tokens",
        description="The maximum number of tokens to generate. "
        "Provide max_tokens=-1 to dynamically calculate the maximum number of tokens "
        "to generate given the length of the prompt",
        default=-1,
    )
    top_p: Optional[float] = Field(
        title="Top p probability mass",
        description="An alternative to sampling with temperature, "
        "called nucleus sampling, where the model considers the results "
        "of the tokens with top_p probability mass.",
        default=1,
    )
    stop: Optional[Union[str, List[str]]] = Field(
        title="Stop sequence(s)",
        description="The string (or list of strings) after which the model will stop "
        "generating. The returned text will not contain the stop sequence.",
        default=None,
    )
    presence_penalty: Optional[float] = Field(
        title="Penalize tokens on whether present.",
        description="Number between -2.0 and 2.0. Positive values penalize new tokens "
        "based on whether they appear in the generation so far.",
        default=0,
    )
    frequency_penalty: Optional[float] = Field(
        title="Penalize tokens on whether frequent.",
        description="Number between -2.0 and 2.0. Positive values penalize new tokens "
        "based on how frequently they appear in the generation so far.",
        default=0,
    )
    other: Optional[Dict[str, Any]] = Field(
        title="Other provider parameters",
        description="Other parameter values to be passed to the provider call.",
        default={},
    )
    type: str = "model"


class ToolConfig(Config):
    source: Optional[str] = Field(
        title="Tool source",
        description="The source code for the tool.",
        default=None,
    )
    other: Optional[Dict[str, Any]] = Field(
        title="Other tool parameters",
        description="Other parameter values that uniquely identify the tool.",
        default={},
    )
    type: str = "tool"


class AgentOther(BaseModel):
    max_iterations: int
    stop: Optional[Union[str, List[str]]]
    output_parser: Optional[str]


class AgentConfig(Config):
    agent_class: str
    tools: List[ToolConfig]
    model_config: ModelConfig
    other: AgentOther
    type: str = "agent"


class Log(BaseModel):
    project: Optional[str] = Field(
        title="Project name",
        description="The name of the project under which you're running the tracing",
    )
    event_id: Optional[str] = Field(
        title="Event ID",
        description="A unique ID for the event",
    )
    parent_id: Optional[str] = Field(
        title="Parent ID",
        description="Event ID of the parent event",
    )
    event_type: str = Field(
        title="Event type",
        description="Event type: Model, Tool, Chain or Generic",
    )
    event_name: str = Field(
        title="Function name",
        description="Function name. If it does not exist, a new function will be "
        "created.",
    )
    config: Union[Config, ModelConfig, ToolConfig, AgentConfig] = Field(
        title="Config",
        description="The config used for a specific step in the chain.",
    )
    inputs: Dict[str, Any] = Field(
        title="Project input data",
        description="List of (name, value) pairs for the inputs used by your prompt "
        "template, or directly by your project.",
    )
    outputs: Optional[Dict[str, Any]] = Field(
        title="Model output",
        description="Generated output from your model for the provided inputs. Can be None if error encountered.",
    )
    children: Optional[List[Log]]
    user_properties: Optional[Dict[str, Any]] = Field(
        title="User properties",
        description="Metadata associated with the user",
        default={},
    )
    metadata: Optional[Dict[str, Any]] = Field(
        title="Event properties",
        description="Metadata associated with the event",
        default={},
    )
    source: Optional[str] = Field(
        title="Source of generation",
        description="What was source of the model used for this generation? "
        "e.g. langchain",
        default="langchain",
    )
    start_time: Optional[int] = Field(
        title="Start time",
        description="The time in epoch microseconds the event started",
    )
    end_time: Optional[int] = Field(
        title="End time",
        description="How time in epoch microseconds the event ended",
    )
    duration: Optional[float] = Field(
        title="Duration (in ms)",
        description="The duration of the event in milliseconds",
    )
    error: Optional[str] = Field(
        title="Log error",
        description="Captures error thrown by model.",
        default=None,
    )
    metrics: Optional[Dict[str, float]] = Field(
        title="Metrics",
        description="Metrics associated with the event",
        default={},
    )
    feedback: Optional[Dict[str, Any]] = Field(
        title="Feedback",
        description="Feedback associated with the event",
        default={},
    )


def log_to_dict(log):
    if isinstance(log, Log):
        return {
            "project": log.project,
            "event_id": log.event_id,
            "parent_id": log.parent_id,
            "event_type": log.event_type,
            "event_name": log.event_name,
            "config": config_to_dict(log.config),
            "inputs": recursive_serialize(log.inputs),
            "outputs": recursive_serialize(log.outputs),
            "children": [log_to_dict(c) for c in log.children]
            if log.children
            else None,
            "start_time": log.start_time,
            "end_time": log.end_time,
            "user_properties": log.user_properties,
            "metadata": log.metadata,
            "source": log.source,
            "error": log.error,
            "metrics": log.metrics,
            "feedback": log.feedback,
            "duration": log.duration,
        }


def recursive_serialize(item):
    # Base case: if the item is a dictionary, process its values
    if isinstance(item, dict):
        return {k: recursive_serialize(v) for k, v in item.items()}

    # If the item is a list or tuple, process its elements
    elif isinstance(item, (list, tuple)):
        return [recursive_serialize(e) for e in item]

    # If the item has a to_dict method, call it
    elif hasattr(item, "to_dict"):
        return recursive_serialize(item.to_dict())

    # Try to serialize the item using the default JSON serialization
    try:
        json.dumps(item)
        return item
    except TypeError:
        # If the item is not JSON serializable, return its string representation
        return str(item)


def config_to_dict(config):
    # Handle config field
    if config:
        return config.dict()
    return None


__all__ = ["HoneyHiveLangChainTracer"]
