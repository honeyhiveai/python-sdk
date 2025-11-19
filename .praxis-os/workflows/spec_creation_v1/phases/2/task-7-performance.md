# Task 6: Plan Performance

**Phase:** 2 (Technical Design)  
**Purpose:** Define performance strategies and optimizations  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Define performance strategies, optimizations, and monitoring to meet non-functional requirements.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-5 must be completed

⚠️ MUST-READ: Reference template

See `core/specs-template.md` for complete performance section.

---

## Steps

### Step 1: Add Performance Section

Append to specs.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'

---

## 6. Performance Design

---

EOF
```

### Step 2: Define Caching Strategy

Follow pattern from `core/specs-template.md`:

```markdown
### 6.1 Caching

**L1: Application Cache**
- Technology: Redis
- TTL: 5 minutes
- Eviction: LRU

**L2: Query Cache**
- Expensive queries
- TTL: 1 hour
```

### Step 3: Define Database Optimization

```markdown
### 6.2 Database Optimization

- Index foreign keys
- Connection pooling (20 connections)
- Read replicas (2 replicas)
```

### Step 4: Define API Optimization

```markdown
### 6.3 API Optimization

**Targets:**
- Simple queries: < 100ms p95
- Complex queries: < 200ms p95

**Strategies:**
- Pagination (max 100 items)
- Compression (gzip > 1KB)
- Rate limiting (100 req/min/user)
```

### Step 5: Define Scaling Strategy

```markdown
### 6.4 Scaling

**Horizontal:**
- Stateless servers
- Load balancer
- Auto-scaling at CPU > 70%

**Load Testing:**
- 1,000 req/sec sustained
- 5,000 concurrent users
```

### Step 6: Define Monitoring

```markdown
### 6.5 Monitoring

**Metrics:**
- Response time (p50, p95, p99)
- Throughput (req/sec)
- Error rate

**SLIs:**
- Availability: 99.9%
- Latency p95: < 200ms
- Error rate: < 0.1%

**Alerts:**
- Response time p95 > 500ms: Warning
- Error rate > 1%: Warning
```

📊 COUNT-AND-DOCUMENT: Performance strategies
- Cache layers: [number]
- Optimizations: [number]
- Monitoring metrics: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Caching strategy defined ✅/❌
- [ ] Database optimization planned ✅/❌
- [ ] API targets set ✅/❌
- [ ] Scaling strategy documented ✅/❌
- [ ] Monitoring defined ✅/❌

---

## Phase 2 Completion

🎯 PHASE-COMPLETE: Technical design complete

specs.md should contain:
- ✅ Architecture with diagrams
- ✅ Component definitions
- ✅ API specifications
- ✅ Data models
- ✅ Security controls
- ✅ Performance strategies

Submit checkpoint evidence to advance to Phase 3.