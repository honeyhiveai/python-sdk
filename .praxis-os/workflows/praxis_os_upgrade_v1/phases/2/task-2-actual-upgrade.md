# Execute Upgrade

**Phase:** 2  
**Purpose:** Execute actual upgrade of .praxis-os content  

---

## Objective

Safely upgrade .praxis-os content from universal/ directory while preserving user-created content.

---

## ⚠️ CRITICAL SAFETY RULES

**NEVER use `--delete` flag on user-writable directories!**

### Directories Classification

**System-Managed (CAN use --delete)**:
- `.praxis-os/standards/universal/` - prAxIs OS owns this
- `.praxis-os/workflows/` - prAxIs OS workflow definitions

**User-Writable (NEVER --delete)**:
- `.praxis-os/usage/` - Users may add custom docs
- `.praxis-os/specs/` - User specs (NEVER touch!)
- `.praxis-os/standards/development/` - User-generated content

---

## Steps

### Step 1: Upgrade Standards (Safe with --delete)

```bash
# ✅ SAFE: prAxIs OS fully owns universal standards
rsync -av --delete universal/standards/ .praxis-os/standards/universal/
```

**Why --delete is safe**: We fully own and control `standards/universal/`

---

### Step 2: Upgrade Usage Docs (NO --delete!)

```bash
# ✅ SAFE: Update prAxIs OS docs, preserve user docs
rsync -av universal/usage/ .praxis-os/usage/
```

**Why NO --delete**: Users may have added custom documentation files

---

### Step 3: Upgrade Workflows (Safe with --delete)

```bash
# ✅ SAFE: prAxIs OS owns workflow definitions
rsync -av --delete universal/workflows/ .praxis-os/workflows/
```

**Why --delete is safe**: Workflows are system-managed, users don't modify

---

### Step 4: Update Version Info

```bash
# Record upgrade
echo "version_updated=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .praxis-os/VERSION.txt
echo "commit=$(git rev-parse --short HEAD)" >> .praxis-os/VERSION.txt
echo "source=$SOURCE_PATH" >> .praxis-os/VERSION.txt
```

---

### Step 5: Verify File Counts

```bash
# Verify upgrade
echo "Standards: $(find .praxis-os/standards/universal -type f | wc -l) files"
echo "Usage: $(find .praxis-os/usage -type f | wc -l) files"
echo "Workflows: $(find .praxis-os/workflows -type f | wc -l) files"
```

---

## Completion Criteria

🛑 VALIDATE-GATE: Upgrade Complete

- [ ] Standards upgraded successfully ✅/❌
- [ ] Usage docs updated (not deleted!) ✅/❌
- [ ] Workflows upgraded successfully ✅/❌
- [ ] Version info updated ✅/❌
- [ ] File counts verified ✅/❌
- [ ] User specs UNTOUCHED ✅/❌

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Upgrade Results

**Standards files:** [count]  
**Usage files:** [count]  
**Workflow files:** [count]  
**User specs preserved:** YES ✅  
**Upgrade timestamp:** [timestamp]

---

## Next Step

🎯 NEXT-MANDATORY: [task-3-update-gitignore.md](task-3-update-gitignore.md)
