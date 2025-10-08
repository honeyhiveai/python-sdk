# README Template

Template for creating README.md during Phase 5 (executive summary of the spec).

---

## Complete README.md Structure

```markdown
# {FEATURE_NAME}

**Status:** {Draft/In Review/Approved/In Progress/Complete}  
**Priority:** {Critical/High/Medium/Low}  
**Category:** {Feature/Enhancement/Fix}  
**Date:** {CURRENT_DATE}

---

## Executive Summary

{One paragraph overview: What is this feature, why it matters, what problem it solves}

**Key Benefits:**
- {Benefit 1}
- {Benefit 2}
- {Benefit 3}

---

## Quick Links

- **Requirements:** [srd.md](srd.md)
- **Technical Design:** [specs.md](specs.md)
- **Implementation Tasks:** [tasks.md](tasks.md)
- **Implementation Guide:** [implementation.md](implementation.md)

---

## Overview

### What This Feature Does

{2-3 sentences explaining the feature in plain language}

### Who It's For

- **Primary Users:** {User type and their needs}
- **Secondary Users:** {Other users who benefit}

### Success Metrics

- {Metric 1}: {Target}
- {Metric 2}: {Target}
- {Metric 3}: {Target}

---

## Requirements Summary

### Business Goals

1. **{Goal 1}:** {Brief description}
2. **{Goal 2}:** {Brief description}

### Key User Stories

- **Story 1:** As a {user}, I want to {action} so that {benefit}
- **Story 2:** As a {user}, I want to {action} so that {benefit}

### Functional Requirements (Summary)

- {FR-001}: {Brief description}
- {FR-002}: {Brief description}
- {FR-003}: {Brief description}

**Total:** {number} functional requirements

### Non-Functional Requirements (Summary)

- **Performance:** API response time < 200ms (p95)
- **Security:** OAuth 2.0 authentication, RBAC authorization
- **Reliability:** 99.9% uptime SLA
- **Scalability:** Support 10,000 concurrent users

---

## Technical Design Summary

### Architecture

**Pattern:** {Architecture pattern - e.g., Layered, Microservices}

**Key Components:**
- {Component 1}: {Responsibility}
- {Component 2}: {Responsibility}
- {Component 3}: {Responsibility}

### Technology Stack

- **Frontend:** {Technology}
- **Backend:** {Technology}
- **Database:** {Technology}
- **Infrastructure:** {Technology}

### Data Models

- {Entity 1}: {Brief description}
- {Entity 2}: {Brief description}

### APIs

- `GET /resources`: Retrieve resources
- `POST /resources`: Create resource
- `PUT /resources/{id}`: Update resource
- `DELETE /resources/{id}`: Delete resource

---

## Implementation Plan

### Timeline

**Total Estimated Time:** {hours/days}

**Phases:**
1. **Phase 1 ({duration}):** {Phase name and purpose}
2. **Phase 2 ({duration}):** {Phase name and purpose}
3. **Phase 3 ({duration}):** {Phase name and purpose}

### Key Milestones

- **Milestone 1:** {Description} - {Date/Duration}
- **Milestone 2:** {Description} - {Date/Duration}
- **Milestone 3:** {Description} - {Date/Duration}

### Dependencies

- {Dependency 1}: {Description}
- {Dependency 2}: {Description}

---

## Risks and Mitigations

### Risk 1: {Risk Description}

**Impact:** {High/Medium/Low}  
**Probability:** {High/Medium/Low}  
**Mitigation:** {How we'll address it}

### Risk 2: {Risk Description}

**Impact:** {Impact level}  
**Mitigation:** {Mitigation strategy}

---

## Out of Scope

**Not included in this release:**
- {Feature 1}: {Brief reason}
- {Feature 2}: {Brief reason}
- {Platform 1}: {Brief reason}

**Future considerations:**
- {Feature for Phase 2}
- {Feature for Phase 3}

---

## Getting Started

### For Implementers

1. Read [srd.md](srd.md) for requirements context
2. Review [specs.md](specs.md) for technical design
3. Follow [tasks.md](tasks.md) for implementation sequence
4. Reference [implementation.md](implementation.md) for patterns

### For Reviewers

1. Review [srd.md](srd.md) to understand requirements
2. Check [specs.md](specs.md) for design approach
3. Validate [tasks.md](tasks.md) for completeness

### For Stakeholders

- **Summary:** See "Executive Summary" above
- **Timeline:** See "Implementation Plan" section
- **Progress:** Track against milestones in [tasks.md](tasks.md)

---

## Success Criteria

**This feature will be considered successful when:**

- [ ] All functional requirements implemented and tested
- [ ] Non-functional requirements met (performance, security, etc.)
- [ ] User acceptance testing passed
- [ ] Production deployment completed
- [ ] Success metrics achieved

---

## Questions or Feedback

**For implementation questions:** See [implementation.md](implementation.md)  
**For requirements clarification:** See [srd.md](srd.md)  
**For design questions:** See [specs.md](specs.md)

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| {date} | 1.0 | {author} | Initial spec creation |

---

## Approval

**Spec Status:** {Draft/Pending Review/Approved}

**Approvers:**
- [ ] Product Owner: _____________
- [ ] Tech Lead: _____________
- [ ] Engineering Manager: _____________

**Approved Date:** _____________
```

---

## Good README Example

```markdown
# Self-Service Password Reset

**Status:** Approved  
**Priority:** Critical  
**Category:** Feature  
**Date:** 2025-10-07

---

## Executive Summary

Self-service password reset allows users to reset their passwords via email without contacting support. This reduces support costs by 40% ($50K/year savings) and improves user experience by reducing resolution time from 15 minutes to 2 minutes.

**Key Benefits:**
- $50,000/year cost savings in support
- Faster user resolution (2 min vs 15 min)
- Better user satisfaction (4.2/5 vs 3.5/5)

---

## Quick Links

- **Requirements:** [srd.md](srd.md)
- **Technical Design:** [specs.md](specs.md)
- **Implementation Tasks:** [tasks.md](tasks.md)

---

## Overview

### What This Feature Does

Enables registered users to reset forgotten passwords by clicking a link sent to their email, eliminating the need for support tickets.

### Who It's For

- **Primary Users:** Registered users who forgot their password
- **Secondary Users:** Support team (reduced ticket load)

### Success Metrics

- Password reset tickets: 200/week → 120/week
- Average resolution time: 15 min → 2 min
- User satisfaction: 3.5/5 → 4.2/5

---

## Requirements Summary

### Business Goals

1. **Reduce Support Costs:** Save $50K/year by automating password resets
2. **Improve UX:** Enable instant self-service instead of waiting for support

### Key User Stories

- **Story 1:** As a user who forgot my password, I want to reset it via email so I can regain access immediately
- **Story 2:** As a support agent, I want fewer password reset tickets so I can focus on complex issues

### Functional Requirements

- FR-001: Email-based password reset flow
- FR-002: Time-limited reset links (1 hour expiration)
- FR-003: Password strength validation

**Total:** 8 functional requirements

### Non-Functional Requirements

- **Performance:** Reset email delivered within 2 minutes
- **Security:** Bcrypt password hashing, one-time reset tokens
- **Reliability:** 99.9% email delivery rate

---

## Technical Design Summary

### Architecture

**Pattern:** Layered Architecture (API → Service → Repository)

**Key Components:**
- Auth Service: Handles reset token generation
- Email Service: Sends reset emails
- User Repository: Updates passwords

### Technology Stack

- **Backend:** Python 3.11 + FastAPI
- **Database:** PostgreSQL 15
- **Email:** SendGrid API
- **Cache:** Redis (reset tokens)

---

## Implementation Plan

### Timeline

**Total Estimated Time:** 16-20 hours (2-3 days)

**Phases:**
1. **Phase 1 (6h):** Database schema + reset token logic
2. **Phase 2 (8h):** Email integration + API endpoints
3. **Phase 3 (4h):** Testing + deployment

### Key Milestones

- **Milestone 1:** Backend API complete - Day 2
- **Milestone 2:** Email integration tested - Day 3
- **Milestone 3:** Production deployment - Day 3

---

## Risks and Mitigations

### Risk 1: Email Delivery Failures

**Impact:** High (users can't reset)  
**Probability:** Medium  
**Mitigation:** SendGrid has 99.9% SLA, implement retry logic

---

## Out of Scope

**Not included:**
- SMS-based reset (email only for MVP)
- Multi-factor reset verification (future Phase 2)
- Password reset for inactive accounts (60-day rule)

---

## Success Criteria

- [ ] Users can reset passwords via email
- [ ] Reset links expire after 1 hour
- [ ] Email delivery within 2 minutes
- [ ] Support tickets reduced by 40%
```

---

## README Writing Tips

1. **Keep it concise:** README is the executive summary, not the full spec
2. **Link don't duplicate:** Link to detailed docs rather than repeating content
3. **Lead with benefits:** Explain WHY before WHAT
4. **Make it scannable:** Use headings, lists, tables
5. **Update status:** Keep status current as implementation progresses
