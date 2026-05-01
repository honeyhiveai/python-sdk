"""Generate one Markdown reference page per public module under src/honeyhive.

This script is invoked by the mkdocs-gen-files plugin during `properdocs build`
and `properdocs serve`. It walks the source tree, emits a stub Markdown page
for each public module containing a single mkdocstrings `:::` directive, and
writes a SUMMARY.md so mkdocs-literate-nav can render the nav tree without
hand-maintenance.

Excluded from the generated reference:
    - Underscore-prefixed modules and packages (private by convention),
      EXCEPT `_generated/`, which contains the OpenAPI-generated request /
      response models we want surfaced to users (revisit if too noisy).
    - `__init__` files are flattened into their parent package's page.
"""

from pathlib import Path

import mkdocs_gen_files

# Resolve the SDK source root relative to this script. mkdocs-gen-files runs
# with the cwd set to the project root (where properdocs.yml lives), which
# is also python/sdks/python-sdk/, so a relative path here is correct.
SRC_ROOT = Path("src")
PACKAGE = "honeyhive"

nav = mkdocs_gen_files.Nav()

for path in sorted((SRC_ROOT / PACKAGE).rglob("*.py")):
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

    # Build the nav entry. Strip the top-level package name so the nav reads
    # "api > client" rather than "honeyhive > api > client" (the section
    # itself is already labeled "Reference" in properdocs.yml).
    nav_parts = parts[1:] if len(parts) > 1 else parts
    nav[nav_parts] = doc_path.as_posix()

    identifier = ".".join(parts)
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        # Emit a YAML `title:` so the browser tab and nav entries show the
        # full dotted module path. Without this, mkdocs falls back to the
        # filename (e.g. "base") because the inline-code backticks in the
        # h1 below confuse its title-extraction heuristic.
        fd.write(
            f"---\ntitle: {identifier}\n---\n\n"
            f"# `{identifier}`\n\n::: {identifier}\n"
        )

# Write the literate-nav summary so the nav tree mirrors the package layout.
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as fd:
    fd.writelines(nav.build_literate_nav())
