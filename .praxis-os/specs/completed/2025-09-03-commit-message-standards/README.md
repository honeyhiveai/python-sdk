# Commit Message Standards - HoneyHive Python SDK

**Date**: 2025-09-03
**Status**: Active
**Scope**: All commit messages and git operations
**Priority**: High

## Problem Statement

Inconsistent commit message formatting, including missing quotes, malformed syntax, and poor structure undermines:

1. **Code Quality**: Unprofessional appearance in git history
2. **Automation**: Breaks tooling that parses commit messages
3. **Release Notes**: Impacts automated changelog generation
4. **Team Communication**: Reduces clarity of change intentions

### Recent Issues Identified

- **Missing Closing Quotes**: Commit titles without proper quote termination
- **Inconsistent Formatting**: Mixed use of emojis, bullets, and structure
- **Overly Long Lines**: Commit messages exceeding standard line limits
- **Poor Structure**: Lack of clear separation between title and body

## Commit Message Standards

### Format Requirements

#### **Conventional Commits Structure**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### **Title Line (MANDATORY)**
- **Length**: Maximum 50 characters
- **Format**: `<type>: <description>`
- **Capitalization**: First letter capitalized
- **Ending**: No period at the end
- **Quoting**: Use quotes ONLY for actual quoted content

**Examples:**
```bash
# ✅ CORRECT
feat: Add user authentication system
fix: Resolve memory leak in tracer initialization
docs: Update API reference for new endpoints

# ❌ WRONG - Missing closing quote
feat: Add user authentication system
# ❌ WRONG - Unnecessary quotes
"feat: Add user authentication system"
# ❌ WRONG - Too long
feat: Add comprehensive user authentication system with OAuth2 support and JWT tokens
```

#### **Body (OPTIONAL)**
- **Line Length**: Maximum 72 characters per line
- **Blank Line**: Must separate title from body
- **Content**: Explain what and why, not how
- **Bullets**: Use `-` or `*` for lists
- **Formatting**: Use Markdown syntax

#### **Footer (OPTIONAL)**
- **Breaking Changes**: `BREAKING CHANGE: description`
- **Issue References**: `Closes #123`, `Fixes #456`
- **Co-authors**: `Co-authored-by: Name <email>`

### Type Standards

#### **Primary Types (REQUIRED)**
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes affecting build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

#### **Scope (OPTIONAL)**
```bash
feat(auth): Add OAuth2 provider support
fix(tracer): Resolve span context propagation
docs(api): Update tracer initialization examples
```

### AI Assistant Requirements

#### **Commit Message Generation Protocol**

**STEP 1: Structure Validation**
```bash
# Before generating commit message
COMMIT_TITLE="feat: Add comprehensive documentation quality control system"
TITLE_LENGTH=${#COMMIT_TITLE}

if [ $TITLE_LENGTH -gt 50 ]; then
    echo "❌ Title too long: $TITLE_LENGTH characters (max 50)"
    echo "Shorten: $COMMIT_TITLE"
    exit 1
fi

# Check for unmatched quotes
if [[ $COMMIT_TITLE =~ ^\"|\"[^\"]*$ ]]; then
    echo "❌ Unmatched quotes in title"
    exit 1
fi
```

**STEP 2: Content Validation**
```bash
# Validate commit message structure
validate_commit_message() {
    local title="$1"
    local body="$2"
    
    # Check title format
    if ! [[ $title =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+ ]]; then
        echo "❌ Invalid title format: $title"
        return 1
    fi
    
    # Check for quotes misuse
    if [[ $title =~ ^\" ]] && [[ ! $title =~ \"$ ]]; then
        echo "❌ Missing closing quote in title"
        return 1
    fi
    
    # Check body line length
    if [ -n "$body" ]; then
        while IFS= read -r line; do
            if [ ${#line} -gt 72 ]; then
                echo "❌ Body line too long: ${#line} characters (max 72)"
                echo "Line: $line"
                return 1
            fi
        done <<< "$body"
    fi
    
    return 0
}
```

**STEP 3: Quality Checklist**
- [ ] Title under 50 characters
- [ ] No unmatched quotes
- [ ] Proper type prefix (feat:, fix:, docs:, etc.)
- [ ] Descriptive but concise
- [ ] Body lines under 72 characters
- [ ] Blank line between title and body
- [ ] Clear explanation of changes

### Enhanced Validation Rules

#### **Quote Usage Standards**

**NEVER use quotes unless quoting actual content:**
```bash
# ✅ CORRECT - No quotes needed
feat: Add user authentication system
fix: Resolve memory leak in tracer initialization

# ✅ CORRECT - Quoting actual content
docs: Update "Getting Started" section
fix: Handle missing "api_key" parameter error

# ❌ WRONG - Unnecessary quotes around entire title
"feat: Add user authentication system"

# ❌ WRONG - Unmatched quotes
feat: Add user authentication system"
"fix: Resolve memory leak in tracer initialization
```

#### **Line Length Enforcement**

**Title: 50 characters maximum**
```bash
# ✅ CORRECT (48 characters)
feat: Add comprehensive documentation system

# ❌ WRONG (67 characters)
feat: Add comprehensive documentation quality control system with validation
```

**Body: 72 characters maximum per line**
```bash
# ✅ CORRECT
This implements a comprehensive documentation quality control system
that prevents broken links from reaching production by treating all
Sphinx warnings as errors.

# ❌ WRONG
This implements a comprehensive documentation quality control system that prevents broken links from reaching production.
```

#### **Structure Validation**

**Proper separation and formatting:**
```bash
# ✅ CORRECT
feat: Add documentation quality control

Implement comprehensive validation system to prevent broken
documentation from reaching production:

- Add -W flag to Sphinx builds for strict validation
- Enhance CI/CD with broken link detection  
- Create Agent OS specification for quality standards
- Update pre-commit hooks with documentation checks

BREAKING CHANGE: Documentation builds now fail on warnings
Closes #123

# ❌ WRONG - No blank line separation
feat: Add documentation quality control
Implement comprehensive validation system...

# ❌ WRONG - Poor formatting
feat: Add documentation quality control

Implement comprehensive validation system to prevent broken documentation from reaching production: Add -W flag to Sphinx builds for strict validation, Enhance CI/CD with broken link detection, Create Agent OS specification for quality standards, Update pre-commit hooks with documentation checks

BREAKING CHANGE: Documentation builds now fail on warnings Closes #123
```

### Pre-commit Hook Integration

#### **Commit Message Validation Hook**

**File**: `.pre-commit-config.yaml`
```yaml
- repo: local
  hooks:
    - id: commit-msg-validation
      name: Commit Message Validation
      entry: scripts/validate-commit-msg.sh
      language: script
      stages: [commit-msg]
      always_run: true
```

**File**: `scripts/validate-commit-msg.sh`
```bash
#!/bin/bash
# Commit message validation script

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Extract title (first line)
TITLE=$(echo "$COMMIT_MSG" | head -n1)
TITLE_LENGTH=${#TITLE}

echo "🔍 Validating commit message..."
echo "Title: $TITLE"
echo "Length: $TITLE_LENGTH characters"

# Check title length
if [ $TITLE_LENGTH -gt 50 ]; then
    echo "❌ Title too long: $TITLE_LENGTH characters (max 50)"
    echo "Current: $TITLE"
    echo "Please shorten your commit title"
    exit 1
fi

# Check for conventional commit format
if ! [[ $TITLE =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+ ]]; then
    echo "❌ Invalid commit format"
    echo "Expected: <type>[scope]: <description>"
    echo "Example: feat: Add new feature"
    echo "Current: $TITLE"
    exit 1
fi

# Check for quote issues
if [[ $TITLE =~ ^\" ]] && [[ ! $TITLE =~ \"$ ]]; then
    echo "❌ Missing closing quote in title"
    echo "Current: $TITLE"
    exit 1
fi

if [[ $TITLE =~ \".*\" ]] && [[ ! $TITLE =~ \"[^\"]+\" ]]; then
    echo "❌ Unnecessary quotes around entire title"
    echo "Current: $TITLE"
    echo "Remove quotes unless quoting specific content"
    exit 1
fi

# Check for period at end
if [[ $TITLE =~ \.$ ]]; then
    echo "❌ Don't end title with period"
    echo "Current: $TITLE"
    exit 1
fi

# Validate body line lengths
BODY=$(echo "$COMMIT_MSG" | tail -n +3)
if [ -n "$BODY" ]; then
    while IFS= read -r line; do
        if [ ${#line} -gt 72 ]; then
            echo "❌ Body line too long: ${#line} characters (max 72)"
            echo "Line: $line"
            exit 1
        fi
    done <<< "$BODY"
fi

echo "✅ Commit message validation passed"
```

### AI Assistant Training Updates

#### **Mandatory Commit Message Protocol**

**Before EVERY commit, AI assistants MUST:**

1. **Generate Structured Message**
   ```bash
   # Template usage
   TYPE="feat"  # or fix, docs, etc.
   SCOPE=""     # optional
   DESCRIPTION="Add comprehensive documentation quality control"
   
   if [ -n "$SCOPE" ]; then
       TITLE="$TYPE($SCOPE): $DESCRIPTION"
   else
       TITLE="$TYPE: $DESCRIPTION"
   fi
   
   # Validate length
   if [ ${#TITLE} -gt 50 ]; then
       echo "❌ Title too long, shortening..."
       # Implement shortening logic
   fi
   ```

2. **Validate Format**
   ```bash
   # Check structure
   validate_commit_message "$TITLE" "$BODY"
   
   # Verify no quote issues
   if [[ $TITLE =~ ^\"|\"[^\"]*$ ]]; then
       echo "❌ Quote formatting error"
       exit 1
   fi
   ```

3. **Review Before Commit**
   ```bash
   echo "=== COMMIT MESSAGE REVIEW ==="
   echo "Title: $TITLE"
   echo "Length: ${#TITLE} characters"
   echo "Body preview:"
   echo "$BODY" | head -5
   echo "==========================="
   ```

#### **Common Mistakes Prevention**

**MISTAKE 1: Missing Closing Quotes**
```bash
# ❌ WRONG
git commit -m "feat: Add new feature

# ✅ CORRECT
git commit -m "feat: Add new feature"
```

**MISTAKE 2: Unnecessary Quotes**
```bash
# ❌ WRONG
git commit -m "\"feat: Add new feature\""

# ✅ CORRECT  
git commit -m "feat: Add new feature"
```

**MISTAKE 3: Title Too Long**
```bash
# ❌ WRONG (71 characters)
git commit -m "feat: Add comprehensive documentation quality control system validation"

# ✅ CORRECT (47 characters)
git commit -m "feat: Add documentation quality control system"
```

### Enforcement and Monitoring

#### **Pre-commit Integration**
- **Automatic Validation**: Every commit message checked
- **Fast Failure**: Invalid messages rejected immediately
- **Clear Feedback**: Specific error messages with examples

#### **CI/CD Integration**
- **Commit Message Linting**: Validate conventional commit format
- **Changelog Generation**: Automated release notes from commits
- **Release Notes**: Structured commit history for releases

#### **Quality Metrics**
- **Compliance Rate**: % of commits following standards
- **Rejection Rate**: % of commits rejected for format issues
- **Length Distribution**: Average title and body lengths
- **Type Usage**: Distribution of commit types

### Success Criteria

This specification succeeds when:

1. **Zero Format Errors**: No commits with quote, length, or structure issues
2. **Consistent Quality**: All commits follow conventional format
3. **Automated Prevention**: Pre-commit hooks catch issues early
4. **Clear History**: Git log is professional and readable
5. **Tool Compatibility**: Commit messages work with automation tools

### Related Standards

- `.praxis-os/specs/2025-09-03-ai-assistant-quality-framework/` - AI quality requirements
- `.praxis-os/standards/best-practices.md` - Development standards
- `.cursorrules` - AI assistant operational guidelines
- **Conventional Commits**: https://www.conventionalcommits.org/

### Implementation Checklist

- [ ] **Create validation script** - `scripts/validate-commit-msg.sh`
- [ ] **Update pre-commit config** - Add commit message validation
- [ ] **Update AI assistant training** - Include commit message standards
- [ ] **Create commit message template** - `.gitmessage` template file
- [ ] **Test validation system** - Verify error catching works
- [ ] **Monitor compliance** - Track commit message quality metrics

**NO MORE** poorly formatted commit messages will enter the repository!
