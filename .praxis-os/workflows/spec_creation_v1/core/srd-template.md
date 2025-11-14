# Software Requirements Document Template

This template provides comprehensive structure and examples for creating srd.md during Phase 1.

---

## Complete SRD Structure

```markdown
# Software Requirements Document

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Priority:** {Critical/High/Medium/Low}  
**Category:** {Feature/Enhancement/Fix}

---

## 1. Introduction

### 1.1 Purpose

This document defines the requirements for {brief_description}.

### 1.2 Scope

This feature will {brief_scope_statement}.

---

## 2. Business Goals

### Goal 1: {Goal Title}

**Objective:** {Specific, measurable business outcome}

**Success Metrics:**
- {Metric 1}: {Current state} → {Target state}
- {Metric 2}: {Current state} → {Target state}

**Business Impact:**
- {Who benefits and how}
- {Expected value or cost savings}

---

## 3. User Stories

### Story 1: {Short Title}

**As a** {specific user type}  
**I want to** {specific capability}  
**So that** {specific benefit}

**Acceptance Criteria:**
- Given {context/precondition}
- When {action taken}
- Then {expected outcome}

**Priority:** {Critical/High/Medium/Low}

---

## 4. Functional Requirements

### FR-001: {Requirement Title}

**Description:** The system shall {specific capability or behavior}.

**Priority:** {Critical/High/Medium/Low}

**Related User Stories:** Story {number}

**Acceptance Criteria:**
- {Specific, testable criterion}
- {Specific, testable criterion}

---

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-P1: Response Time**
- API endpoints: 95th percentile response time < 200ms
- Database queries: 99th percentile < 100ms

### 5.2 Security

**NFR-S1: Authentication**
- All API endpoints require authentication
- Support OAuth 2.0 and API key authentication

### 5.3 Reliability

**NFR-R1: Availability**
- System uptime: 99.9%

### 5.4 Scalability

**NFR-SC1: Horizontal Scaling**
- System shall scale horizontally

### 5.5 Usability

**NFR-U1: Accessibility**
- WCAG 2.1 Level AA compliance

### 5.6 Maintainability

**NFR-M1: Code Quality**
- Test coverage: minimum 80%

---

## 6. Out of Scope

### Explicitly Excluded

#### Features

**Not Included in This Release:**
1. **{Feature Name}**
   - **Reason:** {Why excluded}
   - **Future Consideration:** {Potential for future phase}

#### User Types / Personas

**Not Supported:**
- **{User Type}**: {Reason}

#### Platforms / Environments

**Not Supported:**
- **{Platform}**: {Reason}

---

## 6.1 Future Enhancements

**Potential Phase 2:**
- {Feature or capability}

**Potential Phase 3:**
- {Feature or capability}
```

---

## Good Examples

### Good Business Goal

```markdown
### Goal 1: Reduce Customer Support Costs

**Objective:** Enable users to self-serve password resets, reducing support tickets by 40%

**Success Metrics:**
- Password reset tickets: 200/week → 120/week
- Average resolution time: 15 minutes → 2 minutes
- User satisfaction: 3.5/5 → 4.2/5

**Business Impact:**
- Save $50,000/year in support costs
- Improve user experience (faster resolution)
- Free support team for complex issues
```

### Good User Story

```markdown
### Story 1: Self-Service Password Reset

**As a** registered user who forgot their password  
**I want to** reset my password via email link  
**So that** I can regain access without contacting support

**Acceptance Criteria:**
- Given I'm on the login page
- When I click "Forgot Password" and enter my email
- Then I receive a reset link within 2 minutes
- And the link expires after 1 hour
- And I can set a new password meeting security requirements
- And I'm automatically logged in after reset

**Priority:** Critical
```

### Good Functional Requirement

```markdown
### FR-001: Email Validation

**Description:** The system shall validate all email addresses against RFC 5322 format before accepting registration.

**Priority:** Critical

**Related User Stories:** Story 1, Story 3

**Acceptance Criteria:**
- Email format validation completes within 50ms
- Invalid emails display error message within 100ms
- Error message identifies specific format issue
- Special characters (@, +, .) handled correctly
- International domains (IDN) supported
```

---

## Bad Examples (Anti-Patterns)

### ❌ Vague Business Goal

```markdown
### Goal: Better System

**Objective:** Make the system better and more user-friendly

**Success Metrics:**
- Improve things
- Make users happy
```

**Why Bad:** Not measurable, no specific outcomes, no business impact

### ❌ Solution-Focused User Story

```markdown
**As a** developer  
**I want to** implement a REST API endpoint  
**So that** the system has better architecture
```

**Why Bad:** Technical solution, not user need; "better architecture" isn't a user benefit

### ❌ Untestable Requirement

```markdown
### FR-X: Good Performance

The system should be fast and responsive with good performance.
```

**Why Bad:** Not measurable, no specific criteria, can't be tested

---

## Validation Checklist

Before completing Phase 1, verify:

**Business Goals:**
- [ ] At least 1 goal defined
- [ ] Each has measurable success metrics
- [ ] Business impact clearly stated

**User Stories:**
- [ ] At least 1 story documented
- [ ] Follows "As a...I want...So that" format
- [ ] Has specific acceptance criteria
- [ ] Prioritized

**Functional Requirements:**
- [ ] At least 3 requirements defined
- [ ] Each has FR-XXX identifier
- [ ] Specific and testable
- [ ] Linked to user stories

**Non-Functional Requirements:**
- [ ] At least 3 categories addressed
- [ ] Measurable criteria specified
- [ ] Realistic and achievable

**Out of Scope:**
- [ ] Boundaries clearly defined
- [ ] Rationale provided
- [ ] Future path noted

---

## Common Pitfalls

1. **Requirements as Solutions:** Describe WHAT not HOW
2. **Missing Metrics:** Every goal needs measurable success criteria
3. **Vague NFRs:** "Fast" → "95th percentile < 200ms"
4. **Ignoring Out-of-Scope:** Explicit boundaries prevent scope creep
5. **No Traceability:** Link requirements to user stories and business goals
