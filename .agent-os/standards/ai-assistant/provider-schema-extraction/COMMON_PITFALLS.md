# Common Pitfalls - Provider Schema Extraction Framework

## 🎯 **Purpose**

This document tracks common mistakes and lessons learned from provider schema extraction runs to prevent repetition.

---

## 🚨 **Critical Pitfalls**

### **Pitfall 1: Assuming Documentation is Complete**

**Problem**: Relying solely on official documentation, which is often incomplete or outdated.

**Example**:
- OpenAI's docs don't list all finish_reason values
- Gemini's docs omit certain response fields
- Pricing documentation lags behind model releases

**Solution**:
✅ **Always prioritize SDK type definitions over documentation**
✅ Cross-validate between Python and TypeScript SDKs
✅ Use documentation as supplementary source, not primary

**Framework Phase**: Phase 1 (SDK extraction is primary)

---

### **Pitfall 2: Not Recording Exact SDK Versions**

**Problem**: Extracting schema without documenting exact SDK version and commit hash.

**Why It's Bad**:
- Cannot reproduce the extraction
- Cannot track when schema changed
- Cannot correlate schema with API version

**Solution**:
✅ Always record git commit hash (not just tag)
✅ Document extraction date
✅ Link SDK version to API version (if known)

**Framework Phase**: Phase 1, Task 2 (clone and inspect)

---

### **Pitfall 3: Missing JSON String Fields**

**Problem**: Not identifying fields that are JSON strings (e.g., `tool_calls.function.arguments`).

**Why It's Critical**:
- DSL navigation rules will fail
- Transform functions will receive wrong type
- Real-world data won't match schema

**Example**:
```python
# Wrong assumption
function.arguments: Dict[str, Any]

# Actual API reality
function.arguments: str  # JSON string, not object!
```

**Solution**:
✅ Carefully check SDK types for `str` fields with "json" in name
✅ Add custom `format: "json-string"` to schema
✅ Test with real API examples

**Framework Phase**: Phase 2 (schema extraction), Phase 3 (example collection)

---

### **Pitfall 4: Ignoring Nullable vs Optional**

**Problem**: Treating "optional" and "nullable" as the same thing.

**Reality**:
- **Optional**: Field may not be present in response
- **Nullable**: Field is present but value is `null`

**TypeScript Example**:
```typescript
field1?: string          // Optional, not nullable
field2: string | null    // Required but nullable
field3?: string | null   // Optional AND nullable
```

**Solution**:
✅ Track both `required` and `nullable` separately
✅ In JSON Schema, use `required` array + `nullable` keyword
✅ Test with examples where fields are null vs absent

**Framework Phase**: Phase 1, Task 3 (parse type definitions)

---

### **Pitfall 5: Forgetting Nested Types**

**Problem**: Parsing only top-level types, missing nested object structures.

**Example**:
```python
# Parsed this
class ChatCompletion:
    choices: List[Choice]  # ← What is Choice?

# Forgot to parse this
class Choice:
    message: ChatCompletionMessage  # ← What is ChatCompletionMessage?
```

**Solution**:
✅ Create a parsing queue for all referenced types
✅ Recursively parse until no unresolved types remain
✅ Document the type hierarchy

**Framework Phase**: Phase 1, Task 3 (parse type definitions)

---

### **Pitfall 6: URL Rot (Documentation Moves)**

**Problem**: Saving URLs without fallback strategies; links break when docs reorganize.

**Solution**:
✅ Document search terms used to find the URL
✅ Save Archive.org snapshot
✅ Record page structure/title for re-finding
✅ Use SDK repos as source of truth (more stable than docs)

**Framework Phase**: Phase 1, Task 4 (source tracking)

---

### **Pitfall 7: Language-Specific Type Mismatches**

**Problem**: Python and TypeScript SDKs don't always match perfectly.

**Examples**:
- Python uses `int`, TypeScript uses `number`
- Python `List[]` vs TypeScript `Array<>`
- Python `Literal[]` vs TypeScript string literals

**Solution**:
✅ Always cross-validate between languages
✅ Document discrepancies with explanations
✅ When in conflict, prefer TypeScript (closer to JSON)

**Framework Phase**: Phase 1, Task 3 (cross-validation)

---

### **Pitfall 8: Skipping Example Validation**

**Problem**: Creating schema without validating against real examples.

**Why It's Bad**:
- Schema may be theoretically correct but practically wrong
- Miss edge cases (streaming, errors, special formats)
- Transform functions will fail on real data

**Solution**:
✅ Collect at least 3 real examples (basic, complex, error)
✅ Validate examples against schema
✅ Fix schema if examples don't validate

**Framework Phase**: Phase 3 (example collection), Phase 5 (validation)

---

### **Pitfall 9: Provider-Specific Data in JSON Strings**

**Problem**: Complex provider-specific data serialized as JSON strings.

**Example**:
```json
{
  "content": "[{\"type\": \"text\", \"text\": \"Hello\"}]"  // ← JSON string!
}
```

**Why It's Tricky**:
- Looks like an array, but it's a string
- Must be parsed by transform functions
- Schema must mark as `format: "json-string"`

**Solution**:
✅ Test with real API responses (not just SDK types)
✅ Check if SDK deserializes automatically
✅ Document serialization patterns per provider

**Framework Phase**: Phase 3 (example collection), Phase 4 (schema creation)

---

### **Pitfall 10: Not Testing DSL Integration**

**Problem**: Creating perfect schema that doesn't work with DSL field paths.

**Example**:
```yaml
# This navigation rule
source_field: "choices.0.message.content"

# Won't work if schema has
choices: {type: "json-string"}  # ← Can't navigate into string!
```

**Solution**:
✅ Test field paths from DSL against schema
✅ Verify navigation rules can reach all fields
✅ Ensure transform requirements are met

**Framework Phase**: Phase 7 (integration testing)

---

## 📊 **Lessons Learned by Provider**

### **OpenAI**

**Lesson**: GPT-5 models in production before documentation updated
- **Impact**: Schema missing latest models
- **Solution**: Check SDK for models, not just docs

**Lesson**: `function.arguments` is JSON string, not object
- **Impact**: Navigation rules failed
- **Solution**: Added `format: "json-string"` extension

---

### **Anthropic**

**Lesson**: `content` field is polymorphic (string OR array)
- **Impact**: Single type schema failed
- **Solution**: Use `oneOf` in JSON Schema

---

### **Gemini** (TBD)
---

## 🎯 **Prevention Checklist**

Use this checklist before marking any phase complete:

### **Phase 0: Pre-Research**
- [ ] Provider verified as having public JSON API
- [ ] At least one official SDK located

### **Phase 1: SDK Extraction**
- [ ] Exact commit hash documented
- [ ] Both Python and TypeScript checked (if available)
- [ ] Search strategy documented for resilience

### **Phase 2: Schema Extraction**
- [ ] All nested types parsed recursively
- [ ] Required vs optional documented
- [ ] Nullable vs non-nullable documented
- [ ] JSON string fields identified with `format` tag

### **Phase 3: Example Collection**
- [ ] At least 3 real examples collected
- [ ] Examples include edge cases (tool calls, errors)
- [ ] Examples NOT fabricated

### **Phase 4: JSON Schema Creation**
- [ ] Custom extensions used (`json-string`, `base64`, etc.)
- [ ] All fields from SDK included
- [ ] Source references in descriptions

### **Phase 5: Validation**
- [ ] Examples validate against schema
- [ ] Cross-language validation passed
- [ ] Discrepancies explained

### **Phase 7: Integration**
- [ ] DSL field paths tested
- [ ] Transform requirements verified
- [ ] Schema actually usable

---

## 🔄 **Continuous Improvement**

After each provider extraction, update this document with:
- New pitfalls discovered
- Provider-specific lessons
- Framework improvements needed

---

**Last Updated**: 2025-09-30  
**Framework Version**: 1.0
