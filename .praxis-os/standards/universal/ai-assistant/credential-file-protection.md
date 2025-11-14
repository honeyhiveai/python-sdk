# AI Assistant Credential File Protection Rules

**🚨 CRITICAL: NEVER WRITE TO CREDENTIAL FILES**

## 🚫 ABSOLUTELY FORBIDDEN Operations

**AI assistants are STRICTLY FORBIDDEN from ANY write operations on credential files:**

```bash
# ❌ NEVER USE - Can overwrite user's actual credentials
echo "..." > .env                       # Overwrites .env file
cat > .env << EOF                       # Overwrites .env file  
cp file .env                           # Copies over .env file
mv file .env                           # Moves/renames to .env file
echo "..." >> .env                     # Appends to .env file
sed -i 's/old/new/' .env              # In-place editing of .env

# ❌ NEVER USE - File writing tools on credential files
write(.env, content)                   # Write tool on .env
search_replace(.env, old, new)         # Edit tool on .env  
MultiEdit(.env, edits)                 # Multi-edit tool on .env
```

## 📁 Protected File Patterns

**NEVER write to these files:**
- `.env` and `.env.*` (all variants)
- `credentials.json`, `secrets.yaml`, `auth.json`
- `~/.ssh/*`, `~/.aws/credentials`
- Any file containing API keys, tokens, or passwords

## ✅ SAFE Operations ONLY

```bash
# ✅ SAFE: Read-only operations
read_file(.env)                       # Read file with tool
cat .env                              # Read file contents
grep "PATTERN" .env                   # Search within file
ls -la .env                           # Check file existence

# ✅ SAFE: Work with templates only
cat env.integration.example           # Show template contents
```

## 🚨 Real-World Incident

```bash
# ❌ WHAT HAPPENED: AI assistant overwrote user's .env file
echo "HH_API_KEY=test_key" > .env

# 💥 RESULT: User's actual API keys permanently lost
# 🕐 IMPACT: User had to regenerate all API keys
```

## 🔧 Safe Alternatives

### Instead of Writing .env Files
```bash
# ❌ WRONG: Create or overwrite .env
echo "API_KEY=test" > .env

# ✅ CORRECT: Guide user to create their own
echo "Please create a .env file with your credentials:"
echo "cp env.integration.example .env"
echo "Then edit .env with your actual API keys"
```

### Instead of Modifying Credentials
```bash
# ❌ WRONG: Try to update API key in .env
sed -i 's/old_key/new_key/' .env

# ✅ CORRECT: Instruct user on manual update
echo "To update your API key:"
echo "1. Open .env in your editor"
echo "2. Replace the API key value"
echo "3. Save the file"
```

## 📋 Escalation Protocol

**When credential file operation is requested:**

```
🚨 CREDENTIAL FILE PROTECTION VIOLATION

I cannot write to credential files (.env, etc.) as this could:
- Overwrite your actual API keys and secrets
- Cause permanent loss of credentials

Instead, I can:
- Read the file to understand current configuration
- Provide instructions for manual updates
- Guide you through safe credential management

Please let me know how you'd like to proceed safely.
```

## 🛡️ Enforcement

**Before ANY file operation, check:**
```bash
case "$file" in
    .env|.env.*|*/credentials.*|*/secrets.*|*/.ssh/*|*/.aws/credentials)
        echo "❌ BLOCKED: Cannot write to credential file: $file"
        exit 1
        ;;
esac
```

---

**🔐 Remember**: Credential files contain irreplaceable secrets. Always read-only, never write.
