# SDK Analysis Quick Reference Card

**Quick guide for running SDK analysis workflow**

---

## Setup (5 minutes)

```bash
# 1. Create workspace in /tmp
mkdir -p /tmp/sdk-analysis/{findings,scripts,reports}
cd /tmp/sdk-analysis

# 2. Clone SDK to analyze
git clone https://github.com/{org}/{sdk-repo}.git
cd {sdk-repo}

# 3. Verify you're in the right place
pwd  # Should show: /tmp/sdk-analysis/{sdk-repo}
ls   # Should see: src/, README.md, pyproject.toml, etc.
```

---

## Phase 1: Quick Discovery (30 min)

```bash
# In /tmp/sdk-analysis/{sdk-repo}/

# Count files
find src -name "*.py" | wc -l

# Read complete README
cat README.md

# Read complete dependencies
cat pyproject.toml  # or setup.py or package.json

# Map structure
find src -type d | sort
find src -name "*.py" | sort
```

---

## Phase 2: Find LLM Calls (30 min)

```bash
# In /tmp/sdk-analysis/{sdk-repo}/

# Find OpenAI usage
grep -rn "openai" pyproject.toml setup.py
grep -rn "OpenAI\|AsyncOpenAI" src/
grep -rn "chat.completions.create\|responses.create" src/

# Count all API calls
grep -r "\.create(" src/ | grep -v "test\|#" | wc -l

# Save findings
grep -rn "OpenAI\|AsyncOpenAI" src/ > ../findings/client-instantiation.txt
grep -rn "chat.completions.create\|responses.create" src/ > ../findings/api-calls.txt
```

---

## Phase 3: Check Observability (1 hour)

```bash
# In /tmp/sdk-analysis/{sdk-repo}/

# Check for OpenTelemetry
grep -r "opentelemetry" src/
grep -r "opentelemetry" pyproject.toml

# Check for custom tracing
find src -path "*tracing*" -name "*.py"
find src -path "*observability*" -name "*.py"

# If custom tracing found, read ALL files
for file in $(find src -path "*tracing*" -name "*.py"); do
    echo "=== $file ==="
    cat "$file"
done > ../findings/tracing-complete-code.txt

# Find processor interfaces
grep -rn "class.*Processor" src/
grep -rn "add.*processor\|register.*processor" src/
```

---

## Phase 4: Architecture (2 hours)

```bash
# In /tmp/sdk-analysis/{sdk-repo}/

# Find entry points
cat src/{package}/__init__.py
grep -rn "class.*Runner\|class.*Agent" src/

# Read main execution files (COMPLETE, not head/tail)
cat src/{package}/run.py
cat src/{package}/_run_impl.py
cat src/{package}/agent.py

# Find model abstractions
ls -la src/{package}/models/
cat src/{package}/models/*.py
```

---

## Quick Decision Matrix

**After finding LLM client and observability:**

| Finding | Integration Approach | Effort |
|---------|---------------------|--------|
| Uses OpenAI + No tracing | Existing instrumentor | 0 hours ✅ |
| Uses OpenAI + Custom tracing | Instrumentor + Custom processor | 4-8 hours |
| Uses OpenAI + OpenTelemetry | Standard OTel integration | 2-4 hours |
| Custom LLM calls + No tracing | Build custom instrumentor | 2-3 weeks |

---

## Evidence Checklist

Before finishing, you must have:

```markdown
## Phase 2: LLM Client Discovery
- [ ] Client library: {name} >= {version}
- [ ] Instantiation points: {count} in {files}
- [ ] API call sites: {count} in {files}
- [ ] Files documented with line numbers

## Phase 3: Observability
- [ ] Type: OpenTelemetry / Custom / None
- [ ] Tracing files: {count} files, {LOC} total
- [ ] Processor interface: YES / NO
- [ ] Integration method identified

## Phase 4: Architecture
- [ ] Entry point documented
- [ ] Execution flow: entry → LLM call
- [ ] Main files read completely
```

---

## Common Commands

```bash
# Count occurrences
grep -r "pattern" src/ | wc -l

# Find with line numbers
grep -rn "pattern" src/

# Find with context (5 lines before/after)
grep -rn -B 5 -A 5 "pattern" src/

# Read complete file (NEVER use head/tail for analysis)
cat src/path/to/file.py

# List all files with LOC
find src -name "*.py" -exec wc -l {} + | sort -n

# Find largest files (likely important)
find src -name "*.py" -exec wc -l {} + | sort -n | tail -20
```

---

## Save & Cleanup

```bash
# After analysis complete, save reports
cp /tmp/sdk-analysis/findings/* ~/project/analysis-results/
cp /tmp/sdk-analysis/reports/* ~/project/docs/

# Cleanup /tmp
rm -rf /tmp/sdk-analysis/

# Verify
ls /tmp/sdk-analysis/  # Should error: No such file or directory
```

---

## Anti-Patterns to Avoid

❌ **NEVER:**
- Use `head` or `tail` for code analysis (read COMPLETE files)
- Look at only first few grep results (find ALL occurrences)
- Assume without verifying (grep for actual evidence)
- Skip counting (document exact numbers)
- Clone to workspace (use /tmp for isolation)

✅ **ALWAYS:**
- Read complete files: `cat file.py`
- Find all: `grep -rn "pattern" src/`
- Count: `grep -r "pattern" src/ | wc -l`
- Document line numbers: `-n` flag
- Work in /tmp: `/tmp/sdk-analysis/`

---

## Time Estimates

- **Phase 0:** Setup - 15 minutes
- **Phase 1:** Discovery - 30-60 minutes
- **Phase 2:** LLM Client - 30-60 minutes
- **Phase 3:** Observability - 1-2 hours
- **Phase 4:** Architecture - 2-3 hours
- **Phase 5:** Strategy - 1-2 hours
- **Phase 6:** POC - 1-2 hours
- **Phase 7:** Documentation - 1-2 hours

**Total:** 3-5 days for thorough analysis

---

## Output Example

```markdown
# SDK Analysis Report: {SDK Name}

## Executive Summary
- SDK Purpose: Multi-agent orchestration
- LLM Client: openai >= 2.2.0
- Observability: Custom tracing (not OTel)
- **Recommendation:** Hybrid approach (instrumentor + processor)

## Key Findings
- Client instantiation: 2 files, 3 locations
- API call sites: 2 files, 2 locations (line 293, 306)
- Custom tracing: 12 files, 882 LOC
- Processor interface: YES via add_trace_processor()

## Integration Approach
{Code example and explanation}

## POC Results
{What worked, what's captured}
```

---

**Full Documentation:** See `sdk-instrumentation-analysis-workflow-spec.md`  
**Methodology:** See `SDK_ANALYSIS_METHODOLOGY.md`  
**Date:** 2025-10-15

