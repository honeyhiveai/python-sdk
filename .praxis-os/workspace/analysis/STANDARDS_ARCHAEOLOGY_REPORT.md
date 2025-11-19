# Standards Archaeology Report
## Agent OS → praxis OS: What's Still Valid?

**Date**: November 8, 2025  
**Purpose**: Determine what from Agent OS journey needs to be preserved vs superseded

---

## 🔍 Methodology

Comparing Agent OS (361 files) vs praxis OS (74 files) to determine:
- ✅ **Already Migrated**: Content in praxis OS (universal or development)
- 🔄 **Workflows**: Behavioral content that becomes `pos_workflow` (not standards)
- ⚠️ **Needs Analysis**: May be Python SDK-specific or still valid
- 🗄️ **Historical**: Superseded by praxis OS or obsolete

---

## 📊 Category-by-Category Analysis

### 1. Architecture (4 files) - ✅ COMPLETE

**Agent OS**: `.agent-os/standards/architecture/`
```
- api-design-principles.md
- dependency-injection.md
- separation-of-concerns.md
- solid-principles.md
```

**praxis OS**: `.praxis-os/standards/universal/architecture/`
```
- api-design-principles.md          ✅ EXACT MATCH
- dependency-injection.md           ✅ EXACT MATCH
- separation-of-concerns.md         ✅ EXACT MATCH
- solid-principles.md               ✅ EXACT MATCH
```

**Status**: ✅ **COMPLETE** - All 4 files migrated to praxis OS universal
**Action**: None needed

---

### 2. Workflows (5 files) - ✅ COMPLETE

**Agent OS**: `.agent-os/standards/workflows/`
```
- mcp-rag-configuration.md
- time-estimation-standards.md
- workflow-construction-standards.md
- workflow-metadata-standards.md
- workflow-system-overview.md
```

**praxis OS**: `.praxis-os/standards/universal/workflows/`
```
- creating-specs.md                 ✅ NEW (enhanced)
- mcp-rag-configuration.md          ✅ EXACT MATCH
- time-estimation-standards.md      ✅ EXACT MATCH
- workflow-construction-standards.md ✅ EXACT MATCH
- workflow-metadata-standards.md    ✅ EXACT MATCH
- workflow-system-overview.md       ✅ EXACT MATCH
```

**Status**: ✅ **COMPLETE** - All 5 files migrated, plus 1 new file
**Action**: None needed

---

### 3. Documentation (9 files) - ⚠️ PARTIAL

**Agent OS**: `.agent-os/standards/documentation/`
```
- api-documentation.md              ✅ In praxis OS universal
- code-comments.md                  ✅ In praxis OS universal
- documentation-generation.md       ⚠️ Python SDK-specific?
- documentation-templates.md        ⚠️ Check if superseded
- honeyhive-docs-access.md          ✅ Python SDK-specific (keep)
- mermaid-diagrams.md               ⚠️ Check if in universal
- readme-templates.md               ✅ In praxis OS universal
- requirements.md                   ⚠️ Check if superseded
- rst-documentation-workflow.md     ✅ Python SDK-specific (Sphinx/RST)
```

**praxis OS Universal**: 4 files
**Python SDK-Specific Candidates**: 
- `honeyhive-docs-access.md` (SDK docs portal)
- `rst-documentation-workflow.md` (Sphinx/RST workflow)
- `documentation-generation.md` (Sphinx build process)

**Status**: ⚠️ **NEEDS REVIEW** - 3-5 files may be Python SDK-specific
**Action**: Review documentation standards for SDK-specific content

---

### 4. Testing (10 files) - ⚠️ PARTIAL

**Agent OS**: `.agent-os/standards/testing/`
```
- debugging-methodology.md          ⚠️ Check universal
- fixture-and-patterns.md           ✅ In development/ (test-execution)
- integration-testing-standards.md  ✅ In praxis OS universal
- integration-testing.md            ✅ In praxis OS universal
- property-based-testing.md         ✅ In praxis OS universal
- README.md                         ℹ️ Index file
- test-doubles.md                   ✅ In praxis OS universal
- test-execution-commands.md        ✅ In development/testing/
- test-pyramid.md                   ✅ In praxis OS universal
- unit-testing-standards.md         ⚠️ Check if needed
```

**Status**: ⚠️ **MOSTLY COMPLETE** - May need 1-2 files
**Action**: Quick review of debugging-methodology and unit-testing-standards

---

### 5. Code Generation (198 files) - 🔄 WORKFLOWS

**Agent OS**: `.agent-os/standards/ai-assistant/code-generation/`
```
tests/v3/              (129 files) → 🔄 pos_workflow (test generation)
production/            (29 files)  → 🔄 pos_workflow (code generation)
linters/              (14 files)  → ⚠️ NEEDS REVIEW
shared/               (4 files)   → ⚠️ NEEDS REVIEW
archive/v2/           (22 files)  → 🗄️ Historical reference
```

**Status**: 
- ✅ Test/Production Frameworks → Workflow system
- ⚠️ Linters (14 files) → Tool configs, may need porting
- ⚠️ Shared (4 files) → May have reusable patterns

**Action**: Review linters/ and shared/ for Python SDK-specific configurations

---

### 6. Linter Standards (14 files) - ⚠️ NEEDS REVIEW

**Agent OS**: `.agent-os/standards/ai-assistant/code-generation/linters/`

**Subdirectories**:
- `black/` → Black formatter configurations
- `isort/` → Import sorting configurations
- `mypy/` → Type checking configurations
- `pylint/` → Linting configurations

**Status**: ⚠️ **NEEDS REVIEW** - These are Python SDK tool configurations
**Action**: Determine if these are:
- Universal patterns (→ praxis OS universal)
- SDK-specific configs (→ development/coding/)
- Superseded by pyproject.toml (→ historical)

---

### 7. Coding (5 files) - ⚠️ NEEDS REVIEW

**Agent OS**: `.agent-os/standards/coding/`
```
- architecture-patterns.md          ⚠️ Check if in universal/architecture
- graceful-degradation.md           ⚠️ Check if in universal
- python-standards.md               ⚠️ Python SDK-specific
- refactoring-protocols.md          ⚠️ Check if in universal
- type-safety.md                    ⚠️ Check if in universal
```

**Status**: ⚠️ **NEEDS REVIEW** - May overlap with universal or development/coding/
**Action**: Compare against universal/ and development/coding/

---

### 8. Concurrency (4 files) - ✅ COMPLETE?

**Agent OS**: `.agent-os/standards/concurrency/`

**praxis OS**: `.praxis-os/standards/universal/concurrency/` (4 files)

**Status**: ✅ **LIKELY COMPLETE** - Check file names match
**Action**: Quick validation

---

### 9. Security (3 files) - ⚠️ NEEDS REVIEW

**Agent OS**: `.agent-os/standards/security/` (3 files)
**praxis OS**: `.praxis-os/standards/universal/security/` (1 file)

**Status**: ⚠️ **GAP** - 2 files missing
**Action**: Identify what's in Agent OS but not praxis OS

---

### 10. AI Assistant Core (32 files) - ⚠️ PARTIAL

**Agent OS**: `.agent-os/standards/ai-assistant/` (excluding code-generation/)
```
32 core files about:
- MCP tool usage
- Query construction
- Standards creation
- Commit protocols
- etc.
```

**praxis OS**: `.praxis-os/standards/universal/ai-assistant/` (19 files)

**Status**: ⚠️ **GAP** - ~13 files difference
**Action**: Identify which 13 files are missing/different

---

### 11. Other Categories

**Agent OS unique**:
- `database/` (1 file) → ✅ In praxis OS universal (verified)
- `failure-modes/` (4 files) → ✅ In praxis OS universal (verified)
- `installation/` (2 files) → ✅ In praxis OS universal (3 files)
- `meta-framework/` (5 files) → ⚠️ May be Agent OS-specific
- `meta-workflow/` (5 files) → ✅ In praxis OS universal (5 files)
- `performance/` (1 file) → ✅ In praxis OS universal (1 file)
- `ai-safety/` (5 files) → ✅ In praxis OS universal (5 files)
- Standalone files (17) → ⚠️ Review individually

---

## 📊 Summary Status

| Category | Agent OS | praxis OS | Status | Action Needed |
|----------|----------|-----------|--------|---------------|
| **Architecture** | 4 | 4 | ✅ Complete | None |
| **Workflows** | 5 | 6 | ✅ Complete | None |
| **Test Gen Frameworks** | 175 | 0 | 🔄 Workflows | None (workflow system) |
| **Documentation** | 9 | 4 | ⚠️ Partial | Review 3-5 SDK-specific |
| **Testing** | 10 | ~8 | ⚠️ Mostly | Review 1-2 files |
| **Linters** | 14 | 0 | ⚠️ Review | Determine SDK-specific |
| **Coding** | 5 | ? | ⚠️ Review | Compare with development/ |
| **Security** | 3 | 1 | ⚠️ Gap | Identify 2 missing |
| **AI Assistant Core** | 32 | 19 | ⚠️ Gap | Identify 13 difference |
| **Other** | ~60 | ~50 | ⚠️ Mixed | Individual review |

---

## 🎯 Recommended Action Plan

### Phase 1: Quick Wins (High Confidence)
1. ✅ **DONE**: Architecture (4/4 migrated)
2. ✅ **DONE**: Workflows (5/5 migrated)
3. ✅ **DONE**: Test/Production Frameworks → Workflow system

### Phase 2: Python SDK-Specific Content (Needs Review)
1. **Documentation** (3-5 files): SDK docs, Sphinx/RST workflow
2. **Linters** (14 files): Tool configurations for Python SDK
3. **Coding** (5 files): Python-specific standards

### Phase 3: Gap Analysis (Compare Content)
1. **Security** (2 missing files)
2. **AI Assistant** (13 file difference)
3. **Testing** (1-2 files)

### Phase 4: Historical Artifacts (Archive)
1. Test Framework V2/Archive (22 files) → Reference only
2. Standalone/misc files → Review individually

---

## 💡 Key Insight

**The migration is MORE complete than file counts suggest!**

- **File Gap**: 361 → 74 files (20% coverage)
- **Content Gap**: Much smaller due to:
  - 175 files → Workflow system (not standards)
  - 4+5+4+5+1+5 = 24 files already in universal (exact matches)
  - ~10 files ported to development/
  - ~20 files may be historical/superseded

**Actual Gap to Review**: ~50-70 files (not 287!)

---

## 🔍 Next Steps

**Immediate**: Systematic review of:
1. Linter standards (14 files) - SDK tool configs?
2. Documentation standards (5 files) - SDK-specific?
3. Security (2 files) - What's missing?
4. AI Assistant (13 files) - What's the difference?
5. Coding standards (5 files) - Already covered?

**Method**: For each file, ask:
- Is this in praxis OS universal already?
- Is this Python SDK-specific (→ development/)?
- Is this superseded/historical (→ leave behind)?

