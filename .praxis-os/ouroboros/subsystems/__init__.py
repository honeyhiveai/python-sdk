"""
Ouroboros Subsystems Layer.

Clean-architecture subsystems with one-way dependencies:
- RAG: Multi-index search (standards, code semantic, code graph, AST)
- Workflow: Phase-gated execution with evidence validation
- Browser: Playwright-based browser automation

Dependencies: Foundation Layer only (no Tools, no other Subsystems)
"""

