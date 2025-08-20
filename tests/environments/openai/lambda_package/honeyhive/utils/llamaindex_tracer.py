# pylint: skip-file
import logging
import os
import uuid
from collections import defaultdict, deque
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from llama_index.core.callbacks.base import BaseCallbackHandler
    from llama_index.core.callbacks.schema import (
        TIMESTAMP_FORMAT,
        CBEvent,
        CBEventType,
        LEAF_EVENTS,
    )
    from llama_index.core.callbacks.token_counting import get_llm_token_counts
    from llama_index.core.utilities.token_counting import TokenCounter
except ImportError:
    raise ImportError("Please install our llama_index tracer. You can install it with `pip install honeyhive[llama_index]`")

from .langchain_tracer import (
    Config,
    LLMConfig,
    Log,
    log_to_dict,
    requests_retry_session,
)

import traceback

class HHEventType(str, Enum):
    MODEL = "model"
    CHAIN = "chain"
    TOOL = "tool"


class HoneyHiveLlamaIndexTracer(BaseCallbackHandler):
    _base_url: str = "https://api.honeyhive.ai"
    _headers: Dict[str, Any] = {"Content-Type": "application/json"}
    # Retrieve the API key from the environment variable
    _env_api_key = os.getenv("HH_API_KEY")

    def __init__(
        self,
        project: str,
        name: Optional[str] = None,
        source: Optional[str] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        tokenizer: Optional[TokenCounter] = None,
        event_types_to_ignore: Optional[List[CBEventType]] = None,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        base_url: Optional[str] = None,
    ) -> None:
        if not LLAMAINDEX_INSTALLED:
            raise ImportError("Please install our llama_index tracer. You can install it with `pip install honeyhive[llama_index]`")
        
        self.verbose = verbose
        if self._env_api_key:
            api_key = self._env_api_key
        elif not api_key:
            raise ValueError(
                "HoneyHive API key is not set! Please set the HH_API_KEY environment variable or pass in the api_key value."
            )

        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

        if base_url:
            self._base_url = base_url

        self.event_starts_to_ignore = event_types_to_ignore or []
        self.event_ends_to_ignore = event_types_to_ignore or []
        self._event_pairs_by_id: Dict[str, List[CBEvent]] = defaultdict(list)
        self._cur_trace_id: Optional[str] = None
        self._trace_map: Dict[str, List[str]] = defaultdict(list)
        self.tokenizer = (
            TokenCounter(tokenizer=tokenizer) if tokenizer else TokenCounter()
        )

        self.name = name
        self.project = project
        self.source = source
        self.user_properties = user_properties
        self.metadata = metadata
        self.eval_info = None
        self.last_event_id = None
        self.last_event_metrics = None
        self.last_event_metadata = None
        if self.source == "evaluation":
            try:
                if self.metadata and "run_id" in self.metadata:
                    self.eval_info = {"run_id": self.metadata["run_id"]}
                    if "datapoint_id" in self.metadata:
                        self.eval_info["datapoint_id"] = self.metadata["datapoint_id"]
                elif self.metadata and "dataset_name" in self.metadata:
                    project_res = requests_retry_session().get(
                        url=f"{self._base_url}/projects",
                        headers=self._headers,
                        params={"name": self.project},
                    )
                    if project_res.status_code == 200:
                        project_id = project_res.json()[0]["_id"]
                        dataset_res = requests_retry_session().get(
                            url=f"{self._base_url}/datasets",
                            headers=self._headers,
                            params={
                                "name": self.metadata["dataset_name"],
                                "project": project_id,
                            },
                        )
                        if dataset_res.status_code == 200:
                            dataset = dataset_res.json()["testcases"][0]
                            dataset_id = dataset["_id"]
                            datapoint_ids = dataset["datapoints"]
                            if "run_name" in self.metadata:
                                run_name = self.metadata["run_name"]
                            else:
                                run_name = self.name
                            self.eval_info = {
                                "dataset_id": dataset_id,
                                "datapoint_ids": datapoint_ids,
                                "project_id": project_id,
                                "run_name": run_name,
                            }
            except Exception as error:
                logging.warning(f"Failed to retrieve datapoint ids: {error}")
                if self.verbose:
                    traceback.print_exc()
        self.session_id = None

    def set_metric(
        self,
        metric_name,
        metric_value,
        threshold,
    ):
        if not self.last_event_id:
            raise Exception("No events defined on session to set metric on")
        metrics = self.last_event_metrics.copy()
        metadata = self.last_event_metadata.copy()
        metrics[metric_name] = metric_value
        metadata[f"threshold_{metric_name}"] = threshold
        body = {
            "event_id": self.last_event_id,
            "metadata": metadata,
            "metrics": metrics,
        }
        res = requests_retry_session().put(
            url=f"{self._base_url}/events",
            headers=self._headers,
            json=body,
        )
        if res.status_code == 200:
            self.last_event_metrics = metrics
            self.last_event_metadata = metadata

    def _start_new_session(self, inputs):
        body = {
            "project": self.project,
            "source": self.source,
            "session_name": self.name,
            "session_id": self.session_id,
            "user_properties": self.user_properties,
            "metadata": self.metadata,
            "inputs": inputs,
        }

        res = requests_retry_session().post(
            url=f"{self._base_url}/session/start",
            headers=self._headers,
            json=body,
        )

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Store event start data by event type.

        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.

        """
        event = CBEvent(event_type, payload=payload, id_=event_id)
        self._event_pairs_by_id[event.id_].append(event)
        return event.id_

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Store event end data by event type.

        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.

        """
        event = CBEvent(event_type, payload=payload, id_=event_id)
        self._event_pairs_by_id[event.id_].append(event)
        self._trace_map = defaultdict(list)

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """Launch a trace."""
        self._trace_map = defaultdict(list)
        self._cur_trace_id = trace_id
        self._start_time = datetime.now()

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self._trace_map = trace_map or defaultdict(list)
        self._end_time = datetime.now()
        self.log_trace()

    def _percolate_up_blacklisted(self, trace_map, event_map):
        new_trace_map = defaultdict(list)

        # Create a reverse map to find parents of each event
        parent_map = {}
        for parent, children in trace_map.items():
            for child in children:
                parent_map[child] = parent

        # Helper function to find the nearest non-blacklisted ancestor
        def find_valid_parent(event_id):
            while event_id in parent_map:
                if event_map.get(parent_map[event_id]) is not None:
                    return parent_map[event_id]
                event_id = parent_map[event_id]
            return "root"  # Default to root if no valid parents found

        # Recursively handle all children of each node
        def handle_children(event_id, valid_parent):
            for child in trace_map[event_id]:
                if event_map.get(child) is not None:  # If child is not blacklisted
                    new_trace_map[valid_parent].append(child)
                    handle_children(child, child)  # Child becomes a new valid parent
                else:
                    handle_children(
                        child, valid_parent
                    )  # Continue with the current valid parent

        # Start processing from root
        for child in trace_map["root"]:
            if event_map.get(child) is None:  # Root's direct child is blacklisted
                handle_children(child, "root")  # Handle all descendants under root
            else:
                new_trace_map["root"].append(child)
                handle_children(child, child)

        return new_trace_map

    def log_trace(self) -> None:
        try:
            events = []
            for event_list in self._trace_map.values():
                events.extend(event_list)
            events = set(events)
            event_map = {}
            for event in events:
                event_pair = self._event_pairs_by_id[event]
                event_log = self._convert_event_pair_to_log(event_pair)
                event_map[event] = event_log
            self._trace_map = self._percolate_up_blacklisted(self._trace_map, event_map)
            for event_id, child_event_ids in self._trace_map.items():
                if event_id == "root":
                    continue
                parent_log = event_map.get(event_id)
                for child_event_id in child_event_ids:
                    child_log = event_map.get(child_event_id)
                    if child_log:
                        child_log.parent_id = (
                            None if parent_log is None else parent_log.event_id
                        )
                        if parent_log:
                            if parent_log.children is None:
                                parent_log.children = [child_log]
                            else:
                                parent_log.children += [child_log]
            root_events = []
            for event_id in self._trace_map["root"]:
                event = event_map.get(event_id)
                if event:
                    root_events.append(event_map[event_id])
            root_events.sort(key=lambda event: event.start_time)
            for event in root_events:
                self._post_trace(event)

        except Exception as error:
            logging.warning(f"Failed to log trace: {error}")
            if self.verbose:
                traceback.print_exc()

    def _convert_event_pair_to_log(
        self,
        event_pair: List[CBEvent],
        parent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Optional[Log]:
        """Convert a pair of events to a HoneyHive log."""
        if len(event_pair) < 2:
            return None
        start_time_us, end_time_us = self._get_time_in_us(event_pair)

        event_type = event_pair[0].event_type
        span_kind = self._map_event_type(event_type)

        root_log = Log(
            project=self.project,
            source=self.source,
            event_id=str(uuid.uuid4()),
            inputs={},
            outputs={},
            children=None,
            error=None,
            parent_id=parent_id,
            config=Config(),
            event_name=f"{getattr(event_type, 'value', event_type)}",
            event_type=span_kind,
            start_time=start_time_us,
            end_time=end_time_us,
            duration=(end_time_us - start_time_us) / 1000,
        )

        inputs, outputs, root_log = self._add_payload_to_log(root_log, event_pair)
        root_log.inputs = inputs
        root_log.outputs = outputs

        return root_log

    def _map_event_type(self, event_type: CBEventType) -> str:
        """Map a CBEventType to a HoneyHive event type."""
        if event_type in [
            CBEventType.LLM,
            CBEventType.EMBEDDING,
            CBEventType.AGENT_STEP,
            CBEventType.RERANKING,
        ]:
            hh_event_type = HHEventType.MODEL
        elif event_type in [
            CBEventType.CHUNKING,
            CBEventType.NODE_PARSING,
            CBEventType.TREE,
            CBEventType.TEMPLATING,
            CBEventType.FUNCTION_CALL,
            CBEventType.EXCEPTION,
        ]:
            hh_event_type = HHEventType.TOOL
        else:
            hh_event_type = HHEventType.CHAIN

        return hh_event_type

    def _add_payload_to_log(
        self, span: Log, event_pair: List[CBEvent]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Log]:
        """Add the event's payload to the span."""
        assert len(event_pair) == 2
        event_type = event_pair[0].event_type
        inputs = None
        outputs = {}

        if event_type == CBEventType.NODE_PARSING:
            inputs, outputs = self._handle_node_parsing_payload(event_pair)
        elif event_type == CBEventType.LLM:
            inputs, outputs, span = self._handle_llm_payload(event_pair, span)
        elif event_type == CBEventType.QUERY:
            inputs, outputs = self._handle_query_payload(event_pair)
        elif event_type == CBEventType.EMBEDDING:
            inputs, outputs, span = self._handle_embedding_payload(event_pair, span)
        elif event_type == CBEventType.RETRIEVE:
            inputs, outputs = self._handle_retrieve_payload(event_pair)
        elif event_type == CBEventType.SYNTHESIZE:
            inputs, outputs = self._handle_synthesize_payload(event_pair)
        elif event_type == CBEventType.TEMPLATING:
            inputs, outputs = self._handle_templating_payload(event_pair)
        elif event_type == CBEventType.TREE:
            inputs, outputs = self._handle_tree_payload(event_pair)
        elif event_type == CBEventType.SUB_QUESTION:
            inputs, outputs = self._handle_sub_question_payload(event_pair)
        elif event_type == CBEventType.FUNCTION_CALL:
            inputs, outputs = self._handle_function_call_payload(event_pair)
        elif event_type == CBEventType.RERANKING:
            inputs, outputs, span = self._handle_reranking_payload(event_pair, span)
        elif event_type == CBEventType.EXCEPTION:
            inputs, outputs = self._handle_exception_payload(event_pair)
        elif event_type == CBEventType.AGENT_STEP:
            inputs, outputs = self._handle_agent_step_payload(event_pair)

        return inputs, outputs, span

    def _handle_agent_step_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # TODO: Implement this
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_exception_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # TODO: Implement this
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_reranking_payload(
        self, event_pair: List[CBEvent], span: Log
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Log]:
        input_payload = event_pair[0].payload
        outputs = event_pair[-1].payload

        inputs = {}
        if "nodes" in input_payload:
            inputs["nodes"] = input_payload["nodes"]
        if "query_str" in input_payload:
            inputs["query_str"] = input_payload["query_str"]
        if "top_k" in input_payload:
            inputs["top_k"] = input_payload["top_k"]

        if "model_name" in input_payload:
            config = LLMConfig()
            config.model_name = input_payload["model_name"]
            span.config = config

        return inputs, outputs or {}, span

    def _handle_function_call_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # TODO: Implement this
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_sub_question_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # TODO: Implement this
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_tree_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # TODO: Implement this
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_retrieve_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = {"query_str": event_pair[0].payload["query_str"]}
        chunks = []
        for node in event_pair[1].payload["nodes"]:
            chunks.append({"score": node.score, "text": node.node.text})
        outputs = {"chunks": chunks}
        return inputs, outputs

    def _handle_templating_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_synthesize_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_node_parsing_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs or {}, outputs or {}

    def _handle_llm_payload(
        self, event_pair: List[CBEvent], span: Log
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Log]:
        """Handle the payload of a LLM event."""
        input_payload = event_pair[0].payload
        outputs = event_pair[-1].payload

        inputs = {}

        # Get `original_template` from Prompt
        if "formatted_prompt" in input_payload:
            inputs["formatted_prompt"] = input_payload["formatted_prompt"]

        # Format messages
        if "messages" in input_payload:
            inputs["chat_history"] = []
            for message in input_payload["messages"]:
                role, content = str(message).split(":", 1)
                inputs["chat_history"].append({"role": role, "content": content})

        if "serialized" in input_payload:
            config = LLMConfig()
            if input_payload["serialized"].get("model"):
                config.model_name = input_payload["serialized"]["model"]
            if input_payload["serialized"].get("model_name"):
                config.model_name = input_payload["serialized"]["model_name"]
            if input_payload["serialized"].get("api_base"):
                config.api_base = input_payload["serialized"]["api_base"]
            if input_payload["serialized"].get("api_version"):
                config.api_version = input_payload["serialized"]["api_version"]
            if input_payload["serialized"].get("class_name"):
                config.class_name = input_payload["serialized"]["class_name"]
            span.config = config

        token_counts = get_llm_token_counts(self.tokenizer, outputs)
        metadata = {
            "formatted_prompt_tokens_count": token_counts.prompt_token_count,
            "prediction_tokens_count": token_counts.completion_token_count,
            "total_tokens_used": token_counts.total_token_count,
        }
        span.metadata = metadata

        # Make `response` part of `outputs`
        if "response" in outputs:
            outputs = {"response": outputs["response"]}
        elif "completion" in outputs:
            outputs = {"response": outputs["completion"].text}

        return inputs, outputs, span

    def _handle_query_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """Handle the payload of a QUERY event."""
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload
        return inputs, outputs

    def _handle_embedding_payload(
        self,
        event_pair: List[CBEvent],
        span: Log,
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], Log]:
        input_payload = event_pair[0].payload
        outputs = event_pair[-1].payload

        chunks = []
        if outputs:
            chunks = outputs.get("chunks", [])

        inputs = {}
        if "serialized" in input_payload:
            config = LLMConfig()
            if input_payload["serialized"].get("model"):
                config.model_name = input_payload["serialized"]["model"]
            if input_payload["serialized"].get("model_name"):
                config.model_name = input_payload["serialized"]["model_name"]
            if input_payload["serialized"].get("api_base"):
                config.api_base = input_payload["serialized"]["api_base"]
            if input_payload["serialized"].get("api_version"):
                config.api_version = input_payload["serialized"]["api_version"]
            if input_payload["serialized"].get("class_name"):
                config.class_name = input_payload["serialized"]["class_name"]
            span.config = config

        inputs["chunks"] = chunks

        return inputs, {}, span

    def _get_time_in_us(self, event_pair: List[CBEvent]) -> Tuple[int, int]:
        """Get the start and end time of an event pair in microseconds."""
        start_time = datetime.strptime(event_pair[0].time, TIMESTAMP_FORMAT)
        end_time = datetime.strptime(event_pair[1].time, TIMESTAMP_FORMAT)

        start_time_in_ms = int(
            (start_time - datetime(1970, 1, 1)).total_seconds() * 1000000
        )
        end_time_in_ms = int(
            (end_time - datetime(1970, 1, 1)).total_seconds() * 1000000
        )

        return start_time_in_ms, end_time_in_ms

    def _post_trace(self, root_log: Log) -> None:
        root_log = log_to_dict(root_log)
        self.final_outputs = root_log["outputs"]
        first_trace = False
        if self.session_id is None:
            first_trace = True
            self.session_id = str(uuid.uuid4())
            self._start_new_session(root_log["inputs"])
        self._crawl(root_log, self.session_id)

        trace_response = requests_retry_session().post(
            url=f"{self._base_url}/session/{self.session_id}/traces",
            json={"logs": [root_log]},
            headers=self._headers,
        )
        if trace_response.status_code != 200:
            raise Exception(
                f"Failed to post trace to HoneyHive with status code {trace_response.status_code}"
            )
        requests_retry_session().put(
            url=f"{self._base_url}/events",
            json={
                "event_id": self.session_id,
                "outputs": self.final_outputs,
            },
            headers=self._headers,
        )
        if self.eval_info and first_trace:
            try:
                if "run_id" in self.eval_info:
                    run_res = requests_retry_session().get(
                        url=f"{self._base_url}/runs/{self.eval_info['run_id']}",
                        headers=self._headers,
                    )
                    event_ids = run_res.json()["evaluation"]["event_ids"]
                    event_ids.append(self.session_id)
                    datapoint_ids = run_res.json()["evaluation"]["event_ids"]
                    if "datapoint_id" in self.eval_info:
                        datapoint_ids.append(self.eval_info["datapoint_id"])
                    requests_retry_session().put(
                        url=f"{self._base_url}/runs/{self.eval_info['run_id']}",
                        json={"event_ids": event_ids, "datapoint_ids": datapoint_ids},
                        headers=self._headers,
                    )
                else:
                    body = {
                        "event_ids": [self.session_id],
                        "dataset_id": self.eval_info["dataset_id"],
                        "datapoint_ids": self.eval_info["datapoint_ids"],
                        "project": self.eval_info["project_id"],
                        "status": "completed",
                        "name": self.eval_info["run_name"],
                    }
                    if "config" in root_log:
                        body["configuration"] = root_log["config"]
                    run_res = requests_retry_session().post(
                        url=f"{self._base_url}/runs",
                        headers=self._headers,
                        json=body,
                    )
                    run_id = run_res.json()["run_id"]
                    self.eval_info["run_id"] = run_id
            except Exception as error:
                logging.warning(f"Failed to process eval: {error}")
                if self.verbose:
                    traceback.print_exc()

    def _parse_chat_history(self, chat_string):
        # Split the string into lines
        lines = chat_string.split("\n")

        # This list will store our parsed chat history
        chat_history = []

        # Temporary variables to hold current role and content
        current_role = None
        content = []

        # Helper function to add an entry to chat history
        def add_entry(role, content):
            if content:
                chat_history.append(
                    {"role": role, "content": "\n".join(content).strip()}
                )

        # Iterate through each line to process the content
        for line in lines:
            # Check if the line starts a new role section
            if line.startswith(("system:", "user:", "assistant:")):
                # If there is an existing role and content, save it
                if current_role is not None:
                    add_entry(current_role, content)

                # Reset for the new role
                parts = line.split(":", 1)
                current_role = parts[0].strip()
                content = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continue accumulating content for the current role
                content.append(line)

        # Don't forget to add the last accumulated content to the chat history
        add_entry(current_role, content)

        return chat_history

    def _crawl(self, trace, session_id) -> None:
        def crawl(node):
            if node is None:
                return
            node["session_id"] = session_id
            self.last_event_id = node["event_id"]
            self.last_event_metrics = node.get("metrics", {})
            self.last_event_metadata = node.get("metadata", {})
            self.final_outputs = node["outputs"]
            if node["children"]:
                """
                We do a pattern-match for the following pattern in the event tree:
                synthesize
                  llm
                  templating

                We then replace this pattern with a single event that has all of the information from these events rolled into one.
                TODO: Look into replacing this workaround if the instrumentation from the LlamaIndex side changes.
                """
                if (
                    len(node["children"]) == 2
                    and node["event_name"] == CBEventType.SYNTHESIZE
                ):
                    child1, child2 = node["children"][0], node["children"][1]
                    pattern = set([CBEventType.TEMPLATING, CBEventType.LLM])
                    child_event_names = set(
                        [child1["event_name"], child2["event_name"]]
                    )
                    if (
                        pattern == child_event_names
                        and not child1["children"]
                        and not child2["children"]
                    ):
                        if child1["event_name"] == CBEventType.LLM:
                            llm_event = child1
                            templating_event = child2
                        else:
                            llm_event = child2
                            templating_event = child1
                        node["children"] = None
                        node["outputs"] = llm_event.get("outputs")
                        node["config"] = llm_event["config"]
                        inputs = {}
                        if "chat_history" in llm_event["inputs"]:
                            inputs["chat_history"] = llm_event["inputs"]["chat_history"]
                        if "template" in templating_event["inputs"]:
                            node["config"]["template"] = self._parse_chat_history(
                                templating_event["inputs"]["template"]
                            )
                        if "template_vars" in templating_event["inputs"]:
                            template_vars = templating_event["inputs"]["template_vars"]
                            if "query_str" in template_vars:
                                inputs["query_str"] = template_vars["query_str"]
                            if "context_str" in template_vars:
                                inputs["context_str"] = template_vars["context_str"]
                        node["inputs"] = inputs
                        node["event_type"] = HHEventType.MODEL
                        return
                for child in node["children"]:
                    child["parent_id"] = node["event_id"]
                    crawl(child)

        crawl(trace)

    def finish(self) -> None:
        pass
