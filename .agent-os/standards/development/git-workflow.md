# Git Workflow Standards - HoneyHive Python SDK

**🎯 MISSION: Maintain clean, traceable git history with consistent branching and commit practices**

## Git Branching Strategy

### Branch Model
**HoneyHive Python SDK follows a simplified branching model:**

- **`main`**: The only protected branch containing production-ready code
- **All other branches**: Temporary working feature branches (deleted after merge)

### Branch Types
```bash
# Feature branches (temporary)
feature/add-anthropic-support
feature/improve-error-handling
bugfix/fix-span-serialization
docs/update-api-reference
refactor/modernize-architecture

# Current working branches (temporary)
complete-refactor    # Major architecture changes
develop             # Legacy branch (will be removed)
```

### Workflow Rules

**✅ DO:**
- Create feature branches from `main`
- Use descriptive branch names: `feature/`, `bugfix/`, `docs/`, `refactor/`
- Open PRs targeting `main` when ready for review
- Delete feature branches after successful merge
- Rebase feature branches to keep history clean

**❌ DON'T:**
- Consider any branch other than `main` as permanent
- Create long-lived development branches
- Merge directly to `main` without PR review
- Push directly to `main` (use PRs for all changes)

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

## Commit Standards

### Commit Message Format

**MANDATORY: Use Conventional Commits format**

```bash
# Template: <type>: <description> (max 50 chars)
git commit -m "feat: add dynamic baggage management"
git commit -m "fix: resolve span processor race condition"
git commit -m "docs: update API reference examples"

# With body (max 72 chars per line)
git commit -m "feat: add provider detection

Implements dynamic pattern matching for OpenTelemetry providers
with extensible configuration and multi-instance support."
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

### Common Commit Errors to Prevent
- ❌ Missing closing quotes: `git commit -m "feat: Add feature`
- ❌ Unnecessary quotes: `git commit -m "\"feat: Add feature\""`
- ❌ Too long: `feat: Add comprehensive documentation quality control system validation` (71 chars)
- ❌ Wrong format: Missing type prefix or colon
- ❌ Periods at end: `feat: Add feature.`

## Pull Request Standards

### PR Requirements

**Every PR must include:**
- [ ] Clear title describing the change
- [ ] Link to relevant issues
- [ ] Test coverage for new functionality
- [ ] Updated documentation
- [ ] All CI checks passing
- [ ] Code review approval

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

## Git Safety Rules

### Forbidden Operations

**❌ NEVER DO THESE:**
```bash
# Never force push to main
git push --force origin main

# Never rewrite public history
git rebase -i HEAD~10  # On pushed commits

# Never commit secrets
git add .env
git commit -m "Add API keys"  # NEVER!

# Never bypass pre-commit hooks without reason
git commit --no-verify
```

### Safe Operations

**✅ SAFE TO DO:**
```bash
# Force push to feature branches (your own)
git push --force-with-lease origin feature/my-branch

# Rebase feature branches before merge
git rebase main

# Amend last commit (if not pushed)
git commit --amend

# Interactive rebase (on unpushed commits)
git rebase -i HEAD~3
```

### Recovery Procedures

**If you accidentally:**

**Committed secrets:**
```bash
# Remove from history immediately
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/secret/file' \
--prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner for large repos
```

**Force pushed to main:**
```bash
# Contact team immediately
# Restore from backup or previous commit
git reset --hard <last-good-commit>
git push --force-with-lease origin main
```

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
# Create PR via GitHub UI or CLI
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
# Edit pyproject.toml, CHANGELOG.md
git add .
git commit -m "chore: prepare v1.2.0 release"

# 3. Create release PR
git push origin release/v1.2.0
# PR review focuses on version, changelog, documentation

# 4. After merge, tag release
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

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
git config --global alias.visual '!gitk'
```

### Repository-Specific Settings

```bash
# In project root
git config core.autocrlf false  # Consistent line endings
git config pull.rebase true     # Rebase on pull instead of merge
git config branch.autosetupmerge always
git config branch.autosetuprebase always
```

## References

- **[Environment Setup](environment-setup.md)** - Development environment configuration
- **[Testing Standards](testing-standards.md)** - Test requirements before commits
- **[AI Assistant Commit Protocols](../ai-assistant/commit-protocols.md)** - AI-specific commit requirements

---

**📝 Next Steps**: Review [Testing Standards](testing-standards.md) for test requirements before commits.
