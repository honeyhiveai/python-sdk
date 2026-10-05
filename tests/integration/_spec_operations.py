"""What the Data Plane OpenAPI spec declares, and which of its operations the shim calls.

The spec-driven key suites and the twin wrapper check compare these two
sources. Each operation in the spec declares the one security scheme, and so
the one kind of key, it takes. The shim calls a generated service function per
operation it wraps, and the function's name is the operation's operationId.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterator, Optional

import pytest
import yaml

from honeyhive.api import client as client_module

# A symlink into the monorepo's generated spec; it resolves in a monorepo
# checkout and dangles in an image built from the package directory alone.
SPEC_PATH = Path(__file__).resolve().parents[2] / "openapi" / "dataplane.yaml"
CLIENT_SOURCE = Path(client_module.__file__)

# `<alias>_svc.<operation>(` or the `_svc_async` twin: a shim call into a
# generated service function, whose name is the spec's operationId.
_SERVICE_CALL = re.compile(
    r"\b[a-z_]+_svc(?P<asynchronous>_async)?\.(?P<operation>[A-Za-z_]+)\("
)


def require_spec() -> None:
    """Fail in CI, skip elsewhere, when the spec symlink does not resolve.

    A skip in CI would hide the guard, which is how a dangling link in a test
    image went unnoticed once.
    """
    if SPEC_PATH.exists():
        return
    message = f"{SPEC_PATH} does not resolve, so the spec guard cannot run"
    if os.environ.get("CI"):
        pytest.fail(message)
    pytest.skip(message)


def _spec_operations() -> Iterator[Dict[str, Any]]:
    with SPEC_PATH.open(encoding="utf-8") as handle:
        spec = yaml.safe_load(handle)
    for path_item in spec["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                yield operation


def spec_operations_declaring(scheme: str) -> FrozenSet[str]:
    """The operationIds whose ``security`` names ``scheme``."""
    return frozenset(
        operation["operationId"]
        for operation in _spec_operations()
        if any(scheme in requirement for requirement in operation.get("security") or [])
    )


def spec_client_facing_twins() -> Dict[str, str]:
    """Each twin pair the TypeScript SDK emits, as flat operationId to scoped operationId.

    The flat arm of a pair carries ``x-twin``, whose ``op`` names the scoped
    arm. A pair the TypeScript SDK excludes is not offered by any client.
    """
    return {
        operation["operationId"]: operation["x-twin"]["op"]
        for operation in _spec_operations()
        if "x-twin" in operation and operation.get("x-ts-sdk-exclude") is not True
    }


def shim_operations(*, asynchronous: Optional[bool] = None) -> FrozenSet[str]:
    """The operations the shim calls a generated service function for.

    Args:
        asynchronous: True for the calls into the async services only, False
            for the sync services only, None for both.
    """
    return frozenset(
        match.group("operation")
        for match in _SERVICE_CALL.finditer(CLIENT_SOURCE.read_text())
        if asynchronous is None
        or (match.group("asynchronous") is not None) == asynchronous
    )


def data_plane_url() -> str:
    """The Data Plane URL the live tests target."""
    return os.environ.get("HH_API_URL", "https://api.dp1.us.honeyhive.ai")
