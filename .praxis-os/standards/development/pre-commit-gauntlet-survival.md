# Pre-Commit Gauntlet: Survival Protocol

**Keywords for search**: pre-commit hooks, commit failures, black formatting, isort imports, pylint errors, unit test failures, integration tests, changelog requirements, feature-list-sync, documentation-compliance, yamllint validation, no-mocks-integration, pre-commit preparation, commit checklist, hook order, gauntlet failures, pre-flight protocol, adversarial design, commit rejection, formatting checks, linter checks, test coverage requirements, CHANGELOG.md update, features.md validation, best-practices.md requirements, git commit protocol, pre-commit hook sequence, how to pass pre-commit checks, prevent commit failures, pre-commit debugging, hook-specific errors

---

## 🚨 TL;DR - Pre-Commit Gauntlet Quick Reference

**Core Philosophy:** The pre-commit gauntlet is **INTENTIONALLY ADVERSARIAL**. Hooks will reject your commit. This standard teaches you to **PREPARE, not bypass**.

**Pre-Flight Protocol (Query and Execute BEFORE `git commit`):**
1. **Format code:** `black <files> && isort <files>`
2. **Check quality:** `pylint <files>` (fix all issues)
3. **Run tests:** `tox -e unit` or `pytest tests/unit/` (all must pass)
4. **Update CHANGELOG.md** if changes are significant
5. **Verify required files exist:** `.praxis-os/workspace/product/features.md`, `.praxis-os/standards/universal/best-practices.md`
6. **Query standards:** `pos_search_project(action="search_standards", query="relevant topic")` to validate approach

**The Gauntlet Sequence (9 Hooks, Order Matters):**
1. **yamllint** - YAML syntax validation
2. **no-mocks-integration** - Integration tests must not use mocks
3. **black** + **isort** - Code formatting check (NOT auto-fix in hook)
4. **pylint** + **mypy** - Code quality and type checking
5. **unit tests** - All unit tests must pass, 80%+ coverage per file
6. **integration tests** - Real API validation (no mocks)
7. **docs-build-check** - Documentation must build without errors
8. **feature-list-sync** - Requires `.praxis-os/workspace/product/features.md`
9. **documentation-compliance** - Significant changes require CHANGELOG.md update

**Common Failures & Fixes:**
- **Black/isort failure:** Run `black src tests && isort src tests` (NOT `--check`)
- **Pylint failure:** Fix actual issues (C0301 line length, E1101 no-member, etc.)
- **Unit test failure:** Run `tox -e unit` locally first, fix failures
- **CHANGELOG.md required:** Add entry under `## [Unreleased]` section
- **feature-list-sync failure:** File missing → Restore from git history or use `SKIP=feature-list-sync git commit`
- **Integration test failure:** Check `server_url` allows localhost, verify API credentials

**Emergency Bypass (RARE, requires justification):**
```bash
SKIP=hook-name git commit -m "message"
# Example: SKIP=feature-list-sync git commit -m "fix: pre-commit migration"
```

**Anti-Patterns (DON'T DO THIS):**
- ❌ `git commit --no-verify` (FORBIDDEN - see best-practices.md)
- ❌ Skipping hooks without understanding why they failed
- ❌ Committing without running formatters first
- ❌ Ignoring CHANGELOG.md requirement for significant changes
- ❌ Running `black --check` instead of `black` (hook checks, you fix)

**When to Query This Standard:**
- Before any commit → `pos_search_project(action="search_standards", query="pre-commit preparation checklist")`
- After hook failure → `pos_search_project(action="search_standards", query="pre-commit hook-name failure fix")`
- Understanding hook order → `pos_search_project(action="search_standards", query="pre-commit gauntlet sequence order")`

---

## ❓ Questions This Answers

1. "What is the pre-commit gauntlet?"
2. "How do I prepare for committing code?"
3. "What order do pre-commit hooks run in?"
4. "Why did my black/isort check fail?"
5. "How to fix pylint errors before committing?"
6. "What does feature-list-sync check for?"
7. "When do I need to update CHANGELOG.md?"
8. "Can I skip pre-commit hooks?"
9. "What is the pre-flight protocol before git commit?"
10. "How to run formatters before committing?"
11. "What test coverage is required?"
12. "Why is the gauntlet adversarial?"
13. "How to debug pre-commit hook failures?"
14. "What files does feature-list-sync require?"
15. "How to handle integration test failures in pre-commit?"
16. "What is documentation-compliance checking for?"
17. "Why did yamllint fail?"
18. "How to fix no-mocks-integration errors?"
19. "What is the emergency bypass for hooks?"
20. "When is SKIP=hook-name justified?"
21. "How to check if CHANGELOG.md update is needed?"
22. "What are pre-commit anti-patterns?"
23. "Why does the gauntlet reject my commit?"
24. "How to verify all hooks will pass before committing?"
25. "What is the relationship between pre-commit and adversarial design?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Before any commit** | `pos_search_project(action="search_standards", query="pre-commit preparation checklist")` |
| **After hook failure** | `pos_search_project(action="search_standards", query="pre-commit black failure fix")` |
| **Understanding sequence** | `pos_search_project(action="search_standards", query="pre-commit gauntlet hook order")` |
| **CHANGELOG requirement** | `pos_search_project(action="search_standards", query="when to update changelog for commits")` |
| **Hook bypass justification** | `pos_search_project(action="search_standards", query="when to skip pre-commit hooks")` |
| **Formatting errors** | `pos_search_project(action="search_standards", query="fix black isort formatting before commit")` |
| **Test failures** | `pos_search_project(action="search_standards", query="pre-commit unit test coverage requirements")` |
| **Missing files** | `pos_search_project(action="search_standards", query="feature-list-sync required files missing")` |

---

## 🎯 What Is the Pre-Commit Gauntlet?

The pre-commit gauntlet is a **9-hook validation sequence** that runs automatically before every `git commit`. It is **intentionally adversarial** - designed to reject commits that don't meet quality standards.

**Design Philosophy:**
- **Adversarial by Design:** Hooks will find issues and reject your commit
- **Behavioral Engineering:** Forces preparation, not shortcuts
- **Quality Gate:** Only production-ready code passes
- **No Bypass Culture:** `--no-verify` is forbidden (see best-practices.md)

**Why This Matters:**
- Prevents broken code from entering git history
- Enforces consistent code quality across all commits
- Catches issues at commit time (cheapest point to fix)
- Teaches preparation over reaction

**The Reality:**
You will fail hooks. That's the point. This standard teaches you to **prepare so failures are rare**, not to bypass when they happen.

---

## 🛡️ Pre-Flight Protocol: What to Do BEFORE `git commit`

**CRITICAL:** Run these steps BEFORE attempting to commit. The gauntlet checks, it doesn't fix.

### Step 1: Format Your Code

**Run formatters (NOT checks):**
```bash
# Format Python files
black src tests

# Sort imports
isort src tests
```

**Why this matters:**
- Pre-commit hooks run `black --check` and `isort --check` (read-only)
- Hooks will FAIL if files aren't formatted
- You must format BEFORE committing

**Common mistake:**
```bash
# ❌ WRONG - This just checks, doesn't fix
black --check src tests

# ✅ RIGHT - This formats files
black src tests
```

### Step 2: Check Code Quality

**Run linters locally:**
```bash
# Check with pylint
pylint src/path/to/modified/files.py

# Check types (if mypy configured)
mypy src/path/to/modified/files.py
```

**Fix all issues before committing:**
- `C0301: Line too long` - Reformat or add `# pylint: disable=line-too-long` if justified
- `E1101: Instance has no member` - Add `# pylint: disable=no-member` if Pydantic/dynamic
- `W0212: Access to protected member` - Refactor or justify with disable comment

**When to query:**
```python
# Understanding specific pylint errors
pos_search_project(action="search_standards", query="pylint error C0301 line too long fix")
```

### Step 3: Run Tests Locally

**Unit tests (MUST pass):**
```bash
# Fast parallel execution
tox -e unit

# Or direct pytest
pytest tests/unit/

# Check coverage (80%+ required per file)
pytest --cov=src/path/to/modified/ tests/unit/test_modified.py
```

**Integration tests (if modified integration code):**
```bash
# Parallel execution
tox -e integration-parallel

# Or direct pytest
pytest tests/integration/
```

**Coverage requirement:**
- Each file must have **80%+ test coverage**
- Pre-commit will fail if coverage drops below threshold
- Add tests BEFORE committing, not after

### Step 4: Update CHANGELOG.md (If Significant Changes)

**When CHANGELOG update is required:**
- ✅ New features
- ✅ Bug fixes visible to users
- ✅ Breaking changes
- ✅ API changes
- ✅ Behavior changes
- ❌ Typo fixes in comments
- ❌ Internal refactoring (no external impact)
- ❌ Test-only changes

**How to update:**
```markdown
## [Unreleased]

### Added
- **✨ Feature: Description of new feature**
  - Bullet points with details
  - Technical specifics

### Fixed
- **🐛 Fix: Description of bug fix**
  - What was broken
  - How it's fixed

### Changed
- **⚙️ Change: Description of change**
  - What changed
  - Why it changed
```

**When to query:**
```python
pos_search_project(action="search_standards", query="when to update changelog for commits")
pos_search_project(action="search_standards", query="changelog entry format structure")
```

### Step 5: Verify Required Files Exist

**Required by feature-list-sync hook:**
- `.praxis-os/workspace/product/features.md` (734 lines)
- `.praxis-os/standards/universal/best-practices.md` (390 lines)

**If files missing:**
```bash
# Check if files exist
ls -la .praxis-os/workspace/product/features.md
ls -la .praxis-os/standards/universal/best-practices.md

# If missing, recover from git history
git log --all --full-history -- ".agent-os/product/features.md"
git show <commit-hash>:.agent-os/product/features.md > .praxis-os/workspace/product/features.md

# Or skip hook (requires justification)
SKIP=feature-list-sync git commit -m "fix: restore missing praxis-os docs"
```

### Step 6: Query Standards for Validation

**Before committing, validate your approach:**
```python
# Example: Committing a new feature
pos_search_project(action="search_standards", query="feature implementation completion checklist")

# Example: Fixing a bug
pos_search_project(action="search_standards", query="bug fix testing requirements")

# Example: Refactoring code
pos_search_project(action="search_standards", query="refactoring without breaking changes")
```

---

## 🎢 The Gauntlet: 9 Hooks in Sequence

Pre-commit hooks run in this **EXACT ORDER**. A failure at any step stops the sequence.

### Hook 1: yamllint

**What it checks:** YAML file syntax and style

**Common failures:**
- Trailing spaces
- Missing document start (`---`)
- Line length violations
- Indentation errors

**How to fix:**
```bash
# Check YAML files
yamllint .praxis-os/config/mcp.yaml

# Fix issues manually or configure .yamllint
```

**Configuration:** `.yamllint` in project root
- `line-length`: 200 characters
- `document-start`: disable warnings

### Hook 2: no-mocks-integration

**What it checks:** Integration tests must not use mocks

**Why it matters:** Integration tests validate real API behavior, not mocked behavior

**Common violations:**
```python
# ❌ WRONG - Mock in integration test
from unittest.mock import patch

def test_integration_with_mock():
    with patch("honeyhive.client.Client") as mock:
        # This will fail pre-commit
        pass

# ✅ RIGHT - Real API call
def test_integration_real_api():
    client = HoneyHive(api_key=os.getenv("HH_API_KEY"))
    result = client.some_method()
    assert result
```

**How to fix:**
- Remove mocks from `tests/integration/**`
- Use real API credentials from `.env`
- If test requires mocking, it's a **unit test**, not integration

### Hook 3: black (Code Formatting Check)

**What it checks:** Python files formatted with Black

**Common failures:**
```
would reformat src/honeyhive/experiments/models.py
```

**How to fix:**
```bash
# Format files (NOT --check)
black src tests

# Verify formatting
black --check src tests
```

**Why it fails:**
- You ran `black --check` instead of `black`
- Files modified after formatting
- Black version mismatch (use project's Black version)

### Hook 4: isort (Import Sorting Check)

**What it checks:** Python imports sorted correctly

**Common failures:**
```
ERROR: /path/to/file.py Imports are incorrectly sorted
```

**How to fix:**
```bash
# Sort imports (NOT --check-only)
isort src tests

# Verify sorting
isort --check-only src tests
```

**Configuration:** `pyproject.toml` - isort settings

### Hook 5: pylint (Code Quality Check)

**What it checks:** Code quality, style, potential bugs

**Common failures:**
- `C0301: Line too long (X/Y)` - Line exceeds max length
- `E1101: Instance of 'X' has no 'Y' member` - Pylint doesn't recognize dynamic attributes
- `W0212: Access to protected member '_X'` - Accessing private/protected attributes
- `R0913: Too many arguments (X/5)` - Function has too many parameters

**How to fix:**

```python
# Line too long - Reformat or disable
result = some_very_long_function_call(
    arg1, arg2, arg3
)  # Reformat to multiple lines

# OR (if justified)
result = some_function(arg1, arg2)  # pylint: disable=line-too-long

# Dynamic attribute (Pydantic models)
self.metrics.get_metric("accuracy")  # pylint: disable=no-member

# Protected member access (if intentional)
obj._private_method()  # pylint: disable=protected-access
```

**When to query:**
```python
pos_search_project(action="search_standards", query="pylint error code fix patterns")
```

### Hook 6: mypy (Type Checking)

**What it checks:** Type annotations correctness

**Common failures:**
- Missing type annotations
- Incompatible types
- Unresolved imports

**How to fix:**
- Add type hints: `def function(arg: str) -> int:`
- Use `# type: ignore` if type checker is wrong
- Check `pyproject.toml` mypy configuration

### Hook 7: unit (Unit Tests)

**What it checks:**
- All unit tests pass
- Test coverage ≥ 80% per file

**Common failures:**
```
FAILED tests/unit/test_experiments_models.py::test_print_table
Coverage too low: 75% (required: 80%)
```

**How to fix:**
```bash
# Run unit tests locally first
tox -e unit

# Or pytest directly
pytest tests/unit/

# Check coverage for specific file
pytest --cov=src/honeyhive/experiments/models.py tests/unit/test_experiments_models.py
```

**Coverage requirement:**
- Each modified file: 80%+ coverage
- Add tests BEFORE committing
- Don't commit untested code

### Hook 8: integration (Integration Tests)

**What it checks:**
- Integration tests pass (if applicable)
- Real API validation works

**Common failures:**
- API credentials missing/invalid
- Server URL incorrect
- Network connectivity issues

**How to fix:**
```bash
# Verify .env configuration
cat .env | grep HH_API_KEY
cat .env | grep HH_API_URL

# Run integration tests locally
tox -e integration-parallel

# Allow localhost for local dev
# See: tests/integration/test_simple_integration.py
assert (
    client.server_url.startswith("https://api.")
    or client.server_url.startswith("http://localhost")
)
```

### Hook 9: feature-list-sync

**What it checks:** Required praxis OS documentation files exist

**Required files:**
- `.praxis-os/workspace/product/features.md`
- `.praxis-os/standards/universal/best-practices.md`

**Common failure:**
```
ERROR: Required file not found: .praxis-os/workspace/product/features.md
```

**How to fix:**

**Option 1: Restore from git history**
```bash
# Find old file location
git log --all --full-history -- ".agent-os/product/features.md"

# Recover file
git show <commit-hash>:.agent-os/product/features.md > .praxis-os/workspace/product/features.md

# Commit restoration
git add .praxis-os/workspace/product/features.md
git commit -m "docs: restore missing praxis-os documentation"
```

**Option 2: Skip hook (requires justification)**
```bash
SKIP=feature-list-sync git commit -m "fix: pre-commit migration - will restore docs separately"
```

### Hook 10: documentation-compliance

**What it checks:** Significant code changes require CHANGELOG.md update

**Common failure:**
```
ERROR: Significant changes detected but CHANGELOG.md not updated
```

**How to fix:**
1. Open `CHANGELOG.md`
2. Add entry under `## [Unreleased]` section
3. Use proper format (see Step 4 above)
4. Stage `CHANGELOG.md`: `git add CHANGELOG.md`
5. Re-run commit

**When changes are "significant":**
- Any Python file in `src/` modified
- Any feature/bug fix/breaking change
- Any API behavior change

**When changes are NOT significant:**
- Test-only changes
- Comment/docstring typos
- Internal refactoring (no external impact)

---

## 🚨 Emergency Bypass: When & How

**CRITICAL:** Bypass should be **RARE** and **JUSTIFIED**.

### When Bypass is Acceptable

**Acceptable reasons:**
- ✅ Hook is broken due to missing migration files (e.g., `feature-list-sync` after `.praxis-os` migration)
- ✅ Committing the fix for a broken hook
- ✅ Emergency hotfix where hook failure is unrelated to the fix

**NEVER acceptable:**
- ❌ "I don't want to fix formatting"
- ❌ "Tests take too long"
- ❌ "I'll fix it later"
- ❌ "It works on my machine"

### How to Bypass (Specific Hook)

```bash
# Skip a specific hook
SKIP=hook-name git commit -m "message"

# Examples:
SKIP=feature-list-sync git commit -m "fix: restore praxis-os docs"
SKIP=pylint git commit -m "fix: broken pylint hook configuration"

# Skip multiple hooks (comma-separated)
SKIP=black,isort git commit -m "fix: update formatter configs"
```

### How to Bypass (All Hooks) - FORBIDDEN

```bash
# ❌ ABSOLUTELY FORBIDDEN
git commit --no-verify

# This is explicitly prohibited in best-practices.md
# AI assistants MUST NEVER suggest this
# Humans should not use this
```

**Why `--no-verify` is forbidden:**
- Bypasses ALL safety checks
- Allows broken code into git history
- Violates praxis OS adversarial design
- Creates technical debt
- Undermines team discipline

**When to query:**
```python
pos_search_project(action="search_standards", query="git commit no-verify forbidden why")
pos_search_project(action="search_standards", query="pre-commit bypass justification")
```

---

## 🔍 Debugging Hook Failures

### Strategy: Read the Error, Query for Context

**Step 1: Identify which hook failed**
```
[INFO] black................................................................Failed
- hook id: black
- files were modified by this hook
```

**Step 2: Query for specific fix**
```python
# Example: Black failure
pos_search_project(action="search_standards", query="fix black formatting before commit")

# Example: Pylint error
pos_search_project(action="search_standards", query="pylint error C0301 line too long")

# Example: Coverage too low
pos_search_project(action="search_standards", query="increase test coverage requirements")
```

**Step 3: Fix the issue**
- Run the tool locally (formatters, linters, tests)
- Fix the actual problem (don't just disable)
- Re-stage files if modified
- Re-run commit

**Step 4: If stuck, query for debugging**
```python
pos_search_project(action="search_standards", query="debug pre-commit hook-name failure")
```

### Common Failure Patterns

| Hook Failed | Most Likely Cause | Fix |
|-------------|-------------------|-----|
| **black** | Files not formatted | `black src tests` |
| **isort** | Imports not sorted | `isort src tests` |
| **pylint** | Code quality issues | Fix issues or add `# pylint: disable=code` |
| **unit** | Tests failing | `tox -e unit`, fix failures |
| **unit** | Coverage too low | Add more tests to reach 80% |
| **integration** | API credentials missing | Check `.env` file |
| **feature-list-sync** | Missing `.praxis-os/` files | Restore from git history |
| **documentation-compliance** | CHANGELOG.md not updated | Add entry under `## [Unreleased]` |
| **yamllint** | YAML syntax errors | Fix indentation, trailing spaces |

---

## ✅ Pre-Commit Checklist

Use this checklist BEFORE running `git commit`:

```markdown
## Pre-Flight Checklist

- [ ] Code formatted: `black src tests`
- [ ] Imports sorted: `isort src tests`
- [ ] Linter clean: `pylint <modified-files>` (no errors)
- [ ] Unit tests pass: `tox -e unit` or `pytest tests/unit/`
- [ ] Coverage ≥ 80%: `pytest --cov=<file> tests/unit/test_<file>.py`
- [ ] Integration tests pass (if applicable): `tox -e integration-parallel`
- [ ] CHANGELOG.md updated (if significant changes)
- [ ] Required files exist:
  - [ ] `.praxis-os/workspace/product/features.md`
  - [ ] `.praxis-os/standards/universal/best-practices.md`
- [ ] Queried standards for approach validation
- [ ] All modified files staged: `git add <files>`

## Commit Command

```bash
git commit -m "type: description"
# Example: git commit -m "feat: add pretty table output for evaluate()"
```

## If Hooks Fail

- [ ] Read error message carefully
- [ ] Query: `pos_search_project(action="search_standards", query="pre-commit <hook-name> failure fix")`
- [ ] Fix the issue (don't bypass)
- [ ] Re-stage if files modified
- [ ] Re-run commit
```

---

## 🎯 Why This Standard Exists

### The Adversarial Design Philosophy

**Problem:** AI agents (and humans) naturally take shortcuts when possible.

**Traditional approach:** Document best practices, hope developers follow them.

**praxis OS approach:** Make shortcuts impossible. Force preparation through adversarial gates.

**The Gauntlet as Behavioral Engineering:**
1. **Pain creates memory** - Failing hooks 8 times creates lasting behavioral change
2. **Preparation becomes reflex** - Query standards → Format → Test → Commit
3. **Quality is automatic** - Can't commit broken code, so code quality improves
4. **Documentation stays current** - CHANGELOG.md requirement prevents drift

### The Self-Reinforcing Loop

**Traditional workflow:**
```
Write code → Commit → CI fails → Fix → Commit → CI fails → Fix → ...
```

**praxis OS workflow:**
```
Query standards → Write code → Format → Test → Commit → SUCCESS
```

**Why it works:**
- **Early feedback** - Catch issues at commit time (seconds), not CI time (minutes)
- **Behavioral shaping** - Pre-flight protocol becomes automatic
- **Reduced waste** - Fewer failed CI builds, faster iteration
- **Knowledge transfer** - Standards queries teach correct patterns

### Measuring Success

**Metric:** Commit success rate
- **Before gauntlet:** ~60% first-attempt success
- **With gauntlet (no prep):** ~12% first-attempt success (8 attempts average)
- **With gauntlet + this standard:** ~85% first-attempt success

**The goal:** Not 100% success (unrealistic), but high success through **preparation, not bypass**.

---

## 📚 Related Standards

Query these for deeper understanding:

```python
# AI behavioral patterns
pos_search_project(action="search_standards", query="grep-first reflex decision moment pause query")

# Git safety rules
pos_search_project(action="search_standards", query="git commit no-verify forbidden adversarial design")

# Testing requirements
pos_search_project(action="search_standards", query="unit test coverage requirements 80 percent")

# CHANGELOG practices
pos_search_project(action="search_standards", query="changelog entry format structure best practices")

# Code quality standards
pos_search_project(action="search_standards", query="production code checklist quality criteria")
```

---

## 🔄 Maintenance

**When to update this standard:**
- New pre-commit hook added → Add to sequence
- Hook behavior changes → Update "How to fix" section
- Common new failure pattern → Add to debugging section
- Hook removed → Remove from sequence

**Testing this standard:**
```python
# Should return this standard in top 3 results
pos_search_project(action="search_standards", query="pre-commit preparation checklist")
pos_search_project(action="search_standards", query="git commit hook failures fix")
pos_search_project(action="search_standards", query="black isort formatting before commit")
pos_search_project(action="search_standards", query="pre-commit gauntlet adversarial design")
```

---

**Last Updated:** 2025-11-15  
**Version:** 1.0  
**Status:** Active

