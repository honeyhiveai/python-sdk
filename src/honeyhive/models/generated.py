"""Auto-generated Pydantic models for HoneyHive API.

This module contains automatically generated Pydantic models based on the
HoneyHive API specification. These models are used for request/response
serialization and validation.

Note: This file is auto-generated and should not be manually edited.
Any changes should be made to the source schema and regenerated.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionStartRequest(BaseModel):
    project: str = Field(..., description="Project name associated with the session")
    session_name: str = Field(..., description="Name of the session")
    source: str = Field(
        ..., description="Source of the session - production, staging, etc"
    )
    session_id: Optional[str] = Field(
        None,
        description="Unique id of the session, if not set, it will be auto-generated",
    )
    children_ids: Optional[List[str]] = Field(
        None, description="Id of events that are nested within the session"
    )
    config: Optional[Dict[str, Any]] = Field(
        None, description="Associated configuration for the session"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Input object passed to the session - user query, text blob, etc",
    )
    outputs: Optional[Dict[str, Any]] = Field(
        None, description="Final output of the session - completion, chunks, etc"
    )
    error: Optional[str] = Field(
        None, description="Any error description if session failed"
    )
    duration: Optional[float] = Field(
        None, description="How long the session took in milliseconds"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Any user properties associated with the session"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Any values computed over the output of the session"
    )
    feedback: Optional[Dict[str, Any]] = Field(
        None, description="Any user feedback provided for the session output"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Any system or application metadata associated with the session",
    )
    start_time: Optional[float] = Field(
        None, description="UTC timestamp (in milliseconds) for the session start"
    )
    end_time: Optional[int] = Field(
        None, description="UTC timestamp (in milliseconds) for the session end"
    )


class SessionPropertiesBatch(BaseModel):
    session_name: Optional[str] = Field(None, description="Name of the session")
    source: Optional[str] = Field(
        None, description="Source of the session - production, staging, etc"
    )
    session_id: Optional[str] = Field(
        None,
        description="Unique id of the session, if not set, it will be auto-generated",
    )
    config: Optional[Dict[str, Any]] = Field(
        None, description="Associated configuration for the session"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Input object passed to the session - user query, text blob, etc",
    )
    outputs: Optional[Dict[str, Any]] = Field(
        None, description="Final output of the session - completion, chunks, etc"
    )
    error: Optional[str] = Field(
        None, description="Any error description if session failed"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Any user properties associated with the session"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Any values computed over the output of the session"
    )
    feedback: Optional[Dict[str, Any]] = Field(
        None, description="Any user feedback provided for the session output"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Any system or application metadata associated with the session",
    )


class EventType(Enum):
    session = "session"
    model = "model"
    tool = "tool"
    chain = "chain"


class Event(BaseModel):
    project_id: Optional[str] = Field(
        None, description="Name of project associated with the event"
    )
    source: Optional[str] = Field(
        None, description="Source of the event - production, staging, etc"
    )
    event_name: Optional[str] = Field(None, description="Name of the event")
    event_type: Optional[EventType] = Field(
        None,
        description='Specify whether the event is of "session", "model", "tool" or "chain" type',
    )
    event_id: Optional[str] = Field(
        None,
        description="Unique id of the event, if not set, it will be auto-generated",
    )
    session_id: Optional[str] = Field(
        None,
        description="Unique id of the session associated with the event, if not set, it will be auto-generated",
    )
    parent_id: Optional[str] = Field(
        None, description="Id of the parent event if nested"
    )
    children_ids: Optional[List[str]] = Field(
        None, description="Id of events that are nested within the event"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Associated configuration JSON for the event - model name, vector index name, etc",
    )
    inputs: Optional[Dict[str, Any]] = Field(
        None, description="Input JSON given to the event - prompt, chunks, etc"
    )
    outputs: Optional[Dict[str, Any]] = Field(
        None, description="Final output JSON of the event"
    )
    error: Optional[str] = Field(
        None, description="Any error description if event failed"
    )
    start_time: Optional[float] = Field(
        None, description="UTC timestamp (in milliseconds) for the event start"
    )
    end_time: Optional[int] = Field(
        None, description="UTC timestamp (in milliseconds) for the event end"
    )
    duration: Optional[float] = Field(
        None, description="How long the event took in milliseconds"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Any system or application metadata associated with the event"
    )
    feedback: Optional[Dict[str, Any]] = Field(
        None, description="Any user feedback provided for the event output"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Any values computed over the output of the event"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Any user properties associated with the event"
    )


class Operator(Enum):
    is_ = "is"
    is_not = "is not"
    contains = "contains"
    not_contains = "not contains"
    greater_than = "greater than"


class Type(Enum):
    string = "string"
    number = "number"
    boolean = "boolean"
    id = "id"


class EventFilter(BaseModel):
    field: Optional[str] = Field(
        None,
        description="The field name that you are filtering by like `metadata.cost`, `inputs.chat_history.0.content`",
    )
    value: Optional[str] = Field(
        None, description="The value that you are filtering the field for"
    )
    operator: Optional[Operator] = Field(
        None,
        description='The type of filter you are performing - "is", "is not", "contains", "not contains", "greater than"',
    )
    type: Optional[Type] = Field(
        None,
        description='The data type you are using - "string", "number", "boolean", "id" (for object ids)',
    )


class EventType1(Enum):
    model = "model"
    tool = "tool"
    chain = "chain"


class CreateEventRequest(BaseModel):
    project: str = Field(..., description="Project associated with the event")
    source: str = Field(
        ..., description="Source of the event - production, staging, etc"
    )
    event_name: str = Field(..., description="Name of the event")
    event_type: EventType1 = Field(
        ...,
        description='Specify whether the event is of "model", "tool" or "chain" type',
    )
    event_id: Optional[str] = Field(
        None,
        description="Unique id of the event, if not set, it will be auto-generated",
    )
    session_id: Optional[str] = Field(
        None,
        description="Unique id of the session associated with the event, if not set, it will be auto-generated",
    )
    parent_id: Optional[str] = Field(
        None, description="Id of the parent event if nested"
    )
    children_ids: Optional[List[str]] = Field(
        None, description="Id of events that are nested within the event"
    )
    config: Dict[str, Any] = Field(
        ...,
        description="Associated configuration JSON for the event - model name, vector index name, etc",
    )
    inputs: Dict[str, Any] = Field(
        ..., description="Input JSON given to the event - prompt, chunks, etc"
    )
    outputs: Optional[Dict[str, Any]] = Field(
        None, description="Final output JSON of the event"
    )
    error: Optional[str] = Field(
        None, description="Any error description if event failed"
    )
    start_time: Optional[float] = Field(
        None, description="UTC timestamp (in milliseconds) for the event start"
    )
    end_time: Optional[int] = Field(
        None, description="UTC timestamp (in milliseconds) for the event end"
    )
    duration: float = Field(..., description="How long the event took in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Any system or application metadata associated with the event"
    )
    feedback: Optional[Dict[str, Any]] = Field(
        None, description="Any user feedback provided for the event output"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Any values computed over the output of the event"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Any user properties associated with the event"
    )


class CreateModelEvent(BaseModel):
    project: str = Field(..., description="Project associated with the event")
    model: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider")
    messages: List[Dict[str, Any]] = Field(
        ..., description="Messages passed to the model"
    )
    response: Dict[str, Any] = Field(..., description="Final output JSON of the event")
    duration: float = Field(..., description="How long the event took in milliseconds")
    usage: Dict[str, Any] = Field(..., description="Usage statistics of the model")
    cost: Optional[float] = Field(None, description="Cost of the model completion")
    error: Optional[str] = Field(
        None, description="Any error description if event failed"
    )
    source: Optional[str] = Field(
        None, description="Source of the event - production, staging, etc"
    )
    event_name: Optional[str] = Field(None, description="Name of the event")
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, description="Hyperparameters used for the model"
    )
    template: Optional[List[Dict[str, Any]]] = Field(
        None, description="Template used for the model"
    )
    template_inputs: Optional[Dict[str, Any]] = Field(
        None, description="Inputs for the template"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        None, description="Tools used for the model"
    )
    tool_choice: Optional[str] = Field(None, description="Tool choice for the model")
    response_format: Optional[Dict[str, Any]] = Field(
        None, description="Response format for the model"
    )


class Type1(Enum):
    custom = "custom"
    model = "model"
    human = "human"
    composite = "composite"


class ReturnType(Enum):
    boolean = "boolean"
    float = "float"
    string = "string"


class Threshold(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class Metric(BaseModel):
    name: str = Field(..., description="Name of the metric")
    criteria: Optional[str] = Field(
        None, description="Criteria for human or composite metrics"
    )
    code_snippet: Optional[str] = Field(
        None, description="Associated code block for the metric"
    )
    prompt: Optional[str] = Field(None, description="Evaluator prompt for the metric")
    task: str = Field(..., description="Name of the project associated with metric")
    type: Type1 = Field(
        ...,
        description='Type of the metric - "custom", "model", "human" or "composite"',
    )
    description: str = Field(
        ..., description="Short description of what the metric does"
    )
    enabled_in_prod: Optional[bool] = Field(
        None, description="Whether to compute on all production events automatically"
    )
    needs_ground_truth: Optional[bool] = Field(
        None,
        description="Whether a ground truth (on metadata) is required to compute it",
    )
    return_type: ReturnType = Field(
        ...,
        description='The data type of the metric value - "boolean", "float", "string"',
    )
    threshold: Optional[Threshold] = Field(
        None,
        description="Threshold for numeric metrics to decide passing or failing in tests",
    )
    pass_when: Optional[bool] = Field(
        None,
        description="Threshold for boolean metrics to decide passing or failing in tests",
    )
    field_id: Optional[str] = Field(None, alias="_id", description="Unique idenitifier")
    event_name: Optional[str] = Field(
        None, description="Name of event that the metric is set to be computed on"
    )
    event_type: Optional[str] = Field(
        None, description="Type of event that the metric is set to be computed on"
    )
    model_provider: Optional[str] = Field(
        None,
        description="Provider of the model, formatted as a LiteLLM provider prefix",
    )
    model_name: Optional[str] = Field(
        None, description="Name of the model, formatted as a LiteLLM model name"
    )
    child_metrics: Optional[List[Dict[str, Any]]] = Field(
        None, description="Child metrics added under composite events"
    )


class EventType2(Enum):
    model = "model"
    tool = "tool"
    chain = "chain"
    session = "session"


class MetricEdit(BaseModel):
    metric_id: str = Field(..., description="Unique identifier of the metric")
    criteria: Optional[str] = Field(
        None, description="Criteria for human or composite metrics"
    )
    name: Optional[str] = Field(None, description="Updated name of the metric")
    description: Optional[str] = Field(
        None, description="Short description of what the metric does"
    )
    code_snippet: Optional[str] = Field(
        None, description="Updated code block for the metric"
    )
    prompt: Optional[str] = Field(
        None, description="Updated Evaluator prompt for the metric"
    )
    type: Optional[Type1] = Field(
        None,
        description='Type of the metric - "custom", "model", "human" or "composite"',
    )
    enabled_in_prod: Optional[bool] = Field(
        None, description="Whether to compute on all production events automatically"
    )
    needs_ground_truth: Optional[bool] = Field(
        None,
        description="Whether a ground truth (on metadata) is required to compute it",
    )
    return_type: Optional[ReturnType] = Field(
        None,
        description='The data type of the metric value - "boolean", "float", "string"',
    )
    threshold: Optional[Threshold] = Field(
        None,
        description="Threshold for numeric metrics to decide passing or failing in tests",
    )
    pass_when: Optional[bool] = Field(
        None,
        description="Threshold for boolean metrics to decide passing or failing in tests",
    )
    event_name: Optional[str] = Field(
        None, description="Name of event that the metric is set to be computed on"
    )
    event_type: Optional[EventType2] = Field(
        None, description="Type of event that the metric is set to be computed on"
    )
    model_provider: Optional[str] = Field(
        None,
        description="Provider of the model, formatted as a LiteLLM provider prefix",
    )
    model_name: Optional[str] = Field(
        None, description="Name of the model, formatted as a LiteLLM model name"
    )
    child_metrics: Optional[List[Dict[str, Any]]] = Field(
        None, description="Child metrics added under composite events"
    )


class ToolType(Enum):
    function = "function"
    tool = "tool"


class Tool(BaseModel):
    field_id: Optional[str] = Field(None, alias="_id")
    task: str = Field(..., description="Name of the project associated with this tool")
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(
        ..., description="These can be function call params or plugin call params"
    )
    tool_type: ToolType


class Type3(Enum):
    function = "function"
    tool = "tool"


class CreateToolRequest(BaseModel):
    task: str = Field(..., description="Name of the project associated with this tool")
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(
        ..., description="These can be function call params or plugin call params"
    )
    type: Type3


class UpdateToolRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]


class Datapoint(BaseModel):
    field_id: Optional[str] = Field(
        None, alias="_id", description="UUID for the datapoint"
    )
    tenant: Optional[str] = None
    project_id: Optional[str] = Field(
        None, description="UUID for the project where the datapoint is stored"
    )
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Arbitrary JSON object containing the inputs for the datapoint",
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conversation history associated with the datapoint"
    )
    ground_truth: Optional[Dict[str, Any]] = None
    linked_event: Optional[str] = Field(
        None, description="Event id for the event from which the datapoint was created"
    )
    linked_evals: Optional[List[str]] = Field(
        None, description="Ids of evaluations where the datapoint is included"
    )
    linked_datasets: Optional[List[str]] = Field(
        None, description="Ids of all datasets that include the datapoint"
    )
    saved: Optional[bool] = None
    type: Optional[str] = Field(
        None, description="session or event - specify the type of data"
    )
    metadata: Optional[Dict[str, Any]] = None


class CreateDatapointRequest(BaseModel):
    project: str = Field(
        ..., description="Name for the project to which the datapoint belongs"
    )
    inputs: Dict[str, Any] = Field(
        ..., description="Arbitrary JSON object containing the inputs for the datapoint"
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conversation history associated with the datapoint"
    )
    ground_truth: Optional[Dict[str, Any]] = Field(
        None, description="Expected output JSON object for the datapoint"
    )
    linked_event: Optional[str] = Field(
        None, description="Event id for the event from which the datapoint was created"
    )
    linked_datasets: Optional[List[str]] = Field(
        None, description="Ids of all datasets that include the datapoint"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Any additional metadata for the datapoint"
    )


class UpdateDatapointRequest(BaseModel):
    inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Arbitrary JSON object containing the inputs for the datapoint",
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conversation history associated with the datapoint"
    )
    ground_truth: Optional[Dict[str, Any]] = Field(
        None, description="Expected output JSON object for the datapoint"
    )
    linked_evals: Optional[List[str]] = Field(
        None, description="Ids of evaluations where the datapoint is included"
    )
    linked_datasets: Optional[List[str]] = Field(
        None, description="Ids of all datasets that include the datapoint"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Any additional metadata for the datapoint"
    )


class Type4(Enum):
    evaluation = "evaluation"
    fine_tuning = "fine-tuning"


class PipelineType(Enum):
    event = "event"
    session = "session"


class CreateDatasetRequest(BaseModel):
    project: str = Field(
        ...,
        description="Name of the project associated with this dataset like `New Project`",
    )
    name: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="A description for the dataset"
    )
    type: Optional[Type4] = Field(
        None,
        description='What the dataset is to be used for - "evaluation" (default) or "fine-tuning"',
    )
    datapoints: Optional[List[str]] = Field(
        None, description="List of unique datapoint ids to be included in this dataset"
    )
    linked_evals: Optional[List[str]] = Field(
        None,
        description="List of unique evaluation run ids to be associated with this dataset",
    )
    saved: Optional[bool] = None
    pipeline_type: Optional[PipelineType] = Field(
        None,
        description='The type of data included in the dataset - "event" (default) or "session"',
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Any helpful metadata to track for the dataset"
    )


class Dataset(BaseModel):
    project: Optional[str] = Field(
        None, description="UUID of the project associated with this dataset"
    )
    name: Optional[str] = Field(None, description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="A description for the dataset"
    )
    type: Optional[Type4] = Field(
        None,
        description='What the dataset is to be used for - "evaluation" or "fine-tuning"',
    )
    datapoints: Optional[List[str]] = Field(
        None, description="List of unique datapoint ids to be included in this dataset"
    )
    num_points: Optional[int] = Field(
        None, description="Number of datapoints included in the dataset"
    )
    linked_evals: Optional[List[str]] = None
    saved: Optional[bool] = Field(
        None, description="Whether the dataset has been saved or detected"
    )
    pipeline_type: Optional[PipelineType] = Field(
        None,
        description='The type of data included in the dataset - "event" (default) or "session"',
    )
    created_at: Optional[str] = Field(
        None, description="Timestamp of when the dataset was created"
    )
    updated_at: Optional[str] = Field(
        None, description="Timestamp of when the dataset was last updated"
    )


class DatasetUpdate(BaseModel):
    dataset_id: str = Field(
        ..., description="The unique identifier of the dataset being updated"
    )
    name: Optional[str] = Field(None, description="Updated name for the dataset")
    description: Optional[str] = Field(
        None, description="Updated description for the dataset"
    )
    datapoints: Optional[List[str]] = Field(
        None,
        description="Updated list of datapoint ids for the dataset - note the full list is needed",
    )
    linked_evals: Optional[List[str]] = Field(
        None,
        description="Updated list of unique evaluation run ids to be associated with this dataset",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Updated metadata to track for the dataset"
    )


class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str


class Status(Enum):
    pending = "pending"
    completed = "completed"


class UpdateRunResponse(BaseModel):
    evaluation: Optional[Dict[str, Any]] = Field(
        None, description="Database update success message"
    )
    warning: Optional[str] = Field(
        None,
        description="A warning message if the logged events don't have an associated datapoint id on the event metadata",
    )


class Datapoints(BaseModel):
    passed: Optional[List[str]] = None
    failed: Optional[List[str]] = None


class Detail(BaseModel):
    metric_name: Optional[str] = None
    metric_type: Optional[str] = None
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    aggregate: Optional[float] = None
    values: Optional[List[Union[float, bool]]] = None
    datapoints: Optional[Datapoints] = None


class Metrics(BaseModel):
    aggregation_function: Optional[str] = None
    details: Optional[List[Detail]] = None


class Metric1(BaseModel):
    name: Optional[str] = None
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    value: Optional[Union[float, bool]] = None
    passed: Optional[bool] = None


class Datapoint1(BaseModel):
    datapoint_id: Optional[str] = None
    session_id: Optional[str] = None
    passed: Optional[bool] = None
    metrics: Optional[List[Metric1]] = None


class ExperimentResultResponse(BaseModel):
    status: Optional[str] = None
    success: Optional[bool] = None
    passed: Optional[List[str]] = None
    failed: Optional[List[str]] = None
    metrics: Optional[Metrics] = None
    datapoints: Optional[List[Datapoint1]] = None


class Metric2(BaseModel):
    metric_name: Optional[str] = None
    event_name: Optional[str] = None
    metric_type: Optional[str] = None
    event_type: Optional[str] = None
    old_aggregate: Optional[float] = None
    new_aggregate: Optional[float] = None
    found_count: Optional[int] = None
    improved_count: Optional[int] = None
    degraded_count: Optional[int] = None
    same_count: Optional[int] = None
    improved: Optional[List[str]] = None
    degraded: Optional[List[str]] = None
    same: Optional[List[str]] = None
    old_values: Optional[List[Union[float, bool]]] = None
    new_values: Optional[List[Union[float, bool]]] = None


class EventDetail(BaseModel):
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    presence: Optional[str] = None


class OldRun(BaseModel):
    field_id: Optional[str] = Field(None, alias="_id")
    run_id: Optional[str] = None
    project: Optional[str] = None
    tenant: Optional[str] = None
    created_at: Optional[datetime] = None
    event_ids: Optional[List[str]] = None
    session_ids: Optional[List[str]] = None
    dataset_id: Optional[str] = None
    datapoint_ids: Optional[List[str]] = None
    evaluators: Optional[List[Dict[str, Any]]] = None
    results: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    passing_ranges: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    name: Optional[str] = None


class NewRun(BaseModel):
    field_id: Optional[str] = Field(None, alias="_id")
    run_id: Optional[str] = None
    project: Optional[str] = None
    tenant: Optional[str] = None
    created_at: Optional[datetime] = None
    event_ids: Optional[List[str]] = None
    session_ids: Optional[List[str]] = None
    dataset_id: Optional[str] = None
    datapoint_ids: Optional[List[str]] = None
    evaluators: Optional[List[Dict[str, Any]]] = None
    results: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    passing_ranges: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    name: Optional[str] = None


class ExperimentComparisonResponse(BaseModel):
    metrics: Optional[List[Metric2]] = None
    commonDatapoints: Optional[List[str]] = None
    event_details: Optional[List[EventDetail]] = None
    old_run: Optional[OldRun] = None
    new_run: Optional[NewRun] = None


class UUIDType(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, value: UUID):
        super().__init__()
        self._value = value

    @property
    def root(self) -> UUID:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"UUIDType({self._value})"


class EnvEnum(Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class CallType(Enum):
    chat = "chat"
    completion = "completion"


class SelectedFunction(BaseModel):
    id: Optional[str] = Field(None, description="UUID of the function")
    name: Optional[str] = Field(None, description="Name of the function")
    description: Optional[str] = Field(None, description="Description of the function")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameters for the function"
    )


class FunctionCallParams(Enum):
    none = "none"
    auto = "auto"
    force = "force"


class Parameters(BaseModel):
    model_config = ConfigDict(extra="allow")

    call_type: CallType = Field(
        ..., description='Type of API calling - "chat" or "completion"'
    )
    model: str = Field(..., description="Model unique name")
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, description="Model-specific hyperparameters"
    )
    responseFormat: Optional[Dict[str, Any]] = Field(
        None,
        description='Response format for the model with the key "type" and value "text" or "json_object"',
    )
    selectedFunctions: Optional[List[SelectedFunction]] = Field(
        None,
        description="List of functions to be called by the model, refer to OpenAI schema for more details",
    )
    functionCallParams: Optional[FunctionCallParams] = Field(
        None, description='Function calling mode - "none", "auto" or "force"'
    )
    forceFunction: Optional[Dict[str, Any]] = Field(
        None, description="Force function-specific parameters"
    )


class Type6(Enum):
    LLM = "LLM"
    pipeline = "pipeline"


class Configuration(BaseModel):
    field_id: Optional[str] = Field(
        None, alias="_id", description="ID of the configuration"
    )
    project: str = Field(
        ..., description="ID of the project to which this configuration belongs"
    )
    name: str = Field(..., description="Name of the configuration")
    env: Optional[List[EnvEnum]] = Field(
        None, description="List of environments where the configuration is active"
    )
    provider: str = Field(
        ..., description='Name of the provider - "openai", "anthropic", etc.'
    )
    parameters: Parameters
    type: Optional[Type6] = Field(
        None,
        description='Type of the configuration - "LLM" or "pipeline" - "LLM" by default',
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Details of user who created the configuration"
    )


class Parameters1(BaseModel):
    model_config = ConfigDict(extra="allow")

    call_type: CallType = Field(
        ..., description='Type of API calling - "chat" or "completion"'
    )
    model: str = Field(..., description="Model unique name")
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, description="Model-specific hyperparameters"
    )
    responseFormat: Optional[Dict[str, Any]] = Field(
        None,
        description='Response format for the model with the key "type" and value "text" or "json_object"',
    )
    selectedFunctions: Optional[List[SelectedFunction]] = Field(
        None,
        description="List of functions to be called by the model, refer to OpenAI schema for more details",
    )
    functionCallParams: Optional[FunctionCallParams] = Field(
        None, description='Function calling mode - "none", "auto" or "force"'
    )
    forceFunction: Optional[Dict[str, Any]] = Field(
        None, description="Force function-specific parameters"
    )


class PutConfigurationRequest(BaseModel):
    project: str = Field(
        ..., description="Name of the project to which this configuration belongs"
    )
    name: str = Field(..., description="Name of the configuration")
    provider: str = Field(
        ..., description='Name of the provider - "openai", "anthropic", etc.'
    )
    parameters: Parameters1
    env: Optional[List[EnvEnum]] = Field(
        None, description="List of environments where the configuration is active"
    )
    type: Optional[Type6] = Field(
        None,
        description='Type of the configuration - "LLM" or "pipeline" - "LLM" by default',
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Details of user who created the configuration"
    )


class Parameters2(BaseModel):
    model_config = ConfigDict(extra="allow")

    call_type: CallType = Field(
        ..., description='Type of API calling - "chat" or "completion"'
    )
    model: str = Field(..., description="Model unique name")
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, description="Model-specific hyperparameters"
    )
    responseFormat: Optional[Dict[str, Any]] = Field(
        None,
        description='Response format for the model with the key "type" and value "text" or "json_object"',
    )
    selectedFunctions: Optional[List[SelectedFunction]] = Field(
        None,
        description="List of functions to be called by the model, refer to OpenAI schema for more details",
    )
    functionCallParams: Optional[FunctionCallParams] = Field(
        None, description='Function calling mode - "none", "auto" or "force"'
    )
    forceFunction: Optional[Dict[str, Any]] = Field(
        None, description="Force function-specific parameters"
    )


class PostConfigurationRequest(BaseModel):
    project: str = Field(
        ..., description="Name of the project to which this configuration belongs"
    )
    name: str = Field(..., description="Name of the configuration")
    provider: str = Field(
        ..., description='Name of the provider - "openai", "anthropic", etc.'
    )
    parameters: Parameters2
    env: Optional[List[EnvEnum]] = Field(
        None, description="List of environments where the configuration is active"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        None, description="Details of user who created the configuration"
    )


class CreateRunRequest(BaseModel):
    project: str = Field(
        ..., description="The UUID of the project this run is associated with"
    )
    name: str = Field(..., description="The name of the run to be displayed")
    event_ids: List[UUIDType] = Field(
        ..., description="The UUIDs of the sessions/events this run is associated with"
    )
    dataset_id: Optional[str] = Field(
        None, description="The UUID of the dataset this run is associated with"
    )
    datapoint_ids: Optional[List[str]] = Field(
        None,
        description="The UUIDs of the datapoints from the original dataset this run is associated with",
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None, description="The configuration being used for this run"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the run"
    )
    status: Optional[Status] = Field(None, description="The status of the run")


class UpdateRunRequest(BaseModel):
    event_ids: Optional[List[UUIDType]] = Field(
        None, description="Additional sessions/events to associate with this run"
    )
    dataset_id: Optional[str] = Field(
        None, description="The UUID of the dataset this run is associated with"
    )
    datapoint_ids: Optional[List[str]] = Field(
        None, description="Additional datapoints to associate with this run"
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None, description="The configuration being used for this run"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the run"
    )
    name: Optional[str] = Field(None, description="The name of the run to be displayed")
    status: Optional[Status] = None


class DeleteRunResponse(BaseModel):
    id: Optional[UUIDType] = None
    deleted: Optional[bool] = None


class EvaluationRun(BaseModel):
    run_id: Optional[UUIDType] = Field(None, description="The UUID of the run")
    project: Optional[str] = Field(
        None, description="The UUID of the project this run is associated with"
    )
    created_at: Optional[datetime] = Field(
        None, description="The date and time the run was created"
    )
    event_ids: Optional[List[UUIDType]] = Field(
        None, description="The UUIDs of the sessions/events this run is associated with"
    )
    dataset_id: Optional[str] = Field(
        None, description="The UUID of the dataset this run is associated with"
    )
    datapoint_ids: Optional[List[str]] = Field(
        None,
        description="The UUIDs of the datapoints from the original dataset this run is associated with",
    )
    results: Optional[Dict[str, Any]] = Field(
        None,
        description="The results of the evaluation (including pass/fails and metric aggregations)",
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None, description="The configuration being used for this run"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the run"
    )
    status: Optional[Status] = None
    name: Optional[str] = Field(None, description="The name of the run to be displayed")


class CreateRunResponse(BaseModel):
    evaluation: Optional[EvaluationRun] = Field(
        None, description="The evaluation run created"
    )
    run_id: Optional[UUIDType] = Field(None, description="The UUID of the run created")


class GetRunsResponse(BaseModel):
    evaluations: Optional[List[EvaluationRun]] = None


class GetRunResponse(BaseModel):
    evaluation: Optional[EvaluationRun] = None
