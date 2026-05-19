"""Generate one Markdown reference page per public module under src/honeyhive.

This script is invoked by the mkdocs-gen-files plugin during `properdocs build`
and `properdocs serve`. It walks the source tree, emits a stub Markdown page
for each public module containing a single mkdocstrings `:::` directive, and
writes a SUMMARY.md so mkdocs-literate-nav can render the nav tree without
hand-maintenance.

Pages are generated for every public module so that cross-reference links
(``signature_crossrefs`` in properdocs.yml) resolve correctly even for modules
that are hidden from the sidebar.

Nav ordering and visibility
---------------------------
The ``honeyhive`` root module page appears first in the sidebar because it
documents all top-level exports (``HoneyHiveTracer``, ``trace``,
``enrich_span``, ``enrich_session``, ``evaluate``, ``HoneyHive``, etc.) —
the functions customers import most.

``NAV_PRIORITY_SECTIONS`` controls which sub-package sections appear next,
in order.  All other sections are shown after in alphabetical order.  Only
sections listed in ``NAV_HIDDEN_SECTIONS`` are omitted from the nav (pages
are still generated so cross-ref links keep working).

Within ``tracer/``, ``NAV_HIDDEN_TRACER_SUBS`` hides truly internal
sub-packages (no root-level exports, not referenced in product docs).  All
other tracer sub-packages remain visible because they contain functions
exported at the ``honeyhive`` or ``honeyhive.tracer`` level.

The ordering was derived by cross-referencing the product documentation at
https://docs.honeyhive.ai — modules that appear most prominently in customer-
facing tutorials, how-tos, and SDK reference pages are listed first.

Excluded from the reference site entirely (no page generated):
    - Underscore-prefixed modules and packages (private by convention),
      EXCEPT ``_generated/``, which contains the OpenAPI-generated request /
      response models we want surfaced to users.
    - ``__init__`` files are flattened into their parent package's page.
    - ``_generated/services/`` (raw HTTP wrappers; customers use
      ``honeyhive.api`` instead).
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

# ---------------------------------------------------------------------------
# Source layout
# ---------------------------------------------------------------------------

SRC_ROOT = Path("src")
PACKAGE = "honeyhive"

# ---------------------------------------------------------------------------
# Nav ordering & visibility
# ---------------------------------------------------------------------------

# The honeyhive root module page is shown first (rank -1 in _sort_key),
# then these sub-package sections in order.
# All other sections appear after in alphabetical order, UNLESS they
# are listed in NAV_HIDDEN_SECTIONS.
#
# Order rationale (from docs.honeyhive.ai prominence):
#   1. tracer      – HoneyHiveTracer.init, trace, enrich_span/session
#   2. experiments – evaluate(), compare_runs
#   3. api         – HoneyHive client (datasets, events, query)
#   4. models      – EventFilter, EventType, request/response models
NAV_PRIORITY_SECTIONS: tuple[str, ...] = (
    "tracer",
    "experiments",
    "api",
    "models",
)

# Top-level sections hidden from the nav entirely.  These are internal
# modules with no root-level exports and no references in product docs.
# Pages are still generated so cross-ref links keep working.
NAV_HIDDEN_SECTIONS: frozenset[str] = frozenset(
    {
        "cli",
        "config",
    }
)

# Tracer sub-packages hidden from the nav.  These are internal implementation
# details with no exports at the ``honeyhive`` or ``honeyhive.tracer`` level
# and no direct references in product docs.
NAV_HIDDEN_TRACER_SUBS: frozenset[str] = frozenset(
    {
        "infra",
        "utils",
    }
)


def _section(parts: tuple[str, ...]) -> str:
    """Return the top-level section name (e.g. 'tracer', 'api')."""
    return parts[1] if len(parts) > 1 else ""


def _sort_key(path: Path) -> tuple[int, str]:
    """Sort modules so the root package comes first, then priority sections."""
    parts = path.relative_to(SRC_ROOT).with_suffix("").parts
    # Flatten __init__ to match how we treat it in the nav (package page).
    if parts[-1] == "__init__":
        parts = parts[:-1]
    section = _section(parts)

    # Root honeyhive package page (from __init__.py) comes first.
    if not section:
        return (-1, path.as_posix())

    try:
        rank = NAV_PRIORITY_SECTIONS.index(section)
    except ValueError:
        rank = len(NAV_PRIORITY_SECTIONS)
    return (rank, path.as_posix())


def _is_nav_visible(parts: tuple[str, ...]) -> bool:
    """Return True if a module should appear in the sidebar navigation."""
    section = _section(parts)

    # Hide explicitly excluded top-level sections.
    if section in NAV_HIDDEN_SECTIONS:
        return False

    # Within tracer/, hide truly internal sub-packages.
    if section == "tracer" and len(parts) > 2 and parts[2] in NAV_HIDDEN_TRACER_SUBS:
        return False

    return True


# ---------------------------------------------------------------------------
# Generate pages + nav
# ---------------------------------------------------------------------------

nav = mkdocs_gen_files.Nav()

for path in sorted((SRC_ROOT / PACKAGE).rglob("*.py"), key=_sort_key):
    # Convert e.g. src/honeyhive/api/client.py -> ("honeyhive", "api", "client")
    module_path = path.relative_to(SRC_ROOT).with_suffix("")
    parts: tuple[str, ...] = tuple(module_path.parts)

    # Flatten package __init__.py into the package itself.
    if parts[-1] == "__init__":
        parts = parts[:-1]
        if not parts:
            continue  # top-level src/__init__.py, skip

    # Skip private modules and dunder files. The single exception is
    # `_generated`: it holds the OpenAPI-generated request/response models
    # which are part of the public API surface even though the package name
    # is underscore-prefixed.
    if any(p.startswith("_") and p != "_generated" for p in parts):
        continue

    # Skip _generated/services/. These are HTTP service-call wrappers around
    # the OpenAPI client; the public surface customers consume is the high-
    # level honeyhive.api.client (and its async counterpart), not the raw
    # service modules. Excluding them keeps the reference site focused on
    # the request/response models, which is what customers actually read.
    if parts[1:3] == ("_generated", "services"):
        continue

    # Output path under docs/: reference/honeyhive/api/client.md
    doc_path = Path(*parts).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    # --- Nav entry (only for customer-facing modules) ---
    if _is_nav_visible(parts):
        nav_parts = parts[1:] if len(parts) > 1 else parts
        nav[nav_parts] = doc_path.as_posix()

    # --- Page (always generated, even for hidden modules) ---
    identifier = ".".join(parts)
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(
            f"---\ntitle: {identifier}\n---\n\n# `{identifier}`\n\n::: {identifier}\n"
        )

# Write the literate-nav summary so the nav tree mirrors the package layout.
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as fd:
    fd.writelines(nav.build_literate_nav())
