"""
Framework Generator - Create AI-assisted workflow frameworks.

Uses meta-workflow principles to generate compliant framework structures:
- Three-tier architecture
- Command language
- Validation gates
- ≤100 line task files
"""

# pylint: disable=broad-exception-caught,missing-raises-doc,unused-argument,too-many-arguments,too-many-positional-arguments
# Justification: Generator uses broad exceptions for robustness, standard
# exception documentation in docstrings, workflow_type parameter reserved for
# template customization, and generate_framework requires 6 parameters for flexibility

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .rag_engine import RAGEngine


@dataclass
class FrameworkDefinition:
    """Definition of a generated framework."""

    name: str
    workflow_type: str
    phases: List[str]
    files: Dict[str, str]  # filepath -> content
    metadata: Dict[str, Any]

    def save(self, base_path: Path) -> None:
        """Save framework to disk."""
        base_path.mkdir(parents=True, exist_ok=True)

        for filepath, content in self.files.items():
            file_path = base_path / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)


class FrameworkGenerator:
    """Generates AI-assisted workflow frameworks using meta-workflow principles."""

    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize framework generator.

        :param rag_engine: RAG engine for querying meta-workflow standards
        """
        self.rag_engine = rag_engine

    def generate_framework(
        self,
        name: str,
        workflow_type: str,
        phases: List[str],
        target_language: str = "python",
        quick_start: bool = True,
    ) -> FrameworkDefinition:
        """
        Generate new framework using meta-workflow principles.

        :param name: Framework name (e.g., "api-documentation")
        :param workflow_type: Type of workflow (e.g., "documentation", "testing")
        :param phases: List of phase names
        :param target_language: Target programming language
        :param quick_start: Use quick start template (minimal)
        :returns: Generated framework definition
        """
        # Query meta-workflow principles from RAG
        principles = self._query_principles()

        # Generate framework structure
        files = {}

        # 1. Command glossary
        files["core/command-language-glossary.md"] = self._generate_glossary()

        # 2. Entry point
        files["FRAMEWORK_ENTRY_POINT.md"] = self._generate_entry_point(
            name, workflow_type, phases
        )

        # 3. Progress tracking
        files["core/progress-tracking.md"] = self._generate_progress_tracking(phases)

        # 4. Phase task files
        for phase_idx, phase_name in enumerate(phases):
            phase_dir = f"phases/{phase_idx}"

            # Phase entry (using phase.md per workflow-construction-standards.md)
            files[f"{phase_dir}/phase.md"] = self._generate_phase_entry(
                phase_idx, phase_name, workflow_type
            )

            # Default task
            files[f"{phase_dir}/task-1-{phase_name.lower().replace(' ', '-')}.md"] = (
                self._generate_task_file(phase_idx, phase_name, workflow_type)
            )

        # Create framework definition
        framework = FrameworkDefinition(
            name=name,
            workflow_type=workflow_type,
            phases=phases,
            files=files,
            metadata={
                "language": target_language,
                "quick_start": quick_start,
                "principles": principles,
                "file_count": len(files),
                "compliance": {
                    "three_tier": True,
                    "command_language": True,
                    "validation_gates": True,
                },
            },
        )

        return framework

    def _query_principles(self) -> Dict[str, str]:
        """Query meta-workflow principles from RAG."""
        try:
            # Query key principles
            results = self.rag_engine.search(
                query="meta-workflow principles three-tier command "
                "language validation",
                n_results=3,
            )

            principles = {}
            for chunk in results.chunks:
                if "three-tier" in chunk["content"].lower():
                    principles["three_tier"] = chunk["content"][:200]
                if "command" in chunk["content"].lower():
                    principles["command_language"] = chunk["content"][:200]
                if "validation" in chunk["content"].lower():
                    principles["validation_gates"] = chunk["content"][:200]

            return principles
        except Exception:
            # Fallback if RAG not available
            return {
                "three_tier": (
                    "Organize into Tier 1 (≤100 lines), "
                    "Tier 2 (200-500), Tier 3 (outputs)"
                ),
                "command_language": "Use 🛑 🎯 ⚠️ 📊 symbols for binding instructions",
                "validation_gates": "Add quality gates at phase boundaries",
            }

    def _generate_glossary(self) -> str:
        """Generate command language glossary."""
        return """# Command Language Glossary

This framework uses standardized command symbols for clarity and compliance.

## 🚨 Critical Foundation

This command language is **paired with a binding contract** (see framework entry point) to ensure maximum AI compliance.

**Compliance Impact**:
- Command language only: ~85%
- **Command + Contract: ~95%** ✅

## Command Reference

🛑 **EXECUTE-NOW**: Cannot proceed until executed  
⚠️ **MUST-READ**: Required reading before proceeding  
🎯 **NEXT-MANDATORY**: Explicit next step routing  
📊 **COUNT-AND-DOCUMENT**: Provide quantified evidence  
🔄 **UPDATE-TABLE**: Update progress tracking  
🛑 **VALIDATE-GATE**: Verify criteria before proceeding  
🚨 **FRAMEWORK-VIOLATION**: Detected shortcut/error

## Usage

Always follow commands in order:
1. Execute blocking commands (🛑)
2. Read required files (⚠️)
3. Complete task
4. Validate gate (🛑)
5. Update progress (🔄)
6. Navigate next (🎯)

## Why Commands Are Binding

Commands create explicit, non-negotiable obligations:
- **Symbols are visual**: Hard to miss in text
- **Meaning is clear**: No ambiguity in intent
- **Compliance is measurable**: Can verify execution
- **Contract enforces**: Framework entry point requires acknowledgment

**Violation Consequences**: Skipping commands triggers 🚨 FRAMEWORK-VIOLATION

---

**Command language is binding. All 🛑 commands must be executed. Contract acknowledgment is mandatory.**
"""

    def _generate_entry_point(
        self, name: str, workflow_type: str, phases: List[str]
    ) -> str:
        """Generate framework entry point."""
        phase_table = "\n".join(
            [f"| {i} | {phase} | varies |" for i, phase in enumerate(phases)]
        )

        # Generate binding contract commitments
        commitments = [
            f"I will follow ALL {len(phases)} phases systematically "
            f"(0-{len(phases)-1} in order)",
            "I will NOT skip steps or claim premature completion",
            "I will execute ALL 🛑 commands before proceeding",
            "I will read ALL ⚠️ required files",
            "I will provide quantified 📊 evidence for each phase",
            "I will update 🔄 progress table after each phase",
            "I understand that skipping any step = framework violation",
        ]

        contract_text = "\n".join([f"- {c}" for c in commitments])

        return f"""# {name.replace('-', ' ').title()} Framework

**Workflow Type**: {workflow_type}
**Phases**: {len(phases)}

---

## 🛑 Prerequisites

⚠️ MUST-READ: [core/command-language-glossary.md](core/command-language-glossary.md)

🛑 VALIDATE-GATE: Command Language Understanding
- [ ] All 🛑 commands understood as BLOCKING ✅/❌
- [ ] All ⚠️ commands understood as MANDATORY ✅/❌
- [ ] All 📊 commands understood as EVIDENCE-REQUIRED ✅/❌
- [ ] All 🔄 commands understood as UPDATE-REQUIRED ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without command glossary acknowledgment

---

## 🛑 Binding Framework Contract

**MANDATORY ACKNOWLEDGMENT BEFORE PROCEEDING**

🛑 EXECUTE-NOW: State this exact acknowledgment:

```markdown
✅ I acknowledge the {name.replace('-', ' ').title()} Framework binding contract:
{contract_text}
```

🚨 FRAMEWORK-VIOLATION: If proceeding without exact acknowledgment above

---

## 📊 Framework Phases

| Phase | Purpose | Duration |
|-------|---------|----------|
{phase_table}

---

## 🎯 Begin

🛑 EXECUTE-NOW: Copy progress table from [core/progress-tracking.md](core/progress-tracking.md) to chat

🎯 NEXT-MANDATORY: [phases/0/phase.md](phases/0/phase.md)

---

**Version**: 1.0  
**Generated**: Auto-generated using meta-workflow
"""

    def _generate_progress_tracking(self, phases: List[str]) -> str:
        """Generate progress tracking template."""
        rows = "\n".join(
            [f"| {i} | {phase} | ⏳ | - | ⏳ |" for i, phase in enumerate(phases)]
        )

        return f"""# Progress Tracking

Track framework execution progress.

## Progress Table

| Phase | Name | Status | Evidence | Gate |
|-------|------|--------|----------|------|
{rows}

## Status Legend

- ⏳ **Pending**: Not started
- 🔄 **In Progress**: Currently working
- ✅ **Complete**: Finished and validated
- ❌ **Failed**: Did not pass validation

## Usage

🔄 UPDATE-TABLE: After completing each phase

Update status, evidence, and gate columns:
- **Evidence**: Quantified metrics (e.g., "45/60 tests written")
- **Gate**: ✅ if validation passed, ❌ if failed, ⏳ if pending

---

**Keep this table updated throughout execution.**
"""

    def _generate_phase_entry(
        self, phase_idx: int, phase_name: str, workflow_type: str
    ) -> str:
        """Generate phase entry file."""
        # Check if this is a pre-generation or reporting phase
        is_output_phase = any(
            keyword in phase_name.lower()
            for keyword in ["pre-generation", "planning", "report", "summary"]
        )

        output_note = ""
        if is_output_phase:
            output_note = """
**🚨 CRITICAL PHASE**: Output required before proceeding.

**Required Output:**
- Complete analysis/plan in markdown format
- All items enumerated
- Strategy documented

"""

        return f"""# Phase {phase_idx}: {phase_name}

## Overview
{output_note}
This phase focuses on {phase_name.lower()}.

---

## Tasks

### Task 1: {phase_name}
🎯 NEXT-MANDATORY: [task-1-{phase_name.lower().replace(' ', '-')}.md]\
(task-1-{phase_name.lower().replace(' ', '-')}.md)

---

## Phase Completion

Upon completing all tasks:

🛑 VALIDATE-GATE: Phase {phase_idx} Complete
- [ ] All tasks completed ✅/❌
- [ ] Evidence documented ✅/❌
- [ ] Quality criteria met ✅/❌

🔄 UPDATE-TABLE: Progress Tracking

🎯 NEXT-MANDATORY: [../{phase_idx + 1}/phase.md](../{phase_idx + 1}/phase.md) (if exists)
"""

    def _generate_task_file(
        self, phase_idx: int, phase_name: str, workflow_type: str
    ) -> str:
        """Generate task file (≤100 lines target)."""
        return f"""# Task: {phase_name}

**Phase**: {phase_idx}
**Purpose**: Execute {phase_name.lower()} for this workflow

---

## Objective

Complete the {phase_name.lower()} step of the workflow.

---

## Steps

### Step 1: Preparation

Prepare for {phase_name.lower()}:
- Review requirements
- Check prerequisites
- Gather inputs

### Step 2: Execution

Execute the main {phase_name.lower()} task:
- Apply systematic approach
- Document progress
- Collect evidence

### Step 3: Validation

Validate results:
- Check quality criteria
- Verify completeness
- Document metrics

---

## Completion

📊 COUNT-AND-DOCUMENT: Results
- Items completed: [number]
- Quality score: [metric]
- Evidence: [specific]

🛑 VALIDATE-GATE: Task Complete
- [ ] All steps executed ✅/❌
- [ ] Evidence documented ✅/❌
- [ ] Quality criteria met ✅/❌

🔄 UPDATE-TABLE: Progress Tracking

🎯 NEXT-MANDATORY: [../phase.md](../phase.md) (return to phase)

---

**Version**: 1.0  
**File size**: Compliant (≤100 lines target)
"""

    def validate_compliance(self, framework: FrameworkDefinition) -> Dict[str, Any]:
        """
        Validate framework compliance with meta-workflow principles.

        :param framework: Framework to validate
        :returns: Compliance report
        """
        report: Dict[str, Any] = {
            "file_count": len(framework.files),
            "file_sizes": {},
            "tier1_compliance": 0,
            "command_usage": 0,
            "gate_coverage": 0,
            "overall_score": 0,
        }

        tier1_files = 0
        tier1_compliant = 0
        files_with_commands = 0
        files_with_gates = 0

        for filepath, content in framework.files.items():
            lines = len(content.split("\n"))
            report["file_sizes"][filepath] = lines

            # Check if Tier 1 (task/phase files)
            if "phases/" in filepath and "task-" in filepath:
                tier1_files += 1
                if lines <= 100:
                    tier1_compliant += 1

            # Check command usage
            if any(cmd in content for cmd in ["🛑", "🎯", "⚠️", "📊", "🔄"]):
                files_with_commands += 1

            # Check gate coverage
            if "VALIDATE-GATE" in content:
                files_with_gates += 1

        # Calculate compliance percentages
        if tier1_files > 0:
            report["tier1_compliance"] = int((tier1_compliant / tier1_files) * 100)

        if len(framework.files) > 0:
            report["command_usage"] = int(
                (files_with_commands / len(framework.files)) * 100
            )
            report["gate_coverage"] = int(
                (files_with_gates / len(framework.files)) * 50
            )  # Expect ~50% to have gates

        # Overall score (weighted average)
        report["overall_score"] = int(
            (
                report["tier1_compliance"] * 0.4
                + report["command_usage"] * 0.3
                + report["gate_coverage"] * 0.3
            )
        )

        return report
