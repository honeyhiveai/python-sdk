# Credential File Protection - Universal AI Safety Pattern

**Timeless rule for AI assistants to never modify credential files.**

## What is Credential File Protection?

Credential file protection is a strict safety rule that prevents AI assistants from writing to files containing API keys, passwords, tokens, or other secrets.

**Key principle:** Credential files contain irreplaceable secrets. Always read-only, never write.

---

## 🚫 ABSOLUTELY FORBIDDEN Operations

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

## 📁 Protected File Patterns

**Never write to:**
- `.env` and `.env.*` (all variants: `.env.local`, `.env.production`, etc.)
- `credentials.json`, `secrets.yaml`, `auth.json`, `config.secret.*`
- `~/.ssh/*` (SSH keys)
- `~/.aws/credentials` (AWS credentials)
- `~/.kube/config` (Kubernetes config)
- Any file containing API keys, tokens, passwords, or secrets

---

## 🚨 Real-World Incident

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

## ✅ Safe Operations ONLY

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

## ✅ Safe Alternatives

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

## 🛡️ Enforcement Protocol

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

## 📋 Compliance Checklist

**Before ANY file write:**

- [ ] Is this a `.env` file? (If YES → BLOCK)
- [ ] Does filename contain "credential", "secret", "auth"? (If YES → BLOCK)
- [ ] Does path contain `.ssh`, `.aws`, `.kube`? (If YES → BLOCK)
- [ ] Can I instruct user instead of writing? (If YES → do that)
- [ ] Is there a `.example` template I can show? (If YES → show it)

---

## 🆘 Escalation Protocol

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

## 🔍 Detection Methods

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

## Testing

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

## Best Practices

### 1. Always Use Templates

```bash
# Project structure
.env.example         # Template with placeholders (committed)
.env                 # Actual credentials (gitignored, never committed)
```

### 2. Document Setup Process

```markdown
## Setup

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

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/ai-workflows/credential-management.md` (Language-specific patterns)
- See `.agent-os/standards/security/secrets-management.md` (Comprehensive security)
- Etc.

---

**Credential files contain irreplaceable secrets. AI assistants must NEVER write to them. Use read-only access and guide users to manage their own credentials safely.**
