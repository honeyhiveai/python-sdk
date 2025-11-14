# Task 2: Read Input Document

**Phase**: 0 - Input Conversion & Preprocessing  
**Purpose**: Read input file contents into memory  
**Depends On**: Task 1 (input_path)  
**Feeds Into**: Task 3 (Extract from Design Document)

---

## Objective

Read the input file (design document or YAML definition) from the path determined in Task 1 and verify it's accessible and readable.

---

## Context

📊 **CONTEXT**: This task performs a simple file read operation. The actual parsing/processing happens in later tasks based on the file type.

---

## Instructions

### Step 1: Verify File Exists

Before reading, confirm the file exists at the specified path:

📖 **DISCOVER-TOOL**: Check if file exists

⚠️ **CONSTRAINT**: If file does not exist, this is a fatal error:

```
Error: Input file not found

Path: {input_path}

Please verify:
  • Path is correct
  • File exists at specified location
  • Permissions allow reading
```

🚨 **CRITICAL**: STOP if file not found. Cannot proceed without input.

### Step 2: Read File Contents

Read the complete file contents:

📖 **DISCOVER-TOOL**: Read file contents

Store the raw content for processing in subsequent tasks.

### Step 3: Verify Content Not Empty

⚠️ **CONSTRAINT**: File must contain content. Empty files cannot be processed.

If file is empty:
```
Error: Input file is empty

Path: {input_path}

Please provide a file with content:
  • Design document with problem statement, phases, tasks
  • YAML definition with required workflow structure
```

### Step 4: Record Success

Store the file contents and confirm successful read:
- `input_document_content`: Full file contents (string)
- `input_document_read`: True

---

## Expected Output

**Variables to Capture**:
- `input_document_content`: String (full file contents)
- `input_document_read`: Boolean (True)
- `input_document_size`: Integer (file size in bytes, for logging)

---

## Quality Checks

✅ File exists and accessible  
✅ File contents read successfully  
✅ Content not empty  
✅ Ready for parsing in next task

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-extract-from-design.md

↩️ **RETURN-TO**: phase.md (after task complete)

