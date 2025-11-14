# Spec Lifecycle Organization Standard

## 🚨 TL;DR - Spec Lifecycle Organization Quick Reference

**Keywords for search**: spec status, specification lifecycle, where to put specs, spec review, approved specs, completed specs, spec tracking, spec organization, specification status management, where specs go by status, spec buckets, spec state transitions, .praxis-os/specs organization, spec directory structure, how to track spec status

**Core Principle:** Spec status should be explicit in the file system. Using `specs/{review/, approved/, completed/}` provides clear lifecycle tracking without additional tooling, enabling both AI agents and humans to quickly discover specs by status.

**The Spec Lifecycle Pattern (3 Status Buckets):**
1. **review/** - New specs waiting for human approval (Phase 2 output)
2. **approved/** - Specs approved for implementation (ready for Phase 3)
3. **completed/** - Specs with finished implementations (archived for reference)

**Spec Lifecycle Checklist:**
- [ ] New specs start in `specs/review/YYYY-MM-DD-name/`
- [ ] After user approval, move to `specs/approved/YYYY-MM-DD-name/`
- [ ] After implementation complete, move to `specs/completed/YYYY-MM-DD-name/`
- [ ] Status transitions done via `git mv` (preserves history)
- [ ] Query this standard before creating or moving specs

**Common Anti-Patterns:**
- ❌ Creating specs in flat `specs/` root (no status tracking)
- ❌ Using external tools to track status (file system is source of truth)
- ❌ Leaving completed specs in `approved/` (archive after implementation)
- ❌ Moving specs without using `git mv` (breaks history)

**When to Query This Standard:**
- Creating new spec → `pos_search_project(content_type="standards", query="where to create new specification")`
- After spec approval → `pos_search_project(content_type="standards", query="spec approved where to move")`
- After implementation → `pos_search_project(content_type="standards", query="spec completed archive lifecycle")`
- Checking spec status → `pos_search_project(content_type="standards", query="spec status tracking organization")`

---

## 🎯 Purpose

Define lifecycle-based organization for specifications in `.praxis-os/specs/` using status subdirectories (`review/`, `approved/`, `completed/`) to provide explicit, discoverable spec state tracking without additional tooling. This standard ensures AI agents and developers can quickly determine spec status through file system structure.

---

## ❌ The Problem (What Happens Without This Standard)

**Without spec lifecycle organization:**

1. **No status visibility** - Can't distinguish specs in review from specs ready to implement from completed specs
2. **Discovery friction** - AI agents and humans must scan all specs to find what needs action
3. **Unclear handoffs** - No explicit approval mechanism between spec creation and implementation
4. **Ad-hoc tracking** - Teams create external systems (like `.current-spec` files) to track what should be structural
5. **Poor lifecycle management** - Completed specs mixed with active work, creating noise

**Real example:** Current `.praxis-os/specs/` has flat structure with no status indication. `.current-spec` file exists as ad-hoc workaround, but isn't a standard and doesn't provide lifecycle management.

**Missing capabilities:**
- "What specs need my review?" → `ls specs/review/`
- "What can I implement?" → `ls specs/approved/`
- "What's been completed?" → `ls specs/completed/`

---

## 📋 The Standard

### Where Does This Spec Go Based on Status?

**Decision Tree for AI Agents:**

```
┌─ Is this a NEW spec from Phase 2 (just created)?
│  └─ YES → .praxis-os/specs/review/YYYY-MM-DD-name/
│  
├─ Has user APPROVED this spec for implementation?
│  └─ YES → Move to specs/approved/YYYY-MM-DD-name/
│
├─ Is Phase 3 implementation COMPLETE (tests passing, code deployed)?
│  └─ YES → Move to specs/completed/YYYY-MM-DD-name/
│
└─ Is this a temporary design doc (NOT formal spec yet)?
   └─ YES → workspace/design/ (see workspace-organization.md)
```

### Spec Directory Structure by Lifecycle

```
.praxis-os/specs/
├── review/                          # New specs awaiting approval
│   ├── 2025-10-21-feature-a/
│   │   ├── README.md
│   │   ├── srd.md
│   │   ├── specs.md
│   │   ├── tasks.md
│   │   └── implementation.md
│   └── 2025-10-22-feature-b/
│       └── [5 spec files]
│
├── approved/                        # Specs approved for implementation
│   └── 2025-10-20-feature-c/
│       └── [5 spec files]
│
└── completed/                       # Finished implementations
    ├── 2025-10-15-feature-d/
    │   └── [5 spec files]
    └── 2025-10-18-feature-e/
        └── [5 spec files]
```

### Mandatory Spec Lifecycle Rules

**For AI Agents:**

✅ **DO:**
- Create new specs in `specs/review/YYYY-MM-DD-name/`
- Use `git mv` for status transitions (preserves history)
- Move to `approved/` only after explicit user approval
- Move to `completed/` after Phase 3 complete (tests passing, code working)
- Query this standard before creating or moving specs
- List directory to find specs by status

❌ **DON'T:**
- Create specs in flat `specs/` root (use status subdirectories)
- Move specs without user approval or completion confirmation
- Use `mv` instead of `git mv` (breaks history tracking)
- Leave completed specs in `approved/` (archive properly)
- Skip status transitions (every spec has a lifecycle)
- Create external tracking systems (file system is source of truth)

🚫 **FRAMEWORK-VIOLATION: Creating specs outside status subdirectories**

Creating formal specifications anywhere except `specs/{review,approved,completed}/` defeats the purpose of lifecycle tracking and makes status discovery impossible.

**Correct:**
```bash
.praxis-os/specs/review/2025-10-21-auth-system/
.praxis-os/specs/approved/2025-10-20-cache-refactor/
.praxis-os/specs/completed/2025-10-15-api-upgrade/
```

**Wrong:**
```bash
.praxis-os/specs/2025-10-21-auth-system/  # ❌ No status bucket
.praxis-os/specs/in-progress/             # ❌ Not a standard status
.praxis-os/specs/archived/                # ❌ Use completed/, not archived/
```

### Spec Lifecycle State Transitions

**Phase 2 → Review Status:**

```
1. SPEC CREATION (Phase 2 complete)
   └─ Agent completes spec creation workflow
   └─ Creates: specs/review/YYYY-MM-DD-name/
   └─ Status: Awaiting human review and approval

2. PRESENT TO USER
   └─ "Spec created at specs/review/YYYY-MM-DD-name/"
   └─ "Review the specification for approval"
   └─ Wait for user response
```

**Review → Approved Status:**

```
3. USER APPROVAL TRIGGER
   └─ User says: "Approved" OR "Implement the spec" OR "Build it"
   └─ Explicit human approval required (NOT auto-advancing)

4. STATUS TRANSITION
   └─ Agent executes: git mv specs/review/YYYY-MM-DD-name specs/approved/YYYY-MM-DD-name
   └─ Status: Ready for Phase 3 implementation
   └─ Agent proceeds to Phase 3 workflow
```

**Approved → Completed Status:**

```
5. IMPLEMENTATION (Phase 3)
   └─ Agent implements from specs/approved/YYYY-MM-DD-name/
   └─ Writes production code
   └─ Creates tests
   └─ Validates quality (tests passing, linter clean)

6. COMPLETION VALIDATION
   └─ All tests passing
   └─ All linter checks clean
   └─ Code deployed/merged
   └─ Implementation complete

7. ARCHIVE TRANSITION
   └─ Agent executes: git mv specs/approved/YYYY-MM-DD-name specs/completed/YYYY-MM-DD-name
   └─ Status: Historical reference
   └─ Spec preserved for future reference
```

**Status Retention Policy:**

- **review/**: Keep until approved or rejected
- **approved/**: Keep until implementation complete
- **completed/**: Keep indefinitely (historical reference)
- **Never delete specs** (they document decisions)

### Status-Based Discovery Patterns

**For AI Agents to Find Specs by Status:**

```python
# Find specs needing review
pos_search_project(content_type="standards", query="specs in review waiting for approval")
# Then: list_dir("specs/review/")

# Find specs ready to implement
pos_search_project(content_type="standards", query="approved specs ready to build")
# Then: list_dir("specs/approved/")

# Find completed specs for reference
pos_search_project(content_type="standards", query="completed specs historical reference")
# Then: list_dir("specs/completed/")
```

**For Humans to Triage Work:**

```bash
# What needs my approval?
ls .praxis-os/specs/review/

# What can be implemented?
ls .praxis-os/specs/approved/

# What's been done?
ls .praxis-os/specs/completed/
```

---

## ✅ Spec Lifecycle Checklist

**Before Creating New Spec (Phase 2):**
- [ ] Queried spec lifecycle organization standard
- [ ] Confirmed Phase 1 design complete (user triggered "create spec")
- [ ] Ready to create in `specs/review/YYYY-MM-DD-name/`

**During Spec Creation:**
- [ ] Creating in `specs/review/` subdirectory
- [ ] Using standard structure (README, srd, specs, tasks, implementation)
- [ ] Following spec creation workflow
- [ ] NOT auto-advancing to implementation

**After Spec Created (Waiting for Approval):**
- [ ] Presented spec location to user
- [ ] Waiting for explicit approval trigger
- [ ] Spec remains in `specs/review/`
- [ ] NOT moving to `approved/` without user consent

**After User Approval:**
- [ ] User explicitly said "Approved" or "Implement" or "Build it"
- [ ] Used `git mv` to move to `specs/approved/`
- [ ] Proceeding to Phase 3 implementation workflow
- [ ] Working from `specs/approved/` location

**After Implementation Complete:**
- [ ] All tests passing
- [ ] Linter checks clean
- [ ] Code deployed/merged
- [ ] Used `git mv` to move to `specs/completed/`
- [ ] Spec archived for historical reference

---

## 📚 Examples

### Example 1: Complete Spec Lifecycle

**Scenario:** Building authentication system through full lifecycle

**Phase 1: Design (workspace)**
```bash
# Conversational design exploration
.praxis-os/workspace/design/2025-10-21-auth-system.md
# User iterates with feedback
```

**Phase 2: Spec Creation (review status)**
```bash
# User says: "Create the spec"

# Agent queries workflow
pos_search_project(content_type="standards", query="how to create specification")

# Agent creates formal spec
.praxis-os/specs/review/2025-10-21-auth-system/
├── README.md
├── srd.md
├── specs.md
├── tasks.md
└── implementation.md

# Agent presents to user
"Spec created at specs/review/2025-10-21-auth-system/"
"Review and approve when ready for implementation"

# Clean up workspace
rm .praxis-os/workspace/design/2025-10-21-auth-system.md
```

**Approval Transition:**
```bash
# User reviews and says: "Approved, implement it"

# Agent moves spec
git mv specs/review/2025-10-21-auth-system \
       specs/approved/2025-10-21-auth-system

# Status now: Ready for Phase 3
```

**Phase 3: Implementation (approved status)**
```bash
# Agent implements from specs/approved/2025-10-21-auth-system/
# Writes code, tests, documentation
# Validates quality
```

**Completion Transition:**
```bash
# All tests passing, implementation complete

# Agent moves spec
git mv specs/approved/2025-10-21-auth-system \
       specs/completed/2025-10-21-auth-system

# Status now: Historical reference
```

### Example 2: Multiple Specs at Different Stages

**Scenario:** Managing portfolio of specs

```bash
.praxis-os/specs/
├── review/
│   ├── 2025-10-21-oauth-integration/    # Awaiting approval
│   └── 2025-10-22-rate-limiting/        # Awaiting approval
│
├── approved/
│   ├── 2025-10-20-cache-refactor/       # Being implemented
│   └── 2025-10-21-api-versioning/       # Next in queue
│
└── completed/
    ├── 2025-10-15-user-management/      # Done
    └── 2025-10-18-logging-system/       # Done
```

**AI Agent Discovery:**
```python
# "What should I implement next?"
pos_search_project(content_type="standards", query="approved specs ready to implement")
list_dir("specs/approved/")
# Result: cache-refactor (oldest), api-versioning

# "What's waiting for review?"
list_dir("specs/review/")
# Result: oauth-integration, rate-limiting
```

**Human Discovery:**
```bash
# Quick status check
ls specs/review/      # 2 specs need approval
ls specs/approved/    # 2 specs ready to build
ls specs/completed/   # 2 specs finished
```

### Example 3: Status Transition Commands

**Creating New Spec:**
```bash
# Phase 2 output
mkdir -p .praxis-os/specs/review/2025-10-21-feature-name
cd .praxis-os/specs/review/2025-10-21-feature-name

# Create 5 spec files
touch README.md srd.md specs.md tasks.md implementation.md
```

**Moving to Approved:**
```bash
# After user approval
git mv .praxis-os/specs/review/2025-10-21-feature-name \
       .praxis-os/specs/approved/2025-10-21-feature-name

git commit -m "Approve spec: feature-name for implementation"
```

**Moving to Completed:**
```bash
# After implementation complete
git mv .praxis-os/specs/approved/2025-10-21-feature-name \
       .praxis-os/specs/completed/2025-10-21-feature-name

git commit -m "Complete implementation of feature-name"
```

### Example 4: Discovering Specs by Status

**AI Agent Query Patterns:**
```python
# Starting new work
pos_search_project(content_type="standards", query="what specs are approved for implementation")
list_dir("specs/approved/")

# Checking review queue
pos_search_project(content_type="standards", query="specs waiting for approval")
list_dir("specs/review/")

# Finding reference implementations
pos_search_project(content_type="standards", query="completed specs similar to authentication")
list_dir("specs/completed/")
# Then search within for relevant specs
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Creating Specs in Flat Root

**Symptom:** Creating specs in `specs/` without status subdirectory

**Problem:**
- No status tracking
- Can't distinguish review from approved from completed
- Recreates the original problem this standard solves

**Example of Wrong Approach:**
```bash
❌ .praxis-os/specs/2025-10-21-feature/
❌ .praxis-os/specs/my-feature/
❌ .praxis-os/specs/YYYY-MM-DD-name/
```

**Correct Approach:**
```bash
✅ .praxis-os/specs/review/2025-10-21-feature/        # New spec
✅ .praxis-os/specs/approved/2025-10-20-feature/      # Approved
✅ .praxis-os/specs/completed/2025-10-15-feature/     # Done
```

---

### Anti-Pattern 2: Moving Without Git

**Symptom:** Using `mv` instead of `git mv` for status transitions

**Problem:**
- Breaks git history tracking
- Appears as delete + create instead of move
- Loses commit history association

**Example of Wrong Approach:**
```bash
❌ mv specs/review/2025-10-21-feature specs/approved/2025-10-21-feature
❌ # Git sees this as: deleted file, new untracked file
```

**Correct Approach:**
```bash
✅ git mv specs/review/2025-10-21-feature specs/approved/2025-10-21-feature
✅ git commit -m "Approve spec: feature for implementation"
✅ # Git tracks this as a move, preserves history
```

---

### Anti-Pattern 3: Auto-Advancing Without Approval

**Symptom:** Moving specs to `approved/` without explicit user trigger

**Problem:**
- Violates phase boundary (Phase 2 → Phase 3 requires human approval)
- Implements specs without review
- Defeats purpose of approval workflow

**Example of Wrong Approach:**
```bash
❌ # Agent completes Phase 2
❌ git mv specs/review/2025-10-21-X specs/approved/2025-10-21-X
❌ # Agent immediately starts Phase 3
❌ # User never got chance to review!
```

**Correct Approach:**
```bash
✅ # Agent completes Phase 2
✅ # Spec stays in specs/review/
✅ # Agent says: "Spec created, awaiting your approval"
✅ # User reviews, then says: "Approved, implement it"
✅ # NOW agent moves to approved/ and proceeds to Phase 3
```

---

### Anti-Pattern 4: Leaving Specs in Wrong Status

**Symptom:** Completed implementations still in `approved/` subdirectory

**Problem:**
- Approved queue cluttered with finished work
- Can't see what's actually ready to implement vs done
- Defeats purpose of lifecycle tracking

**Example of Wrong Approach:**
```bash
❌ # Implementation finished, tests passing, code deployed
❌ # But spec still in approved/:
specs/approved/2025-10-15-feature/  # Should be in completed/
```

**Correct Approach:**
```bash
✅ # After implementation complete:
git mv specs/approved/2025-10-15-feature \
       specs/completed/2025-10-15-feature
git commit -m "Complete implementation of feature"
```

---

### Anti-Pattern 5: Creating Custom Status Subdirectories

**Symptom:** Inventing new status subdirectories beyond review/approved/completed

**Problem:**
- Breaks standard query patterns
- Other AI agents won't know about custom statuses
- Overcomplicated lifecycle

**Example of Wrong Approach:**
```bash
❌ specs/in-progress/       # Use approved/
❌ specs/on-hold/           # Move back to review/
❌ specs/rejected/          # Delete or keep in review/ with note
❌ specs/archived/          # Use completed/
❌ specs/needs-revision/    # Keep in review/
```

**Correct Approach:**
```bash
✅ specs/review/            # New or needs-revision
✅ specs/approved/          # Approved and in-progress
✅ specs/completed/         # Finished (what you might call "archived")
```

---

## 🔍 Questions This Answers

- **Where do I create new specs?** → `specs/review/YYYY-MM-DD-name/`
- **How do I track spec status?** → File system location indicates status
- **Where are specs waiting for approval?** → `specs/review/`
- **Where are specs ready to implement?** → `specs/approved/`
- **Where are completed implementations?** → `specs/completed/`
- **How do I move spec after approval?** → `git mv specs/review/X specs/approved/X`
- **When do I move specs to completed?** → After Phase 3 complete (tests passing, code working)
- **Can I create custom status directories?** → No, use review/approved/completed only
- **How do I find what to work on next?** → `ls specs/approved/` (chronologically sorted)
- **What happened to flat specs/ structure?** → Now organized by lifecycle status

---

## 🔗 Integration with prAxIs OS Development Process

**Phase 1: Conversational Design**
- ✅ Work in `workspace/design/YYYY-MM-DD-feature.md`
- ✅ NOT creating formal spec yet
- ✅ Iterating with user feedback

**Phase 2: Structured Spec Creation**
- ✅ User triggers: "Create the spec"
- ✅ Agent creates in `specs/review/YYYY-MM-DD-feature/`
- ✅ Agent presents for approval
- ✅ Wait for explicit approval (NOT auto-advancing)

**Phase 2 → Phase 3 Transition (CRITICAL):**
- ✅ User approves: "Approved" or "Implement it"
- ✅ Agent moves: `git mv specs/review/X specs/approved/X`
- ✅ Agent proceeds to Phase 3 workflow
- ✅ Now implementing from `specs/approved/X/`

**Phase 3: Structured Implementation**
- ✅ Work from `specs/approved/YYYY-MM-DD-feature/`
- ✅ Implement code, tests, documentation
- ✅ Validate quality (tests passing, linter clean)

**Phase 3 Complete:**
- ✅ Agent moves: `git mv specs/approved/X specs/completed/X`
- ✅ Spec archived for historical reference
- ✅ Implementation documented in git history

**Related Standards:**
- `agent-os-development-process.md` - Three-phase development workflow
- `workspace-organization.md` - Temporary design docs before formal specs
- `creating-specs.md` (usage/) - How to create spec structure

---

## 🛠️ How AI Agents Should Use Spec Lifecycle

### When Starting New Spec (Phase 2)

1. **Query for guidance:**
```python
pos_search_project(content_type="standards", query="where to create new specification")
pos_search_project(content_type="standards", query="spec lifecycle organization")
```

2. **Check Phase 1 complete:**
```bash
# User should have triggered "create the spec"
# Design doc should exist in workspace/design/
```

3. **Create in review status:**
```bash
mkdir -p .praxis-os/specs/review/YYYY-MM-DD-feature-name
cd .praxis-os/specs/review/YYYY-MM-DD-feature-name
# Create 5 spec files...
```

4. **Present for approval:**
```
"Spec created at specs/review/YYYY-MM-DD-feature-name/"
"Review the specification and approve when ready for implementation"
```

### After Receiving Approval

1. **Verify approval trigger:**
```
User said: "Approved" OR "Implement the spec" OR "Build it"
```

2. **Move to approved status:**
```bash
git mv specs/review/YYYY-MM-DD-feature-name \
       specs/approved/YYYY-MM-DD-feature-name
git commit -m "Approve spec: feature-name for implementation"
```

3. **Query implementation workflow:**
```python
pos_search_project(content_type="standards", query="how to execute specification")
pos_search_project(content_type="standards", query="Phase 3 implementation workflow")
```

4. **Proceed to Phase 3:**
```
Now implementing from specs/approved/YYYY-MM-DD-feature-name/
```

### After Implementation Complete

1. **Validate completion:**
```bash
# All tests passing?
# Linter clean?
# Code deployed/merged?
```

2. **Move to completed status:**
```bash
git mv specs/approved/YYYY-MM-DD-feature-name \
       specs/completed/YYYY-MM-DD-feature-name
git commit -m "Complete implementation of feature-name"
```

### For Discovering Work

**What needs review?**
```bash
ls .praxis-os/specs/review/
```

**What can I implement?**
```bash
ls .praxis-os/specs/approved/
```

**What's already done?**
```bash
ls .praxis-os/specs/completed/
```

---

## ✅ Validation and Compliance

**Pre-commit Spec Status Check:**
```bash
# Verify no specs in flat root
ls .praxis-os/specs/*.md 2>/dev/null && echo "❌ Specs in wrong location!"

# Check status subdirectories exist
test -d .praxis-os/specs/review && echo "✅ review/"
test -d .praxis-os/specs/approved && echo "✅ approved/"
test -d .praxis-os/specs/completed && echo "✅ completed/"
```

**Audit Spec Lifecycle Compliance:**
```bash
# Check for specs in wrong location
find .praxis-os/specs -maxdepth 1 -type d ! -name specs ! -name review ! -name approved ! -name completed

# Should return nothing (only status subdirectories)
```

**Spec Status Report:**
```bash
echo "Review queue: $(ls .praxis-os/specs/review/ | wc -l) specs"
echo "Ready to implement: $(ls .praxis-os/specs/approved/ | wc -l) specs"
echo "Completed: $(ls .praxis-os/specs/completed/ | wc -l) specs"
```

**Verify Git History Preserved:**
```bash
# Check that moves used git mv (not mv)
git log --follow specs/approved/YYYY-MM-DD-name/README.md
# Should show history from review/ status
```

---

## 📝 Maintenance

**Review Trigger:** Quarterly or when spec workflow changes

**Update Scenarios:**
- Phase boundary changes in development process
- New spec types requiring different lifecycle
- Integration with project management tools

**Migration from Flat Structure:**
```bash
# If existing specs in flat root:
mkdir -p .praxis-os/specs/review .praxis-os/specs/approved .praxis-os/specs/completed

# Triage each spec by status:
# - Needs review? → git mv to review/
# - Approved? → git mv to approved/  
# - Done? → git mv to completed/
```

**Version:** 1.0.0  
**Last Updated:** 2025-10-21  
**Author:** AI-assisted design with user validation  
**Status:** Active

