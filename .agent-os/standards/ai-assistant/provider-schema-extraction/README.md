# Provider Schema Extraction Framework v1.0

**🎯 Systematic extraction of LLM provider response schemas using OpenAPI-first priority cascade**

⚠️ MUST-READ: [../command-language-glossary.md](../command-language-glossary.md)

---

## 🚀 **Quick Start**

```markdown
1. Read command language glossary
2. Execute entry point: FRAMEWORK_ENTRY_POINT.md
3. Select mode (NEW/UPDATE/AUDIT)
4. Follow phase-by-phase execution
5. Complete all quality gates
```

---

## 📊 **Framework Structure**

```
provider-schema-extraction/
├── FRAMEWORK_ENTRY_POINT.md     # Start here
├── progress-tracking.md          # Copy to chat
├── README.md                     # This file
├── COMMON_PITFALLS.md           # Lessons learned
└── phases/
    ├── 0/  # Pre-Research Setup (4 tasks)
    ├── 1/  # Schema Discovery (6 strategies)
    ├── 2/  # Schema Extraction (4 paths)
    ├── 3/  # Example Collection (3 tasks)
    ├── 4/  # JSON Schema Creation (3 tasks)
    ├── 5/  # Validation (3 tasks)
    ├── 6/  # Documentation (3 tasks)
    └── 7/  # Integration Testing (3 tasks)
```

---

# Provider Schema Extraction Framework v1.0

## 📋 **Overview**

The **Provider Schema Extraction Framework** is a systematic, phase-driven methodology for creating and maintaining versioned JSON Schema definitions of LLM provider API response objects.

This framework ensures:
- ✅ **Repeatability**: Every schema can be reconstructed from documented sources
- ✅ **Resilience**: Handles documentation changes and URL moves
- ✅ **Quality**: Consistent schema structure and validation
- ✅ **Auditability**: Clear source tracking for every field
- ✅ **Maintainability**: Easy to update schemas when APIs change

## 🎯 **Purpose**

Provider response schemas are **critical artifacts** that enable:
1. **DSL Design**: Understanding provider response structures informs DSL primitives
2. **Transform Development**: Knowing field types/structures guides transform implementation
3. **Validation**: Ensuring DSL field paths are valid against actual provider schemas
4. **Documentation**: Providing clear, versioned reference for provider APIs

## 🏗️ **Framework Architecture**

```
.agent-os/standards/ai-assistant/provider-schema-extraction/
├── README.md                          # This file
├── FRAMEWORK_ENTRY_POINT.md          # Start here for any schema work
├── COMMON_PITFALLS.md                # Lessons learned from past runs
├── phases/
│   ├── 0/                            # Pre-Research Setup
│   ├── 1/                            # API Documentation Discovery
│   ├── 2/                            # Schema Extraction
│   ├── 3/                            # Example Collection
│   ├── 4/                            # JSON Schema Creation
│   ├── 5/                            # Validation
│   ├── 6/                            # Documentation
│   └── 7/                            # Integration Testing
├── templates/
│   ├── schema-template.json          # Base JSON Schema template
│   ├── changelog-template.md         # CHANGELOG structure
│   ├── example-template.json         # Example response template
│   └── source-tracking-template.md   # Source documentation template
├── quality-gates/
│   ├── phase-0-gates.md
│   ├── phase-1-gates.md
│   ├── phase-2-gates.md
│   ├── phase-3-gates.md
│   ├── phase-4-gates.md
│   ├── phase-5-gates.md
│   ├── phase-6-gates.md
│   └── phase-7-gates.md
└── RETROSPECTIVE_TEMPLATE.md
```

## 📊 **Framework Phases**

### **Phase 0: Pre-Research Setup** (10 min)
**Purpose**: Initialize schema project and set up tracking

**Tasks**:
- Verify provider existence and official name
- Check if schema already exists (update vs create)
- Create directory structure
- Initialize source tracking document
- Set up progress tracking

**Output**: Clean workspace ready for schema extraction

---

### **Phase 1: API Documentation Discovery** (30-60 min)
**Purpose**: Locate and verify all official documentation sources

**Tasks**:
- Find official API reference documentation
- Locate response object schema documentation
- Find example responses (official examples)
- Verify sources are official (not third-party)
- Document fallback search strategies
- Archive URLs with timestamps

**Output**: Comprehensive source tracking document with verification

**🚨 CRITICAL**: This phase is the foundation for repeatability. Every URL must be documented with:
- Exact URL
- Extraction date
- Page title/section
- Search terms used to find it
- Fallback URLs (mirrors, archives, GitHub)

---

### **Phase 2: Schema Extraction** (1-2 hours)
**Purpose**: Systematically extract response structure from documentation

**Tasks**:
- Extract core response object structure
- Identify all fields (required vs optional)
- Find nested objects and their structures
- **CRITICAL**: Identify JSON strings vs objects
- **CRITICAL**: Find nullable fields with semantic meaning
- Document conditional fields (when they appear)
- Track field-level sources

**Output**: Detailed field inventory with source attribution

**🚨 CRITICAL**: Every field must have:
- Source URL + section
- Required vs optional
- Type (string, object, JSON string, etc.)
- When it appears (always, conditional, etc.)

---

### **Phase 3: Example Collection** (30-60 min)
**Purpose**: Gather real-world examples to validate schema

**Tasks**:
- Collect basic examples (simple use case)
- Collect edge cases (tool calls, multimodal, streaming)
- Collect error responses
- Verify examples are real (from docs, not fabricated)
- Test examples for completeness
- Document example sources

**Output**: At least 3 validated examples with source attribution

---

### **Phase 4: JSON Schema Creation** (1-2 hours)
**Purpose**: Convert extracted structure into formal JSON Schema

**Tasks**:
- Create base JSON Schema structure
- Add custom extensions (json-string, base64, etc.)
- Add descriptions for all fields
- Add metadata (version, extraction date, sources)
- Mark required fields
- Add nullable annotations
- Document conditional logic

**Output**: Complete, valid JSON Schema file

**🚨 CRITICAL**: Schema must include:
- `$schema` version
- `$id` with provider + version
- `title` and `description`
- All fields from Phase 2
- Custom format tags
- Source references in descriptions

---

### **Phase 5: Validation** (30 min)
**Purpose**: Ensure schema quality and completeness

**Tasks**:
- Validate JSON Schema syntax
- Test examples against schema
- Check completeness (all known fields)
- Verify DSL implications
- Run automated quality gates

**Output**: Validated schema passing all quality gates

**Quality Gates**:
- ✅ Valid JSON Schema syntax
- ✅ All examples validate successfully
- ✅ All known fields documented
- ✅ Required fields marked correctly
- ✅ JSON strings have format tags

---

### **Phase 6: Documentation** (30 min)
**Purpose**: Document schema for future reference and updates

**Tasks**:
- Create CHANGELOG entry
- Document critical findings
- Update registry README
- Archive source URLs
- Document known limitations

**Output**: Complete documentation package

---

### **Phase 7: Integration Testing** (30 min)
**Purpose**: Verify schema integrates with DSL system

**Tasks**:
- Test DSL field path validation
- Verify transform requirements
- Document provider-specific patterns
- Test schema evolution scenarios

**Output**: Verified schema ready for production use

---

## 🎯 **Quality Gates Summary**

### **Gate 1: Source Documentation** (Phase 1)
- ✅ All URLs documented with timestamps
- ✅ Search strategies documented
- ✅ Fallback sources identified
- ✅ Sources verified as official

### **Gate 2: Schema Completeness** (Phase 2)
- ✅ All known fields extracted
- ✅ Required vs optional marked
- ✅ Nested objects documented
- ✅ JSON strings identified
- ✅ Field-level sources documented

### **Gate 3: Example Validation** (Phase 3)
- ✅ At least 3 examples collected
- ✅ Examples are real API responses
- ✅ Examples cover edge cases
- ✅ Example sources documented

### **Gate 4: Schema Validity** (Phase 4)
- ✅ Valid JSON Schema syntax
- ✅ All extensions documented
- ✅ Descriptions complete
- ✅ Metadata included

### **Gate 5: Integration** (Phase 5-7)
- ✅ Examples validate against schema
- ✅ DSL integration tested
- ✅ Documentation complete
- ✅ CHANGELOG updated

---

## 🚀 **Getting Started**

### **To Create a New Provider Schema**:
```bash
# Start at the entry point
Read: .agent-os/standards/ai-assistant/provider-schema-extraction/FRAMEWORK_ENTRY_POINT.md

# Follow phases systematically
Phase 0 → Phase 1 → Phase 2 → ... → Phase 7
```

### **To Update an Existing Schema**:
```bash
# Start at entry point with UPDATE mode
Read: .agent-os/standards/ai-assistant/provider-schema-extraction/FRAMEWORK_ENTRY_POINT.md

# Framework will guide you to appropriate phases
# Usually: Phase 1 (re-verify sources) → Phase 2 (extract new fields) → Phase 4-7
```

---

## 🔄 **Resilience & Repeatability**

### **Source Documentation Strategy**

Every piece of data extracted must have:

1. **Primary Source**:
   - Exact URL
   - Page title/section heading
   - Extraction date (YYYY-MM-DD)
   - Quoted text or field name from docs

2. **Search Strategy**:
   - Search terms used to find this page
   - Alternative search terms
   - Expected page structure/layout

3. **Fallback Sources**:
   - Archive.org snapshot URL
   - GitHub repository (if open source)
   - Alternative documentation sites
   - API changelog/version history

### **When Documentation Moves**

If URLs break or docs reorganize:

1. **Try Fallback Sources** (from source tracking doc)
2. **Use Search Strategy** (documented search terms)
3. **Check Provider Changelog** (may mention doc restructuring)
4. **Search GitHub Issues** (community may have discussed it)
5. **Use Archive.org** (retrieve historical version)
6. **Contact Provider** (last resort)

### **Verification Protocol**

When updating a schema:

1. **Re-verify Sources**: Check all URLs still work
2. **Compare Versions**: Has API changed since last extraction?
3. **Update Sources**: Document new URLs if docs moved
4. **Update CHANGELOG**: Document source changes

---

## 📚 **Key Principles**

### **1. Source Attribution is Mandatory**
Every field, every example, every assertion must have a documented source.

### **2. Assume Docs Will Move**
Always document search strategies and fallback sources.

### **3. Repeatability > Speed**
It's better to spend extra time documenting sources than to rush and lose traceability.

### **4. Quality Gates are Blocking**
If a quality gate fails, stop and fix before proceeding.

### **5. Schemas are Living Documents**
Expect to update schemas as provider APIs evolve.

---

## 🛠️ **Tools & Automation**

### **Schema Validation**
```bash
# Validate JSON Schema syntax
python -m jsonschema -i provider_response_schemas/openai/examples/basic_chat.json provider_response_schemas/openai/v2025-01-30.json
```

### **Source Verification**
```bash
# Check if URLs are still accessible (future automation)
python scripts/verify_schema_sources.py provider_response_schemas/openai/
```

### **Schema Diff**
```bash
# Compare schema versions (future automation)
python scripts/diff_schemas.py openai v2025-01-30 v2025-02-15
```

---

## 📖 **Related Documentation**

- **Framework Entry Point**: `FRAMEWORK_ENTRY_POINT.md`
- **Common Pitfalls**: `COMMON_PITFALLS.md`
- **Schema Specification**: `../../../../../../provider_response_schemas/SCHEMA_SPEC.md`
- **Provider DSL Framework**: `.agent-os/standards/ai-assistant/provider-dsl-development/README.md`

---

## 📝 **Framework Metadata**

- **Version**: 1.0
- **Created**: 2025-09-30
- **Last Updated**: 2025-09-30
- **Authors**: HoneyHive AI Team
- **Status**: Active

---

## 🎯 **Success Criteria**

A schema is considered **production-ready** when:

✅ All 7 phases completed
✅ All quality gates passed
✅ Source tracking document complete
✅ At least 3 validated examples
✅ CHANGELOG entry created
✅ DSL integration tested
✅ Retrospective completed (if applicable)

---

**Remember**: This framework exists to ensure schemas are **repeatable, resilient, and high-quality**. Take the time to document sources properly—it will save hours in the future.
