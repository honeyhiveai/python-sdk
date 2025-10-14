# Execute Upgrade

**Phase:** 2  
**Purpose:** Execute actual upgrade of .agent-os content  

---

## Objective

Safely upgrade .agent-os content from universal/ directory while preserving user-created content.

---

## ⚠️ CRITICAL SAFETY RULES

**NEVER use `--delete` flag on user-writable directories!**

### Directories Classification

**System-Managed (CAN use --delete)**:
- `.agent-os/standards/universal/` - Agent OS owns this
- `.agent-os/workflows/` - Agent OS workflow definitions

**User-Writable (NEVER --delete)**:
- `.agent-os/usage/` - Users may add custom docs
- `.agent-os/specs/` - User specs (NEVER touch!)
- `.agent-os/standards/development/` - User-generated content

---

## Steps

### Step 1: Upgrade Standards (Safe with --delete)

```bash
# ✅ SAFE: Agent OS fully owns universal standards
rsync -av --delete universal/standards/ .agent-os/standards/universal/
```

**Why --delete is safe**: We fully own and control `standards/universal/`

---

### Step 2: Upgrade Usage Docs (NO --delete!)

```bash
# ✅ SAFE: Update Agent OS docs, preserve user docs
rsync -av universal/usage/ .agent-os/usage/
```

**Why NO --delete**: Users may have added custom documentation files

---

### Step 3: Upgrade Workflows (Safe with --delete)

```bash
# ✅ SAFE: Agent OS owns workflow definitions
rsync -av --delete universal/workflows/ .agent-os/workflows/
```

**Why --delete is safe**: Workflows are system-managed, users don't modify

---

### Step 4: Update Version Info

```bash
# Record upgrade
echo "version_updated=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .agent-os/VERSION.txt
echo "commit=$(git rev-parse --short HEAD)" >> .agent-os/VERSION.txt
echo "source=$SOURCE_PATH" >> .agent-os/VERSION.txt
```

---

### Step 5: Verify File Counts

```bash
# Verify upgrade
echo "Standards: $(find .agent-os/standards/universal -type f | wc -l) files"
echo "Usage: $(find .agent-os/usage -type f | wc -l) files"
echo "Workflows: $(find .agent-os/workflows -type f | wc -l) files"
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
