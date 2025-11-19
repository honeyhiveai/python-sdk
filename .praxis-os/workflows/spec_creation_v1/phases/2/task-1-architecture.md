# Task 1: Design Architecture

**Phase:** 2 (Technical Design)  
**Purpose:** Define system architecture with diagrams  
**Estimated Time:** 10 minutes

---

## 🎯 Objective

Design the high-level system architecture that satisfies requirements from Phase 1. Document architectural patterns, component relationships, and key design decisions.

---

## Prerequisites

🛑 EXECUTE-NOW: Phase 1 must be completed

- Review srd.md for all requirements

⚠️ MUST-READ: Query MCP and reference templates

```python
MCP: search_standards("architecture patterns SOLID principles")
```

See `core/specs-template.md` for complete specs.md structure.  
See `core/architecture-diagrams.md` for diagram templates.

---

## Steps

### Step 1: Create specs.md

Initialize from `core/specs-template.md`:

```bash
cat > .praxis-os/specs/{SPEC_DIR}/specs.md << 'EOF'
# Technical Specifications

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

EOF
```

### Step 2: Choose Architectural Pattern

Select based on requirements:
- **Layered:** Clear separation (UI, logic, data)
- **Microservices:** Independent services
- **Modular Monolith:** Single deployment, modular design
- **Event-Driven:** Asynchronous, decoupled
- **Serverless:** Function-based
- **Hexagonal:** Domain-centric

**Selection Criteria:** Scale, team size, deployment constraints, integrations

📊 COUNT-AND-DOCUMENT: Pattern selection
- Primary pattern: [name]
- Rationale: [why it fits]

### Step 3: Create Architecture Diagram

Use templates from `core/architecture-diagrams.md`. Choose appropriate diagram:
- Layered Architecture
- Microservices Architecture
- Client-Server Architecture
- Event-Driven Architecture
- Deployment Architecture

Copy diagram and customize labels for your components.

### Step 4: Document Architectural Decisions

Follow pattern from `core/specs-template.md`:

```markdown
### 1.2 Architectural Decisions

#### Decision 1: {Pattern/Technology}

**Decision:** {What was decided}

**Rationale:** 
- {Requirement it addresses}
- {Benefit}

**Alternatives Considered:**
- {Alternative}: {Why not chosen}

**Trade-offs:**
- **Pros:** {advantages}
- **Cons:** {disadvantages}
```

### Step 5: Map Architecture to Requirements

```markdown
### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | Component X | {Explanation} |
| NFR-P1 | Caching Layer | {Explanation} |
```

### Step 6: Define Technology Stack

Follow structure from `core/specs-template.md`:

```markdown
### 1.4 Technology Stack

**Frontend:** {Framework}  
**Backend:** {Language + Framework}  
**Database:** {Primary + Cache}  
**Infrastructure:** {Hosting + Containers}  
**Observability:** {Logging + Metrics}
```

### Step 7: Define Deployment Architecture

Use deployment diagram from `core/architecture-diagrams.md` and customize.

📊 COUNT-AND-DOCUMENT: Architecture complete
- Pattern: [name]
- Diagram: ✅
- Technology stack: ✅
- Requirements traced: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] specs.md created ✅/❌
- [ ] Architecture pattern selected and justified ✅/❌
- [ ] Diagram included (from `core/architecture-diagrams.md`) ✅/❌
- [ ] Architectural decisions documented ✅/❌
- [ ] Technology stack specified ✅/❌
- [ ] Requirements traceability established ✅/❌

🚨 FRAMEWORK-VIOLATION: Architecture without requirements mapping

Every element must trace to a requirement. Over-engineering occurs when architecture doesn't map to specific requirements.

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-components.md](task-2-components.md)