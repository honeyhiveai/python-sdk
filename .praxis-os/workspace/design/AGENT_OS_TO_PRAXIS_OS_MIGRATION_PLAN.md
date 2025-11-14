# Agent OS → praxis OS Migration Plan

**Purpose**: Consolidate learned knowledge from the Agent OS journey into the production praxis OS installation, enabling removal of the old .agent-os/ directory.

---

## 📊 Current State Analysis

### Agent OS (.agent-os/)
```
Standards: 362 files across 18 categories
├─ ai-assistant/: 230 files (BLOATED - learning iterations)
├─ universal/: 52 files (cross-project patterns)
├─ development/: 12 files (Python SDK specific)
├─ testing/: 10 files
├─ documentation/: 9 files
├─ coding/: 5 files
├─ meta-framework/: 5 files
├─ meta-workflow/: 5 files
├─ workflows/: 5 files
├─ ai-safety/: 5 files
├─ architecture/: 4 files
├─ concurrency/: 4 files
├─ failure-modes/: 4 files
├─ security/: 3 files
├─ installation/: 2 files
├─ performance/: 1 file
├─ database/: 1 file
└─ integration/: 0 files

Specs: ~28 spec directories (2025-09-02 through 2025-10-27)
- Completed specs with full execution history
- Contains the "learning journey" of building the SDK
```

### praxis OS (.praxis-os/)
```
Standards: 63 files across 2 categories
├─ universal/: 63 files (curated essentials, RAG-optimized)
│   ├─ ai-assistant/: 19 files
│   ├─ ai-safety/: 5 files
│   ├─ workflows/: 6 files
│   ├─ meta-workflow/: 5 files
│   ├─ documentation/: 4 files
│   ├─ architecture/: 4 files
│   ├─ concurrency/: 4 files
│   ├─ failure-modes/: 4 files
│   ├─ testing/: 4 files
│   ├─ installation/: 3 files
│   ├─ performance/: 1 file
│   ├─ database/: 1 file
│   ├─ security/: 1 files
│   ├─ operations/: 1 file
│   └─ universal/: 1 file
└─ development/: EMPTY (ready for project-specific content)

Specs: Empty directories (approved/, completed/, review/)
```

---

## 🎯 Migration Strategy

### Phase 1: Standards Migration

#### 1.1 Project-Specific Standards to Port
Port from `.agent-os/standards/development/` to `.praxis-os/standards/development/`:

**✅ Port with RAG optimization:**
1. `code-quality.md` → Python SDK specific quality gates
2. `environment-setup.md` → HoneyHive Python SDK env setup
3. `git-workflow.md` → SDK branching/release strategy
4. `release-process.md` → SDK release workflow
5. `testing-standards.md` → SDK-specific testing patterns
6. `version-bump-quick-reference.md` → SDK version management
7. `version-pinning-standards.md` → SDK dependency management
8. `specification-standards.md` → SDK spec standards
9. `performance-guidelines.md` → SDK performance targets
10. `production-code-universal-checklist.md` → SDK prod checklist

**🔧 Each file needs RAG optimization:**
- Add TL;DR section with keyword density
- Add "Questions This Answers" (20+ questions)
- Add "When to Query This Standard" table
- Add "Related Standards" with query workflow
- Optimize headers for natural queries
- Front-load critical information
- Test multi-angle queries

**❌ Skip (likely obsolete or duplicative):**
- `concurrency-analysis-protocol.md` (generic, likely in universal/)
- `failure-mode-analysis-template.md` (generic, likely in universal/)

#### 1.2 Universal Standards
**Do NOT port** - praxis OS already has curated universal/ standards:
- 230 Agent OS `ai-assistant/` files → 19 praxis OS files (distilled)
- Other categories already consolidated

#### 1.3 Validation
After porting each file:
```bash
# Test discoverability
pos_search_project(
    action="search_standards",
    query="[natural language query for this standard]"
)
# Should return in top 3 results
```

### Phase 2: Specs Migration

#### 2.1 All Specs Move to `completed/`
All Agent OS specs represent completed work, so migrate to `.praxis-os/specs/completed/`:

**Migration pattern:**
```bash
# Copy entire spec directory
cp -r .agent-os/specs/2025-MM-DD-feature-name/ \
      .praxis-os/specs/completed/2025-MM-DD-feature-name/
```

**Specs to migrate (~28 directories):**
- 2025-09-02-ai-validation-protocol
- 2025-09-02-cicd-gha-best-practices
- 2025-09-02-performance-optimization
- 2025-09-03-ai-assistant-quality-framework
- 2025-09-03-commit-message-standards
- 2025-09-03-date-usage-standards
- 2025-09-03-documentation-quality-control
- 2025-09-03-documentation-quality-prevention
- 2025-09-03-drop-project-from-tracer-init
- 2025-09-03-evaluation-to-experiment-alignment
- 2025-09-03-openinference-mcp-instrumentor
- 2025-09-03-zero-failing-tests-policy
- 2025-09-04-openllmetry-integration-alternatives
- 2025-09-04-pyproject-integration-titles
- 2025-09-05-compatibility-matrix-framework
- 2025-09-05-comprehensive-testing-strategy
- 2025-09-05-non-instrumentor-integrations
- 2025-09-05-real-api-testing-framework
- 2025-09-06-integration-testing-consolidation
- 2025-09-17-compatibility-matrix-enhancement
- 2025-10-02-langfuse-migration-doc
- 2025-10-03-agent-os-mcp-rag-evolution
- 2025-10-04-honeyhive-sdk-docs-mcp
- 2025-10-07-honeyhive-sdk-docs-mcp-v2
- 2025-10-08-documentation-p0-fixes
- 2025-10-17-simplified-attribute-routing
- 2025-10-27-baggage-enrich-hybrid-fix
- 2025-10-29-documentation-quality-verification

#### 2.2 Update Cross-References
Search for and update any references to `.agent-os/specs/` → `.praxis-os/specs/completed/`:
```bash
grep -r "\.agent-os/specs" .praxis-os/
# Update any found references
```

### Phase 3: RAG Index Rebuild

#### 3.1 Trigger Full Rebuild
```bash
# Restart MCP server to trigger index rebuild
# Server will detect new content and rebuild standards index
```

#### 3.2 Monitor Build
Check logs for:
- Standards index: Should include new `development/` files
- Workflow metadata: Should remain unchanged
- Code index: Should remain unchanged (no code moved)

### Phase 4: Validation

#### 4.1 Test Standards Queries
```python
# Test project-specific standards
pos_search_project(
    action="search_standards",
    query="HoneyHive Python SDK environment setup"
)

pos_search_project(
    action="search_standards",
    query="How to bump version in Python SDK"
)

pos_search_project(
    action="search_standards",
    query="Python SDK release process"
)

# Should return new development/ standards
```

#### 4.2 Verify Spec History
```bash
# Verify specs migrated correctly
ls -la .praxis-os/specs/completed/ | wc -l
# Should show ~28 directories

# Spot check a few specs
ls .praxis-os/specs/completed/2025-10-03-agent-os-mcp-rag-evolution/
# Should contain all original files
```

#### 4.3 Query Behavioral Metrics
```python
# Check server recognizes new content
pos_search_project(
    action="get_server_info",
    action_type="health"
)
# Should show updated file counts in standards index
```

### Phase 5: Cleanup

#### 5.1 Backup Agent OS
```bash
# Create archive before deletion
tar -czf .agent-os-backup-$(date +%Y%m%d).tar.gz .agent-os/
# Store somewhere safe (not in repo)
```

#### 5.2 Remove Agent OS Directory
```bash
rm -rf .agent-os/
```

#### 5.3 Update .cursorrules (if needed)
```bash
# Verify .cursorrules doesn't reference .agent-os/
grep -n "agent-os" .cursorrules
# Should find none (already updated to praxis OS)
```

#### 5.4 Update .gitignore (if needed)
```bash
# Remove any .agent-os/ entries if present
grep -n "agent-os" .gitignore
```

---

## 📋 Execution Checklist

### Standards Migration
- [ ] Create `.praxis-os/standards/development/` directory
- [ ] Port `code-quality.md` with RAG optimization
- [ ] Port `environment-setup.md` with RAG optimization
- [ ] Port `git-workflow.md` with RAG optimization
- [ ] Port `release-process.md` with RAG optimization
- [ ] Port `testing-standards.md` with RAG optimization
- [ ] Port `version-bump-quick-reference.md` with RAG optimization
- [ ] Port `version-pinning-standards.md` with RAG optimization
- [ ] Port `specification-standards.md` with RAG optimization
- [ ] Port `performance-guidelines.md` with RAG optimization
- [ ] Port `production-code-universal-checklist.md` with RAG optimization

### Specs Migration
- [ ] Migrate all 28 spec directories to `.praxis-os/specs/completed/`
- [ ] Update any cross-references from `.agent-os` → `.praxis-os`

### RAG & Validation
- [ ] Restart MCP server to rebuild indexes
- [ ] Test standards queries (10+ queries across different angles)
- [ ] Verify spec migration completeness
- [ ] Check behavioral metrics for updated counts

### Cleanup
- [ ] Create `.agent-os-backup-YYYYMMDD.tar.gz` archive
- [ ] Remove `.agent-os/` directory
- [ ] Verify no references remain in `.cursorrules` or `.gitignore`
- [ ] Confirm MCP server still functional
- [ ] Test orientation flow with new standards

---

## 🎯 Success Criteria

✅ All project-specific standards ported and RAG-optimized  
✅ All 28 specs migrated to `completed/`  
✅ Standards queries return new `development/` content  
✅ No broken cross-references  
✅ RAG indexes rebuilt successfully  
✅ Agent OS directory removed  
✅ MCP server operational with new content  

---

## 📝 Notes

**Why this matters:**
- Consolidates 2 months of learning into production system
- Removes redundant/obsolete Agent OS content (230 files → 19 curated)
- Preserves critical project-specific knowledge (12 development/ files)
- Maintains complete spec history (28 specs as trajectory data)
- Enables clean praxis OS installation going forward

**The Journey:**
- Started with Agent OS (static standards)
- Built 28 specs, learned what works
- Hit scaling issues (230 ai-assistant files!)
- Extracted lessons into praxis OS (63 curated universals)
- Now: Port project-specific back, remove the mess

**The Result:**
- Clean praxis OS installation
- Python SDK specific standards in `development/`
- Complete spec history in `completed/`
- Universal patterns already curated
- Ready for continued development

---

*This is the migration that closes the loop - using praxis OS to clean up the Agent OS mess that taught us how to build praxis OS.*

