# Phase 0.4: Initialize Source Tracking

## 🎯 **Objective**

Create the source tracking template that will document all URLs, SDK repositories, and fallback strategies for resilience.

---

## 📋 **Tasks**

### **Task 4.1: Create SDK_SOURCES.md Template**

**Action**: Initialize the SDK source tracking document.

**File**: `provider_response_schemas/{provider}/SDK_SOURCES.md`

**Content**:
```markdown
# {Provider} SDK Type Definition Sources

## Extraction Metadata
- **Framework Version**: 1.0
- **Extraction Started**: {YYYY-MM-DD}
- **Last Updated**: {YYYY-MM-DD}
- **Extracted By**: AI Assistant

---

## Python SDK

### Repository
- **URL**: TBD
- **Official Org**: TBD
- **Version**: TBD
- **Commit**: TBD
- **Extraction Date**: TBD

### Type Definition Files
| Response Type | File Path | Lines | Commit | Extracted |
|---------------|-----------|-------|--------|-----------|
| TBD | TBD | TBD | TBD | TBD |

### Dependencies
- TBD

### Search Strategy (if repo moves)
**Search Terms**:
- "{provider} official python sdk"
- "{provider} python client"
- "github {provider} python"

**Expected Patterns**:
- Official org name: `{provider}` or `{provider}-inc` or similar
- Repo name pattern: `{provider}-python`, `python-sdk`, `{provider}-client-python`
- Must have: Official maintainer, active commits, pip package link

**Fallback Sources**:
- PyPI package: `{provider}` (extract type stubs from installed package)
- Archive.org: Snapshot of GitHub repo
- Official documentation: May link to SDK

---

## TypeScript SDK

### Repository
- **URL**: TBD
- **Official Org**: TBD
- **Version**: TBD
- **Commit**: TBD
- **Extraction Date**: TBD

### Type Definition Files
| Response Type | File Path | Lines | Commit | Extracted |
|---------------|-----------|-------|--------|-----------|
| TBD | TBD | TBD | TBD | TBD |

### Dependencies
- TBD

### Search Strategy (if repo moves)
**Search Terms**:
- "{provider} official typescript sdk"
- "{provider} node sdk"
- "github {provider} typescript"

**Expected Patterns**:
- Official org name: `{provider}` or `{provider}-inc` or similar
- Repo name pattern: `{provider}-node`, `{provider}-typescript`, `typescript-sdk`
- Must have: Official maintainer, active commits, npm package link

**Fallback Sources**:
- npm package: `@{provider}/{package}` or `{provider}` (extract `.d.ts` files)
- Archive.org: Snapshot of GitHub repo
- DefinitelyTyped: `@types/{provider}` (community-maintained types)

---

## Cross-Language Validation

### Validation Status
- [ ] Field names match across languages
- [ ] Required/optional fields match
- [ ] Types are compatible
- [ ] Nested structures identical

### Discrepancies Found
- None yet

---

## Fallback Strategy

### If GitHub Repos Unavailable
1. **Check Package Registries**:
   - PyPI: `pip install {provider}` → extract type stubs
   - npm: `npm install {provider}` → extract `.d.ts` files

2. **Check Archive.org**:
   - Search for: `https://github.com/{org}/{repo}`
   - Use latest snapshot before URL broke

3. **Check Official Documentation**:
   - API reference may have response schemas
   - OpenAPI/Swagger specs (if available)

4. **Check Community**:
   - GitHub issues/discussions about SDK location
   - Provider's community forums
   - Stack Overflow questions

### If SDK Versions Changed
1. **Use Git Tags**:
   - `git tag -l` to list all versions
   - `git checkout v{version}` to access specific version
   - Document commit hash for exact reproducibility

2. **Use Package Version History**:
   - PyPI: https://pypi.org/project/{package}/#history
   - npm: https://www.npmjs.com/package/{package}?activeTab=versions

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| {YYYY-MM-DD} | Initial creation | Starting schema extraction |

---

## Notes
- This document will be populated during Phase 1
- All TBD fields must be filled before proceeding to Phase 2
```

---

### **Task 4.2: Document Search Strategy**

**Action**: Pre-define search strategies for finding SDKs.

**How**:
1. Document expected patterns for finding official SDKs
2. List search terms to use
3. Define verification criteria
4. Plan fallback strategies

**Evidence Required**:
- Search strategy documented in SDK_SOURCES.md
- Fallback strategies defined
- Verification criteria clear

**This is already in the template above** ✅

---

## ✅ **Quality Gate: Source Tracking Initialized**

Before proceeding to Phase 1, verify:

- ✅ SDK_SOURCES.md created
- ✅ Search strategies documented
- ✅ Fallback strategies defined
- ✅ Template is complete and ready to populate

---

## 📊 **Output**

**File Created**:
```
provider_response_schemas/{provider}/SDK_SOURCES.md
```

**Update**: `provider_response_schemas/{provider}/PROGRESS.md`

**Mark Phase 0 Complete**:
```markdown
| Phase | Status | Date Started | Date Completed | Notes |
|-------|--------|--------------|----------------|-------|
| 0     | ✅     | {YYYY-MM-DD} | {YYYY-MM-DD}   | Pre-research setup complete |
| 1     | 🔄     | {YYYY-MM-DD} | -              | Ready to start |
```

**Update Quality Gates**:
```markdown
## Quality Gates Passed
- [x] Phase 0: Pre-Research Setup
```

---

## 🎯 **Navigation**

### **Current Phase**: 0 - Pre-Research Setup
### **Current Task**: 4 - Initialize Source Tracking (FINAL TASK IN PHASE 0)

### **Phase 0 Complete! Next Phase**:
```
🎯 NEXT-MANDATORY: ../1/task-1-locate-official-sdks.md
```

---

**Phase**: 0  
**Task**: 4  
**Status**: Active
