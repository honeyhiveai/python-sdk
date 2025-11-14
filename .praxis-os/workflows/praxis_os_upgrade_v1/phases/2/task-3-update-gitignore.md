# Update .gitignore

**Phase:** 2  
**Purpose:** Ensure .gitignore has current prAxIs OS entries  

---

## Objective

Update the target project's `.gitignore` with current prAxIs OS requirements from standards to prevent committing ~2.7GB of ephemeral files.

---

## Read Requirements from Standards

```python
import re

# Read canonical gitignore requirements
standards_file = ".praxis-os/standards/universal/installation/gitignore-requirements.md"

with open(standards_file, "r") as f:
    content = f.read()

# Extract code block with required entries
# Look for ```gitignore block under "Required Entries"
match = re.search(r'```gitignore\n(.*?)\n```', content, re.DOTALL)

if not match:
    print("❌ Could not find gitignore entries in standards")
    exit(1)

required_section = match.group(1)
print(f"✅ Loaded requirements from standards")
```

---

## Extract Individual Patterns

```python
# Parse patterns from the standards section
lines = required_section.split("\n")
required_patterns = []
header_line = None

for line in lines:
    stripped = line.strip()
    if stripped.startswith("#"):
        if "Agent OS" in stripped:
            header_line = stripped
    elif stripped:  # Non-empty, non-comment
        required_patterns.append(stripped)

print(f"Found {len(required_patterns)} required patterns")
for p in required_patterns:
    print(f"  - {p}")
```

---

## Check Target .gitignore

```python
# Read or create target .gitignore
if not os.path.exists(".gitignore"):
    print("⚠️  No .gitignore found, creating...")
    with open(".gitignore", "w") as f:
        f.write("# Created during prAxIs OS upgrade\n")
    target_content = ""
else:
    with open(".gitignore", "r") as f:
        target_content = f.read()
    print("✅ Target .gitignore exists")
```

---

## Determine Missing Entries

```python
missing = [p for p in required_patterns if p not in target_content]

if not missing:
    print("✅ All required entries present in .gitignore")
else:
    print(f"⚠️  Missing {len(missing)} entries:")
    for p in missing:
        print(f"   {p}")
```

---

## Append Missing Entries

```python
if missing:
    with open(".gitignore", "a") as f:
        # Ensure proper spacing
        if not target_content.endswith("\n\n"):
            if not target_content.endswith("\n"):
                f.write("\n")
            f.write("\n")
        
        # Add header if this is first prAxIs OS section
        if "# Agent OS" not in target_content and header_line:
            f.write(f"{header_line}\n")
        
        # Add missing entries
        for entry in missing:
            f.write(f"{entry}\n")
    
    print(f"✅ Added {len(missing)} entries to .gitignore")
```

---

## Verify (if git available)

```bash
# Optional: Test if patterns work
git check-ignore .praxis-os/.cache/test 2>/dev/null && echo "✅ Cache ignored"
git check-ignore .praxis-os.backup.test 2>/dev/null && echo "✅ Backups ignored"
```

---

## Completion Criteria

- [ ] Standards file read successfully ✅/❌
- [ ] Required patterns extracted ✅/❌
- [ ] Missing entries identified ✅/❌
- [ ] Entries appended to .gitignore ✅/❌

---

## Evidence

**Patterns from standards:** [count]  
**Missing in target:** [count]  
**Added to .gitignore:** [count]

---

## Next Step

🎯 NEXT-MANDATORY: [task-4-verify-checksums.md](task-4-verify-checksums.md)
