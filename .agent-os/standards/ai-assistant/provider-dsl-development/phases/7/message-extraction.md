# Task 7.1: Message Extraction Transform

**🎯 Define message content extraction transforms**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 6 complete with field mappings validated ✅/❌
- [ ] Message fields mapped in inputs and outputs ✅/❌
- [ ] Provider message structure known from Phase 2 ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Create transforms.yaml File**

🛑 EXECUTE-NOW: Create/open the YAML file

```bash
# File path
config/dsl/providers/{provider}/transforms.yaml
```

📊 QUANTIFY-RESULTS: File created/opened: YES/NO

### **Step 2: Define Message Extraction Transform**

🛑 EXECUTE-NOW: Add extract_message_content_by_role transform

```yaml
# Transforms - Data Processing Functions
# Generated as Python code at build time

extract_message_content_by_role:
  type: "message_extraction"
  description: "Extract message content organized by role (user, assistant, system)"
  parameters:
    messages_field: "messages"  # Field containing message array
    role_field: "role"  # Field in each message containing role
    content_field: "content"  # Field in each message containing content
    separator: "\\n\\n"  # Separator for multiple messages (escaped for YAML)
  output:
    user_messages: "Concatenated user messages"
    assistant_messages: "Concatenated assistant messages"
    system_messages: "Concatenated system messages"
  implementation: "python"  # Code generated at build time
```

**⚠️ CRITICAL**: Escape special characters (e.g., `\\n\\n` for newlines)

📊 QUANTIFY-RESULTS: Message extraction transform defined: YES/NO

### **Step 3: Define Additional Message Transforms (if needed)**

🛑 EXECUTE-NOW: Add provider-specific message transforms

Based on Phase 2 verification, if messages have unique structure:

```yaml
# Example: If provider uses different message structure
extract_message_array:
  type: "array_extraction"
  description: "Extract messages from nested array structure"
  parameters:
    source_field: "messages"
    target_fields: ["role", "content"]
  implementation: "python"
```

📊 COUNT-AND-DOCUMENT: Additional message transforms: [NUMBER]

### **Step 4: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/transforms.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 5: Document Message Transforms**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Transforms - Message Extraction**

**Message Extraction Transform**:
- Name: `extract_message_content_by_role`
- Purpose: Organize messages by role
- Parameters: messages_field, role_field, content_field, separator
- Output: user_messages, assistant_messages, system_messages

**Additional Transforms**: [COUNT]
[List any provider-specific message transforms]

**Implementation**: Python code generated at build time
```

📊 QUANTIFY-RESULTS: Message transforms documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Message Extraction Complete
- [ ] transforms.yaml created ✅/❌
- [ ] extract_message_content_by_role defined ✅/❌
- [ ] Special characters properly escaped ✅/❌
- [ ] YAML compiles ✅/❌
- [ ] Transforms documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If YAML syntax errors present

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 7.1 → Message extraction transform defined
🎯 NEXT-MANDATORY: [finish-reason-normalization.md](finish-reason-normalization.md)
