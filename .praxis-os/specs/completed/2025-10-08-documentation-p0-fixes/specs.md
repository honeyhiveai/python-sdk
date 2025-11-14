# Technical Specifications

**Project:** Documentation P0 Fixes for HoneyHive Python SDK  
**Date:** 2025-10-08  
**Based on:** srd.md (requirements)

---

## Executive Summary

### Project Overview

This specification defines the technical approach for addressing critical documentation gaps in the HoneyHive Python SDK that directly impact customer onboarding and satisfaction. The implementation addresses all P0 (critical), P1 (high priority), and P2 (medium priority) issues identified through comprehensive analysis and customer feedback in December 2024.

### Scope

**What We're Fixing:**
- 12 functional requirements (FR-001 through FR-012) spanning documentation content, structure, and infrastructure
- Top 3 customer complaints: (1) Getting Started section violations, (2) Missing compatibility information, (3) Incomplete custom tracing documentation
- Template system enhancements for consistent integration guide updates across 7 LLM providers

**Business Impact:**
- Eliminate all documented P0/P1/P2 customer complaints
- Reduce new user onboarding friction by 50% (target)
- Enable self-service for common integration issues

### Technical Approach

**Primary Strategy:** Leverage existing Sphinx/RST framework with enhanced template-driven generation system

**Key Components:**
1. **Template System (FR-002/004/006):** Extend existing template to add compatibility matrices to all 7 provider integration guides
2. **Content Reorganization (FR-001):** Restructure How-to section to separate capability-focused guides from migration guides (Divio compliance)
3. **New Guides (FR-003/007-012):** Create 6 new/rewritten comprehensive guides covering critical missing content
4. **Validation Infrastructure (FR-005):** Implement automated validation scripts to prevent future regressions

**Architecture Pattern:** Template-Driven Documentation System with Modular Content Architecture
- Separation of concerns via Divio framework (Tutorials / How-to / Reference / Explanation)
- Single source of truth for integration guides (template propagates to 7 providers)
- Static site generation (Sphinx) with build-time validation

### Implementation Phases

**7 phases totaling ~4.2 hours of AI execution:**
1. Setup & Preparation (~15 min) - Directories + validation scripts
2. Template System Updates (~45 min) - Compatibility matrices for 7 providers
3. P0 Critical Content (~50 min) - Getting Started + Span Enrichment
4. P1 High Priority (~90 min) - LLM Patterns, Production, Class Decorators
5. P2 Medium Priority (~75 min) - SSL, Testing, Advanced Patterns
6. Validation & Quality (~20 min) - All validators pass
7. Final Review (~15 min) - Deployment preparation

### Success Metrics

**Completeness:**
- 12 functional requirements fully implemented
- 4 new Getting Started guides created
- 7 integration guides updated with compatibility sections
- 6 new/rewritten how-to guides

**Quality:**
- 0 Sphinx build errors
- 0 Divio compliance violations
- 0 broken internal links
- 100% of validation checks passing

**Customer Impact:**
- 0 migration guides in Getting Started (top complaint resolved)
- All 7 integration guides have compatibility information (blocking issue resolved)
- Span enrichment guide with 5 patterns (critical missing content added)

### Risk Mitigation

**Primary Risks:**
1. **Risk:** Validation failures during Phase 6
   - **Mitigation:** Continuous validation after each file creation; phase gates catch issues early
2. **Risk:** RST syntax errors in generated content
   - **Mitigation:** Template validation before regeneration; syntax checking in CI/CD
3. **Risk:** Breaking existing documentation links
   - **Mitigation:** Link checker validation; careful file movement with redirect consideration

**Low Overall Risk:** Documentation changes are non-breaking to SDK code; Git provides complete rollback capability.

### Dependencies

**External Dependencies:**
- Sphinx documentation framework (existing, stable)
- Python 3.11+ (existing)
- GitHub repository access (existing)

**Internal Dependencies:**
- Phase 2 (template system) must complete before Phase 3 (content references templates)
- Phase 3 (FR-003 span enrichment) must complete before Phase 5 (FR-012 references FR-003)
- All phases must complete before Phase 6 (validation)

**No Blocking Dependencies:** All tools and infrastructure exist; implementation can start immediately.

### Deployment Strategy

**Atomic Deployment:** Single PR with all changes for coherent documentation update

**Deployment Process:**
1. Create feature branch
2. Implement all 7 phases
3. Pass all validation gates
4. Manual review of generated HTML
5. Create PR with comprehensive description
6. Human review and approval
7. Merge to main → automatic deployment

**Rollback:** Git revert or hotfix branch; static hosting allows instant rollback to previous build.

### Document Navigation

This specification is organized into the following sections:

1. **Architecture Overview** - High-level design and patterns
2. **Component Design** - 10 components with interfaces and responsibilities
3. **API Design** - 8 interfaces (CLI, template, validation, build)
4. **Data Models** - Provider configuration, validation results, file structure, template context
5. **Security Design** - Access control, content integrity, dependency security, deployment security
6. **Performance Design** - Build time optimization, page load performance, developer experience

**Related Documents:**
- `srd.md` - Software Requirements (business goals, user stories, functional requirements)
- `tasks.md` - Implementation Tasks (7 phases, 29 tasks, acceptance criteria, dependencies)
- `implementation.md` - Implementation Guidance (RST patterns, validation, deployment, troubleshooting)
- `supporting-docs/DOCUMENTATION_ANALYSIS_REPORT.md` - Customer feedback and analysis

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Template-Driven Documentation System with Modular Content Architecture

The documentation system follows a **modular content architecture** where documentation is organized into four distinct categories (Divio framework: Tutorials, How-to, Reference, Explanation) with a template-driven generation system for integration guides.

**Key Characteristics:**
- **Separation of Concerns:** Content is strictly categorized by intent (learning, problem-solving, information, understanding)
- **Template-Based Generation:** Integration guides use a single source of truth (template) that generates provider-specific documentation
- **Static Site Generation:** Sphinx builds static HTML from RST source files
- **Version Control:** All documentation source lives in Git for traceability and review

**Pattern Justification:**
- Supports FR-001 (content reorganization) through clear category boundaries
- Enables FR-002 (compatibility matrices) via template system efficiency
- Facilitates FR-003 (span enrichment guide) through modular content addition
- Satisfies NFR-M1 (maintainability) through template propagation to 7 provider guides

### 1.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  Documentation Source Layer                       │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  How-to      │  │  Tutorials   │  │  Reference  │ Explanation│ │
│  │  Guides      │  │              │  │                          │ │
│  │              │  │              │  │                          │ │
│  │ [FR-001]     │  │ (No P0       │  │  (No P0                 │ │
│  │ - Getting    │  │  changes)    │  │   changes)              │ │
│  │   Started    │  │              │  │                          │ │
│  │ - Migration  │  │              │  │                          │ │
│  │              │  │              │  │                          │ │
│  │ [FR-003]     │  │              │  │                          │ │
│  │ - Span       │  │              │  │                          │ │
│  │   Enrichment │  │              │  │                          │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Template Generation System [FR-002, FR-004]         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  docs/_templates/                                          │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────┐             │ │
│  │  │  multi_instrumentor_integration_         │             │ │
│  │  │  formal_template.rst                     │             │ │
│  │  │                                           │             │ │
│  │  │  {{PROVIDER_NAME}}                        │             │ │
│  │  │  {{PYTHON_VERSION_SUPPORT}} [NEW FR-004] │             │ │
│  │  │  {{SDK_VERSION_RANGE}} [NEW FR-004]      │             │ │
│  │  │  {{INSTRUMENTOR_COMPATIBILITY}} [NEW]    │             │ │
│  │  │  {{KNOWN_LIMITATIONS}} [NEW]             │             │ │
│  │  └──────────────────────────────────────────┘             │ │
│  │                         │                                  │ │
│  │                         ▼                                  │ │
│  │  ┌──────────────────────────────────────────┐             │ │
│  │  │  generate_provider_docs.py [FR-006]      │             │ │
│  │  │                                           │             │ │
│  │  │  PROVIDER_CONFIGS = {                    │             │ │
│  │  │    "openai": {...},                      │             │ │
│  │  │    "anthropic": {...},                   │             │ │
│  │  │    ... (7 providers total)               │             │ │
│  │  │  }                                        │             │ │
│  │  └──────────────────────────────────────────┘             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Generated Integration Guides [FR-002]               │
│                                                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  openai    │ │ anthropic  │ │ google-ai  │ │ google-adk │   │
│  │  .rst      │ │ .rst       │ │ .rst       │ │ .rst       │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
│                                                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                   │
│  │  bedrock   │ │ azure-     │ │  mcp       │                   │
│  │  .rst      │ │ openai.rst │ │  .rst      │                   │
│  └────────────┘ └────────────┘ └────────────┘                   │
│                                                                   │
│  All 7 guides include new "Compatibility" section [FR-002]      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Build & Validation Layer [FR-005]             │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Sphinx Build  │  │  Link Checker  │  │  Divio           │  │
│  │  (make html)   │  │  (navigation   │  │  Compliance      │  │
│  │                │  │   validator)   │  │  Validator       │  │
│  │  - RST → HTML  │  │                │  │                  │  │
│  │  - Warnings    │  │  - Internal    │  │  - Getting       │  │
│  │  - Syntax      │  │    links       │  │    Started has 0 │  │
│  │                │  │  - Cross-refs  │  │    migration     │  │
│  │                │  │                │  │    guides        │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Deployed Documentation Site                    │
│                                                                   │
│  - Static HTML (docs/_build/html/)                               │
│  - Search index                                                   │
│  - Cross-referenced navigation                                    │
│  - Syntax-highlighted code examples                               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Architectural Decisions

#### Decision 1: Template-Driven Integration Guide Generation

**Decision:** Use a single template file with variable substitution to generate all 7 provider integration guides, rather than maintaining 7 separate files.

**Rationale:**
- **Addresses FR-002**: Enables adding compatibility matrices to all 7 guides by updating template once
- **Addresses NFR-M1**: Changes propagate automatically to all provider guides
- **Addresses NFR-Q3**: Enforces content consistency across all integration guides
- **Business Impact**: Reduces maintenance burden from 7× effort to 1× effort for structure changes

**Alternatives Considered:**
- **Manual maintenance of 7 separate files**: Rejected due to high maintenance cost, consistency risk, and violates DRY principle
- **Dynamic documentation generation at runtime**: Rejected due to added complexity, Sphinx static generation model, and unnecessary overhead

**Trade-offs:**
- **Pros:** Single source of truth, automatic consistency, bulk updates possible, reduced maintenance burden
- **Cons:** Template syntax adds slight complexity, requires generation step before viewing changes, all guides share same structure

#### Decision 2: Divio Framework for Content Organization

**Decision:** Strictly enforce the Divio documentation system's four-part categorization (Tutorials, How-to, Reference, Explanation) with no category violations.

**Rationale:**
- **Addresses FR-001**: Provides clear rules for "Getting Started" content (capability-focused, not migration-focused)
- **Addresses NFR-Q4**: Ensures each section serves a single, clear purpose for readers
- **Addresses Business Goal 2**: Improves user onboarding by providing predictable, purpose-driven navigation

**Alternatives Considered:**
- **Custom categorization scheme**: Rejected because Divio is industry-standard, well-documented, and user-tested
- **Flexible categorization (allow cross-category content)**: Rejected because current violation (migration in "Getting Started") is root cause of customer complaint

**Trade-offs:**
- **Pros:** Clear boundaries, user expectations met, prevents content drift, industry-standard approach
- **Cons:** Requires content migration (migration guides out of "Getting Started"), writers need framework education

#### Decision 3: RST + Sphinx Build System (No Change)

**Decision:** Continue using reStructuredText (RST) with Sphinx for documentation generation, no migration to alternative systems.

**Rationale:**
- **Addresses NFR-M2**: Existing system already meets documentation-as-code requirements
- **Risk Mitigation**: Changing doc systems during P0 fixes would introduce unnecessary risk
- **Ecosystem**: Sphinx provides excellent Python documentation tooling, cross-references, and API doc generation

**Alternatives Considered:**
- **Markdown + MkDocs**: Rejected due to migration cost, loss of existing Sphinx features, no business value for P0
- **Static site generators (Hugo, Jekyll)**: Rejected due to lack of Python API doc integration

**Trade-offs:**
- **Pros:** Zero migration cost, mature ecosystem, excellent Python integration, team familiarity
- **Cons:** RST syntax is more complex than Markdown (but team already trained)

#### Decision 4: Git-Based Review Process for All Changes

**Decision:** All documentation changes must go through Git pull request review with automated build checks before merge.

**Rationale:**
- **Addresses NFR-M2**: Enables diff-based review of changes
- **Addresses NFR-M3**: Automated checks catch broken links and build errors before merge
- **Addresses NFR-Q1**: Code examples can be validated before publication

**Alternatives Considered:**
- **Direct commits to main branch**: Rejected due to quality risk, no review gate, potential for broken docs
- **Manual review without automation**: Rejected because manual checking is error-prone and slow

**Trade-offs:**
- **Pros:** Quality gate, change visibility, rollback capability, blame tracking, CI integration
- **Cons:** Adds review latency (acceptable for documentation quality)

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | How-to Guides Directory Structure | Reorganize `docs/how-to/index.rst` to separate "Getting Started" and "Migration & Compatibility" sections |
| FR-002 | Template Generation System | Add compatibility section to template, update PROVIDER_CONFIGS, regenerate 7 guides |
| FR-003 | How-to Guides Directory Structure | Add new file `docs/how-to/advanced-tracing/span-enrichment.rst` |
| FR-004 | Template Variable System | Extend template variable placeholders and PROVIDER_CONFIGS schema |
| FR-005 | Build & Validation Layer | Sphinx build + navigation validator + Divio compliance checker |
| FR-006 | Template Generation Script | Enhance `generate_provider_docs.py` with --provider, --all, --dry-run flags |
| NFR-M1 | Template-Driven System | Single template updates propagate to all 7 provider guides automatically |
| NFR-M2 | Git + PR Process | All .rst files in version control with PR-based review workflow |
| NFR-Q3 | Template Enforcement | Template structure enforces consistent terminology, headings, and format |
| NFR-Q4 | Divio Framework Structure | Four distinct directories with strict categorization rules |

### 1.5 Technology Stack

**Documentation Source Format:** reStructuredText (RST)  
**Build System:** Sphinx (Python documentation generator)  
**Template Engine:** Python string templating in `generate_provider_docs.py`  
**Version Control:** Git (GitHub)  
**CI/CD:** GitHub Actions (automated builds, link checking)  
**Hosting:** Static HTML deployment (docs/_build/html/)  
**Validation Tools:** 
- Sphinx warnings/errors detection
- `scripts/validate-docs-navigation.sh` (link checker)
- Custom Divio compliance validator (to be added for FR-005)

**Dependencies:**
- Python 3.11+
- Sphinx 7.x
- sphinx-rtd-theme (Read the Docs theme)
- sphinx-tabs (for dual instrumentor tabs)
- myst-parser (if Markdown interop needed)

### 1.6 Deployment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Developer Workflow                         │
│                                                               │
│  1. Edit .rst files OR update template + regenerate          │
│  2. Commit to feature branch                                 │
│  3. Push to GitHub                                           │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Pull Request                        │
│                                                               │
│  - Code review (content quality)                             │
│  - Automated checks trigger                                  │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline (GitHub Actions)            │
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │ Sphinx Build   │→ │ Link Checker   │→ │ Compliance    │  │
│  │ (make html)    │  │ (navigation)   │  │ Validator     │  │
│  └────────────────┘  └────────────────┘  └───────────────┘  │
│                                                               │
│  Pass ✅ → Approve merge                                     │
│  Fail ❌ → Block merge, request fixes                        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Main Branch Merge                          │
│                                                               │
│  - Triggers production build                                 │
│  - Generates static HTML                                     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Documentation Site Deployment              │
│                                                               │
│  - Static HTML published to docs hosting                     │
│  - Search index updated                                      │
│  - Users access latest docs                                  │
└──────────────────────────────────────────────────────────────┘
```

**Deployment Model:** Static site generation with Git-based source control

**Build Frequency:**
- Per-commit builds on feature branches (validation only)
- Production deployment on merge to main branch

**Rollback Strategy:** Git revert + rebuild from previous commit

---

## 2. Component Design

This section defines the key components of the documentation system and their responsibilities.

---

### 2.1 Component: Getting Started Guides (FR-001)

**Purpose:** Provide capability-focused quick-win guides for users who understand basics but want to see what the SDK can do.

**Responsibilities:**
- Demonstrate core SDK capabilities in <10 minutes per guide
- Show practical, copy-paste examples
- Focus on "what you can accomplish" not "how to migrate"
- Maintain separation from migration documentation

**Requirements Satisfied:**
- FR-001: Getting Started Section Restructure
- Story 1: New User Needs Clear Getting Started Path
- NFR-Q4: Divio Framework Compliance (How-to = problem-solving, not migration)

**Files to Create:**
```
docs/how-to/getting-started/
├── setup-first-tracer.rst (NEW - 200-250 lines)
├── add-llm-tracing-5min.rst (NEW - 200-250 lines)  
├── enable-span-enrichment.rst (NEW - 200-250 lines)
└── configure-multi-instance.rst (NEW - 250-300 lines)
```

**Files to Modify:**
```
docs/how-to/index.rst
- Move migration-guide.rst to new "Migration & Compatibility" section
- Move backwards-compatibility-guide.rst to "Migration & Compatibility"
- Add new getting-started/ toctree entries
```

**Dependencies:**
- Requires: Existing SDK API documentation for cross-references
- Provides: Entry point for new users after completing tutorials

**Error Handling:**
- Broken links: Detected by CI link checker (FR-005)
- Incomplete examples: Code validation ensures examples run

---

### 2.2 Component: Integration Guide Template System (FR-002, FR-004, FR-006)

**Purpose:** Maintain single source of truth for integration guide structure, generate consistent documentation for all 7 LLM provider integrations.

**Responsibilities:**
- Define standard structure for provider integration guides
- Enable bulk updates via template modification
- Enforce consistency across all provider guides
- Support variable substitution for provider-specific details

**Requirements Satisfied:**
- FR-002: Integration Guide Compatibility Matrices
- FR-004: Template System Variable Expansion
- FR-006: Template Generation Automation
- NFR-M1: Template System Efficiency

**Files to Modify:**
```
docs/_templates/multi_instrumentor_integration_formal_template.rst
- Add "Compatibility" section with new variable placeholders:
  {{PYTHON_VERSION_SUPPORT}}
  {{SDK_VERSION_RANGE}}
  {{INSTRUMENTOR_COMPATIBILITY}}
  {{KNOWN_LIMITATIONS}}

docs/_templates/generate_provider_docs.py
- Update PROVIDER_CONFIGS dict for all 7 providers with compatibility metadata
- Add validation for required fields
- Add --all flag for batch regeneration
- Add --dry-run flag for preview

docs/_templates/template_variables.md
- Document new compatibility variables
```

**Generated Files (7 providers):**
```
docs/how-to/integrations/openai.rst
docs/how-to/integrations/anthropic.rst
docs/how-to/integrations/google-ai.rst
docs/how-to/integrations/google-adk.rst
docs/how-to/integrations/bedrock.rst
docs/how-to/integrations/azure-openai.rst
docs/how-to/integrations/mcp.rst
```

**Dependencies:**
- Requires: Python 3.11+ for generation script
- Provides: Consistent integration documentation for all providers

**Error Handling:**
- Missing variable values: Generation script validates completeness
- Template syntax errors: Python runtime errors during generation
- Malformed output: Sphinx build validation catches RST errors

---

### 2.3 Component: Span Enrichment Guide (FR-003)

**Purpose:** Teach users how to add business context, performance metadata, and error context to traces using span enrichment patterns.

**Responsibilities:**
- Document 5+ enrichment patterns with working examples
- Progress from basic to advanced usage
- Show real-world use cases
- Keep concise (150-300 lines per Divio standards)

**Requirements Satisfied:**
- FR-003: Span Enrichment Guide Creation
- Story 3: Observability Engineer Needs Span Enrichment Patterns
- NFR-Q2: Content Completeness

**Files to Create:**
```
docs/how-to/advanced-tracing/span-enrichment.rst (NEW - 200-280 lines)
```

**Files to Modify:**
```
docs/how-to/advanced-tracing/index.rst
- Add span-enrichment.rst to toctree
```

**Content Structure:**
```
1. Problem: Why enrich spans?
2. Pattern 1: Basic enrichment with enrich_span()
3. Pattern 2: Automatic enrichment in decorators
4. Pattern 3: Context-aware enrichment
5. Pattern 4: Performance metadata enrichment
6. Pattern 5: Error context enrichment
7. Cross-references to custom-spans.rst, tracer setup
```

**Dependencies:**
- Requires: Existing custom-spans.rst for cross-reference
- Provides: Foundation for FR-012 (Advanced Tracing Patterns)

**Error Handling:**
- Code example errors: Syntax validation during build
- Broken cross-references: Link checker validation

---

### 2.4 Component: LLM Application Patterns Guide (FR-007)

**Purpose:** Replace generic software patterns with LLM-specific agent architectures and workflow patterns, demonstrating HoneyHive tracing for each.

**Responsibilities:**
- Document agent architectures (ReAct, Plan-and-Execute, Reflexion, Multi-agent, Tool-using, Memory-augmented)
- Document LLM workflow patterns (RAG, Chain-of-thought, Self-correction, Prompt chaining, Few-shot)
- Include tracing examples for each architecture
- Use mermaid diagrams to show trace hierarchies

**Requirements Satisfied:**
- FR-007: Common Patterns Refocus on Agent Architectures
- Story 4: Support Engineer Needs Complete Documentation
- NFR-Q3: Domain Specificity

**Files to Modify:**
```
docs/how-to/common-patterns.rst → docs/how-to/llm-application-patterns.rst (RENAME + REWRITE)
- Remove: Generic retry patterns, config management
- Add: 6 agent architectures with tracing examples
- Add: 5 LLM workflow patterns with tracing examples
- Add: Mermaid diagrams for complex trace hierarchies
- Target: 300-380 lines
```

**Files to Modify:**
```
docs/how-to/index.rst
- Update toctree reference to llm-application-patterns.rst
```

**Dependencies:**
- Requires: Existing tracer documentation for examples
- Provides: Domain-specific value demonstration for HoneyHive

**Error Handling:**
- Mermaid syntax errors: Sphinx mermaid extension validation
- Incorrect architecture descriptions: Review process

---

### 2.5 Component: Production Deployment Guide Optimization (FR-008)

**Purpose:** Condense production guide from 756 lines to ~500 lines by extracting advanced patterns to separate guide while maintaining essential coverage.

**Responsibilities:**
- Maintain core production essentials (security, basic performance, error handling, monitoring, deployment, checklist)
- Extract advanced patterns (circuit breakers, custom monitoring, blue-green) to separate guide
- Use collapsed code blocks for lengthy examples
- Ensure logical navigation between basic and advanced guides

**Requirements Satisfied:**
- FR-008: Production Deployment Guide Condensing
- Story 4: Support Engineer Needs Complete Documentation
- NFR-Q2: Conciseness (deployment guide 300-500 lines max)

**Files to Modify:**
```
docs/how-to/deployment/production.rst (CONDENSE: 756 → 480 lines)
- Keep: Security config, performance basics, error fundamentals, monitoring basics, deployment strategies, containers, checklist
- Remove: Advanced patterns (move to advanced-production.rst)
- Add: Collapsed code blocks for long examples
```

**Files to Create:**
```
docs/how-to/deployment/advanced-production.rst (NEW - 250-300 lines)
- Circuit breaker pattern implementation
- Custom monitoring implementations
- Blue-green deployment details
- Link back to production.rst with "Prerequisites" section
```

**Files to Modify:**
```
docs/how-to/deployment/index.rst
- Add advanced-production.rst to toctree
```

**Dependencies:**
- Requires: Existing production.rst as source material
- Provides: Maintainable production documentation

**Error Handling:**
- Content extraction errors: Manual review ensures no loss of critical info
- Navigation issues: Link checker validates cross-references

---

### 2.6 Component: Class Decorator Guide (FR-009)

**Purpose:** Provide comprehensive guidance on using `@trace_class` decorator for class-level tracing patterns.

**Responsibilities:**
- Document when to use `@trace_class` vs individual `@trace`
- Show inheritance patterns, decorator mixing, performance implications
- Provide service class and agent class patterns
- Include decision matrix for choosing approach

**Requirements Satisfied:**
- FR-009: Class Decorator Coverage Expansion
- Story 3: Observability Engineer Needs Span Enrichment Patterns (partial)

**Implementation Option 1:**
```
docs/how-to/advanced-tracing/custom-spans.rst (EXPAND - add 120-160 lines)
- Add new section: "Class-Level Tracing Patterns"
```

**Implementation Option 2:**
```
docs/how-to/advanced-tracing/class-decorators.rst (NEW - 150-180 lines)
- Dedicated guide for class decorator patterns
```

**Files to Modify:**
```
docs/how-to/advanced-tracing/index.rst
- Add class-decorators.rst to toctree (if Option 2)
```

**Dependencies:**
- Requires: Existing custom-spans.rst for context
- Provides: Complete decorator coverage

**Error Handling:**
- Example validation: Code examples must be syntactically valid

---

### 2.7 Component: SSL/TLS Troubleshooting Section (FR-010)

**Purpose:** Provide self-service solutions for SSL/TLS and network issues commonly encountered in corporate environments.

**Responsibilities:**
- Document SSL certificate verification failures
- Document corporate proxy SSL errors
- Document self-signed certificate handling
- Provide diagnostic commands and configuration examples

**Requirements Satisfied:**
- FR-010: SSL/TLS Troubleshooting Section
- Story 4: Support Engineer Needs Complete Documentation
- Goal 3: Reduce Support Burden

**Files to Modify:**
```
docs/how-to/index.rst (ADD 60-90 lines to Troubleshooting section)
- New subsection: "Network & SSL Issues"
- SSL certificate errors with solutions
- Network connectivity issues
- Diagnostic commands
- Cross-references to configuration docs
```

**Dependencies:**
- Requires: reference/configuration/authentication.rst (for SSL config examples)
- Provides: Self-service SSL troubleshooting

**Error Handling:**
- Incorrect configuration examples: Code validation ensures examples are correct

---

### 2.8 Component: Testing Applications Guide (FR-011)

**Purpose:** Replace ad-hoc testing content with structured guide covering unit, integration, and evaluation testing.

**Responsibilities:**
- Document unit testing with mocked tracer
- Document integration testing with real LLM calls
- Document evaluation testing with experiments
- Provide pytest examples and fixture patterns

**Requirements Satisfied:**
- FR-011: Testing Section Restructure
- Story 4: Support Engineer Needs Complete Documentation

**Files to Create:**
```
docs/how-to/testing-applications.rst (NEW - 280-330 lines)
Structure:
- Unit Testing (mocking tracer, testing traced functions, fixtures)
- Integration Testing (real LLM calls, test mode, dataset-driven)
- Evaluation Testing (testing evaluators, regression, CI/CD)
```

**Files to Modify:**
```
docs/how-to/index.rst
- Remove: Current ad-hoc note block about testing
- Add: testing-applications.rst to toctree
```

**Dependencies:**
- Requires: Link to evaluation guides for advanced testing
- Provides: Comprehensive testing guidance

**Error Handling:**
- Example validation: All pytest examples must be runnable

---

### 2.9 Component: Advanced Tracing Patterns Guide (FR-012)

**Purpose:** Extend tracing documentation beyond basic span enrichment to cover distributed tracing, context propagation, and advanced patterns.

**Responsibilities:**
- Document session enrichment (`enrich_session()`)
- Document link/unlink patterns for distributed tracing
- Document context propagation, baggage usage
- Document custom event types, span status management

**Requirements Satisfied:**
- FR-012: Advanced Tracing Patterns Guide
- Story 3: Observability Engineer Needs Span Enrichment Patterns (advanced)

**Files to Create:**
```
docs/how-to/advanced-tracing/advanced-patterns.rst (NEW - 240-280 lines)
Structure (by complexity):
- Session enrichment patterns
- Context propagation basics
- Link/unlink for distributed tracing
- Baggage usage patterns
- Custom event types
- Span status management
- Manual span lifecycle control
```

**Files to Modify:**
```
docs/how-to/advanced-tracing/index.rst
- Add advanced-patterns.rst to toctree
- Add prerequisites note (requires span-enrichment.rst understanding)
```

**Dependencies:**
- Requires: FR-003 (span-enrichment.rst) as prerequisite
- Provides: Complete advanced tracing coverage

**Error Handling:**
- Example validation: Complex examples must be syntactically correct
- Cross-reference validation: Links to span-enrichment.rst must work

---

### 2.10 Component: Build & Validation System (FR-005)

**Purpose:** Ensure all documentation changes meet quality standards before merge through automated validation.

**Responsibilities:**
- Build all RST files to HTML with zero errors
- Validate internal links and cross-references
- Check Divio compliance (Getting Started has 0 migration guides)
- Verify completeness (compatibility sections exist in all integration guides)

**Requirements Satisfied:**
- FR-005: Documentation Build Validation
- All NFR-Q requirements (Quality)
- All user stories (ensures quality before delivery)

**Implementation:**
```
Sphinx Build:
- Command: cd docs && make html
- Check: Exit code 0, warning count not increased

Link Checker:
- Script: scripts/validate-docs-navigation.sh
- Check: All internal links resolve

Divio Compliance Validator (NEW):
- Script: scripts/validate-divio-compliance.py
- Checks:
  * docs/how-to/index.rst "Getting Started" section has 0 migration guides
  * All integration guides have "Compatibility" section

Completeness Checker (NEW):
- Script: scripts/validate-completeness.py  
- Checks:
  * FR-003: span-enrichment.rst exists
  * FR-002: All 7 integration guides have compatibility section
  * FR-001: 4 new getting-started guides exist
```

**Dependencies:**
- Requires: All component implementation complete
- Provides: Quality gate before merge

**Error Handling:**
- Build failures: Block PR merge, display errors
- Link failures: Block PR merge, list broken links
- Compliance failures: Block PR merge, identify violations

---

## 2.11 Component Interactions

**Documentation Workflow:**

```
Developer/AI Author
        │
        ▼
  Edit .rst files OR Update template
        │
        ├─→ Direct .rst edit ─────→ Stage for build
        │
        └─→ Template update ───┐
                               │
                               ▼
                Template Generation Script (FR-006)
                      │
                      ├─→ Validate PROVIDER_CONFIGS
                      ├─→ Generate 7 provider .rst files
                      └─→ Write to docs/how-to/integrations/
                               │
                               ▼
                         Stage for build
                               │
                               ▼
                      Sphinx Build System
                      │
                      ├─→ Parse all .rst files
                      ├─→ Generate HTML
                      └─→ Create search index
                               │
                               ▼
                      Build & Validation (FR-005)
                      │
                      ├─→ Link checker
                      ├─→ Divio compliance validator
                      └─→ Completeness checker
                               │
                               ├─→ PASS ✅ → Ready for review
                               │
                               └─→ FAIL ❌ → Block merge, report errors
```

**Component Dependency Table:**

| Component | Depends On | Provides To |
|-----------|-----------|-------------|
| Getting Started Guides (FR-001) | API reference, tutorials | New user onboarding |
| Template System (FR-002/004/006) | Python 3.11+, template syntax | 7 integration guides |
| Span Enrichment (FR-003) | Custom spans guide | Advanced patterns (FR-012) |
| LLM Patterns (FR-007) | Tracer docs, mermaid | Domain-specific value demo |
| Production Guide (FR-008) | Existing content | Basic + Advanced guides |
| Class Decorators (FR-009) | Custom spans guide | Complete decorator coverage |
| SSL Troubleshooting (FR-010) | Authentication config | Self-service support |
| Testing Guide (FR-011) | Evaluation guides | Testing best practices |
| Advanced Patterns (FR-012) | Span enrichment (FR-003) | Complete tracing coverage |
| Build/Validation (FR-005) | All above components | Quality gate |

---

## 2.12 Module Organization

**Documentation Source Structure:**

```
docs/
├── how-to/
│   ├── index.rst (MODIFY: reorganize Getting Started + Migration sections)
│   │
│   ├── getting-started/ (NEW DIRECTORY)
│   │   ├── setup-first-tracer.rst (NEW - FR-001)
│   │   ├── add-llm-tracing-5min.rst (NEW - FR-001)
│   │   ├── enable-span-enrichment.rst (NEW - FR-001)
│   │   └── configure-multi-instance.rst (NEW - FR-001)
│   │
│   ├── migration-compatibility/ (NEW DIRECTORY)
│   │   ├── migration-guide.rst (MOVED from root)
│   │   └── backwards-compatibility-guide.rst (MOVED from root)
│   │
│   ├── llm-application-patterns.rst (RENAMED + REWRITTEN - FR-007)
│   │   [was: common-patterns.rst]
│   │
│   ├── testing-applications.rst (NEW - FR-011)
│   │
│   ├── advanced-tracing/
│   │   ├── index.rst (MODIFY: add new guides)
│   │   ├── custom-spans.rst (EXISTING)
│   │   ├── tracer-auto-discovery.rst (EXISTING)
│   │   ├── span-enrichment.rst (NEW - FR-003)
│   │   ├── class-decorators.rst (NEW - FR-009)
│   │   └── advanced-patterns.rst (NEW - FR-012)
│   │
│   ├── deployment/
│   │   ├── index.rst (MODIFY: add advanced guide)
│   │   ├── production.rst (CONDENSE: 756 → 480 lines - FR-008)
│   │   └── advanced-production.rst (NEW - FR-008)
│   │
│   └── integrations/
│       ├── openai.rst (REGENERATE with compatibility - FR-002)
│       ├── anthropic.rst (REGENERATE - FR-002)
│       ├── google-ai.rst (REGENERATE - FR-002)
│       ├── google-adk.rst (REGENERATE - FR-002)
│       ├── bedrock.rst (REGENERATE - FR-002)
│       ├── azure-openai.rst (REGENERATE - FR-002)
│       └── mcp.rst (REGENERATE - FR-002)
│
├── _templates/
│   ├── multi_instrumentor_integration_formal_template.rst (MODIFY - FR-002)
│   ├── generate_provider_docs.py (MODIFY - FR-004/006)
│   └── template_variables.md (MODIFY - FR-004)
│
├── tutorials/ (NO CHANGES - already excellent)
├── reference/ (NO CHANGES - already comprehensive)
└── explanation/ (NO CHANGES - already solid)
```

**Validation Scripts:**

```
scripts/
├── validate-docs-navigation.sh (EXISTING - used for FR-005)
├── validate-divio-compliance.py (NEW - FR-005)
└── validate-completeness.py (NEW - FR-005)
```

**Dependency Rules:**
- No circular dependencies between guides
- Cross-references flow: Basic → Advanced (never Advanced → Basic without context)
- Template changes always regenerate before committing
- Validation always runs before merge

---

## 3. API Design & Interfaces

This section defines the programmatic interfaces for documentation generation, validation, and template management.

---

### 3.1 Template Generation Script Interface (FR-006)

**Purpose:** Command-line interface for generating provider integration documentation from templates.

**Script:** `docs/_templates/generate_provider_docs.py`

**Command-Line Interface:**

```bash
# Generate single provider
python docs/_templates/generate_provider_docs.py --provider openai

# Generate all providers
python docs/_templates/generate_provider_docs.py --all

# Dry-run mode (preview without writing)
python docs/_templates/generate_provider_docs.py --provider openai --dry-run

# Validate configuration completeness
python docs/_templates/generate_provider_docs.py --validate

# Show help
python docs/_templates/generate_provider_docs.py --help
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--provider` | str | Conditional | Provider name (openai, anthropic, google-ai, google-adk, bedrock, azure-openai, mcp). Required unless --all or --validate |
| `--all` | flag | No | Generate all 7 provider guides |
| `--dry-run` | flag | No | Preview changes without writing files |
| `--validate` | flag | No | Validate PROVIDER_CONFIGS completeness without generating |
| `--help` | flag | No | Show usage information |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success (all files generated or validation passed) |
| 1 | Invalid provider name specified |
| 2 | Missing required configuration fields |
| 3 | Template file not found |
| 4 | File write error |

**Output:**

```
Generation successful:
  - docs/how-to/integrations/openai.rst (12,345 bytes)
Validation: PASSED
  - All required fields present
  - Template variables substituted
  - No {{PLACEHOLDER}} text remaining
```

**Error Messages:**

```
ERROR: Missing required field 'python_version_support' for provider 'openai'
ERROR: Template file not found: docs/_templates/multi_instrumentor_integration_formal_template.rst
WARNING: Compatibility section missing from template
```

---

### 3.2 Template Variable Contract (FR-004)

**Purpose:** Define data contract for provider configuration that must be supplied for template generation.

**Configuration Location:** `PROVIDER_CONFIGS` dict in `docs/_templates/generate_provider_docs.py`

**Required Fields:**

```python
PROVIDER_CONFIG_SCHEMA = {
    # Existing fields (already in template)
    "provider_name": str,           # Display name (e.g., "OpenAI")
    "provider_key": str,            # URL-safe key (e.g., "openai")
    "provider_sdk": str,            # PyPI package (e.g., "openai>=1.0.0")
    "openinference_package": str,   # Instrumentor package
    
    # NEW fields for FR-002/FR-004
    "python_version_support": {
        "supported": [str],         # ["3.11+", "3.12+"]
        "partial": [str],           # ["3.10 (requires workaround)"]
        "unsupported": [str]        # ["3.9 and below"]
    },
    "sdk_version_range": {
        "minimum": str,             # "1.0.0"
        "recommended": str,         # "1.5.0+"
        "tested_versions": [str]    # ["1.0.x", "1.5.x", "2.0.x"]
    },
    "instrumentor_compatibility": {
        "openinference": {
            "status": str,          # "fully_supported" | "partial" | "not_supported"
            "notes": str            # Additional context
        },
        "traceloop": {
            "status": str,
            "notes": str
        }
    },
    "known_limitations": [
        {
            "feature": str,         # "Streaming responses"
            "status": str,          # "supported" | "partial" | "not_supported"
            "notes": str,           # "Requires callback configuration"
            "workaround": str       # Optional workaround description
        }
    ]
}
```

**Example Configuration (OpenAI):**

```python
"openai": {
    "provider_name": "OpenAI",
    "provider_key": "openai",
    "provider_sdk": "openai>=1.0.0",
    "openinference_package": "openinference-instrumentation-openai",
    
    # NEW compatibility fields
    "python_version_support": {
        "supported": ["3.11+", "3.12+"],
        "partial": ["3.10 (requires async workarounds)"],
        "unsupported": ["3.9 and below"]
    },
    "sdk_version_range": {
        "minimum": "1.0.0",
        "recommended": "1.5.0+",
        "tested_versions": ["1.0.x", "1.5.x", "1.35.x"]
    },
    "instrumentor_compatibility": {
        "openinference": {
            "status": "fully_supported",
            "notes": "Complete support for all OpenAI features"
        },
        "traceloop": {
            "status": "fully_supported",
            "notes": "Complete support with automatic span generation"
        }
    },
    "known_limitations": [
        {
            "feature": "Streaming responses",
            "status": "supported",
            "notes": "Full support with automatic chunk tracking",
            "workaround": None
        },
        {
            "feature": "Batch API",
            "status": "supported",
            "notes": "Full support for batch operations",
            "workaround": None
        },
        {
            "feature": "Function calling",
            "status": "supported",
            "notes": "Automatic tracing of function calls and results",
            "workaround": None
        }
    ]
}
```

**Validation Rules:**

1. All required fields must be present
2. `status` values must be from allowed enum: `"fully_supported"`, `"partial"`, `"not_supported"`
3. `python_version_support` must have at least one supported version
4. `tested_versions` must be non-empty list
5. `known_limitations` must have at least 3 feature entries

---

### 3.3 Validation Script Interfaces

**Purpose:** Provide command-line interfaces for documentation quality validation.

#### 3.3.1 Divio Compliance Validator (NEW - FR-005)

**Script:** `scripts/validate-divio-compliance.py`

**Command-Line Interface:**

```bash
# Validate entire documentation
python scripts/validate-divio-compliance.py

# Validate specific file
python scripts/validate-divio-compliance.py --file docs/how-to/index.rst

# Output JSON for CI integration
python scripts/validate-divio-compliance.py --format json
```

**Validation Checks:**

| Check | Rule | Violation Detection |
|-------|------|---------------------|
| Getting Started purity | How-to "Getting Started" section must contain 0 migration guides | Searches for "migration-guide" and "backwards-compatibility-guide" in Getting Started toctree |
| Category separation | Migration content must be in separate "Migration & Compatibility" section | Verifies migration guides are NOT in main How-to areas |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | All Divio compliance checks passed |
| 1 | Divio violations found |
| 2 | File not found or invalid path |

**Output Format:**

```
Divio Compliance Report
=======================

✅ PASS: Getting Started section (0 migration guides found)
✅ PASS: Migration guides in correct section

Summary: 2/2 checks passed
```

**JSON Output (--format json):**

```json
{
  "status": "pass",
  "checks": [
    {
      "name": "getting_started_purity",
      "status": "pass",
      "details": "0 migration guides found in Getting Started section"
    },
    {
      "name": "migration_separation",
      "status": "pass",
      "details": "All migration guides in Migration & Compatibility section"
    }
  ],
  "violations": []
}
```

#### 3.3.2 Completeness Checker (NEW - FR-005)

**Script:** `scripts/validate-completeness.py`

**Command-Line Interface:**

```bash
# Check all requirements
python scripts/validate-completeness.py

# Check specific requirement
python scripts/validate-completeness.py --requirement FR-001

# Output JSON
python scripts/validate-completeness.py --format json
```

**Validation Checks:**

| Check | Requirement | File/Pattern Checked |
|-------|-------------|---------------------|
| Getting Started guides exist | FR-001 | docs/how-to/getting-started/*.rst (4 files) |
| Span enrichment guide exists | FR-003 | docs/how-to/advanced-tracing/span-enrichment.rst |
| Compatibility sections exist | FR-002 | All 7 integration guides have "Compatibility" header |
| Template variables defined | FR-004 | docs/_templates/template_variables.md contains new variables |
| Class decorator guide exists | FR-009 | docs/how-to/advanced-tracing/class-decorators.rst OR expanded custom-spans.rst |
| SSL troubleshooting exists | FR-010 | docs/how-to/index.rst contains "Network & SSL Issues" |
| Testing guide exists | FR-011 | docs/how-to/testing-applications.rst |
| Advanced patterns guide exists | FR-012 | docs/how-to/advanced-tracing/advanced-patterns.rst |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | All completeness checks passed |
| 1 | Missing required files or sections |

**Output:**

```
Completeness Report
===================

FR-001 Getting Started Guides:
  ✅ setup-first-tracer.rst
  ✅ add-llm-tracing-5min.rst
  ✅ enable-span-enrichment.rst
  ✅ configure-multi-instance.rst

FR-002 Compatibility Sections:
  ✅ openai.rst (has "Compatibility" header)
  ✅ anthropic.rst (has "Compatibility" header)
  ... (5 more)

FR-003 Span Enrichment Guide:
  ✅ span-enrichment.rst exists

Summary: 12/12 checks passed
```

#### 3.3.3 Link Checker (EXISTING)

**Script:** `scripts/validate-docs-navigation.sh`

**Usage:**

```bash
# Check all links
./scripts/validate-docs-navigation.sh

# Check specific file
./scripts/validate-docs-navigation.sh docs/how-to/index.rst
```

**Validation:** Verifies all internal cross-references resolve correctly

---

### 3.4 Sphinx Build Interface

**Purpose:** Build documentation from RST source to static HTML.

**Command:**

```bash
cd docs && make html
```

**Output Directory:** `docs/_build/html/`

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Build successful (warnings OK) |
| non-zero | Build failed (errors present) |

**Warning Detection:**

```bash
# Save warnings to file
make html 2>&1 | tee build.log

# Count warnings
grep "WARNING" build.log | wc -l

# Baseline: <current_count>
# Requirement: New changes must not increase warning count
```

---

### 3.5 RST Cross-Reference Syntax (Documentation Interface)

**Purpose:** Define standard cross-reference patterns for linking between documentation files.

**Internal Links:**

```rst
:doc:`/how-to/advanced-tracing/span-enrichment`
:ref:`section-label-name`
```

**API References:**

```rst
:class:`honeyhive.HoneyHiveTracer`
:meth:`honeyhive.enrich_span`
:func:`honeyhive.trace`
```

**External Links:**

```rst
`Python Documentation <https://docs.python.org/>`_
```

**Code Blocks:**

```rst
.. code-block:: python
   :emphasize-lines: 3,5

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="my-project"
   )
```

**Admonitions:**

```rst
.. note::
   This is a note block for additional context.

.. warning::
   This is a warning for potential issues.

.. tip::
   This is a helpful tip for users.
```

**Tabbed Content (for dual instrumentor support):**

```rst
.. tabs::

   .. tab:: OpenInference

      .. code-block:: python

         # OpenInference code example

   .. tab:: Traceloop

      .. code-block:: python

         # Traceloop code example
```

**Collapsible Sections:**

```rst
.. collapse:: Advanced Configuration (Click to expand)

   Detailed advanced configuration content here.
```

---

### 3.6 Template Variable Substitution Interface

**Purpose:** Define how template placeholders are replaced with provider-specific values.

**Template Syntax:**

```rst
{{VARIABLE_NAME}}
```

**Variable Categories:**

**Provider Identity:**
- `{{PROVIDER_NAME}}` → "OpenAI"
- `{{PROVIDER_KEY}}` → "openai"
- `{{PROVIDER_SDK}}` → "openai>=1.0.0"

**Compatibility (NEW - FR-004):**
- `{{PYTHON_VERSION_SUPPORT}}` → Formatted table of supported Python versions
- `{{SDK_VERSION_RANGE}}` → Formatted version requirements
- `{{INSTRUMENTOR_COMPATIBILITY}}` → Formatted compatibility matrix
- `{{KNOWN_LIMITATIONS}}` → Formatted list of feature limitations

**Substitution Rules:**

1. All `{{VARIABLE}}` placeholders MUST be replaced
2. Missing variables cause generation failure
3. Nested structures (dicts/lists) are formatted into RST tables/lists
4. Empty lists render as "None" or "No limitations"

**Formatting Functions:**

```python
def format_python_versions(versions_dict: dict) -> str:
    """Convert python_version_support dict to RST table."""
    # Returns formatted table

def format_sdk_versions(versions_dict: dict) -> str:
    """Convert sdk_version_range dict to RST content."""
    # Returns formatted content

def format_compatibility_matrix(compat_dict: dict) -> str:
    """Convert instrumentor_compatibility to RST table."""
    # Returns formatted table

def format_limitations(limitations_list: list) -> str:
    """Convert known_limitations list to RST list."""
    # Returns formatted list
```

---

## 3.7 Interface Contracts Summary

| Interface | Type | Purpose | Consumers |
|-----------|------|---------|-----------|
| Template Generation CLI | Command-line | Generate provider docs from template | AI author, CI/CD |
| Provider Config Schema | Data contract | Define provider metadata | Template generation script |
| Divio Validator CLI | Command-line | Ensure content categorization compliance | CI/CD quality gate |
| Completeness Checker CLI | Command-line | Verify all requirements implemented | CI/CD quality gate |
| Link Checker CLI | Command-line | Validate cross-references | CI/CD quality gate |
| Sphinx Build | Build system | Transform RST to HTML | Documentation deployment |
| RST Cross-Reference Syntax | Documentation DSL | Link between docs | Documentation authors |
| Template Variables | Template syntax | Provider-specific substitution | Template system |

**API Stability:**

- Template generation CLI: Stable interface, new flags may be added
- Provider config schema: Breaking change if required fields added (validation will catch)
- Validation CLIs: Stable exit codes, output format may evolve
- RST syntax: Stable (Sphinx-defined standard)
- Template variables: New variables can be added, existing cannot be removed

---

## 4. Data Models

This section defines the data structures and schemas for documentation configuration, validation, and generation.

---

### 4.1 Provider Configuration Data Model (FR-002, FR-004)

**Purpose:** Structured configuration for each LLM provider's integration guide generation.

**Data Structure:**

```python
from typing import TypedDict, List, Literal

class PythonVersionSupport(TypedDict):
    """Python version compatibility information."""
    supported: List[str]      # Fully supported versions: ["3.11+", "3.12+"]
    partial: List[str]         # Partially supported: ["3.10 (requires workarounds)"]
    unsupported: List[str]     # Not supported: ["3.9 and below"]

class SDKVersionRange(TypedDict):
    """Provider SDK version requirements."""
    minimum: str               # Minimum version: "1.0.0"
    recommended: str           # Recommended version: "1.5.0+"
    tested_versions: List[str] # Tested version ranges: ["1.0.x", "1.5.x"]

class InstrumentorInfo(TypedDict):
    """Instrumentor compatibility details."""
    status: Literal["fully_supported", "partial", "not_supported"]
    notes: str                 # Additional context about support

class InstrumentorCompatibility(TypedDict):
    """Compatibility for both instrumentor types."""
    openinference: InstrumentorInfo
    traceloop: InstrumentorInfo

class KnownLimitation(TypedDict):
    """Known limitation or feature support status."""
    feature: str               # Feature name: "Streaming responses"
    status: Literal["supported", "partial", "not_supported"]
    notes: str                 # Details about support
    workaround: str | None     # Optional workaround instructions

class ProviderConfig(TypedDict):
    """Complete provider configuration for template generation."""
    # Existing fields
    provider_name: str                          # Display name: "OpenAI"
    provider_key: str                           # URL-safe key: "openai"
    provider_sdk: str                           # PyPI requirement: "openai>=1.0.0"
    openinference_package: str                  # Instrumentor package name
    
    # NEW fields for compatibility matrices (FR-002, FR-004)
    python_version_support: PythonVersionSupport
    sdk_version_range: SDKVersionRange
    instrumentor_compatibility: InstrumentorCompatibility
    known_limitations: List[KnownLimitation]

# Configuration dictionary type
ProviderConfigs = dict[str, ProviderConfig]
```

**Example Instance:**

```python
PROVIDER_CONFIGS: ProviderConfigs = {
    "openai": {
        "provider_name": "OpenAI",
        "provider_key": "openai",
        "provider_sdk": "openai>=1.0.0",
        "openinference_package": "openinference-instrumentation-openai",
        "python_version_support": {
            "supported": ["3.11+", "3.12+"],
            "partial": ["3.10 (requires async workarounds)"],
            "unsupported": ["3.9 and below"]
        },
        "sdk_version_range": {
            "minimum": "1.0.0",
            "recommended": "1.5.0+",
            "tested_versions": ["1.0.x", "1.5.x", "1.35.x"]
        },
        "instrumentor_compatibility": {
            "openinference": {
                "status": "fully_supported",
                "notes": "Complete support for all OpenAI features"
            },
            "traceloop": {
                "status": "fully_supported",
                "notes": "Complete support with automatic span generation"
            }
        },
        "known_limitations": [
            {
                "feature": "Streaming responses",
                "status": "supported",
                "notes": "Full support with automatic chunk tracking",
                "workaround": None
            },
            {
                "feature": "Batch API",
                "status": "supported",
                "notes": "Full support for batch operations",
                "workaround": None
            },
            {
                "feature": "Function calling",
                "status": "supported",
                "notes": "Automatic tracing of function calls and results",
                "workaround": None
            }
        ]
    },
    # ... 6 more providers (anthropic, google-ai, google-adk, bedrock, azure-openai, mcp)
}
```

**Validation Rules:**

```python
def validate_provider_config(config: ProviderConfig, provider_key: str) -> List[str]:
    """
    Validate provider configuration completeness.
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Required field presence
    required_fields = [
        "provider_name", "provider_key", "provider_sdk", "openinference_package",
        "python_version_support", "sdk_version_range", 
        "instrumentor_compatibility", "known_limitations"
    ]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field '{field}' for provider '{provider_key}'")
    
    # Python version support validation
    if "python_version_support" in config:
        pvs = config["python_version_support"]
        if not pvs.get("supported"):
            errors.append(f"Provider '{provider_key}' must have at least one supported Python version")
    
    # SDK version validation
    if "sdk_version_range" in config:
        svr = config["sdk_version_range"]
        if not svr.get("tested_versions"):
            errors.append(f"Provider '{provider_key}' must have at least one tested version")
    
    # Instrumentor status validation
    valid_statuses = {"fully_supported", "partial", "not_supported"}
    if "instrumentor_compatibility" in config:
        ic = config["instrumentor_compatibility"]
        for inst_type in ["openinference", "traceloop"]:
            if inst_type in ic:
                status = ic[inst_type].get("status")
                if status not in valid_statuses:
                    errors.append(
                        f"Invalid status '{status}' for {inst_type} in provider '{provider_key}'. "
                        f"Must be one of: {valid_statuses}"
                    )
    
    # Known limitations validation
    if "known_limitations" in config:
        limitations = config["known_limitations"]
        if len(limitations) < 3:
            errors.append(
                f"Provider '{provider_key}' must document at least 3 features in known_limitations"
            )
        for idx, limitation in enumerate(limitations):
            if limitation.get("status") not in valid_statuses:
                errors.append(
                    f"Invalid status in limitation {idx} for provider '{provider_key}'"
                )
    
    return errors
```

**Constraints:**

- All 7 providers must have identical schema structure
- Enum values (`status`) must be from predefined sets
- At least 1 supported Python version required
- At least 3 features documented in `known_limitations`
- Non-empty `tested_versions` list required

---

### 4.2 Validation Result Data Models (FR-005)

**Purpose:** Structured representation of validation check results for CI/CD integration.

**Data Structures:**

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class ValidationStatus(Enum):
    """Status of a validation check."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class ValidationCheck:
    """Individual validation check result."""
    name: str                    # Check identifier: "getting_started_purity"
    status: ValidationStatus     # Pass/Fail/Warning/Skip
    details: str                 # Human-readable details
    file_path: Optional[str]     # File that was checked (if applicable)
    line_number: Optional[int]   # Line number (if applicable)
    
@dataclass
class ValidationViolation:
    """Detailed violation information."""
    check_name: str              # Which check failed
    severity: str                # "error" | "warning"
    message: str                 # Violation description
    file_path: str               # File containing violation
    line_number: Optional[int]   # Line number (if known)
    suggested_fix: Optional[str] # How to fix the violation

@dataclass
class ValidationReport:
    """Complete validation report."""
    status: ValidationStatus                  # Overall status
    checks: List[ValidationCheck]             # All checks performed
    violations: List[ValidationViolation]     # Any violations found
    total_checks: int                         # Total number of checks
    passed_checks: int                        # Number of passed checks
    failed_checks: int                        # Number of failed checks
    warnings: int                             # Number of warnings
    timestamp: str                            # ISO 8601 timestamp
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "details": c.details,
                    "file_path": c.file_path,
                    "line_number": c.line_number
                }
                for c in self.checks
            ],
            "violations": [
                {
                    "check_name": v.check_name,
                    "severity": v.severity,
                    "message": v.message,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "suggested_fix": v.suggested_fix
                }
                for v in self.violations
            ],
            "summary": {
                "total_checks": self.total_checks,
                "passed_checks": self.passed_checks,
                "failed_checks": self.failed_checks,
                "warnings": self.warnings
            },
            "timestamp": self.timestamp
        }
```

**Example Validation Report:**

```python
# Successful validation
report = ValidationReport(
    status=ValidationStatus.PASS,
    checks=[
        ValidationCheck(
            name="getting_started_purity",
            status=ValidationStatus.PASS,
            details="0 migration guides found in Getting Started section",
            file_path="docs/how-to/index.rst",
            line_number=None
        ),
        ValidationCheck(
            name="span_enrichment_exists",
            status=ValidationStatus.PASS,
            details="span-enrichment.rst found",
            file_path="docs/how-to/advanced-tracing/span-enrichment.rst",
            line_number=None
        )
    ],
    violations=[],
    total_checks=2,
    passed_checks=2,
    failed_checks=0,
    warnings=0,
    timestamp="2025-10-08T14:56:00Z"
)

# Failed validation
report_failed = ValidationReport(
    status=ValidationStatus.FAIL,
    checks=[
        ValidationCheck(
            name="getting_started_purity",
            status=ValidationStatus.FAIL,
            details="Found migration guide in Getting Started section",
            file_path="docs/how-to/index.rst",
            line_number=45
        )
    ],
    violations=[
        ValidationViolation(
            check_name="getting_started_purity",
            severity="error",
            message="Migration guide 'migration-guide.rst' found in Getting Started toctree",
            file_path="docs/how-to/index.rst",
            line_number=45,
            suggested_fix="Move migration-guide.rst to 'Migration & Compatibility' section"
        )
    ],
    total_checks=1,
    passed_checks=0,
    failed_checks=1,
    warnings=0,
    timestamp="2025-10-08T14:56:00Z"
)
```

---

### 4.3 Documentation File Structure Model

**Purpose:** Define the expected directory structure and file organization for documentation.

**File System Schema:**

```python
from pathlib import Path
from typing import Set

class DocumentationStructure:
    """Expected documentation file structure."""
    
    # Root directories
    ROOT = Path("docs")
    TEMPLATES_DIR = ROOT / "_templates"
    SCRIPTS_DIR = Path("scripts")
    
    # Main documentation sections
    HOW_TO_DIR = ROOT / "how-to"
    TUTORIALS_DIR = ROOT / "tutorials"
    REFERENCE_DIR = ROOT / "reference"
    EXPLANATION_DIR = ROOT / "explanation"
    
    # How-to subdirectories
    GETTING_STARTED_DIR = HOW_TO_DIR / "getting-started"  # NEW - FR-001
    MIGRATION_DIR = HOW_TO_DIR / "migration-compatibility"  # NEW - FR-001
    ADVANCED_TRACING_DIR = HOW_TO_DIR / "advanced-tracing"
    DEPLOYMENT_DIR = HOW_TO_DIR / "deployment"
    INTEGRATIONS_DIR = HOW_TO_DIR / "integrations"
    
    # Required files for FR-001
    GETTING_STARTED_FILES: Set[Path] = {
        GETTING_STARTED_DIR / "setup-first-tracer.rst",
        GETTING_STARTED_DIR / "add-llm-tracing-5min.rst",
        GETTING_STARTED_DIR / "enable-span-enrichment.rst",
        GETTING_STARTED_DIR / "configure-multi-instance.rst",
    }
    
    # Required files for FR-003, FR-009, FR-012
    ADVANCED_TRACING_FILES: Set[Path] = {
        ADVANCED_TRACING_DIR / "index.rst",
        ADVANCED_TRACING_DIR / "custom-spans.rst",
        ADVANCED_TRACING_DIR / "tracer-auto-discovery.rst",
        ADVANCED_TRACING_DIR / "span-enrichment.rst",  # NEW - FR-003
        ADVANCED_TRACING_DIR / "class-decorators.rst",  # NEW - FR-009
        ADVANCED_TRACING_DIR / "advanced-patterns.rst",  # NEW - FR-012
    }
    
    # Integration guide files (generated from template - FR-002)
    INTEGRATION_PROVIDERS: Set[str] = {
        "openai", "anthropic", "google-ai", "google-adk",
        "bedrock", "azure-openai", "mcp"
    }
    
    # Template files (FR-002, FR-004, FR-006)
    TEMPLATE_FILES: Set[Path] = {
        TEMPLATES_DIR / "multi_instrumentor_integration_formal_template.rst",
        TEMPLATES_DIR / "generate_provider_docs.py",
        TEMPLATES_DIR / "template_variables.md",
    }
    
    # Validation scripts (FR-005)
    VALIDATION_SCRIPTS: Set[Path] = {
        SCRIPTS_DIR / "validate-docs-navigation.sh",
        SCRIPTS_DIR / "validate-divio-compliance.py",  # NEW
        SCRIPTS_DIR / "validate-completeness.py",  # NEW
    }
    
    # Other required files
    TESTING_GUIDE = HOW_TO_DIR / "testing-applications.rst"  # NEW - FR-011
    LLM_PATTERNS_GUIDE = HOW_TO_DIR / "llm-application-patterns.rst"  # RENAMED - FR-007
    PRODUCTION_GUIDE = DEPLOYMENT_DIR / "production.rst"  # MODIFIED - FR-008
    ADVANCED_PRODUCTION_GUIDE = DEPLOYMENT_DIR / "advanced-production.rst"  # NEW - FR-008
    
    @classmethod
    def validate_structure(cls) -> List[str]:
        """
        Validate that expected directory structure exists.
        
        Returns:
            List of missing files/directories
        """
        missing = []
        
        # Check directories
        for dir_path in [
            cls.GETTING_STARTED_DIR,
            cls.MIGRATION_DIR,
            cls.ADVANCED_TRACING_DIR,
            cls.DEPLOYMENT_DIR,
            cls.INTEGRATIONS_DIR,
        ]:
            if not dir_path.exists():
                missing.append(f"Directory: {dir_path}")
        
        # Check required files
        for file_path in cls.GETTING_STARTED_FILES:
            if not file_path.exists():
                missing.append(f"File: {file_path}")
        
        # Check integration guides
        for provider in cls.INTEGRATION_PROVIDERS:
            guide_path = cls.INTEGRATIONS_DIR / f"{provider}.rst"
            if not guide_path.exists():
                missing.append(f"Integration guide: {guide_path}")
        
        return missing
```

**Directory Structure Diagram:**

```
docs/
├── how-to/
│   ├── index.rst (MODIFY)
│   ├── getting-started/ (NEW DIR - FR-001)
│   │   ├── setup-first-tracer.rst (NEW)
│   │   ├── add-llm-tracing-5min.rst (NEW)
│   │   ├── enable-span-enrichment.rst (NEW)
│   │   └── configure-multi-instance.rst (NEW)
│   ├── migration-compatibility/ (NEW DIR - FR-001)
│   │   ├── migration-guide.rst (MOVED)
│   │   └── backwards-compatibility-guide.rst (MOVED)
│   ├── llm-application-patterns.rst (RENAMED - FR-007)
│   ├── testing-applications.rst (NEW - FR-011)
│   ├── advanced-tracing/
│   │   ├── index.rst (MODIFY)
│   │   ├── custom-spans.rst (EXISTING)
│   │   ├── tracer-auto-discovery.rst (EXISTING)
│   │   ├── span-enrichment.rst (NEW - FR-003)
│   │   ├── class-decorators.rst (NEW - FR-009)
│   │   └── advanced-patterns.rst (NEW - FR-012)
│   ├── deployment/
│   │   ├── index.rst (MODIFY)
│   │   ├── production.rst (CONDENSE - FR-008)
│   │   └── advanced-production.rst (NEW - FR-008)
│   └── integrations/
│       ├── openai.rst (REGENERATE - FR-002)
│       ├── anthropic.rst (REGENERATE - FR-002)
│       ├── google-ai.rst (REGENERATE - FR-002)
│       ├── google-adk.rst (REGENERATE - FR-002)
│       ├── bedrock.rst (REGENERATE - FR-002)
│       ├── azure-openai.rst (REGENERATE - FR-002)
│       └── mcp.rst (REGENERATE - FR-002)
├── _templates/
│   ├── multi_instrumentor_integration_formal_template.rst (MODIFY - FR-002)
│   ├── generate_provider_docs.py (MODIFY - FR-004/006)
│   └── template_variables.md (MODIFY - FR-004)
├── tutorials/ (NO CHANGES)
├── reference/ (NO CHANGES)
└── explanation/ (NO CHANGES)

scripts/
├── validate-docs-navigation.sh (EXISTING)
├── validate-divio-compliance.py (NEW - FR-005)
└── validate-completeness.py (NEW - FR-005)
```

---

### 4.4 Template Rendering Context Model

**Purpose:** Define the data passed to template rendering engine for variable substitution.

**Data Structure:**

```python
from typing import Any

class TemplateContext:
    """Context data for template rendering."""
    
    def __init__(self, provider_config: ProviderConfig):
        """Initialize template context from provider configuration."""
        self.provider_config = provider_config
        self._rendered_cache: dict[str, str] = {}
    
    def get_variable(self, variable_name: str) -> str:
        """
        Get rendered value for a template variable.
        
        Args:
            variable_name: Variable name without {{}} delimiters
            
        Returns:
            Rendered RST content for the variable
        """
        if variable_name in self._rendered_cache:
            return self._rendered_cache[variable_name]
        
        # Simple string variables
        if variable_name == "PROVIDER_NAME":
            return self.provider_config["provider_name"]
        elif variable_name == "PROVIDER_KEY":
            return self.provider_config["provider_key"]
        elif variable_name == "PROVIDER_SDK":
            return self.provider_config["provider_sdk"]
        elif variable_name == "OPENINFERENCE_PACKAGE":
            return self.provider_config["openinference_package"]
        
        # Complex structured variables (NEW - FR-004)
        elif variable_name == "PYTHON_VERSION_SUPPORT":
            rendered = self._render_python_versions()
        elif variable_name == "SDK_VERSION_RANGE":
            rendered = self._render_sdk_versions()
        elif variable_name == "INSTRUMENTOR_COMPATIBILITY":
            rendered = self._render_compatibility_matrix()
        elif variable_name == "KNOWN_LIMITATIONS":
            rendered = self._render_limitations()
        else:
            raise ValueError(f"Unknown template variable: {variable_name}")
        
        self._rendered_cache[variable_name] = rendered
        return rendered
    
    def _render_python_versions(self) -> str:
        """Render Python version support as RST table."""
        pvs = self.provider_config["python_version_support"]
        
        table = []
        table.append(".. list-table::")
        table.append("   :header-rows: 1")
        table.append("   :widths: 30 70")
        table.append("")
        table.append("   * - Support Level")
        table.append("     - Python Versions")
        
        if pvs["supported"]:
            versions = ", ".join(pvs["supported"])
            table.append(f"   * - ✅ Fully Supported")
            table.append(f"     - {versions}")
        
        if pvs["partial"]:
            versions = ", ".join(pvs["partial"])
            table.append(f"   * - ⚠️ Partial Support")
            table.append(f"     - {versions}")
        
        if pvs["unsupported"]:
            versions = ", ".join(pvs["unsupported"])
            table.append(f"   * - ❌ Not Supported")
            table.append(f"     - {versions}")
        
        return "\n".join(table)
    
    def _render_sdk_versions(self) -> str:
        """Render SDK version information as RST content."""
        svr = self.provider_config["sdk_version_range"]
        
        lines = []
        lines.append(f"**Minimum Version:** ``{svr['minimum']}``")
        lines.append("")
        lines.append(f"**Recommended Version:** ``{svr['recommended']}``")
        lines.append("")
        lines.append("**Tested Versions:**")
        for version in svr["tested_versions"]:
            lines.append(f"  - ``{version}``")
        
        return "\n".join(lines)
    
    def _render_compatibility_matrix(self) -> str:
        """Render instrumentor compatibility as RST table."""
        ic = self.provider_config["instrumentor_compatibility"]
        
        table = []
        table.append(".. list-table::")
        table.append("   :header-rows: 1")
        table.append("   :widths: 30 20 50")
        table.append("")
        table.append("   * - Instrumentor")
        table.append("     - Status")
        table.append("     - Notes")
        
        for inst_type, info in ic.items():
            status_icon = {
                "fully_supported": "✅",
                "partial": "⚠️",
                "not_supported": "❌"
            }[info["status"]]
            
            table.append(f"   * - {inst_type.capitalize()}")
            table.append(f"     - {status_icon} {info['status'].replace('_', ' ').title()}")
            table.append(f"     - {info['notes']}")
        
        return "\n".join(table)
    
    def _render_limitations(self) -> str:
        """Render known limitations as RST list."""
        limitations = self.provider_config["known_limitations"]
        
        lines = []
        for limitation in limitations:
            status_icon = {
                "supported": "✅",
                "partial": "⚠️",
                "not_supported": "❌"
            }[limitation["status"]]
            
            lines.append(f"**{limitation['feature']}:** {status_icon} {limitation['status'].title()}")
            lines.append(f"  {limitation['notes']}")
            if limitation.get("workaround"):
                lines.append(f"  *Workaround:* {limitation['workaround']}")
            lines.append("")
        
        return "\n".join(lines)
```

---

### 4.5 Data Model Summary

| Model | Purpose | Validation | Persistence |
|-------|---------|------------|-------------|
| `ProviderConfig` | Template generation input | Schema validation, field presence | Python dict in generate_provider_docs.py |
| `ValidationReport` | Quality check results | Status enum validation | JSON output for CI/CD |
| `DocumentationStructure` | Expected file organization | File existence checks | File system |
| `TemplateContext` | Template rendering state | Variable name validation | In-memory during generation |

**Data Flow:**

```
ProviderConfig (Python dict)
    │
    ├─→ Validation (schema check)
    │
    └─→ TemplateContext (rendering engine)
            │
            └─→ Template + Variables → Generated RST files
                    │
                    └─→ Sphinx Build → HTML output
                            │
                            └─→ ValidationReport → CI/CD decision
```

**Constraints:**

1. **Immutability:** Provider configs should not be modified after validation
2. **Completeness:** All required fields must be present before generation
3. **Type Safety:** Use TypedDict for static type checking
4. **Validation First:** Always validate before rendering
5. **Cache Rendered Values:** Template context caches rendered variables for efficiency

---

## 5. Security Design

This section defines security controls for the documentation system, focusing on content integrity, access control, and build-time security.

---

### 5.1 Access Control & Authentication

**Purpose:** Control who can modify documentation source and deploy changes.

**Git-Based Access Control:**

| Role | Permissions | Authentication |
|------|-------------|----------------|
| Documentation Author | Create branches, submit PRs | GitHub account + 2FA required |
| Code Reviewer | Approve PRs, request changes | GitHub account + 2FA required, team membership |
| Maintainer | Merge to main, deploy docs | GitHub account + 2FA required, admin team membership |
| Public Reader | View published documentation | None (public access) |

**Branch Protection Rules:**

```yaml
# .github/branch-protection.yml
main:
  required_reviews: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  required_status_checks:
    - sphinx-build
    - link-checker
    - divio-compliance
    - completeness-check
  enforce_admins: true
  restrict_push: true
  allowed_push_users: []  # Nobody can push directly
```

**PR Approval Requirements:**
- At least 1 code review approval required
- All CI checks must pass (build, validation, linting)
- No direct commits to `main` branch
- PR author cannot approve their own PR

---

### 5.2 Content Integrity & Validation

**Purpose:** Prevent malicious or broken content from being published.

**Build-Time Validation (FR-005):**

```python
class SecurityValidator:
    """Validate documentation content for security issues."""
    
    @staticmethod
    def validate_rst_file(file_path: Path) -> List[str]:
        """
        Check RST file for security issues.
        
        Returns:
            List of security warnings/errors
        """
        issues = []
        content = file_path.read_text()
        
        # Check for raw HTML injection attempts
        if ".. raw:: html" in content:
            issues.append(
                f"{file_path}: Raw HTML directive found. "
                "Review carefully for XSS risks."
            )
        
        # Check for external script inclusions
        if "<script" in content.lower():
            issues.append(
                f"{file_path}: Script tag found in content. "
                "External scripts are not allowed."
            )
        
        # Check for suspicious external links
        suspicious_domains = ["bit.ly", "tinyurl.com", "goo.gl"]
        for domain in suspicious_domains:
            if domain in content:
                issues.append(
                    f"{file_path}: Suspicious URL shortener found ({domain}). "
                    "Use full URLs for transparency."
                )
        
        # Check for embedded credentials
        patterns = [
            r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9]{20,}",
            r"password\s*[:=]\s*['\"]?[^\s'\"]{8,}",
            r"secret\s*[:=]\s*['\"]?[a-zA-Z0-9]{20,}"
        ]
        import re
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(
                    f"{file_path}: Potential hardcoded credential found. "
                    "Remove sensitive data from documentation."
                )
        
        return issues
```

**Content Sanitization:**
- Sphinx automatically escapes HTML in code blocks
- RST directives are strictly controlled (no arbitrary Python execution)
- Template variable substitution uses string formatting (not eval)
- Generated HTML is static (no server-side execution)

**Input Validation:**
- Provider configuration validated against schema before rendering
- Template variables validated for allowed character sets
- File paths validated to prevent directory traversal
- No user-supplied input executed as code

---

### 5.3 Dependency Security

**Purpose:** Manage security vulnerabilities in documentation toolchain dependencies.

**Dependency Management:**

```toml
# docs/requirements.txt (pinned versions)
sphinx==7.2.6
sphinx-rtd-theme==1.3.0
sphinx-tabs==3.4.1
myst-parser==2.0.0

# Security scanning
safety==2.3.5  # For vulnerability scanning
```

**Security Scanning Process:**

```bash
# Run in CI/CD pipeline
pip install safety
safety check --file docs/requirements.txt --json

# Exit code non-zero if vulnerabilities found
```

**Vulnerability Response:**
1. **Critical vulnerabilities:** Block deployment, patch immediately
2. **High vulnerabilities:** Create issue, patch within 7 days
3. **Medium/Low vulnerabilities:** Schedule for next release
4. **False positives:** Document in `.safety-policy.yml`

**Update Strategy:**
- Monthly dependency updates via Dependabot
- Security patches applied immediately
- Pin major versions to prevent breaking changes
- Test all updates in staging before production

---

### 5.4 Build & Deployment Security

**Purpose:** Secure the documentation build and deployment pipeline.

**CI/CD Security:**

```yaml
# .github/workflows/docs-build.yml
name: Documentation Build

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'scripts/validate-*.py'
  
permissions:
  contents: read      # Read repo contents
  pull-requests: write  # Comment on PRs
  statuses: write     # Update commit status

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false  # Don't persist GitHub token
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install --require-hashes -r docs/requirements.txt
      
      - name: Security scan
        run: |
          pip install safety
          safety check --file docs/requirements.txt
      
      - name: Build documentation
        run: |
          cd docs && make html
      
      - name: Run validation
        run: |
          python scripts/validate-divio-compliance.py
          python scripts/validate-completeness.py
          ./scripts/validate-docs-navigation.sh
```

**Build Environment Security:**
- Use official GitHub Actions runners (trusted environment)
- Pin action versions with SHA hashes (prevent supply chain attacks)
- Minimal permissions granted to workflows
- No secrets required for documentation builds
- Build artifacts scanned before deployment

**Deployment Security:**
- Deploy only from `main` branch after PR merge
- Require signed commits for main branch (optional)
- Deploy to static hosting (no server-side execution)
- Use HTTPS for documentation site
- Enable HSTS headers on documentation server

---

### 5.5 Content Security Policy

**Purpose:** Define security headers for published documentation site.

**CSP Headers:**

```nginx
# Documentation server configuration
add_header Content-Security-Policy "
    default-src 'none';
    script-src 'self' 'unsafe-inline';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' data:;
    connect-src 'self';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'none';
" always;

add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

**Security Headers Explained:**
- `default-src 'none'`: Block all by default
- `script-src 'self'`: Only allow scripts from same origin (Sphinx search.js)
- `style-src 'self' 'unsafe-inline'`: Allow inline styles (Sphinx generates some)
- `img-src 'self' data: https:`: Allow images from same origin, data URIs, and HTTPS
- `frame-ancestors 'none'`: Prevent clickjacking
- `X-Frame-Options "DENY"`: Prevent embedding in iframes
- `X-Content-Type-Options "nosniff"`: Prevent MIME sniffing attacks

---

### 5.6 Secret Management

**Purpose:** Ensure no secrets are accidentally committed to documentation source.

**Pre-Commit Hook:**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Scan for potential secrets
if git diff --cached | grep -iE '(api[_-]?key|password|secret|token)\s*[:=]\s*['\''"]?[a-zA-Z0-9]{20,}'; then
    echo "ERROR: Potential secret found in staged changes"
    echo "Remove sensitive data before committing"
    exit 1
fi

# Scan for AWS keys, private keys
if git diff --cached | grep -E '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH) PRIVATE KEY-----)'; then
    echo "ERROR: AWS key or private key found in staged changes"
    exit 1
fi

exit 0
```

**Secret Scanning Tools:**
- GitHub secret scanning (automatic)
- `git-secrets` pre-commit hook
- CI/CD secret detection via `trufflehog` or `gitleaks`

**Remediation:**
If secrets are accidentally committed:
1. Rotate the compromised secret immediately
2. Remove from Git history using `git filter-branch` or BFG Repo-Cleaner
3. Force push to rewrite history (requires coordination)
4. Notify security team

---

### 5.7 Supply Chain Security

**Purpose:** Protect against compromised dependencies and malicious code injection.

**Dependency Verification:**

```bash
# Generate hash file for requirements
pip-compile --generate-hashes docs/requirements.in -o docs/requirements.txt

# Install with hash verification
pip install --require-hashes -r docs/requirements.txt
```

**Template Generation Script Security:**

```python
# docs/_templates/generate_provider_docs.py

def generate_docs_safely(template_path: Path, provider_config: ProviderConfig) -> str:
    """
    Generate documentation with security controls.
    
    Security measures:
    - No eval() or exec() of user-supplied data
    - String formatting only (no code execution)
    - Path traversal prevention
    - Input validation
    """
    # Validate template path (prevent directory traversal)
    template_path = template_path.resolve()
    if not str(template_path).startswith(str(Path.cwd())):
        raise SecurityError("Template path outside project directory")
    
    # Read template safely
    template_content = template_path.read_text(encoding='utf-8')
    
    # Validate provider config against schema
    validation_errors = validate_provider_config(provider_config, provider_config["provider_key"])
    if validation_errors:
        raise ValidationError(f"Invalid config: {validation_errors}")
    
    # Render using safe string substitution (no eval/exec)
    context = TemplateContext(provider_config)
    for variable_name in extract_variables(template_content):
        value = context.get_variable(variable_name)
        template_content = template_content.replace(f"{{{{{variable_name}}}}}", value)
    
    return template_content
```

**Package Integrity:**
- Verify package signatures where available
- Use hash pinning in requirements.txt
- Monitor for typosquatting attacks
- Review dependency updates in PRs

---

### 5.8 Security Checklist

**Pre-Deployment Security Checklist:**

- [ ] All dependencies scanned for vulnerabilities (safety check passed)
- [ ] No hardcoded secrets in documentation source
- [ ] All RST files validated for security issues
- [ ] Build completed without errors or warnings
- [ ] All validation checks passed (Divio, completeness, links)
- [ ] PR approved by required reviewers
- [ ] Branch protection rules enforced
- [ ] Build artifacts scanned for malware (if applicable)
- [ ] Security headers configured on documentation server
- [ ] HTTPS enabled with valid certificate
- [ ] No raw HTML directives without review
- [ ] No external script inclusions

**Ongoing Security Monitoring:**

- [ ] Monthly dependency updates scheduled
- [ ] GitHub security alerts monitored
- [ ] Access logs reviewed for suspicious activity
- [ ] Documentation site uptime monitored
- [ ] SSL certificate expiry tracked

---

### 5.9 Threat Model

**Threats & Mitigations:**

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| XSS via malicious RST content | Medium | Low | Sphinx sanitization, RST validation, PR review |
| Compromised dependency | High | Medium | Hash pinning, vulnerability scanning, rapid patching |
| Unauthorized documentation changes | Medium | Low | Branch protection, required reviews, 2FA |
| Secret leakage in docs | High | Low | Pre-commit hooks, secret scanning, PR review |
| Supply chain attack (compromised package) | High | Low | Hash verification, trusted sources only |
| Documentation defacement | Low | Very Low | Git history, rapid rollback capability |
| DoS on documentation site | Low | Medium | CDN, rate limiting (hosting provider level) |
| Broken links causing phishing | Low | Medium | Link validation in CI/CD |

**Risk Acceptance:**
- Static HTML generation eliminates most server-side attack vectors
- Git history provides complete audit trail and rollback capability
- Public documentation has lower security requirements than application code

---

### 5.10 Security Design Summary

| Security Control | Implementation | Validation |
|------------------|----------------|------------|
| Access Control | GitHub branch protection + 2FA | PR process enforcement |
| Content Integrity | Build-time validation, RST scanning | Automated in CI/CD |
| Dependency Security | Hash pinning, vulnerability scanning | Monthly safety checks |
| Build Security | Minimal permissions, signed commits | GitHub Actions audit logs |
| Deployment Security | HTTPS, security headers, static hosting | Server configuration review |
| Secret Management | Pre-commit hooks, secret scanning | Automated detection |
| Supply Chain | Hash verification, trusted sources | Package signature verification |

**Security Principles:**
1. **Defense in Depth:** Multiple layers of security controls
2. **Least Privilege:** Minimal permissions at all levels
3. **Fail Secure:** Validation failures block deployment
4. **Audit Trail:** Git history + CI/CD logs
5. **Rapid Response:** Automated vulnerability detection and patching

---

## 6. Performance Design

This section defines performance strategies and optimizations for documentation build, generation, and delivery. Aligns with NFR-P1 and NFR-P2.

---

### 6.1 Build Time Optimization (NFR-P1)

**Target:** Full Sphinx documentation build completes in < 3 minutes

**Current Baseline:** (To be measured)

**Optimization Strategies:**

**6.1.1 Sphinx Build Parallelization:**

```python
# docs/conf.py

# Enable parallel build
# -j auto uses all available CPU cores
# Command: make html -j auto
html_builder_parallel = True

# Limit parallel workers to avoid memory issues
html_builder_workers = 8  # Max 8 workers regardless of CPU count
```

**6.1.2 Incremental Builds:**

```bash
# Only rebuild changed files
sphinx-build -b html docs/ docs/_build/html --incremental

# For development: use sphinx-autobuild for live reload
pip install sphinx-autobuild
sphinx-autobuild docs/ docs/_build/html
```

**6.1.3 Template Generation Caching:**

```python
# docs/_templates/generate_provider_docs.py

class TemplateGenerator:
    """Optimized template generator with caching."""
    
    def __init__(self):
        self._template_cache: dict[str, str] = {}
        self._rendered_cache: dict[tuple[str, str], str] = {}
    
    def generate(self, provider_key: str) -> str:
        """Generate provider docs with caching."""
        cache_key = (provider_key, self._get_template_hash())
        
        # Return cached result if available
        if cache_key in self._rendered_cache:
            return self._rendered_cache[cache_key]
        
        # Generate fresh
        result = self._generate_fresh(provider_key)
        
        # Cache result
        self._rendered_cache[cache_key] = result
        return result
    
    def _get_template_hash(self) -> str:
        """Get hash of template file for cache invalidation."""
        template_path = Path("docs/_templates/multi_instrumentor_integration_formal_template.rst")
        return hashlib.sha256(template_path.read_bytes()).hexdigest()[:8]
```

**6.1.4 Minimize File I/O:**

```python
# Batch file operations
def regenerate_all_providers(configs: ProviderConfigs) -> None:
    """Regenerate all provider guides with minimal I/O."""
    # Read template once
    template = read_template_once()
    
    # Generate all providers in memory
    results = {
        provider: generate_in_memory(provider, config, template)
        for provider, config in configs.items()
    }
    
    # Write all at once
    write_batch(results)
```

**Build Time Targets:**

| Build Type | Target | Measurement |
|------------|--------|-------------|
| Full build (cold cache) | < 3 minutes | CI/CD logs |
| Incremental build (1 file change) | < 30 seconds | Developer experience |
| Template regeneration (all 7 providers) | < 5 seconds | Script execution time |
| Validation suite (all checks) | < 20 seconds | CI/CD logs |

---

### 6.2 Page Load Performance (NFR-P2)

**Target:** Documentation HTML pages load in < 2 seconds (95th percentile)

**Current Baseline:** (To be measured)

**Optimization Strategies:**

**6.2.1 Asset Optimization:**

```python
# docs/conf.py

# Minimize CSS/JS
html_minify_css = True
html_minify_js = True

# Compress static assets
html_use_smartypants = True
```

**6.2.2 Image Optimization:**

```bash
# Optimize images before adding to docs
# PNG optimization
optipng -o7 docs/_static/images/*.png

# JPEG optimization
jpegoptim --max=85 docs/_static/images/*.jpg

# WebP conversion for modern browsers
cwebp -q 85 input.png -o output.webp
```

**6.2.3 CDN & Caching Headers:**

```nginx
# Documentation server configuration

location ~* \.(css|js|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(png|jpg|jpeg|gif|webp|svg)$ {
    expires 30d;
    add_header Cache-Control "public, max-age=2592000";
}

location ~* \.html$ {
    expires 1h;
    add_header Cache-Control "public, max-age=3600";
}
```

**6.2.4 Search Index Optimization:**

```python
# docs/conf.py

# Generate search index at build time (not runtime)
html_use_index = True
html_split_index = False  # Keep index in single file for smaller total size

# Optimize search index
html_search_language = 'en'
html_search_options = {
    'type': 'default',
    'min_word_length': 3,  # Don't index short words
}
```

**6.2.5 HTTP/2 Server Push:**

```nginx
# Push critical assets
location = /index.html {
    http2_push /_static/css/theme.css;
    http2_push /_static/js/theme.js;
    http2_push /_static/searchtools.js;
}
```

**Page Load Targets:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to First Byte (TTFB) | < 200ms | Lighthouse, WebPageTest |
| First Contentful Paint (FCP) | < 1.0s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.0s | Lighthouse, Core Web Vitals |
| Total Page Load | < 2.0s (95th percentile) | Real User Monitoring |
| Page Size (HTML + Assets) | < 500KB compressed | Browser DevTools |

---

### 6.3 Developer Iteration Speed

**Target:** Fast feedback loop for documentation authors

**Optimization Strategies:**

**6.3.1 Live Reload for Development:**

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live reload server
sphinx-autobuild docs/ docs/_build/html \
    --port 8000 \
    --open-browser \
    --delay 1 \
    --ignore "*.swp" \
    --ignore "*.swo"
```

**6.3.2 Selective Validation:**

```bash
# Only validate changed files in development
git diff --name-only | grep "\.rst$" | while read file; do
    python scripts/validate-rst-file.py "$file"
done
```

**6.3.3 Fast Preview Builds:**

```bash
# Skip heavy processing for quick previews
SPHINX_NO_SEARCH=1 SPHINX_NO_LATEX=1 sphinx-build -b html docs/ docs/_build/html
```

**Developer Experience Targets:**

| Action | Target Time | Measurement |
|--------|-------------|-------------|
| Edit → Preview refresh | < 2 seconds | Developer observation |
| Template regeneration → Preview | < 5 seconds | Script + build time |
| Validation (single file) | < 1 second | Script execution time |
| Local full build | < 3 minutes | Time command |

---

### 6.4 CI/CD Pipeline Performance

**Target:** Fast feedback for pull requests

**Optimization Strategies:**

**6.4.1 CI Cache Strategy:**

```yaml
# .github/workflows/docs-build.yml

- name: Cache Sphinx environment
  uses: actions/cache@v4
  with:
    path: docs/_build/.doctrees
    key: sphinx-doctrees-${{ hashFiles('docs/**/*.rst') }}
    restore-keys: |
      sphinx-doctrees-

- name: Cache Python packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('docs/requirements.txt') }}
    restore-keys: |
      pip-
```

**6.4.2 Parallel CI Jobs:**

```yaml
# .github/workflows/docs-build.yml

jobs:
  build:
    runs-on: ubuntu-latest
    # ...
  
  validate-divio:
    runs-on: ubuntu-latest
    needs: []  # Run in parallel with build
    # ...
  
  validate-links:
    runs-on: ubuntu-latest
    needs: []  # Run in parallel with build
    # ...
  
  validate-completeness:
    runs-on: ubuntu-latest
    needs: []  # Run in parallel with build
    # ...
```

**6.4.3 Smart Build Triggers:**

```yaml
# Only build docs if documentation files changed
on:
  pull_request:
    paths:
      - 'docs/**'
      - 'scripts/validate-*.py'
      - '.github/workflows/docs-build.yml'
```

**CI/CD Performance Targets:**

| Pipeline Stage | Target Time | Measurement |
|----------------|-------------|-------------|
| Checkout + Setup | < 30 seconds | CI logs |
| Sphinx Build | < 3 minutes | CI logs |
| All Validations (parallel) | < 30 seconds | CI logs |
| Total Pipeline | < 4 minutes | CI logs |
| PR Feedback Time | < 5 minutes (from push to status) | Developer experience |

---

### 6.5 Template Generation Performance (FR-006)

**Target:** Generate all 7 provider guides in < 5 seconds

**Current Baseline:** (To be measured)

**Optimization Strategies:**

**6.5.1 Batch Generation:**

```python
# docs/_templates/generate_provider_docs.py

def generate_all_providers_optimized(configs: ProviderConfigs) -> dict[str, str]:
    """Generate all providers efficiently."""
    # Read template once (not 7 times)
    template_content = read_template()
    
    # Generate all in parallel using multiprocessing
    from multiprocessing import Pool
    
    with Pool(processes=4) as pool:
        results = pool.starmap(
            generate_single_provider,
            [(provider, config, template_content) for provider, config in configs.items()]
        )
    
    return dict(zip(configs.keys(), results))
```

**6.5.2 Lazy Variable Rendering:**

```python
class TemplateContext:
    """Context with lazy rendering and caching."""
    
    def get_variable(self, variable_name: str) -> str:
        """Get variable with lazy rendering and caching."""
        if variable_name not in self._rendered_cache:
            self._rendered_cache[variable_name] = self._render(variable_name)
        return self._rendered_cache[variable_name]
```

**Template Generation Targets:**

| Operation | Target Time | Measurement |
|-----------|-------------|-------------|
| Single provider generation | < 1 second | Script timing |
| All 7 providers (sequential) | < 5 seconds | Script timing |
| All 7 providers (parallel) | < 2 seconds | Script timing with multiprocessing |
| Template validation | < 100ms | Script timing |

---

### 6.6 Search Performance

**Target:** Instant search results (< 200ms)

**Optimization Strategies:**

**6.6.1 Search Index Optimization:**

```python
# docs/conf.py

# Optimize search index generation
html_search_scorer = 'score.js'  # Use scoring for relevance

# Exclude from search index
html_search_exclude = [
    '_build',
    '_templates',
    '_static',
]
```

**6.6.2 Client-Side Search:**

```javascript
// Custom search implementation using Lunr.js
// Pre-build search index at build time
// Load index on demand (lazy loading)
```

**Search Performance Targets:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search index size | < 500KB | File size |
| Search index load time | < 200ms | Browser DevTools |
| Search query response time | < 200ms | Browser DevTools |
| Results rendering time | < 100ms | Browser DevTools |

---

### 6.7 Performance Monitoring

**Metrics Collection:**

```yaml
# .github/workflows/docs-build.yml

- name: Measure build performance
  run: |
    echo "=== Performance Metrics ===" > performance.txt
    /usr/bin/time -v make html 2>&1 | tee -a performance.txt
    
    echo "Build time: $(grep 'Elapsed' performance.txt)" >> $GITHUB_STEP_SUMMARY
    echo "Peak memory: $(grep 'Maximum' performance.txt)" >> $GITHUB_STEP_SUMMARY

- name: Upload performance metrics
  uses: actions/upload-artifact@v4
  with:
    name: performance-metrics
    path: performance.txt
```

**Performance Regression Detection:**

```python
# scripts/check-performance-regression.py

def check_build_time_regression(current_time: float, baseline_time: float) -> bool:
    """Check if build time has regressed significantly."""
    threshold = 1.2  # 20% regression threshold
    
    if current_time > baseline_time * threshold:
        print(f"WARNING: Build time regression detected")
        print(f"Current: {current_time:.2f}s, Baseline: {baseline_time:.2f}s")
        return True
    
    return False
```

**Monitoring Dashboard:**

- Build time trends (CI/CD metrics)
- Page load metrics (Lighthouse CI, SpeedCurve)
- Real user monitoring (if applicable)
- Search performance metrics

---

### 6.8 Performance Optimization Checklist

**Build-Time Optimizations:**
- [ ] Sphinx parallel build enabled (`-j auto`)
- [ ] Incremental builds for development
- [ ] Template generation caching implemented
- [ ] CI/CD caching configured (Python packages, Sphinx doctrees)
- [ ] Parallel validation jobs in CI/CD

**Runtime Optimizations:**
- [ ] CSS/JS minification enabled
- [ ] Images optimized (PNG, JPEG, WebP)
- [ ] CDN configured with appropriate cache headers
- [ ] HTTP/2 enabled
- [ ] Gzip/Brotli compression enabled
- [ ] Search index pre-generated at build time

**Developer Experience:**
- [ ] Live reload configured for development
- [ ] Fast preview builds available
- [ ] Selective validation for changed files
- [ ] Clear performance feedback in CI/CD

**Monitoring:**
- [ ] Build time metrics tracked
- [ ] Page load metrics monitored (Lighthouse)
- [ ] Performance regression detection in place
- [ ] Alerts configured for degradation

---

### 6.9 Performance Targets Summary

| Category | Metric | Target | NFR Reference |
|----------|--------|--------|---------------|
| Build | Full build time | < 3 minutes | NFR-P1 |
| Build | Incremental build | < 30 seconds | NFR-P1 |
| Build | Template generation (7 providers) | < 5 seconds | NFR-M1 |
| Runtime | Page load (95th percentile) | < 2 seconds | NFR-P2 |
| Runtime | First Contentful Paint | < 1.0 seconds | NFR-P2 |
| Runtime | Search response time | < 200ms | NFR-P2 |
| CI/CD | Total pipeline time | < 4 minutes | Developer experience |
| CI/CD | PR feedback time | < 5 minutes | Developer experience |

**Performance Principles:**
1. **Measure First:** Establish baselines before optimizing
2. **Optimize Bottlenecks:** Focus on slowest operations
3. **Cache Aggressively:** Reuse computed results when safe
4. **Parallelize:** Run independent tasks concurrently
5. **Monitor Continuously:** Detect regressions early

---

