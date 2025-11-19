# Workspace Organization Standard

## 🚨 TL;DR - Workspace Organization Quick Reference

**Keywords for search**: workspace directory, temporary files, ephemeral content, where to put design docs, Phase 1 artifacts, uncommitted work, working documents, design-doc.md, draft documents, WIP files, temporary analysis, scratch notes, temporary screenshots, pos_browser output, verification images, workspace/, .praxis-os/workspace, where do temporary files go, ephemeral file organization, git pollution prevention

**Core Principle:** If a document is not ready to commit, it belongs in `.praxis-os/workspace/`. Workspace provides a designated location for all temporary development artifacts, preventing git pollution and maintaining clear separation between ephemeral and permanent content.

**The Workspace Pattern (3 Subdirectories):**
1. **design/** - Phase 1 conversational design explorations (before formal spec)
2. **analysis/** - Research, investigation, and comparison documents
3. **scratch/** - Experiments, session notes, and truly temporary content

**Workspace Usage Checklist:**
- [ ] Phase 1 design docs go in `.praxis-os/workspace/design/`
- [ ] Research/analysis goes in `.praxis-os/workspace/analysis/`
- [ ] Temporary notes go in `.praxis-os/workspace/scratch/`
- [ ] Files named with date prefix: `YYYY-MM-DD-topic.md`
- [ ] Files deleted or archived after promotion to formal spec
- [ ] `.praxis-os/workspace/` is .gitignored (never committed)

**Common Anti-Patterns:**
- ❌ Creating design docs in `.praxis-os/specs/` root
- ❌ Committing workspace content to git
- ❌ Skipping Phase 1 workspace and going directly to formal spec
- ❌ Leaving workspace files after formal spec created
- ❌ Saving temporary screenshots to `docs/static/img/` instead of `workspace/scratch/`

**When to Query This Standard:**
- Creating design document → `pos_search_project(content_type="standards", query="where to put design documents")`
- Starting Phase 1 → `pos_search_project(content_type="standards", query="workspace organization Phase 1")`
- Taking screenshots → `pos_search_project(content_type="standards", query="where do temporary screenshots go")`
- Cleaning up files → `pos_search_project(content_type="standards", query="workspace lifecycle ephemeral")`
- Checking git safety → `pos_search_project(content_type="standards", query="temporary files gitignore workspace")`

---

## 🎯 Purpose

Define rules for managing temporary development artifacts in `.praxis-os/workspace/` to prevent git pollution and maintain clean separation between ephemeral and permanent content. This standard ensures AI agents and developers have a clear, consistent location for work-in-progress documents that are not yet ready to commit.

---

## ❌ The Problem (What Happens Without This Standard)

**Without workspace organization:**

1. **Git pollution** - Temporary files scattered throughout `.praxis-os/specs/`, creating confusion about what is permanent vs ephemeral
2. **Accidental commits** - Committing 35+ design docs that should have been temporary (actual problem that motivated this standard)
3. **No clear lifecycle** - Uncertainty about when/where to create temporary documents
4. **Mixed artifacts** - Formal specifications mixed with draft explorations
5. **Poor discoverability** - AI agents don't know where to put temporary work
6. **Cleanup confusion** - Unclear what can be deleted vs what must be kept

**Real example:** `.praxis-os/specs/` accumulated 35+ temporary analysis files like `amplifier-agents-detailed-2025-10-20.md`, `cache-analysis-2025-10-13.md` at root level, mixing with formal spec directories.

---

## 📋 The Standard

### Where Does This File Go?

**Decision Tree for AI Agents:**

```
┌─ Is this a formal specification with structured directory?
│  └─ YES → .praxis-os/specs/YYYY-MM-DD-name/
│  
├─ Is this a standards document for RAG indexing?
│  └─ YES → .praxis-os/standards/
│
├─ Is this a completed workflow definition?
│  └─ YES → .praxis-os/workflows/
│
├─ Is this Phase 1 conversational design exploration?
│  └─ YES → .praxis-os/workspace/design/
│
├─ Is this temporary analysis, research, or investigation?
│  └─ YES → .praxis-os/workspace/analysis/
│
└─ Is this scratch notes, experiments, or WIP?
   └─ YES → .praxis-os/workspace/scratch/
```

### Workspace Directory Structure

```
.praxis-os/workspace/
├── README.md              # User-friendly lifecycle guide
├── design/                # Phase 1 conversational design
│   └── YYYY-MM-DD-*.md   # Design explorations
├── analysis/              # Research and investigation
│   └── YYYY-MM-DD-*.md   # Analysis documents
└── scratch/               # Experiments and temporary notes
    └── *.md              # Any temporary content
```

### Mandatory Workspace Rules

**For AI Agents:**

✅ **DO:**
- Create Phase 1 design docs in `.praxis-os/workspace/design/`
- Use `.praxis-os/workspace/analysis/` for research documents
- Use `.praxis-os/workspace/scratch/` for experiments and notes
- Name files with dates: `YYYY-MM-DD-topic.md`
- Include "DRAFT" or "WIP" in document headers
- Clean up after promoting to formal spec
- Query this standard before creating temporary files

❌ **DON'T:**
- Commit workspace/ content (it's .gitignored)
- Create formal specs in workspace/
- Store permanent reference material in workspace/
- Leave workspace files after formal spec created
- Create workspace files outside these three subdirs
- Skip Phase 1 workspace and go directly to formal spec

🚫 **FRAMEWORK-VIOLATION: Creating ephemeral files outside workspace/**

Creating temporary design docs, analysis, or WIP files anywhere except `.praxis-os/workspace/` defeats the purpose of separation and risks git pollution.

**Correct:**
```bash
.praxis-os/workspace/design/2025-10-21-auth-system.md
.praxis-os/workspace/analysis/2025-10-21-cache-comparison.md
```

**Wrong:**
```bash
.praxis-os/specs/auth-system-draft.md  # ❌ Not in workspace
.praxis-os/design-notes.md             # ❌ Wrong location
./working-doc.md                      # ❌ Root pollution
```

### Workspace Lifecycle Management

**Phase 1 → Phase 2 Transition:**

```
1. EXPLORATION (Phase 1)
   └─ Create: .praxis-os/workspace/design/2025-10-21-feature.md
   └─ Iterate with user through conversation
   └─ Refine approach based on feedback

2. TRIGGER ("create the spec")
   └─ User explicitly approves formalization
   └─ Phase 1 complete

3. FORMALIZATION (Phase 2)
   └─ Create: .praxis-os/specs/2025-10-21-feature/
   └─ Extract insights from workspace doc
   └─ Create structured spec files (srd.md, specs.md, etc.)

4. CLEANUP
   └─ Delete .praxis-os/workspace/design/2025-10-21-feature.md
   └─ OR move to specs/2025-10-21-feature/supporting-docs/
   └─ Purpose served, formal spec is source of truth
```

**Workspace Retention Policy:**

- **Delete after formalization** (preferred)
- **Archive in spec's supporting-docs/** (if historical context valuable)
- **Never commit** (workspace/ is .gitignored)

### Subdirectory Purposes

**design/** - Phase 1 conversational design before formal spec
- Conversational design documents
- Trade-off analysis
- Approach proposals
- User feedback iterations

**analysis/** - Research and investigation
- Comparison documents (e.g., "amplifier vs agent-os")
- Technical research
- Performance analysis
- Security investigations
- Feasibility studies

**scratch/** - Temporary notes, experiments, and verification assets
- Session notes
- Quick experiments
- WIP documents
- Brainstorming notes
- Temporary screenshots (pos_browser verification, UI checks)
- Anything truly temporary

---

## ✅ Workspace Usage Checklist

**Before creating any document:**
- [ ] Queried workspace organization standard
- [ ] Determined correct location (workspace vs specs vs standards)
- [ ] Used correct subdirectory (design/analysis/scratch)
- [ ] Named file with date prefix (YYYY-MM-DD-*)
- [ ] Added DRAFT/WIP header if appropriate

**During Phase 1 (Conversational Design):**
- [ ] Working in `.praxis-os/workspace/design/` file
- [ ] Updating as conversation evolves
- [ ] NOT creating formal spec until user triggers
- [ ] Incorporating user feedback iteratively

**After "create the spec" Trigger:**
- [ ] Queried spec creation workflow
- [ ] Created formal spec directory
- [ ] Extracted insights from workspace doc
- [ ] Deleted workspace doc (or archived in supporting-docs/)
- [ ] Verified only formal spec remains

**Workspace Cleanup:**
- [ ] Checked for orphaned workspace files
- [ ] Deleted or archived files corresponding to formal specs
- [ ] Verified workspace/ not staged for commit

---

## 📚 Examples

### Example 1: Phase 1 Design Document Creation

**Scenario:** User says "Build an authentication system"

**Correct Approach:**
```bash
# Step 1: Query for guidance
pos_search_project(content_type="standards", query="where to put design documents")
pos_search_project(content_type="standards", query="Phase 1 conversational design")

# Step 2: Create workspace design doc
.praxis-os/workspace/design/2025-10-21-authentication-system.md

# Step 3: Iterate with user in Phase 1
# Document evolves through conversation

# Step 4: User says "create the spec"
# Now formalize into .praxis-os/specs/2025-10-21-authentication-system/

# Step 5: Delete workspace doc
rm .praxis-os/workspace/design/2025-10-21-authentication-system.md
```

### Example 2: Research Analysis

**Scenario:** Need to compare two approaches before deciding

**Correct Approach:**
```bash
# Create analysis document
.praxis-os/workspace/analysis/2025-10-21-cache-strategy-comparison.md

# Content:
## Redis vs In-Memory Caching

### Performance Analysis
[Research findings]

### Cost Analysis
[Comparison]

### Recommendation
[Decision with rationale]

# After decision made and incorporated into spec:
# Delete analysis document
```

### Example 3: Temporary Experiment

**Scenario:** Quick experiment to validate an approach

**Correct Approach:**
```bash
# Create scratch document
.praxis-os/workspace/scratch/2025-10-21-api-rate-limit-test.md

# After experiment complete and findings documented elsewhere:
# Delete scratch file
```

### Example 4: Temporary Screenshots

**Scenario:** Using pos_browser to verify component layout during development

**Correct Approach:**
```bash
# Take verification screenshots
pos_browser(screenshot_path=".praxis-os/workspace/scratch/component-before.png")
pos_browser(screenshot_path=".praxis-os/workspace/scratch/component-after.png")

# Compare, make decision, document findings

# After verification complete:
# Delete temporary screenshots
rm .praxis-os/workspace/scratch/component-*.png
```

**Wrong Approach:**
```bash
❌ pos_browser(screenshot_path="docs/static/img/temp-screenshot.png")
# Pollutes static assets with temporary verification images
```

### Example 5: File Naming Convention

**Correct:**
```bash
.praxis-os/workspace/design/2025-10-21-oauth-integration.md
.praxis-os/workspace/analysis/2025-10-21-database-performance.md
.praxis-os/workspace/scratch/2025-10-21-quick-test.md
```

**Wrong:**
```bash
.praxis-os/workspace/design/oauth.md              # ❌ No date
.praxis-os/workspace/oauth-design.md             # ❌ Wrong subdirectory
.praxis-os/workspace/design/DRAFT-oauth.md       # ❌ Date should be prefix
```

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Creating Design Docs in specs/ Root

**Symptom:** Creating temporary documents directly in `.praxis-os/specs/`

**Problem:**
- Mixes ephemeral with permanent content
- Risks accidental commit
- Pollutes formal spec directory

**Example of Wrong Approach:**
```bash
❌ .praxis-os/specs/feature-draft.md
❌ .praxis-os/specs/2025-10-21-feature-design.md
❌ .praxis-os/specs/auth-exploration.md
```

**Correct Approach:**
```bash
✅ .praxis-os/workspace/design/2025-10-21-feature.md
✅ (after "create spec") .praxis-os/specs/2025-10-21-feature/
```

---

### Anti-Pattern 2: Committing Workspace Content

**Symptom:** Attempting to `git add .praxis-os/workspace/`

**Problem:**
- Defeats purpose of ephemeral workspace
- Creates git pollution
- Confuses permanent vs temporary artifacts

**Example of Wrong Approach:**
```bash
❌ git add .praxis-os/workspace/
❌ git commit -m "Added design docs"
# This should fail due to .gitignore
```

**Correct Approach:**
```bash
✅ # Workspace is .gitignored automatically
✅ # Only commit formal specs in .praxis-os/specs/
git add .praxis-os/specs/2025-10-21-feature/
git commit -m "Add authentication system spec"
```

---

### Anti-Pattern 3: Skipping Phase 1 Workspace

**Symptom:** Going directly from user request to formal spec

**Problem:**
- Skips conversational design phase
- Misses opportunity for user feedback
- Creates specs without validation

**Example of Wrong Approach:**
```bash
❌ User: "Build feature X"
❌ Agent: *immediately creates .praxis-os/specs/2025-10-21-X/*
```

**Correct Approach:**
```bash
✅ User: "Build feature X"
✅ Agent: *creates workspace/design/2025-10-21-X.md*
✅ Agent: *iterates with user in Phase 1*
✅ User: "Create the spec"
✅ Agent: *now creates formal spec*
```

---

### Anti-Pattern 4: Leaving Orphaned Workspace Files

**Symptom:** Workspace files remaining after formal spec created

**Problem:**
- Duplicate content in two locations
- Confusion about source of truth
- Workspace bloat

**Example of Wrong Approach:**
```bash
❌ # Both exist simultaneously:
.praxis-os/workspace/design/2025-10-21-feature.md
.praxis-os/specs/2025-10-21-feature/
```

**Correct Approach:**
```bash
✅ # Only formal spec exists after formalization:
.praxis-os/specs/2025-10-21-feature/
# Workspace file deleted or archived in supporting-docs/
```

---

### Anti-Pattern 5: Wrong Subdirectory Usage

**Symptom:** Putting files in incorrect workspace subdirectory

**Problem:**
- Breaks semantic organization
- Makes discovery harder
- Violates clear purpose boundaries

**Example of Wrong Approach:**
```bash
❌ .praxis-os/workspace/scratch/2025-10-21-auth-design.md  # Should be design/
❌ .praxis-os/workspace/design/quick-experiment.md        # Should be scratch/
❌ .praxis-os/workspace/analysis/session-notes.md         # Should be scratch/
```

**Correct Approach:**
```bash
✅ .praxis-os/workspace/design/2025-10-21-auth-design.md   # Phase 1 design
✅ .praxis-os/workspace/scratch/quick-experiment.md        # Temporary test
✅ .praxis-os/workspace/analysis/2025-10-21-perf-study.md  # Research doc
```

---

## 🔍 Questions This Answers

- **Where do I put temporary design documents?** → `.praxis-os/workspace/design/`
- **Where do Phase 1 design explorations go?** → `.praxis-os/workspace/design/`
- **What do I do with design docs after creating formal spec?** → Delete or archive
- **Can I commit workspace files?** → No, `.praxis-os/workspace/` is .gitignored
- **Where do research and analysis documents go?** → `.praxis-os/workspace/analysis/`
- **Where do quick experiments and notes go?** → `.praxis-os/workspace/scratch/`
- **Where do temporary screenshots go?** → `.praxis-os/workspace/scratch/` (pos_browser verification, UI checks)
- **Where do permanent documentation images go?** → `docs/static/img/` (social cards, logos, committed assets)
- **How do I name workspace files?** → `YYYY-MM-DD-topic.md`
- **When do I clean up workspace files?** → After promoting to formal spec
- **What's the difference between workspace and specs?** → `.praxis-os/workspace/` = ephemeral, specs = permanent
- **How do I prevent git pollution with temporary files?** → Use `.praxis-os/workspace/` (it's .gitignored)

---

## 🔗 Integration with prAxIs OS Development Process

**Phase 1: Conversational Design**
- ✅ Create `.praxis-os/workspace/design/YYYY-MM-DD-feature.md`
- ✅ Iterate with user
- ✅ Wait for "create spec" trigger (NOT auto-advancing)

**Phase 2: Structured Spec**
- ✅ Create `.praxis-os/specs/YYYY-MM-DD-feature/`
- ✅ Extract insights from `.praxis-os/workspace/design/` file
- ✅ Delete `.praxis-os/workspace/design/` file (or archive in supporting-docs/)

**Phase 3: Structured Implementation**
- ✅ Work from formal spec only
- ✅ No workspace files needed

**Related Standards:**
- `agent-os-development-process.md` - Three-phase development workflow
- `gitignore-requirements.md` - Git safety and ephemeral content handling
- `rag-content-authoring.md` - Content optimization for discovery

---

## 🛠️ How AI Agents Should Use Workspace

### When Starting New Feature Work

1. **Query for existing context:**
```
pos_search_project(content_type="standards", query="where to put design documents")
pos_search_project(content_type="standards", query="workspace organization")
```

2. **Check if formal spec exists:**
```bash
ls .praxis-os/specs/ | grep feature-name
```

3. **Create Phase 1 design doc:**
```bash
.praxis-os/workspace/design/YYYY-MM-DD-feature-name.md
```

### During Conversational Design (Phase 1)

- Work in `.praxis-os/workspace/design/` file
- Update as conversation evolves
- Don't create formal spec until user triggers
- Incorporate feedback iteratively

### After "create the spec" Trigger

1. Query spec creation workflow
2. Create formal spec directory
3. Extract insights from workspace doc
4. Delete workspace doc (or archive)

### For Ad-Hoc Analysis

- Create in `.praxis-os/workspace/analysis/`
- Use for research, investigation, comparison
- Delete when insights incorporated elsewhere

### For Quick Experiments

- Create in `.praxis-os/workspace/scratch/`
- Use for temporary tests, notes, and verification screenshots
- Delete when no longer needed

---

## ✅ Validation and Compliance

**Pre-commit Check:**
```bash
git status --porcelain | grep ".praxis-os/workspace/"
# Should return nothing (workspace is .gitignored)
```

**Audit Command:**
```bash
# Check for orphaned workspace files
ls .praxis-os/workspace/design/
ls .praxis-os/specs/

# If design file date matches spec dir date → delete design file
```

**Workspace Health Check:**
```bash
# Should have clear subdirectories
ls .praxis-os/workspace/
# Expected: README.md design/ analysis/ scratch/

# Should NOT be in git
git ls-files .praxis-os/workspace/
# Expected: empty (nothing tracked)
```

---

## 📝 Maintenance

**Review Trigger:** Quarterly or when workspace patterns change

**Update Scenarios:**
- New subdirectory types needed
- Lifecycle changes to development process
- Integration with new workflow systems

**Version:** 1.0.0  
**Last Updated:** 2025-10-21  
**Author:** AI-assisted design with user validation  
**Status:** Active
