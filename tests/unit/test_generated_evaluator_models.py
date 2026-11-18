"""Generated evaluator models preserve definition and criteria variants."""

from typing import Union

import pytest
from pydantic import TypeAdapter, ValidationError

from honeyhive._generated.models.CreateEvaluatorRequest import CreateEvaluatorRequest
from honeyhive._generated.models.EvaluatorDefinition import EvaluatorDefinition
from honeyhive._generated.models.EvaluatorTestCriteria import EvaluatorTestCriteria
from honeyhive._generated.models.HumanEvaluatorDefinition import (
    HumanEvaluatorDefinition,
)
from honeyhive._generated.models.LLMEvaluatorDefinition import LLMEvaluatorDefinition
from honeyhive._generated.models.PythonEvaluatorDefinition import (
    PythonEvaluatorDefinition,
)


@pytest.mark.parametrize(
    ("kind", "model"),
    [
        ("python", PythonEvaluatorDefinition),
        ("llm", LLMEvaluatorDefinition),
        ("human", HumanEvaluatorDefinition),
    ],
)
def test_definition_accepts_matching_model_and_round_trips(
    kind: str,
    model: type[
        Union[
            PythonEvaluatorDefinition, LLMEvaluatorDefinition, HumanEvaluatorDefinition
        ]
    ],
) -> None:
    config: dict[str, object] = {
        "name": "Example",
        "metadata": {},
        "score_schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"score": {"type": "number"}},
            "required": ["score"],
            "additionalProperties": False,
        },
    }
    if kind != "human":
        config.update(
            sampling={"sampling_percentage": 100},
            filters={
                "filterArray": [
                    {
                        "field": "event_type",
                        "operator": "is",
                        "value": "model",
                        "type": "string",
                    }
                ]
            },
        )
    if kind == "python":
        config["code_execution"] = {"code_snippet": "return {'score': 1}"}
    if kind == "llm":
        config.update(
            model={"model_provider": "example", "model_name": "example"},
            llm_execution={"system_prompt": "Return a score."},
        )
    raw = {"type": kind, kind: config}
    definition = TypeAdapter(EvaluatorDefinition).validate_python(raw)
    assert isinstance(definition, model)
    request = CreateEvaluatorRequest(slug="example", definition=definition)
    assert request.definition is definition
    assert request.model_dump(exclude_none=True)["definition"] == raw


@pytest.mark.parametrize(
    ("kind", "operator", "operands", "expected"),
    [
        ("numeric", "lt", {"value": 1}, "NumericLtTestCriteria"),
        ("categorical", "gt", {"value": 1}, "CategoricalNumericGtTestCriteria"),
        ("boolean", "is_false", {}, "BooleanIsFalseTestCriteria"),
        (
            "string",
            "eq",
            {"value": "example", "case_sensitive": True},
            "StringEqTestCriteria",
        ),
    ],
)
def test_criteria_selects_matching_variant(
    kind: str, operator: str, operands: dict[str, object], expected: str
) -> None:
    criteria = {"type": kind, "operator": operator, **operands}
    result = EvaluatorTestCriteria.model_validate(
        {"field": "score", "criteria": criteria}
    )
    assert type(result.criteria).__name__ == expected
    assert result.criteria.model_dump() == criteria


@pytest.mark.parametrize(
    "criteria",
    [
        {"type": "unknown", "operator": "gt", "value": 1},
        {"type": "numeric", "operator": "unknown", "value": 1},
        {"type": "boolean", "operator": "gt", "value": 1},
    ],
)
def test_criteria_rejects_invalid_tags(criteria: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        EvaluatorTestCriteria.model_validate({"field": "score", "criteria": criteria})


def test_definition_rejects_unknown_and_mismatched_tags() -> None:
    adapter = TypeAdapter(EvaluatorDefinition)
    for value in [{"type": "unknown"}, {"type": "python", "human": {}}]:
        with pytest.raises(ValidationError):
            adapter.validate_python(value)
