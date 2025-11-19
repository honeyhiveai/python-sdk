# Python SDK Git Workflow Standards

**Maintain clean, traceable git history with consistent branching and commit practices for the HoneyHive Python SDK.**

---

## 🚨 TL;DR - Git Workflow Quick Reference

**Keywords for search**: Python SDK git workflow, HoneyHive SDK branching strategy, git commit standards, conventional commits Python SDK, main branch only, feature branches temporary, pull request requirements, PR template, git safety rules, never force push main, commit message format, squash merge, delete feature branches, git configuration Python SDK, pre-commit hooks mandatory, hotfix workflow, release workflow, branch naming conventions, git rebase strategy

**Core Principle:** `main` is the ONLY protected branch. All other branches are temporary and deleted after merge. Use Conventional Commits format for all commits.

**Branch Strategy:**
- `main` = protected, production-ready code
- All others = temporary feature branches (deleted after merge)
- Naming: `feature/`, `bugfix/`, `docs/`, `refactor/`, `hotfix/`, `release/`

**Commit Format (Mandatory):**
```bash
<type>: <description>  # Max 50 chars, no period

# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
```

**PR Requirements:**
- [ ] All CI checks passing
- [ ] Code review approval
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

**Safety Rules:**
- ❌ NEVER `git push --force origin main`
- ❌ NEVER `git commit --no-verify` (bypasses pre-commit hooks)
- ❌ NEVER commit secrets (.env files)
- ✅ Always create PR for `main` changes
- ✅ Delete feature branches after merge

---

## ❓ Questions This Answers

1. "What is the Python SDK branching strategy?"
2. "How do I create a feature branch for Python SDK?"
3. "What commit message format does Python SDK use?"
4. "How do I format conventional commits for Python SDK?"
5. "What are the PR requirements for Python SDK?"
6. "How do I merge changes to main in Python SDK?"
7. "Should I delete feature branches after merging?"
8. "What git operations are forbidden in Python SDK?"
9. "Can I force push to main branch?"
10. "How do I bypass pre-commit hooks in Python SDK?"
11. "What is the hotfix workflow for Python SDK?"
12. "How do I create a release in Python SDK?"
13. "What branch types are used in Python SDK?"
14. "How do I rebase feature branches?"
15. "What is the CI/CD trigger strategy?"
16. "What git configuration is recommended for Python SDK?"
17. "How do I recover from accidentally committing secrets?"
18. "What is the branch lifecycle in Python SDK?"
19. "How do I squash merge PRs?"
20. "What are the commit types for conventional commits?"
21. "How do I keep feature branch up to date with main?"
22. "What is the review process for PRs?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating feature branch** | `pos_search_project(action="search_standards", query="Python SDK create feature branch")` |
| **Commit message format** | `pos_search_project(action="search_standards", query="Python SDK commit message conventional commits")` |
| **PR requirements** | `pos_search_project(action="search_standards", query="Python SDK pull request requirements")` |
| **Git safety rules** | `pos_search_project(action="search_standards", query="Python SDK git forbidden operations")` |
| **Hotfix workflow** | `pos_search_project(action="search_standards", query="Python SDK hotfix workflow")` |
| **Release workflow** | `pos_search_project(action="search_standards", query="Python SDK release workflow git")` |
| **Branch naming** | `pos_search_project(action="search_standards", query="Python SDK branch naming conventions")` |
| **Git configuration** | `pos_search_project(action="search_standards", query="Python SDK git config settings")` |

---

## 🎯 Purpose

Define git workflows, branching strategy, commit standards, and safety rules for the HoneyHive Python SDK to ensure clean, traceable git history and consistent collaboration practices.

**Without this standard**: Inconsistent commits, unclear git history, accidental force pushes, long-lived feature branches, and collaboration friction.

---

## Git Branching Strategy

### Branch Model

**HoneyHive Python SDK follows a simplified branching model:**

- **`main`**: The ONLY protected branch containing production-ready code
- **All other branches**: Temporary working feature branches (deleted after merge)

**No permanent development branches.** Every branch except `main` is temporary.

### Branch Types and Naming Conventions

```bash
# Feature branches (temporary)
feature/add-anthropic-support
feature/improve-error-handling

# Bug fixes (temporary)
bugfix/fix-span-serialization
bugfix/resolve-context-leak

# Documentation (temporary)
docs/update-api-reference
docs/add-migration-guide

# Refactoring (temporary)
refactor/modernize-architecture
refactor/simplify-config

# Hotfixes (temporary, fast-tracked)
hotfix/critical-security-fix

# Releases (temporary)
release/v1.2.0
```

### Workflow Rules

**✅ DO:**
- Create feature branches from `main`
- Use descriptive branch names with prefix: `feature/`, `bugfix/`, `docs/`, `refactor/`
- Open PRs targeting `main` when ready for review
- Delete feature branches immediately after successful merge
- Rebase feature branches to keep history clean
- Keep feature branches short-lived (days, not weeks)

**❌ DON'T:**
- Consider any branch other than `main` as permanent
- Create long-lived development branches
- Merge directly to `main` without PR review
- Push directly to `main` (use PRs for all changes)
- Keep feature branches around after merge

### CI/CD Trigger Strategy

**GitHub Actions Workflows:**
```yaml
push:
  branches: [main]  # Only run on pushes to the protected main branch
pull_request:
  # Run on ALL PRs - immediate feedback on feature branch work
```

**Rationale:**
- **No duplicates**: Feature branch pushes only trigger via PR workflows
- **Immediate feedback**: All PRs get tested regardless of target branch
- **Gate keeping**: Direct pushes to `main` get validated (though should be rare)
- **Resource efficient**: Single workflow run per feature branch change

### Branch Lifecycle

1. **Create**: `git checkout -b feature/my-feature main`
2. **Develop**: Regular commits with quality checks on every push
3. **Integrate**: Open PR to `main` when ready
4. **Review**: Automated + manual review process
5. **Merge**: Squash merge to `main` with clean commit message
6. **Cleanup**: Delete feature branch immediately after merge

---

## Commit Standards

### Commit Message Format (Mandatory)

**MANDATORY: Use Conventional Commits format**

**Template:**
```bash
<type>: <description>  # Max 50 chars, no period at end
```

**Examples:**
```bash
feat: add dynamic baggage management
fix: resolve span processor race condition
docs: update API reference examples
style: format code with black
refactor: simplify tracer initialization
perf: optimize span collection
test: add unit tests for evaluate
build: update dependencies
ci: fix GitHub Actions workflow
chore: update pre-commit hooks
```

**With body (optional):**
```bash
git commit -m "feat: add provider detection

Implements dynamic pattern matching for OpenTelemetry providers
with extensible configuration and multi-instance support."
```

### Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New features | `feat: add session enrichment` |
| `fix` | Bug fixes | `fix: resolve context propagation` |
| `docs` | Documentation changes | `docs: update README` |
| `style` | Code style changes (formatting) | `style: apply black formatting` |
| `refactor` | Code refactoring | `refactor: simplify config loading` |
| `perf` | Performance improvements | `perf: optimize span batching` |
| `test` | Test additions or modifications | `test: add integration tests` |
| `build` | Build system changes | `build: update pyproject.toml` |
| `ci` | CI/CD changes | `ci: add coverage reporting` |
| `chore` | Maintenance tasks | `chore: update dependencies` |

### Common Commit Errors to Prevent

**❌ Wrong:**
```bash
git commit -m "feat: Add feature  # Missing closing quote
git commit -m "\"feat: Add feature\""  # Unnecessary escaping
git commit -m "feat: Add comprehensive documentation quality control system validation framework"  # Too long (91 chars)
git commit -m "Add feature"  # Missing type
git commit -m "feat Add feature"  # Missing colon
git commit -m "feat: Add feature."  # Period at end
```

**✅ Correct:**
```bash
git commit -m "feat: add feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update guide"
```

---

## Pull Request Standards

### PR Requirements

**Every PR must include:**
- [ ] Clear title describing the change
- [ ] Link to relevant issues
- [ ] Test coverage for new functionality
- [ ] Updated documentation
- [ ] All CI checks passing
- [ ] Code review approval
- [ ] CHANGELOG.md updated (if user-facing change)

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] All tests pass locally
```

### Review Process

1. **Automated Checks**: All CI/CD checks must pass
2. **Code Review**: At least one approval required
3. **Documentation Review**: Verify docs are updated
4. **Test Coverage**: Ensure adequate test coverage
5. **Final Validation**: Reviewer runs tests locally if needed

---

## Git Safety Rules

### Forbidden Operations

**❌ NEVER DO THESE:**

```bash
# NEVER force push to main
git push --force origin main  # ❌ FORBIDDEN

# NEVER rewrite public history
git rebase -i HEAD~10  # ❌ On pushed commits

# NEVER commit secrets
git add .env  # ❌ FORBIDDEN
git commit -m "Add API keys"  # ❌ NEVER!

# NEVER bypass pre-commit hooks without explicit approval
git commit --no-verify  # ❌ FORBIDDEN for AI assistants
```

**Why these are forbidden:**
- Force push to `main` destroys team's work
- Rewriting public history breaks collaborators' repos
- Committing secrets exposes credentials
- Bypassing hooks skips quality gates

### Safe Operations

**✅ SAFE TO DO:**

```bash
# Force push to YOUR OWN feature branches
git push --force-with-lease origin feature/my-branch  # ✅ SAFE

# Rebase feature branches before merge
git rebase main  # ✅ SAFE (on feature branch)

# Amend last commit (if not pushed)
git commit --amend  # ✅ SAFE (before push)

# Interactive rebase (on unpushed commits)
git rebase -i HEAD~3  # ✅ SAFE (before push)
```

### Recovery Procedures

**If you accidentally committed secrets:**

```bash
# Remove from history immediately
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/secret/file' \
--prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner for large repos
bfg --delete-files secret-file.env
```

**If you accidentally force pushed to main:**

```bash
# 1. Contact team immediately
# 2. Restore from backup or previous commit
git reset --hard <last-good-commit>
git push --force-with-lease origin main  # Only if approved
```

---

## Advanced Git Workflows

### Feature Branch Workflow

```bash
# 1. Start new feature
git checkout main
git pull origin main
git checkout -b feature/new-feature

# 2. Develop with regular commits
git add .
git commit -m "feat: implement core functionality"
git commit -m "test: add unit tests"
git commit -m "docs: update API documentation"

# 3. Keep up to date with main
git fetch origin
git rebase origin/main

# 4. Push and create PR
git push origin feature/new-feature
# Create PR via GitHub UI or gh CLI
```

### Hotfix Workflow

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Implement minimal fix
git add .
git commit -m "fix: resolve critical security issue"

# 3. Test thoroughly
tox -e unit -e integration

# 4. Fast-track review and merge
git push origin hotfix/critical-bug-fix
# Create PR with "hotfix" label for priority review
```

### Release Workflow

```bash
# 1. Create release branch
git checkout main
git pull origin main
git checkout -b release/v1.2.0

# 2. Update version and changelog
# Edit src/honeyhive/__init__.py, CHANGELOG.md
git add src/honeyhive/__init__.py CHANGELOG.md
git commit -m "release: prepare v1.2.0"

# 3. Create release PR
git push origin release/v1.2.0
# PR review focuses on version, changelog, documentation

# 4. After merge, workflow creates tag automatically
# Or manual tag:
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

---

## Git Configuration

### Required Git Settings

```bash
# Set up identity
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# Set up signing (recommended)
git config --global user.signingkey <your-gpg-key-id>
git config --global commit.gpgsign true

# Set up helpful aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
```

### Repository-Specific Settings

```bash
# In project root
git config core.autocrlf false  # Consistent line endings
git config pull.rebase true     # Rebase on pull instead of merge
git config branch.autosetupmerge always
git config branch.autosetuprebase always
```

---

## 🔗 Related Standards

**Query workflow for git workflow:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK git workflow")`
2. **Learn release process** → `pos_search_project(action="search_standards", query="Python SDK release process")` → `standards/development/workflow/release-process.md`
3. **Understand commit protocols** → `pos_search_project(action="search_standards", query="AI commit protocol")` → `standards/universal/ai-assistant/commit-protocol.md`
4. **Environment setup** → `pos_search_project(action="search_standards", query="Python SDK environment setup")` → `standards/development/environment/setup.md`

**By Category:**

**Workflow:**
- `standards/development/workflow/release-process.md` → `pos_search_project(action="search_standards", query="Python SDK release process")`

**Environment:**
- `standards/development/environment/setup.md` → `pos_search_project(action="search_standards", query="Python SDK environment setup")`

**Universal Standards:**
- `standards/universal/ai-assistant/commit-protocol.md` → `pos_search_project(action="search_standards", query="AI commit protocol")`
- `standards/universal/ai-safety/credential-file-protection.md` → `pos_search_project(action="search_standards", query="credential safety git")`

---

## Validation Checklist

Before considering git workflow complete:

- [ ] Feature branch created from `main`
- [ ] Branch name follows convention (`feature/`, `bugfix/`, etc.)
- [ ] Commits use Conventional Commits format
- [ ] Commit messages under 50 characters
- [ ] All pre-commit hooks passed
- [ ] All tests passing locally
- [ ] PR created targeting `main`
- [ ] PR includes all required sections
- [ ] CHANGELOG.md updated (if needed)
- [ ] CI checks passing
- [ ] Code review approval received
- [ ] Feature branch will be deleted after merge

---

**📝 Remember**: `main` is the only permanent branch. Delete feature branches immediately after merge.

