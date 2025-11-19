# Technical Specifications Template

This template provides comprehensive structure for creating specs.md during Phase 2.

---

## Complete Specs.md Structure

```markdown
# Technical Specifications

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 System Architecture

[Insert architecture diagram from core/architecture-diagrams.md]

**Key Components:**
- **Component A:** {Responsibility}
- **Component B:** {Responsibility}

**Architectural Principles:**
- {Principle 1}
- {Principle 2}

### 1.2 Architectural Decisions

#### Decision 1: {Pattern/Technology Choice}

**Decision:** {What was decided}

**Rationale:** 
- {Requirement it addresses}
- {Benefit}

**Alternatives Considered:**
- {Alternative}: {Why not chosen}

**Trade-offs:**
- **Pros:** {advantages}
- **Cons:** {disadvantages}

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | Component X | {Explanation} |

### 1.4 Technology Stack

**Frontend:**
- Framework: {e.g., React}

**Backend:**
- Language: {e.g., Python}
- Framework: {e.g., FastAPI}

**Database:**
- Primary: {e.g., PostgreSQL}
- Cache: {e.g., Redis}

---

## 2. Component Design

### 2.1 Component: {Name}

**Purpose:** {What it does}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}

**Requirements Satisfied:**
- FR-{XXX}: {How}

**Public Interface:**
```python
class ComponentName:
    def method_1(self, param: Type) -> ReturnType:
        """Handle operation."""
        pass
```

**Dependencies:**
- Requires: {Component/service}
- Provides: {What others depend on}

**Error Handling:**
- {Condition} → {How handled}

---

## 3. API Design

### 3.1 REST API Endpoints

#### GET /resources

**Purpose:** Retrieve resources

**Authentication:** Required

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number |

**Response 200:**
```json
{
  "data": [],
  "meta": {}
}
```

**Error Responses:**
- 401: Unauthorized
- 404: Not found

### 3.2 Internal Interfaces

```python
class ServiceInterface:
    def create(self, data: DTO) -> Entity:
        pass
```

### 3.3 DTOs

```python
@dataclass
class ResourceDTO:
    name: str
    description: Optional[str]
```

### 3.4 Event Schemas

```json
{
  "event_type": "resource.created",
  "data": {}
}
```

### 3.5 Error Handling

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable"
  }
}
```

---

## 4. Data Models

### 4.1 Domain Models

```python
@dataclass
class Resource:
    id: UUID
    name: str
    status: Status
    created_at: datetime
```

### 4.2 Database Schema

**Table: resources**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Identifier |
| name | VARCHAR(255) | NOT NULL | Name |

**Indexes:**
- idx_resources_owner ON (owner_id)

### 4.3 Relationships

[Insert ERD from core/architecture-diagrams.md]

### 4.4 Validation

- `name`: 1-255 characters
- `status`: Valid enum value

---

## 5. Security Design

### 5.1 Authentication

**Mechanism:** OAuth 2.0 + JWT

**Token Structure:**
```json
{
  "sub": "user_id",
  "exp": 1234567890
}
```

### 5.2 Authorization

**Model:** RBAC

**Roles:**
- user: Read own
- admin: Full access

### 5.3 Data Protection

**Encryption:**
- At rest: AES-256
- In transit: TLS 1.3

**PII Handling:**
- Encrypted in database
- Masked in logs

### 5.4 Input Validation

- Parameterized queries
- Sanitize inputs
- CSRF tokens

### 5.5 Security Monitoring

**Audit Logging:**
- Authentication attempts
- Authorization failures

---

## 6. Performance Design

### 6.1 Caching

**L1: Application Cache**
- Redis
- TTL: 5 minutes

**L2: Query Cache**
- Expensive queries
- TTL: 1 hour

### 6.2 Database Optimization

- Index foreign keys
- Connection pooling
- Read replicas

### 6.3 API Optimization

**Targets:**
- Simple queries: < 100ms p95
- Complex queries: < 200ms p95

**Strategies:**
- Pagination
- Compression
- Rate limiting

### 6.4 Scaling

**Horizontal:**
- Stateless servers
- Load balancer
- Auto-scaling

### 6.5 Monitoring

**Metrics:**
- Response time (p50, p95, p99)
- Throughput
- Error rate

**SLIs:**
- Availability: 99.9%
- Latency p95: < 200ms
```

---

## Quick Reference

### Component Definition Pattern

```markdown
### Component: {Name}

**Purpose:** {One-sentence description}

**Responsibilities:**
- {What it does}

**Interface:**
```python
# Code example
```

**Dependencies:** {What it needs}
```

### API Endpoint Pattern

```markdown
#### GET /endpoint

**Purpose:** {What it does}

**Request:**
| Param | Type | Required | Desc |
|-------|------|----------|------|

**Response 200:**
```json
{}
```

**Errors:** 401, 404, 500
```

### Data Model Pattern

```markdown
### Model: {Name}

```python
@dataclass
class Model:
    field: Type
```

**Validation:**
- {Rule}

**Business Logic:**
- {Rule}
```
