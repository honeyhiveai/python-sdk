# Auto-Generate Python SDK Reference Documentation

## Objective
Analyze the HoneyHive Python SDK source code and generate/update reference documentation in MDX format. Only update documentation when there are meaningful changes to avoid unnecessary commits.

## Context
- **SDK Location**: `src/honeyhive/` (focus on `tracer/`, `evaluation/`, core SDK files)
- **Docs Location**: `sdk-reference/python-*.mdx` files in another github repo
- **Current Version**: Extract from `pyproject.toml`
- **Existing Style**: Analyze existing `.mdx` files for formatting patterns

## Tasks

### 1. Source Code Analysis
Scan these key files and extract API information:
- `src/honeyhive/tracer/__init__.py` → `python-tracer-ref.mdx`
- `src/honeyhive/evaluation/` → `python-experiments-ref.mdx` 
- `src/honeyhive/sdk.py` → `python-sdk-ref.mdx`
- Core modules: `events.py`, `datasets.py`, `configurations.py`, etc.

For each class/function, extract:
- Class/function signatures with type hints
- Docstrings (Google/NumPy/Sphinx format)
- Parameters with types and descriptions
- Return types and descriptions
- Raises/Exceptions
- Usage examples from docstrings or comments
- Static/class methods vs instance methods

### 2. Documentation Generation Rules

**Format Requirements:**
- Generate MDX format matching existing style
- Use existing frontmatter structure (title, description, icon)
- Maintain consistent heading hierarchy (##, ###, ####)
- Preserve code block formatting with proper language tags
- Include parameter tables when there are 3+ parameters

**Content Structure:**
- Start with class/module overview
- List key attributes and their types
- Document methods in logical order (init, core methods, utilities)
- Include practical examples for each major method
- Add Notes/Warnings for important behaviors
- Cross-reference related methods/classes

**Example Extraction:**
- Look for example code in docstrings
- Generate minimal working examples for core methods
- Ensure examples use realistic parameter values
- Include both basic and advanced usage patterns

### 3. Change Detection Strategy
Before updating documentation:
- Compare method signatures between current docs and source
- Check for new/removed/modified methods
- Detect parameter changes (names, types, defaults)
- Identify docstring updates
- Only generate new docs if meaningful changes detected

### 4. Specific Documentation Patterns

**For Classes:**
```markdown
## ClassName

Brief description from class docstring.

### Attributes
- **attr_name** (`type`): Description

### Methods

#### `method_name`
Description from docstring.

**Parameters**:
- **param** (`type`, optional): Description (default: value)

**Returns**: `return_type` - Description

**Example**:
```python
# Working code example
```
```

**For Functions:**
Follow similar pattern but without class structure.

### 5. Version and Metadata Handling
- Extract version from `pyproject.toml` 
- Add "Last Updated" timestamp to generated files
- Include link to source code on GitHub
- Reference current commit hash for traceability

### 6. Error Handling
- Log warnings for missing docstrings
- Handle malformed type hints gracefully  
- Provide fallback descriptions for undocumented parameters
- Skip private methods (starting with `_`) unless explicitly documented

### 7. Output Requirements
Generate these files in `sdk-reference/`:
- `python-tracer-ref.mdx` (HoneyHiveTracer, @trace, @atrace, enrich_*)
- `python-sdk-ref.mdx` (HoneyHive client, core SDK methods)
- `python-experiments-ref.mdx` (evaluation module)
- `python-logger-ref.mdx` (if logging utilities exist)

### 8. Quality Checks
- Validate MDX syntax
- Ensure all public methods are documented
- Check that examples are syntactically correct
- Verify cross-references resolve correctly
- Maintain consistency with existing documentation tone

## Execution Notes
- Run as GitHub Action on `schedule` (daily) and `push` to main
- Only commit changes if documentation actually differs
- Use clear commit messages: "docs: auto-update Python SDK reference (v0.2.56)"
- Consider creating PR instead of direct commit for review
