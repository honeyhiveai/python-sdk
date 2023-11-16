import os
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from llama_index.callbacks.base import BaseCallbackHandler
from llama_index.callbacks.schema import TIMESTAMP_FORMAT, CBEvent, CBEventType
from llama_index.callbacks.token_counting import get_llm_token_counts
from llama_index.utils import globals_helper

from honeyhive.sdk.langchain_tracer import Config, Log, log_to_dict


class HHEventType(str, Enum):
    MODEL = "model"
    CHAIN = "chain"
    TOOL = "tool"
    GENERIC = "generic"


class HoneyHiveLlamaIndexTracer(BaseCallbackHandler):
    _base_url: str = "https://api.honeyhive.ai"
    _headers: Dict[str, Any] = {"Content-Type": "application/json"}
    # Retrieve the API key from the environment variable
    _env_api_key = os.getenv("HONEYHIVE_API_KEY")

    def __init__(
        self,
        project: str,
        name: Optional[str] = None,
        source: Optional[str] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        tokenizer: Optional[Callable[[str], List]] = None,
        event_starts_to_ignore: Optional[List[CBEventType]] = None,
        event_ends_to_ignore: Optional[List[CBEventType]] = None,
        api_key: Optional[str] = None,
    ) -> None:
        if self._env_api_key:
            api_key = self._env_api_key
        elif not api_key:
            raise ValueError(
                "HoneyHive API key is not set! Please set the HONEYHIVE_API_KEY environment variable or pass in the api_key value."
            )

        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

        self.event_starts_to_ignore = event_starts_to_ignore or []
        self.event_ends_to_ignore = event_ends_to_ignore or []
        self._event_pairs_by_id: Dict[str, List[CBEvent]] = defaultdict(list)
        self._cur_trace_id: Optional[str] = None
        self._trace_map: Dict[str, List[str]] = defaultdict(list)
        self.tokenizer = tokenizer or globals_helper.tokenizer

        self.name = name
        self.project = project
        self.source = source
        self.user_properties = user_properties

    def _start_new_session(self):
        self.session_id = str(uuid.uuid4())
        body = {
            "project": self.project,
            "source": self.source,
            "session_name": self.name,
            "session_id": self.session_id,
            "user_properties": self.user_properties,
        }

        session_response = requests.post(
            url=f"{self._base_url}/session/start",
            headers=self._headers,
            json=body,
        )

        res = session_response.json()
        self.session_id = res['session_id']

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

    def log_trace(self) -> None:
        try:
            child_nodes = self._trace_map.get("root")
            if child_nodes:
                root_span = self._convert_event_pair_to_log(
                    self._event_pairs_by_id.get(child_nodes[0]),
                    trace_id=self._cur_trace_id
                    if len(child_nodes) > 1
                    else None,
                )
                if len(child_nodes) == 1:
                    child_nodes = self._trace_map.get(child_nodes[0])
                    root_span = self._build_trace(child_nodes, root_span)
                else:
                    root_span = self._build_trace(child_nodes, root_span)
                if root_span and root_span.event_type == 'chain':
                    self._post_trace(root_span)
        except Exception:
            # Silently ignore errors to not break user code
            pass

    def _build_trace(
        self, events: List[str], span: Log, parent_id: Optional[str] = None
    ) -> Log:
        """Build the trace tree from the trace map."""
        for child_event in events:
            child_span = self._convert_event_pair_to_log(
                self._event_pairs_by_id[child_event], parent_id=parent_id
            )
            child_span = self._build_trace(
                self._trace_map[child_event], child_span, child_span.event_id
            )
            if span.children is None:
                span.children = [child_span]
            else:
                span.children.append(child_span)
        return span

    def _convert_event_pair_to_log(
        self,
        event_pair: List[CBEvent],
        parent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Log:
        """Convert a pair of events to a HoneyHive log."""
        start_time_us, end_time_us, end_time = self._get_time_in_us(event_pair)

        if trace_id is None:
            event_type = event_pair[0].event_type
            span_kind = self._map_event_type(event_type)
        else:
            event_type = trace_id  # type: ignore
            span_kind = "generic"

        root_log = Log(
            project=self.project,
            source=self.source,
            event_id=str(uuid.uuid4()),
            inputs={},
            outputs=None,
            children=None,
            error=None,
            parent_id=parent_id,
            config=Config(),
            event_name=f"{event_type}",
            event_type=span_kind,
            start_time=start_time_us,
            end_time=end_time_us,
            duration=(end_time_us - start_time_us) / 1000,
        )

        inputs, outputs, root_log = self._add_payload_to_log(
            root_log, event_pair
        )
        root_log.inputs = inputs
        root_log.outputs = outputs

        return root_log

    def _map_event_type(self, event_type: CBEventType) -> str:
        """Map a CBEventType to a HoneyHive event type."""
        if event_type in [
            CBEventType.EMBEDDING,
            CBEventType.LLM,
            CBEventType.SYNTHESIZE,
        ]:
            hh_event_type = HHEventType.MODEL
        elif event_type in [
            CBEventType.QUERY,
            CBEventType.TREE,
            CBEventType.SUB_QUESTION,
        ]:
            hh_event_type = HHEventType.CHAIN
        elif event_type == CBEventType.RETRIEVE:
            hh_event_type = HHEventType.TOOL
        else:
            hh_event_type = HHEventType.GENERIC

        return hh_event_type

    def _add_payload_to_log(
        self, span: Log, event_pair: List[CBEvent]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Log]:
        """Add the event's payload to the span."""
        assert len(event_pair) == 2
        event_type = event_pair[0].event_type
        inputs = None
        outputs = None

        if event_type == CBEventType.NODE_PARSING:
            # TODO: disabled full detailed inputs/outputs due to UI lag
            inputs, outputs = self._handle_node_parsing_payload(event_pair)
        elif event_type == CBEventType.LLM:
            inputs, outputs, span = self._handle_llm_payload(event_pair, span)
        elif event_type == CBEventType.QUERY:
            inputs, outputs = self._handle_query_payload(event_pair)
        elif event_type == CBEventType.EMBEDDING:
            inputs, outputs = self._handle_embedding_payload(event_pair)
        elif event_type == CBEventType.RETRIEVE:
            inputs, outputs = self._handle_retrieve_payload(event_pair)

        return inputs, outputs, span

    def _handle_retrieve_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = {'query_str': event_pair[0].payload['query_str']}
        chunks = []
        for node in event_pair[1].payload['nodes']:
            chunks.append({'score': node.score, 'text': node.node.text})
        outputs = {'chunks': chunks}
        return inputs, outputs

    def _handle_node_parsing_payload(
        self, event_pair: List[CBEvent]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle the payload of a NODE_PARSING event."""
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload

        if inputs and "documents" in inputs:
            documents = inputs.pop("documents")
            inputs["num_documents"] = len(documents)

        if outputs and "nodes" in outputs:
            nodes = outputs.pop("nodes")
            outputs["num_nodes"] = len(nodes)

        return inputs or {}, outputs or {}

    def _handle_llm_payload(
        self, event_pair: List[CBEvent], span: Log
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Log]:
        """Handle the payload of a LLM event."""
        inputs = event_pair[0].payload
        outputs = event_pair[-1].payload

        assert isinstance(inputs, dict) and isinstance(outputs, dict)

        # Get `original_template` from Prompt
        if "formatted_prompt" in inputs:
            inputs["formatted_prompt"] = inputs["formatted_prompt"]

        # Format messages
        if "messages" in inputs:
            inputs["messages"] = "\n".join(
                [str(x) for x in inputs["messages"]]
            )

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

        if outputs:
            response = outputs["response"]

            if type(response).__name__ == "Response":
                response = response.response
            elif type(response).__name__ == "StreamingResponse":
                response = response.get_response().response
        else:
            response = " "

        outputs = {"response": response}

        return inputs, outputs

    def _handle_embedding_payload(
        self,
        event_pair: List[CBEvent],
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        event_pair[0].payload
        outputs = event_pair[-1].payload

        chunks = []
        if outputs:
            chunks = outputs.get("chunks", [])

        return {}, {"chunks": chunks}

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

        return start_time_in_ms, end_time_in_ms, end_time

    def _post_trace(self, root_log: Log) -> None:
        self._start_new_session()
        root_log = log_to_dict(root_log)
        root_log['session_id'] = str(uuid.uuid4())
        trace_response = requests.post(
            url=f"{self._base_url}/session/{self.session_id}/traces",
            json={"logs": [root_log]},
            headers=self._headers,
        )
        if trace_response.status_code != 200:
            raise Exception(
                f"Failed to post trace to HoneyHive with status code {trace_response.status_code}"
            )

    def finish(self) -> None:
        pass
