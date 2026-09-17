"""The API key and API URL are read and resolved in exactly the places that should.

``honeyhive.config.resolved`` owns the variable names, the precedence, and the
alternates; only the three entry points that send requests call
``ResolvedConfig.resolve``; and nothing outside the module calls the
environment helpers the config models use as ``default_factory``. Any other
read or resolution would reintroduce the divergence the module exists to
remove, so these tests scan the package source, generated code included. The
alternates are undocumented, so the scan for them also covers the examples and
the README, which reach the same readers.

The scan matches literal names. A variable name built at runtime is outside
its reach; the one such reader, ``_try_environment_variable_access`` in
``tracer/core/config_interface.py``, is pinned by its own unit test instead.
"""

import re
from pathlib import Path
from typing import Iterable, List, Tuple

import honeyhive
from honeyhive.config import resolved

PACKAGE_ROOT = Path(honeyhive.__file__).resolve().parent
OWNER = Path(resolved.__file__).resolve()

# This file sits at tests/unit/ under the package repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
# Ships beside the package and teaches variable names to the same readers.
SHIPPED_PROSE = (REPO_ROOT / "examples", REPO_ROOT / "README.md")
SCANNED_SUFFIXES = (".py", ".md")

PREFERRED = ("HH_API_KEY", "HH_INGESTION_API_KEY", "HH_API_URL")
ALTERNATES = ("HONEYHIVE_API_KEY", "HONEYHIVE_SERVER_URL", "HH_SERVER_URL")
ENVIRONMENT_HELPERS = (
    "environment_api_key",
    "environment_ingestion_api_key",
    "environment_api_url",
)

# The entry points that send requests to HoneyHive on their own; each resolves
# once and passes the result down.
ENTRY_POINTS = frozenset({"api/client.py", "cli/main.py", "tracer/core/base.py"})

# os.getenv("X"), os.environ.get("X"), os.environ["X"], and the same after a
# ``from os import getenv`` or ``from os import environ``; either quote, any
# whitespace or line break inside the call.
_READ = re.compile(
    r"(?<![\w.])(?:os\.)?(?:getenv|environ\.get|environ)\s*[(\[]\s*"
    r"['\"](?P<name>[A-Z_]+)['\"]"
)
_RESOLVE = re.compile(r"(?P<name>ResolvedConfig\.resolve)\(")
# A call, not the bare reference a ``default_factory=`` declaration makes.
_HELPER_CALL = re.compile(
    r"(?P<name>environment_api_key|environment_ingestion_api_key|environment_api_url)\("
)
_ALTERNATE = re.compile(
    r"(?P<name>HONEYHIVE_API_KEY|HONEYHIVE_SERVER_URL|HH_SERVER_URL)"
)


def _files(root: Path) -> Iterable[Path]:
    """The scannable files under ``root``, or ``root`` itself when it is a file."""
    assert root.exists(), f"{root} is missing, so the scan would cover nothing"
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*") if p.suffix in SCANNED_SUFFIXES)


def _label(path: Path) -> str:
    """Package-relative inside the package, repository-relative otherwise."""
    for base in (PACKAGE_ROOT, REPO_ROOT):
        if path.is_relative_to(base):
            return str(path.relative_to(base))
    return str(path)


def _offending_lines(
    names: Tuple[str, ...],
    pattern: re.Pattern,
    roots: Tuple[Path, ...] = (PACKAGE_ROOT,),
) -> List[str]:
    """Every match whose ``name`` group is in ``names``, as ``path:line: text``.

    The whole file is searched, so a call the formatter wrapped across lines
    is still seen.
    """
    found = []
    for root in roots:
        for path in _files(root):
            if path.resolve() == OWNER:
                continue
            text = path.read_text()
            lines = text.splitlines()
            for match in pattern.finditer(text):
                if match.group("name") in names:
                    number = text.count("\n", 0, match.start()) + 1
                    found.append(
                        f"{_label(path)}:{number}: {lines[number - 1].strip()}"
                    )
    return found


def test_preferred_variables_are_read_only_by_the_resolver() -> None:
    """No getenv / environ read of HH_API_KEY or HH_API_URL outside the owner."""
    offenders = _offending_lines(PREFERRED, _READ)
    assert not offenders, offenders


def test_alternate_names_appear_only_in_the_resolver() -> None:
    """No other file names an alternate, examples and README included."""
    offenders = _offending_lines(
        ALTERNATES, _ALTERNATE, roots=(PACKAGE_ROOT, *SHIPPED_PROSE)
    )
    assert not offenders, offenders


def test_only_the_entry_points_resolve() -> None:
    """Everything below an entry point receives resolved values instead of resolving."""
    callers = {
        line.split(":", 1)[0]
        for line in _offending_lines(("ResolvedConfig.resolve",), _RESOLVE)
    }
    assert callers == ENTRY_POINTS, sorted(callers ^ ENTRY_POINTS)


def test_nothing_calls_the_environment_helpers() -> None:
    """The factories are referenced by the config models, never called elsewhere.

    A direct call would be a fourth place that resolves from the environment.
    """
    offenders = _offending_lines(ENVIRONMENT_HELPERS, _HELPER_CALL)
    assert not offenders, offenders
