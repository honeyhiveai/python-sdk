# Task 3: Add Deployment Guidance

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Document deployment steps and rollback  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Document deployment procedures including steps, environment configuration, database migrations, and rollback strategies.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-2 must be completed

⚠️ MUST-READ: Reference template

See `core/implementation-template.md` for deployment examples.

---

## Steps

### Step 1: Add Deployment Section

Append to implementation.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/implementation.md << 'EOF'

---

## 5. Deployment

EOF
```

### Step 2: Document Deployment Steps

```markdown
### Deployment Steps

1. Run tests: `pytest`
2. Run linter: `flake8`
3. Build: `{build command}`
4. Run migrations: `{migration command}`
5. Deploy: `{deploy command}`
6. Verify health: `curl {health-endpoint}`
7. Smoke test critical paths
```

### Step 3: Document Environment Variables

```markdown
### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...
API_KEY=xxx

# Optional
LOG_LEVEL=INFO
CACHE_TTL=300
```

**Security:** Never commit secrets to git. Use environment variables or secret management.
```

### Step 4: Document Database Migrations

```markdown
### Database Migrations

```bash
# Create migration
alembic revision -m "description"

# Apply migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

**Pre-deployment:** Test migrations on staging

**Post-deployment:** Verify data integrity
```

### Step 5: Document Rollback Strategy

```markdown
### Rollback Strategy

**If deployment fails:**

1. Identify issue severity
2. Stop deployment if critical
3. Run rollback script: `{rollback command}`
4. Verify system health
5. Investigate root cause

**Rollback checklist:**
- [ ] Previous version artifacts available
- [ ] Database migrations reversible
- [ ] Data backup recent
- [ ] Rollback tested on staging
```

### Step 6: Add Deployment Checklist

Use checklist from `core/implementation-template.md`:

```markdown
### Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Migrations tested
- [ ] Environment variables configured

**Deployment:**
- [ ] Migrations run successfully
- [ ] Application deployed
- [ ] Health checks passing

**Post-Deployment:**
- [ ] Metrics normal
- [ ] Logs clean
- [ ] Critical paths tested
```

📊 COUNT-AND-DOCUMENT: Deployment guidance
- Deployment steps: [number]
- Environment variables: [number]
- Rollback procedures: ✅

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Deployment steps documented ✅/❌
- [ ] Environment variables listed ✅/❌
- [ ] Migration guidance provided ✅/❌
- [ ] Rollback strategy defined ✅/❌
- [ ] Deployment checklist included ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-4-troubleshooting.md](task-4-troubleshooting.md)
