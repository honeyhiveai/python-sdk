# Tool Usage Patterns for Cursor IDE

**🎯 Empirical knowledge for AI assistants operating in Cursor environment**

⚠️ MUST-READ: These patterns are based on real-world usage and may not be documented in official Cursor documentation.

---

## 📝 **LARGE FILE CREATION: WRITE TOOL LIMITATIONS**

### **Empirical Constraint Discovery**

**Write Tool Parameter Size Limit**:
- **Failure Threshold**: ~5,000 lines
- **Error Symptom**: "Error calling tool: Error calling tool." (generic error)
- **Root Cause**: Undocumented parameter size constraint in Cursor tool call infrastructure
- **Status**: Not in official Cursor documentation (as of September 2025)

**Evidence**:
```
User observation: "usually anything over 5000 lines hits the error state"
AI experience: ~15,000 line file failed with generic error
Workaround success: Same content succeeded via shell command
Confidence: HIGH - observed across multiple sessions
```

---

## ✅ **RECOMMENDED APPROACH: SIZE-BASED DECISION LOGIC**

### **Decision Tree for File Creation**

**Size Categories**:

1. **Small Files (< 3,000 lines)** → Use write tool ✅
   - Reliability: HIGH (no observed failures)
   - Method: Standard write tool

2. **Medium Files (3,000-5,000 lines)** → Use write tool with caution ⚠️
   - Reliability: MEDIUM (occasional failures)
   - Be prepared to fall back to shell workaround

3. **Large Files (≥ 5,000 lines)** → Use shell workaround ✅
   - Reliability: HIGH (no size constraints)
   - Method: `cat > file << 'EOF'`

---

## 🚨 **MANDATORY GUIDELINES FOR AI ASSISTANTS**

### **Before Creating Large Documentation Files**

**1. Estimate Line Count**
- Comprehensive case study: ~1,700 lines
- Framework documentation: ~500-800 lines
- AI perspective document: ~15,000 lines
- Reference documentation: ~300-500 lines

**2. Choose Method Proactively**
- ❌ Don't attempt write tool for files > 5,000 lines
- ✅ Use shell workaround from the start
- ✅ Saves time and avoids error states

**3. If Write Tool Fails**
- **Symptom**: "Error calling tool: Error calling tool."
- **Action**: Switch to `cat << 'EOF'` approach immediately
- **Don't**: Retry write tool with same content (error is deterministic)

---

## 📋 **IMPLEMENTATION PATTERNS**

### **Pattern 1: Small Files (< 3,000 lines)**

```python
# Use write tool directly
write(
    file_path="/path/to/file.md",
    contents="[content up to 3000 lines]"
)
```

### **Pattern 2: Large Files (≥ 5,000 lines)**

```bash
# Use shell workaround
cat > /path/to/file.md << 'EOF'
[content over 5000 lines]
EOF
```

**Why Shell Workaround Works**:
- No tool call parameter serialization overhead
- No JSON encoding size limits
- Direct file system write without IDE intermediation
- No observed size constraints

---

## 📊 **OTHER KNOWN CURSOR LIMITATIONS**

### **Tool Call Count Limits**

**Default Mode**:
- Limit: 25 tool calls per interaction
- Continuation: Manual "Resume" or type "continue"

**MAX Mode**:
- Limit: 200 tool calls per interaction
- Cost: Each tool call charged separately

**AI Strategy**:
- Track tool call count during execution
- Batch operations to reduce tool calls
- Warn user if approaching limit

### **File Editing Limits**

**Cursor Auto-Edit**:
- Limit: ~400-500 lines for auto-edit feature
- Workaround: Use search_replace or MultiEdit

**Context Reading**:
- Performance degradation: Files > 6,000 lines (250K characters)
- Best practice: Modularize to keep files manageable

---

## 🎯 **REAL-WORLD EXAMPLES**

### **Example 1: Large Documentation (15,000 lines)**

**Task**: Create AI perspective document

❌ **Wrong**:
```python
write(file_path="...", contents="[15,000 lines]")  # WILL FAIL
```

✅ **Correct**:
```bash
cat > file.md << 'EOF'
[15,000 lines]
EOF
```

### **Example 2: Medium Documentation (800 lines)**

**Task**: Create framework reference

✅ **Safe**:
```python
write(file_path="...", contents="[800 lines]")  # SAFE
```

---

## 🔄 **CONTINUOUS LEARNING**

### **Update Protocol**

If you discover:
- New limits (higher or lower)
- Official documentation
- New workarounds

→ Update this file and document findings

---

## 📋 **QUICK REFERENCE**

**Decision Logic**:
```
if line_count < 3000:
    → use write tool (safe)
elif line_count >= 5000:
    → use cat << 'EOF' (mandatory)
else:  # 3000-5000
    → use write tool (with fallback ready)
```

**Critical Threshold**: **5,000 lines**

---

**Document Metadata**:
- **Created**: September 29, 2025
- **Source**: User empirical observation + AI session experience
- **Confidence**: HIGH
- **Status**: Living document - update as patterns evolve
