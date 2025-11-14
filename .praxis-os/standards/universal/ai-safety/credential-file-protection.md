# Credential File Protection - Universal AI Safety Pattern

**Timeless rule for AI assistants to never modify credential files.**

---

## 🎯 TL;DR - Credential File Protection Quick Reference

**Keywords for search**: credential protection, .env safety, API key protection, never write credentials, secrets safety, credential files, environment variables safety, AI safety rules

**Core Principle:** NEVER write to credential files. Credentials are irreplaceable secrets. Always read-only, never write.

**ABSOLUTELY FORBIDDEN:**
```bash
❌ echo "API_KEY=test" > .env        # Overwrites real credentials
❌ write(".env", content)            # File tools forbidden
❌ sed -i 's/old/new/' .env          # No in-place editing
❌ mv backup.env .env                # No moving to credential files
```

**Protected File Patterns:**
- `.env` and `.env.*` (all variants)
- `credentials.json`, `secrets.yaml`, `auth.json`
- `~/.ssh/*` (SSH keys)
- `~/.aws/credentials`, `~/.kube/config`
- Any file containing API keys, tokens, passwords

**Safe Operations ONLY:**
- ✅ Read credential files
- ✅ Reference values in code
- ✅ Create `.env.example` templates (fake values)
- ✅ Document credential requirements
- ✅ Validate credential format

**Safe Alternatives:**
- Create example files: `.env.example` with fake values
- Update documentation about required credentials
- Provide instructions for manual setup
- Use configuration management templates

**Why This Matters:**
- Credentials are IRREPLACEABLE (unique, cannot be recovered)
- Overwriting loses access to services permanently
- Regeneration requires updating multiple systems
- Can cause production outages

**Enforcement:**
- Pre-commit hooks validate no credential file modifications
- Linter checks for credential file writes
- Code review flags credential file changes

---

## ❓ Questions This Answers

1. "Can I write to .env files?"
2. "What files are protected from AI modification?"
3. "Why can't AI modify credential files?"
4. "How do I create example credential files?"
5. "What happens if AI writes to .env?"
6. "What are safe operations on credential files?"
7. "How do I handle credential configuration?"
8. "What enforcement exists for credential protection?"
9. "How do I test credential safety?"
10. "What are credential file patterns to avoid?"

---

## What is Credential File Protection?

Credential file protection is a strict safety rule that prevents AI assistants from writing to files containing API keys, passwords, tokens, or other secrets.

**Key principle:** Credential files contain irreplaceable secrets. Always read-only, never write.

---

## What Operations Are ABSOLUTELY FORBIDDEN?

These operations MUST NEVER be performed on credential files under any circumstances.

### Never Write to These Files

```bash
# ❌ NEVER - Overwrites user's actual credentials
echo "API_KEY=test" > .env
cat > .env << EOF
cp file .env
mv file .env
echo "API_KEY=test" >> .env
sed -i 's/old/new/' .env

# ❌ NEVER - File tools on credential files
write(".env", content)
search_replace(".env", old, new)
edit_file(".env", changes)
```

---

## What File Patterns Are Protected?

These file patterns are NEVER to be written to by AI agents.

**Never write to:**
- `.env` and `.env.*` (all variants: `.env.local`, `.env.production`, etc.)
- `credentials.json`, `secrets.yaml`, `auth.json`, `config.secret.*`
- `~/.ssh/*` (SSH keys)
- `~/.aws/credentials` (AWS credentials)
- `~/.kube/config` (Kubernetes config)
- Any file containing API keys, tokens, passwords, or secrets

---

## What Happens When This Rule Is Violated? (Real Incident)

Real-world example demonstrating the catastrophic consequences of violating credential file protection.

### The API Key Loss

```bash
# ❌ What AI did:
echo "HH_API_KEY=test_key_for_demo" > .env

# 💥 What happened:
# - User's actual API key was PERMANENTLY OVERWRITTEN
# - Key was unique, cannot be recovered
# - User had to regenerate ALL API keys
# - Downtime while new keys propagated
# - Multiple services needed reconfiguration
```

**Impact:**
- 2 hours to regenerate keys
- 4 hours to update all services
- Broken production deployments
- Lost user trust in AI assistant

---

## What Operations Are Safe on Credential Files?

ONLY these read-only operations are permitted on credential files.

### Reading is Safe

```bash
# ✅ SAFE: Read-only operations
read_file(".env")
cat .env
grep "PATTERN" .env
ls -la .env
```

---

### Working with Templates

```bash
# ✅ SAFE: Show template to user
cat .env.example
read_file("env.integration.example")
```

---

## What Are Safe Alternatives to Writing Credential Files?

When you need to provide credential configuration guidance, use these safe alternatives.

### Instead of Creating .env → Guide User

```bash
# ❌ WRONG
echo "API_KEY=your_key_here" > .env

# ✅ CORRECT
echo "Please create your .env file:"
echo "  cp .env.example .env"
echo "  then edit .env with your actual credentials"
```

---

### Instead of Modifying Credentials → Instruct User

```bash
# ❌ WRONG
sed -i 's/old_key/new_key/' .env

# ✅ CORRECT
cat << 'EOF'
To update your API key:
1. Open .env in your editor
2. Find the line: API_KEY=old_value
3. Replace with: API_KEY=new_value
4. Save the file
EOF
```

---

### Instead of Writing Secrets → Use Environment Variables

```python
# ❌ WRONG: Hardcode secrets
api_key = "sk-1234567890abcdef"

# ✅ CORRECT: Read from environment
import os
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
```

---

## How Is Credential Protection Enforced?

Multiple layers of enforcement prevent credential file modifications.

### Pre-Write Check (MANDATORY)

**Before ANY file write operation:**

```python
def is_credential_file(filepath):
    """Check if file is a credential file (never write to these)."""
    credential_patterns = [
        ".env",
        ".env.*",
        "credentials",
        "secrets",
        "auth.json",
        ".ssh/",
        ".aws/credentials",
        ".kube/config",
    ]
    
    for pattern in credential_patterns:
        if pattern in filepath:
            return True
    return False

# Usage
if is_credential_file(target_file):
    raise PermissionError(
        f"BLOCKED: Cannot write to credential file: {target_file}"
    )
```

---

## How to Validate Compliance with Credential Protection?

Checklist to verify compliance before any credential-related operation.

**Before ANY file write:**

- [ ] Is this a `.env` file? (If YES → BLOCK)
- [ ] Does filename contain "credential", "secret", "auth"? (If YES → BLOCK)
- [ ] Does path contain `.ssh`, `.aws`, `.kube`? (If YES → BLOCK)
- [ ] Can I instruct user instead of writing? (If YES → do that)
- [ ] Is there a `.example` template I can show? (If YES → show it)

---

## What to Do If Credential File Was Modified? (Escalation)

Immediate action protocol if credential file modification occurs.

### When Operation is Requested

```
🚨 CREDENTIAL FILE PROTECTION VIOLATION

I cannot write to credential files (.env, etc.) as this could:
- Overwrite your actual API keys and secrets
- Cause permanent loss of credentials
- Compromise security

Instead, I can:
- Read the file to understand current configuration
- Provide instructions for manual updates
- Show you the template file (.env.example)
- Guide you through safe credential management

Please let me know how you'd like to proceed safely.
```

---

## Why This Rule Exists

### 1. Credentials Are Irreplaceable

```
API Key: sk-1234567890abcdef
         ↓
    If lost, CANNOT BE RECOVERED
    Must regenerate (time + effort)
    Must update all services using it
```

**Unlike code:** You can't just "undo" to get keys back.

---

### 2. Templates vs Real Files

```
.env.example     → Contains placeholders, safe to overwrite
.env             → Contains REAL secrets, NEVER overwrite
```

---

### 3. Principle of Least Privilege

```
AI assistant needs to:
- Read configuration (to understand setup)
- Write code (implementation)
- Guide user (instructions)

AI assistant does NOT need to:
- Modify credentials (user's responsibility)
```

---

## How to Detect Credential File Violations?

Methods for detecting and preventing credential file modifications.

### Filename Patterns

```regex
# Detect credential files by name
\.env($|\.)              # .env or .env.local, etc.
credentials\.(json|yaml) # credentials.json, credentials.yaml
secrets\.                # secrets.yaml, secrets.json
auth\.json               # auth.json
```

### Path Patterns

```regex
# Detect credential files by path
/\.ssh/                  # SSH keys
/\.aws/credentials       # AWS credentials
/\.kube/config          # Kubernetes config
```

### Content Patterns

```regex
# Detect secrets in file content (warning only)
(api_key|secret|token|password)\s*=\s*['\"][^'\"]+['\"]
```

---

## How to Test Credential Safety?

Testing strategies to validate credential protection compliance.

### Positive Tests (Should Block)

```python
def test_blocks_env_file():
    with pytest.raises(PermissionError):
        write_file(".env", "API_KEY=test")

def test_blocks_credentials_json():
    with pytest.raises(PermissionError):
        write_file("credentials.json", "{}")

def test_blocks_ssh_key():
    with pytest.raises(PermissionError):
        write_file("~/.ssh/id_rsa", "private_key")
```

### Negative Tests (Should Allow)

```python
def test_allows_env_example():
    # .env.example is a template, safe to write
    write_file(".env.example", "API_KEY=your_key_here")

def test_allows_config_py():
    # config.py is not a credential file
    write_file("config.py", "DEBUG = True")
```

---

## What Are Credential Protection Best Practices?

Guidelines for safely handling credential configuration.

### 1. Always Use Templates

```bash
# Project structure
.env.example         # Template with placeholders (committed)
.env                 # Actual credentials (gitignored, never committed)
```

### 2. Document Setup Process

```markdown
## How to Set Up Credential Protection?

Installation and configuration of credential protection enforcement.

1. Copy template: `cp .env.example .env`
2. Edit `.env` with your actual credentials
3. Never commit `.env` to version control
```

### 3. Use Environment Variables

```python
# Good: Read from environment
import os
API_KEY = os.getenv("API_KEY")

# Bad: Hardcode secrets
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS
```

---

## How to Implement Credential Protection by Language?

Language-specific patterns for credential file detection and protection.

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/ai-workflows/credential-management.md` (Language-specific patterns)
- See `.praxis-os/standards/security/secrets-management.md` (Comprehensive security)
- Etc.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Writing to .env** | `pos_search_project(content_type="standards", query="can I write to .env")` |
| **Credential protection** | `pos_search_project(content_type="standards", query="credential file protection")` |
| **Protected files** | `pos_search_project(content_type="standards", query="what files protected AI")` |
| **Safe alternatives** | `pos_search_project(content_type="standards", query="safe alternatives credential files")` |
| **Example files** | `pos_search_project(content_type="standards", query="create env example")` |
| **Enforcement** | `pos_search_project(content_type="standards", query="credential protection enforcement")` |
| **Testing safety** | `pos_search_project(content_type="standards", query="test credential safety")` |
| **Violation response** | `pos_search_project(content_type="standards", query="credential file modified")` |

---

## 🔗 Related Standards

**Query workflow for credential safety:**

1. **Start with protection rules** → `pos_search_project(content_type="standards", query="credential file protection")` (this document)
2. **Learn git safety** → `pos_search_project(content_type="standards", query="git safety rules")` → `standards/ai-safety/git-safety-rules.md`
3. **Understand security patterns** → `pos_search_project(content_type="standards", query="security patterns")` → `standards/security/security-patterns.md`
4. **Learn production checklist** → `pos_search_project(content_type="standards", query="production code checklist")` → `standards/ai-safety/production-code-checklist.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/git-safety-rules.md` - Git operations safety → `pos_search_project(content_type="standards", query="git safety rules")`
- `standards/ai-safety/production-code-checklist.md` - Production code requirements → `pos_search_project(content_type="standards", query="production code checklist")`
- `standards/ai-safety/import-verification-rules.md` - Import safety → `pos_search_project(content_type="standards", query="import verification")`

**Security:**
- `standards/security/security-patterns.md` - Universal security practices → `pos_search_project(content_type="standards", query="security patterns")`

**Installation:**
- `standards/installation/gitignore-requirements.md` - Gitignore patterns → `pos_search_project(content_type="standards", query="gitignore requirements")`

---

**Credential files contain irreplaceable secrets. AI assistants must NEVER write to them. Use read-only access and guide users to manage their own credentials safely.**
