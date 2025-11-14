# AI Assistant Commit Protocols

**🎯 Review checkpoints and commit procedures for AI assistants**

This document defines the mandatory commit protocols that AI assistants must follow to ensure proper review, documentation, and quality control before any code is committed.

## 🛑 MANDATORY: Commit Review Protocol

**🚨 CRITICAL FOR AI ASSISTANTS**: All commits require review checkpoints, especially when CHANGELOG updates are involved.

### Pre-Commit Review Checkpoint

**MANDATORY steps before any commit:**

1. **📋 Quality Gates Verification**
   ```bash
   # All quality gates must pass
   tox -e format           # Black formatting
   tox -e lint            # Pylint + mypy  
   tox -e unit            # Unit tests
   tox -e integration     # Integration tests
   ```

2. **📚 Documentation Review**
   - Verify all code has proper Sphinx docstrings
   - Check that examples in documentation work
   - Ensure cross-references are valid

3. **📝 CHANGELOG Assessment**
   - Determine if changes require CHANGELOG.md update
   - Verify CHANGELOG accurately reflects what was done vs what needs to be implemented
   - Check that both CHANGELOG.md and docs/changelog.rst are updated if needed

4. **🔍 User Review Request**
   ```
   🛑 COMMIT REVIEW CHECKPOINT
   
   Changes ready for commit:
   - [List of files changed]
   - [Summary of changes made]
   - [Quality gates status: ✅ All passed]
   
   CHANGELOG update needed: [Yes/No]
   If yes: [Brief description of what should be documented]
   
   Please review and choose:
   1. Create new commit
   2. Amend existing commit  
   3. Request changes
   ```

### CHANGELOG Review Protocol

**When CHANGELOG updates are identified as needed:**

1. **📖 Content Verification**
   - Does the CHANGELOG entry accurately describe the changes?
   - Is it in the correct section (Added/Changed/Fixed/Removed)?
   - Does it provide enough context for users?

2. **📚 Dual Changelog Sync**
   - Is CHANGELOG.md updated with technical details?
   - Is docs/changelog.rst updated with user-friendly highlights?
   - Are both files consistent in their coverage of the changes?

3. **🎯 User Decision Point**
   ```
   📝 CHANGELOG REVIEW
   
   Proposed CHANGELOG entry:
   [Show the proposed entry]
   
   This entry will be added to:
   - CHANGELOG.md (technical details)
   - docs/changelog.rst (user highlights)
   
   Please confirm:
   1. ✅ Approve and commit
   2. 📝 Modify entry
   3. ❌ Skip CHANGELOG for this change
   ```

## 💬 Commit Message Standards

**🚨 CRITICAL**: Follow conventional commit format exactly

### Correct Format
```bash
# Basic format: <type>: <description> (max 50 chars)
git commit -m "feat: add dynamic baggage management"
git commit -m "fix: resolve span processor race condition"  
git commit -m "docs: update API reference examples"

# With body (72 chars max per line)
git commit -m "feat: add provider detection

Implements dynamic pattern matching for OpenTelemetry providers
with extensible configuration and multi-instance support.

Closes #123"
```

### Commit Types
- **feat**: New features
- **fix**: Bug fixes  
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Test additions or modifications
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks

### Common Errors to Prevent
```bash
# ❌ WRONG - Missing closing quote
git commit -m "feat: Add feature

# ❌ WRONG - Unnecessary quotes  
git commit -m "\"feat: Add feature\""

# ❌ WRONG - Too long (71 chars)
git commit -m "feat: Add comprehensive documentation quality control system validation"

# ❌ WRONG - Missing type prefix
git commit -m "Add new feature"

# ❌ WRONG - Period at end
git commit -m "feat: Add feature."

# ✅ CORRECT
git commit -m "feat: add documentation quality control"
```

## 🔄 Commit Decision Matrix

**AI assistants must ask users to choose the appropriate commit action:**

### New Commit vs Amend

**Create New Commit When:**
- ✅ Implementing a new feature or fix
- ✅ Changes are logically separate from previous commit
- ✅ Previous commit has already been pushed to remote
- ✅ Changes represent a distinct unit of work

**Amend Existing Commit When:**
- ✅ Fixing issues in the most recent commit
- ✅ Adding forgotten files to the last commit
- ✅ Improving commit message of the last commit
- ✅ Last commit hasn't been pushed yet

**Example Decision Prompt:**
```
🔄 COMMIT ACTION DECISION

Recent commit: "feat: add span processor dynamic logic"
Current changes: Fixed linting errors and added missing docstrings

Choose action:
1. 🆕 New commit: "style: fix linting and add docstrings"
2. 🔄 Amend: Include fixes in the existing feature commit
3. 📝 Review: Let me review the changes first

Recommendation: [AI's recommendation with reasoning]
```

## 📋 Enhanced Pre-Commit Quality Gates

**Automatic enforcement via pre-commit hooks:**

### File Pattern Validation
- **Documentation restructuring** (>5 files requires CHANGELOG)
- **Configuration changes** (pyproject.toml, tox.ini)
- **Tooling changes** (scripts/, .github/workflows/)
- **praxis OS documentation** (.agent-os/ files)
- **Examples and integration guides**

### Mandatory Updates
- **Code changes**: CHANGELOG.md must be updated
- **New features**: CHANGELOG.md + docs/reference/index.rst + .agent-os/product/features.md
- **CI/CD workflow changes**: Update docs/development/testing/ci-cd-integration.rst
- **Large changesets**: Comprehensive documentation review required

## 🚨 Forbidden Commit Practices

**❌ AI assistants are STRICTLY FORBIDDEN from:**

### Bypassing Quality Gates
- **`git commit --no-verify`** - NEVER bypass pre-commit hooks
- **Committing failing tests** - All tests must pass
- **Skipping linting fixes** - All quality gates must pass
- **Ignoring documentation requirements** - Updates must be complete

### Unsafe Git Operations
- **Force pushing** without explicit user approval
- **Rewriting published history** without user consent
- **Committing sensitive data** (API keys, credentials)
- **Large binary files** without user approval

## 🔍 Rapid Iteration Protocol

**For pre-commit check fixes, AI assistants may iterate rapidly:**

### Allowed Rapid Fixes
- **Formatting corrections** (Black, isort)
- **Linting fixes** (pylint violations)
- **Type annotation additions** (mypy errors)
- **Import organization** (missing imports)

### Still Requires Review
- **CHANGELOG updates** - Always pause for user review
- **Breaking changes** - Require explicit user approval
- **Architecture modifications** - Need user guidance
- **New dependencies** - Require user approval

**Example Rapid Iteration:**
```
🔄 RAPID ITERATION MODE

Fixing pre-commit issues:
✅ Applied Black formatting
✅ Fixed import order with isort  
✅ Added missing type annotations
✅ Resolved pylint warnings

All quality gates now pass. Ready to commit without additional review.
```

## 📊 Success Metrics

**Commit protocol succeeds when:**

### Quality Metrics
- **100% of commits** pass all quality gates on first attempt
- **Zero reverted commits** due to quality issues
- **Consistent CHANGELOG** maintenance across all changes
- **Complete documentation** for all user-facing changes

### Process Metrics
- **Clear review checkpoints** before every commit
- **Appropriate commit granularity** (neither too large nor too small)
- **Proper commit message format** following conventional commits
- **User satisfaction** with review and commit process

## 📚 Related Standards

- **[Quality Framework](quality-framework.md)** - Overall AI assistant quality requirements
- **[Git Safety Rules](git-safety-rules.md)** - Forbidden git operations and safety protocols
- **[Code Quality](../development/code-quality.md)** - Quality gates and tool requirements
- **[Testing Standards](../development/testing-standards.md)** - Test requirements and procedures

---

**📝 Remember**: The goal is to maintain high quality while enabling efficient development. When in doubt, pause for user review rather than proceeding with uncertain changes.
