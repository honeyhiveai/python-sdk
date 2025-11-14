# Commit Protocol

**Universal standard for structured review and commitment of changes**

---

## 🎯 TL;DR - Commit Protocol Quick Reference

**Keywords for search**: commit protocol, pre-commit review, commit checklist, quality gates, CHANGELOG, commit message, user approval, git commit, code review before commit

**Core Principle:** Never commit without passing ALL quality gates and getting user approval.

**MANDATORY Pre-Commit Steps:**
1. ✅ Run ALL quality gates (format, lint, type-check, tests)
2. ✅ Update CHANGELOG with changes
3. ✅ Present changes to user with summary
4. ✅ Get explicit user approval ("commit it" or similar)
5. ✅ Write clear commit message
6. ✅ Commit with proper git safety

**Quality Gates (ALL must pass):**
- Formatting: 100% compliant
- Linting: Meets project threshold
- Type checking: Zero errors
- Unit tests: 100% pass
- Integration tests: 100% pass

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**When to Query This Standard:**
- Before any commit → `pos_search_project(content_type="standards", query="commit protocol")`
- Quality gates unclear → `pos_search_project(content_type="standards", query="pre-commit checklist")`
- CHANGELOG updates → `pos_search_project(content_type="standards", query="CHANGELOG format")`

---

## ❓ Questions This Answers

1. "What should I do before committing code?"
2. "What quality gates must pass before commit?"
3. "How to structure commit messages?"
4. "When do I need user approval for commits?"
5. "What should be in a CHANGELOG?"
6. "How to review changes before committing?"
7. "What is the commit protocol?"
8. "How to ensure commits are high quality?"
9. "What format for commit messages?"
10. "How to get user approval for commits?"

---

## 📋 Overview

### What is Commit Protocol?

**Commit protocol** is the systematic process for reviewing, validating, and committing changes with appropriate documentation and user approval.

### Why It Matters

Without commit protocol, commits may:
- ❌ Lack proper review
- ❌ Miss CHANGELOG updates
- ❌ Have unclear boundaries (what belongs together?)
- ❌ Skip quality validation
- ❌ Lack proper documentation

With commit protocol, commits:
- ✅ Are properly reviewed
- ✅ Have appropriate CHANGELOG entries
- ✅ Have clear, logical boundaries
- ✅ Pass all quality gates
- ✅ Are well-documented

---

## 🛑 MANDATORY: Pre-Commit Review Checkpoint

**Execute BEFORE any commit. No exceptions.**

### Step 1: Quality Gates Verification

**ALL quality gates must pass before commit.**

```bash
# Run quality gates in sequence
# STOP if any fail - fix before proceeding

[format_command]              # Code formatting (100% compliance)
[lint_command]                # Static analysis (meets project threshold)
[type_check_command]          # Type checking (zero errors if required)
[unit_test_command]           # Unit tests (100% pass)
[integration_test_command]    # Integration tests (100% pass if applicable)

# Examples by language:
#
# Python:
#   tox -e format      # Black + isort
#   tox -e lint        # Pylint + mypy  
#   tox -e unit        # pytest unit tests
#   tox -e integration # pytest integration tests
#
# JavaScript:
#   npm run format     # Prettier
#   npm run lint       # ESLint + TypeScript
#   npm test           # Jest
#   npm run test:e2e   # E2E tests
#
# Go:
#   gofmt -l . && test -z "$(gofmt -l .)"
#   golint ./... && go vet ./...
#   go test ./...
#   go test ./... -tags=integration
#
# Rust:
#   cargo fmt --check
#   cargo clippy -- -D warnings
#   cargo test
#   cargo test --features integration
```

**Checklist**:
- [ ] Formatting: 100% compliant
- [ ] Static analysis: Meets project threshold
- [ ] Type checking: Zero errors (if project requires)
- [ ] Unit tests: 100% pass
- [ ] Integration tests: 100% pass (if applicable)

---

### Step 2: Documentation Review

**Verify code is properly documented.**

```bash
# Check documentation requirements

# 1. Code documentation
[check_docstrings]     # Verify public APIs have docstrings/comments
[check_examples]       # Verify examples work

# 2. Build documentation (if project has docs)
[doc_build_command]    # Documentation builds without errors

# Examples:
# Python: cd docs && make html
# JavaScript: npm run docs
# Rust: cargo doc --no-deps
```

**Checklist**:
- [ ] Public APIs have proper documentation
- [ ] Examples are included where appropriate
- [ ] Documentation builds successfully (if applicable)
- [ ] Cross-references are valid

---

### Step 3: CHANGELOG Assessment

**Determine if changes require CHANGELOG update.**

**When CHANGELOG update is needed**:
- ✅ New features visible to users
- ✅ Bug fixes that users care about
- ✅ Breaking changes or deprecations
- ✅ Performance improvements users will notice
- ✅ Security fixes

**When CHANGELOG update is NOT needed**:
- ❌ Internal refactoring (no visible changes)
- ❌ Test additions/improvements (unless testing framework change)
- ❌ Documentation-only changes (unless major docs rewrite)
- ❌ Build/CI configuration changes

**Decision Tree**:
```
Does this change affect users?
├─ YES → Does it change behavior?
│   ├─ YES → CHANGELOG required (Added/Changed/Fixed/Removed)
│   └─ NO → CHANGELOG optional (Security/Deprecated)
└─ NO → CHANGELOG not needed
```

---

### Step 4: User Review Request

**Present changes to user for review and approval.**

Use this template:

```markdown
🛑 COMMIT REVIEW CHECKPOINT

## Changes Ready for Commit

### Files Changed
- [file1.ext] - [Brief description]
- [file2.ext] - [Brief description]
- [file3.ext] - [Brief description]

### Summary of Changes
[1-2 sentence summary of what was done]

### Quality Gates Status
✅ Formatting: Passed
✅ Static Analysis: Passed ([score/metrics])
✅ Type Checking: Passed ([zero errors/metrics])
✅ Unit Tests: Passed ([count] tests)
✅ Integration Tests: Passed ([count] tests)
✅ Documentation: Built successfully

### CHANGELOG Update
**Needed**: [Yes/No]

[If Yes]:
**Proposed Entry**:
```
### [Added/Changed/Fixed/Removed/Security/Deprecated]
- [Description of change from user perspective]
```

**Category**: [Added/Changed/Fixed/Removed/Security/Deprecated]
**User Impact**: [Brief description]

[If No]:
**Reason**: [Why CHANGELOG not needed]

### Commit Decision
Please choose:
1. ✅ Create new commit
2. 🔄 Amend existing commit
3. 📝 Request changes before commit

[If you recommend new vs amend, state recommendation with reasoning]
```

---

## 🔄 Commit Decision Matrix

**Help user decide: New commit vs Amend existing.**

### Create New Commit When:

- ✅ **Implementing a new feature or fix**
  - Example: "feat: add user authentication"
  
- ✅ **Changes are logically separate from previous commit**
  - Previous: "feat: add API endpoint"
  - Current: "docs: add API documentation"
  - Decision: New commit (different concerns)

- ✅ **Previous commit has already been pushed to remote**
  - Check: `git log origin/branch..HEAD`
  - If empty: Previous commit is pushed
  - Decision: New commit (don't rewrite published history)

- ✅ **Changes represent a distinct unit of work**
  - Example: Previous commit added feature, current commit adds tests
  - Decision: Could be either, but new commit makes history clearer

---

### Amend Existing Commit When:

- ✅ **Fixing issues in the most recent commit**
  - Example: Commit added feature but forgot error handling
  - Decision: Amend (complete the original intent)

- ✅ **Adding forgotten files to the last commit**
  - Example: Forgot to add configuration file
  - Decision: Amend (part of same logical change)

- ✅ **Improving commit message of the last commit**
  - Example: Commit message was unclear
  - Decision: Amend (better communication)

- ✅ **Last commit hasn't been pushed yet**
  - Check: `git log origin/branch..HEAD`
  - If shows commit: Not pushed yet
  - Decision: Amend is safe (no published history rewrite)

- ✅ **Fixing linting/formatting in the last commit**
  - Example: Commit passed but you found minor formatting issue
  - Decision: Amend (cleanup, not separate concern)

---

### Decision Template

Present this to user:

```markdown
🔄 COMMIT ACTION DECISION

### Recent Commit
```
[Show last commit if exists]:
git log -1 --oneline
```

### Current Changes
[List files and summary]

### Recommendation
**[New Commit / Amend Existing]**

**Reasoning**: [Why this choice is appropriate]

### Please Choose
1. 🆕 New commit: "[proposed commit message]"
2. 🔄 Amend: Include changes in the existing commit
3. 📝 Different approach: [Let me know your preference]
```

---

## 📝 CHANGELOG Review Protocol

**When CHANGELOG update is needed.**

### Step 1: Content Verification

**Verify CHANGELOG entry is accurate and helpful.**

```markdown
## CHANGELOG Entry Review

### Proposed Entry
```
### [Category]
- [Entry text]
```

### Verification Checklist
- [ ] **Accurate**: Does it correctly describe the change?
- [ ] **User-Focused**: Is it written from user's perspective?
- [ ] **Correct Category**: Added/Changed/Fixed/Removed/Security/Deprecated?
- [ ] **Sufficient Context**: Does it provide enough information?
- [ ] **Breaking Changes**: Are they clearly marked?
```

---

### Step 2: Dual Changelog Sync (If Applicable)

**Some projects maintain two changelog formats.**

**If your project has**:
- `CHANGELOG.md` (technical details for developers)
- `docs/changelog.rst` (user-friendly highlights for documentation)

**Update both**:
```bash
# 1. Update CHANGELOG.md with technical details
[edit] CHANGELOG.md

# 2. Update docs/changelog.rst with user highlights
[edit] docs/changelog.rst

# 3. Verify consistency
# - Same version number
# - Compatible information
# - User-friendly vs technical tone appropriate
```

**Most projects only have CHANGELOG.md - update that one.**

---

### Step 3: Category Selection

**Choose the right CHANGELOG category.**

| Category | When to Use | Example |
|----------|-------------|---------|
| **Added** | New features, new capabilities | "Added user authentication with JWT tokens" |
| **Changed** | Changes to existing functionality | "Changed API response format to include timestamps" |
| **Fixed** | Bug fixes | "Fixed race condition in tracer initialization" |
| **Removed** | Removed features or functionality | "Removed deprecated config.legacy_mode option" |
| **Security** | Security fixes or improvements | "Fixed SQL injection vulnerability in query builder" |
| **Deprecated** | Features marked for future removal | "Deprecated old_method() in favor of new_method()" |

**Breaking Changes**: Add `**BREAKING**:` prefix
```markdown
### Changed
- **BREAKING**: API now requires authentication for all endpoints
```

---

### Step 4: User Decision Point

**Present CHANGELOG entry for approval.**

```markdown
📝 CHANGELOG REVIEW

### Proposed CHANGELOG Entry

**Category**: [Added/Changed/Fixed/etc.]

**Entry**:
```
- [Entry text]
```

**Will be added to**:
- CHANGELOG.md (version [X.Y.Z] section)
[If applicable]:
- docs/changelog.rst (version [X.Y.Z] section)

### Please Confirm
1. ✅ Approve and commit with CHANGELOG update
2. 📝 Modify entry: [Please provide revised text]
3. ❌ Skip CHANGELOG for this change: [Please confirm skip]
```

---

## 🔍 Rapid Iteration Protocol

**For pre-commit check fixes, AI may iterate rapidly without asking.**

### Allowed Rapid Fixes (No User Review Needed)

These are mechanical fixes that don't change logic:

- ✅ **Formatting corrections**
  - Running Black, Prettier, gofmt, rustfmt
  - Fixing indentation
  - Organizing imports

- ✅ **Linting fixes**
  - Removing unused imports
  - Fixing linter warnings
  - Adding missing type hints (when obvious)

- ✅ **Type annotation additions**
  - Adding type hints for mypy/TypeScript
  - Fixing type errors

- ✅ **Import organization**
  - Sorting imports
  - Removing duplicates
  - Adding missing imports

**AI may state**:
```
"Found formatting issues. Fixing automatically..."
[runs formatter]
"Formatting complete. Re-running quality gates..."
[re-runs gates]
"All quality gates now pass. Ready to commit."
```

---

### Still Requires Review (Must Ask User)

These change behavior or require decisions:

- 🛑 **CHANGELOG updates** - Always pause for user review
- 🛑 **Breaking changes** - Require explicit user approval
- 🛑 **Architecture modifications** - Need user guidance
- 🛑 **New dependencies** - Require user approval
- 🛑 **Logic changes** - Must review with user
- 🛑 **Test changes** (beyond mechanical) - Must review

---

## ✅ Commit Message Standards

**Follow project's commit message convention.**

### Conventional Commits (Common Standard)

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc. (no code change)
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding or correcting tests
- `chore`: Maintenance (dependencies, build, etc.)

**Examples**:
```
feat(auth): add JWT token authentication

Implements JWT-based authentication for API endpoints.
Includes middleware for token validation and refresh.

Closes #123
```

```
fix(tracer): resolve race condition in initialization

Adds mutex lock to prevent concurrent initialization.
Includes regression test.

Fixes #456
```

### Project-Specific Conventions

**Check project's CONTRIBUTING.md or README.md for commit conventions.**

Some projects use:
- Different type names (e.g., `feature:` instead of `feat:`)
- Issue tracker integration (e.g., "Resolves #123")
- Sign-off requirements (e.g., `Signed-off-by:`)
- DCO (Developer Certificate of Origin)

---

## 🎯 Complete Commit Flow Examples

### Example 1: New Feature (Single Commit)

```markdown
🛑 COMMIT REVIEW CHECKPOINT

## Changes Ready for Commit

### Files Changed
- src/auth/jwt.py - JWT authentication implementation
- src/auth/middleware.py - Authentication middleware
- tests/test_auth.py - Comprehensive auth tests
- requirements.txt - Added PyJWT dependency

### Summary of Changes
Implemented JWT-based authentication for API endpoints with token validation and refresh logic.

### Quality Gates Status
✅ Formatting: Passed (Black, isort)
✅ Static Analysis: Passed (Pylint 10.0/10.0, MyPy 0 errors)
✅ Type Checking: Passed (100% typed)
✅ Unit Tests: Passed (24 tests)
✅ Integration Tests: Passed (8 tests)

### CHANGELOG Update
**Needed**: Yes

**Proposed Entry**:
```
### Added
- JWT-based authentication for API endpoints with token refresh
```

**Category**: Added
**User Impact**: Users can now authenticate using JWT tokens

### Commit Decision
**Recommendation**: New commit

**Reasoning**: This is a complete new feature with tests and documentation.

**Proposed commit message**:
```
feat(auth): add JWT token authentication

Implements JWT-based authentication for API endpoints.
Includes middleware for token validation and refresh.

Closes #123
```

Please choose:
1. ✅ Create new commit (recommended)
2. 📝 Modify commit message or CHANGELOG
3. 🔄 Make additional changes
```

---

### Example 2: Bug Fix (Amend Scenario)

```markdown
🛑 COMMIT REVIEW CHECKPOINT

## Recent Commit
```
feat(auth): add JWT token authentication
```
(Not yet pushed to remote)

## Current Changes

### Files Changed
- src/auth/jwt.py - Added missing error handling for expired tokens

### Summary of Changes
Added error handling for expired tokens that was missing from the authentication implementation.

### Quality Gates Status
✅ All gates pass (with fix included)

### CHANGELOG Update
**Needed**: No

**Reason**: This is completing the original feature, not a separate change. The CHANGELOG entry already covers JWT authentication.

### Commit Decision
**Recommendation**: Amend existing commit

**Reasoning**: 
- This error handling was part of the original feature intent
- The original commit hasn't been pushed yet
- This completes the feature rather than being a separate fix

Please choose:
1. 🔄 Amend existing commit (recommended)
2. 🆕 Create new commit (if you prefer separate history)
3. 📝 Different approach
```

---

### Example 3: Rapid Iteration (Formatting Fix)

```markdown
Running pre-commit quality gates...

❌ Formatting: Failed
  - src/auth/jwt.py: Line too long (91 > 88)
  - tests/test_auth.py: Unsorted imports

Fixing formatting issues automatically...
[runs black and isort]

Re-running quality gates...
✅ Formatting: Passed
✅ All other gates: Passed

All quality gates now pass. Ready to commit.

[Proceeds to commit review checkpoint]
```

**Note**: No user interaction needed for mechanical formatting fixes.

---

## 🔗 Project-Specific Commit Protocols

**Projects may extend with additional commit requirements.**

### Creating Commit Protocol Addendum

**File**: `.praxis-os/standards/development/commit-protocol-addendum.md`

**Example Contents**:

```markdown
# Project Name - Commit Protocol Addendum

## Additional Requirements

### Commit Message Format
- Use conventional commits format
- Include issue tracker reference: "Closes #123"
- Sign-off required: `git commit -s`

### Pre-Commit Checks
- Run `npm run pre-commit` before every commit
- Verify package-lock.json is updated if dependencies changed
- Check bundle size hasn't increased more than 5%

### CHANGELOG Management
- Update both CHANGELOG.md and docs/changelog.rst
- Use version from package.json
- Follow semantic versioning

### Review Requirements
- All commits must pass CI before merge
- At least one approval required for PRs
- Breaking changes require architectural review
```

---

## 📚 Commit Hygiene Best Practices

### Small, Focused Commits

✅ **Good**:
```
feat(auth): add JWT token generation
feat(auth): add JWT token validation  
feat(auth): add token refresh endpoint
test(auth): add JWT token tests
```

❌ **Bad**:
```
feat(auth): add complete authentication system
  (Contains 10 different concerns in one commit)
```

---

### Atomic Commits

**Each commit should be independently functional.**

✅ **Good**: Each commit leaves system in working state
- Commit 1: Add feature (system works)
- Commit 2: Add tests (system still works)
- Commit 3: Add docs (system still works)

❌ **Bad**: Commits depend on each other
- Commit 1: Add half of feature (system broken)
- Commit 2: Add other half (system fixed)

---

### Clear Commit Messages

✅ **Good**: Explains what and why
```
fix(auth): prevent race condition in token refresh

The token refresh logic had a race condition when multiple
requests attempted to refresh simultaneously. Added mutex
lock to serialize refresh operations.

Fixes #456
```

❌ **Bad**: Vague or useless
```
fix stuff
update code
wip
```

---

## 🎓 Teaching Commit Protocol to New AI Assistants

### Key Principles

1. **Quality first** - Never commit without passing all quality gates
2. **Review always** - Always present changes for user review
3. **CHANGELOG matters** - User-visible changes need documentation
4. **Atomic commits** - Each commit should be independently meaningful
5. **Rapid iteration for mechanical** - Format/lint fixes can be automatic

---

## 🔗 Related Standards

- **[Pre-Generation Validation](pre-generation-validation.md)** - What to do before generating
- **[Compliance Protocol](compliance-protocol.md)** - Check standards before committing
- **[Analysis Methodology](analysis-methodology.md)** - How to analyze before committing

---

## ❓ FAQ

### Q: Should I commit after every file in a multi-file task?

**A**: No. Generate all related files, then commit them together as one logical unit.

### Q: What if quality gates fail?

**A**: Fix the issues. Never commit with failing quality gates. Use rapid iteration for mechanical fixes (formatting, etc.).

### Q: What if I'm not sure if CHANGELOG is needed?

**A**: Ask yourself: "Will users notice this change?" If yes, CHANGELOG is probably needed. When in doubt, ask user.

### Q: Can I skip user review for small changes?

**A**: No. Always present changes for review (except rapid iteration fixes like formatting).

### Q: What if user wants to modify the CHANGELOG entry?

**A**: Update the CHANGELOG with their revision, then proceed with commit.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Before commit** | `pos_search_project(content_type="standards", query="commit protocol")` |
| **Quality gates** | `pos_search_project(content_type="standards", query="pre-commit checklist")` |
| **Commit messages** | `pos_search_project(content_type="standards", query="commit message format")` |
| **CHANGELOG updates** | `pos_search_project(content_type="standards", query="CHANGELOG format")` |
| **User approval** | `pos_search_project(content_type="standards", query="when to get commit approval")` |

---

## 🔗 Related Standards

**Query workflow for commit mastery:**

1. **Start with commit protocol** → `pos_search_project(content_type="standards", query="commit protocol")` (this document)
2. **Learn production checklist** → `pos_search_project(content_type="standards", query="production code checklist")` → `standards/ai-safety/production-code-checklist.md`
3. **Understand git safety** → `pos_search_project(content_type="standards", query="git safety rules")` → `standards/ai-safety/git-safety-rules.md`
4. **Learn pre-commit checklist** → `pos_search_project(content_type="standards", query="pre-commit checklist")` → `standards/documentation/pre-commit-checklist.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Code quality requirements → `pos_search_project(content_type="standards", query="production code checklist")`
- `standards/ai-safety/git-safety-rules.md` - Git safety → `pos_search_project(content_type="standards", query="git safety rules")`

**Documentation:**
- `standards/documentation/pre-commit-checklist.md` - Quick checklist → `pos_search_project(content_type="standards", query="pre-commit checklist")`
- `standards/documentation/change-impact-analysis.md` - Impact analysis → `pos_search_project(content_type="standards", query="change impact analysis")`

**AI Assistant:**
- `standards/ai-assistant/compliance-protocol.md` - Compliance checking → `pos_search_project(content_type="standards", query="compliance protocol")`

---

**This is a universal standard. It applies to all projects using prAxIs OS, regardless of programming language or technology stack.**

**For project-specific commit requirements, see `.praxis-os/standards/development/commit-protocol-addendum.md` in your project.**

