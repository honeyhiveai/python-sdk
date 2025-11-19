# Task 5: Address Security

**Phase:** 2 (Technical Design)  
**Purpose:** Define security patterns and controls  
**Estimated Time:** 7 minutes

---

## 🎯 Objective

Define security controls and mechanisms that satisfy security requirements from Phase 1.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-4 must be completed

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("security patterns OWASP")
```

See `core/specs-template.md` for complete security section.

---

## Steps

### Step 1: Add Security Section

Append to specs.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'

---

## 5. Security Design

---

EOF
```

### Step 2: Define Authentication

Follow pattern from `core/specs-template.md`:

```markdown
### 5.1 Authentication

**Mechanism:** OAuth 2.0 + JWT

**Token Structure:**
```json
{
  "sub": "user_id",
  "exp": 1234567890
}
```

**Token Lifecycle:**
- Access: 24 hours
- Refresh: 30 days
```

### Step 3: Define Authorization

```markdown
### 5.2 Authorization

**Model:** RBAC

**Roles:**
- user: Read own
- admin: Full access

**Permissions Matrix:**
| Resource | User | Admin |
|----------|------|-------|
| Read | ✅ | ✅ |
| Write | Own only | ✅ |
```

### Step 4: Define Data Protection

```markdown
### 5.3 Data Protection

**Encryption:**
- At rest: AES-256
- In transit: TLS 1.3

**PII:**
- Encrypted in database
- Masked in logs
```

### Step 5: Define Input Validation

```markdown
### 5.4 Input Validation

- Parameterized queries (prevent SQL injection)
- Sanitize inputs (prevent XSS)
- CSRF tokens
```

### Step 6: Define Security Monitoring

```markdown
### 5.5 Security Monitoring

**Audit Logging:**
- Authentication attempts
- Authorization failures
- Sensitive data access
```

📊 COUNT-AND-DOCUMENT: Security controls
- Authentication: ✅
- Authorization: ✅
- Encryption: ✅
- Monitoring: ✅

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Authentication mechanism defined ✅/❌
- [ ] Authorization model specified ✅/❌
- [ ] Data protection controls documented ✅/❌
- [ ] Security monitoring planned ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-6-performance.md](task-6-performance.md)