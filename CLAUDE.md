# CLAUDE.md

## 0. Meta
- Always start in **Plan Mode** (`Shift+Tab` twice) unless I say “EXECUTE NOW”.
- Never modify files outside `src/` and `tests/` without explicit instruction.
- Use the Task Templates in §4.

## 1. Repo Map (Read-Only vs Writable)

- Writable:  `tests/`, `scripts/`

For `src/honeyhive`:

1. Claude can't touch any of the auto-generated files living inside `src/`
2. Within `src/honeyhive`, Claude can only touch the files in these directories
- `cli/`
- `evaluation/`
- `tracer/`
-  `utils/` except it can't touch those that have `DO NOT EDIT` at the beginning


## 2. Workflow Guardrails
- Before any edit: output a granular TODO checklist.
- Run the relevant tests after code changes (unless doc-only).

The documentation on how to run tests is specified in `tests/README.md`.


## 3. Context Hygiene
- When task switches, emit:
```
### RESET CONTEXT

Task: <desc>  
Assumptions to carry over: <list or none>
```
- Do NOT assume prior instructions.


## 4. Task Templates
### 4.1 Bug Fix Template
1. Identify failing test or reproduce
2. Hypothesis + patch plan
3. Edit minimal files
4. Run tests
5. Summarize diff & next steps

### 4.2 Feature Slice Template (Python)
1. API surface
2. Types & dataclasses
3. Tests
4. Docs & changelog
5. Integrations


## 5. Parallelism Rules
- Single-file change => no sub-agents.
- Multi-file feature => up to 7 Tasks (see Feature Implementation Guidelines).
- Combine tiny config/doc edits into Task 7.

## 6. Memory Notes Protocol

- After significant edit, append notes to `/ai/memory/<file>.md`:
    - Naming patterns, tricky deps, gotchas

## 7. Development Setup Instructions

When making changes to the HoneyHive Python SDK:

1. **Uninstall existing package**: `pip3 uninstall honeyhive -y`
2. **Install local version in editable mode**: `pip3 install -e .`

This ensures that tests use the local codebase changes instead of the installed pip package.

## 8. Release and Documentation Protocol

**ALWAYS update CHANGELOG.md** after:
- Running `./scripts/publish.sh` 
- Completing any project that changes functionality
- Making any user-facing changes

Keep changelog entries concise and focus on user impact.
