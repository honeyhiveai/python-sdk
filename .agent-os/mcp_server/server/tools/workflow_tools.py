"""
Workflow management tools for MCP server.

Provides 7 workflow tools:
1. start_workflow - Initialize new workflow session
2. get_current_phase - Get current phase content
3. get_task - Get specific task content (horizontal scaling)
4. complete_phase - Submit evidence and advance
5. get_workflow_state - Get full workflow state
6. create_workflow - Generate new workflow framework
7. current_date - Get current date/time (prevents AI date errors)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# HoneyHive integration (optional)
try:
    from honeyhive.sdk.tracer import enrich_span, tool_trace
    HONEYHIVE_ENABLED = True
except ImportError:
    HONEYHIVE_ENABLED = False
    def tool_trace(func):
        """No-op decorator when HoneyHive not available."""
        return func


def register_workflow_tools(
    mcp: Any,
    workflow_engine: Any,
    framework_generator: Any,
    base_path: Optional[Path] = None
) -> int:
    """
    Register workflow management tools with MCP server.
    
    :param mcp: FastMCP server instance
    :param workflow_engine: WorkflowEngine instance
    :param framework_generator: FrameworkGenerator instance
    :param base_path: Base path for .agent-os (for create_workflow output)
    :return: Number of tools registered
    """
    
    @mcp.tool()
    @tool_trace
    async def start_workflow(
        workflow_type: str,
        target_file: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.

        Initializes a new workflow session, enforcing sequential phase execution.
        Returns Phase 1 content with acknowledgment requirement.

        Args:
            workflow_type: "test_generation_v3" or "production_code_v2"
            target_file: File being worked on (e.g., "config/dsl/compiler.py")
            options: Optional workflow configuration

        Returns:
            Dictionary with session info, Phase 1 content, and acknowledgment
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "start_workflow",
                    "workflow.type": workflow_type,
                    "workflow.target_file": target_file,
                })

            logger.info(
                f"start_workflow: type='{workflow_type}', file='{target_file}'"
            )

            result = workflow_engine.start_workflow(
                workflow_type=workflow_type,
                target_file=target_file,
                metadata=options,
            )

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.session_id": result.get("session_id"),
                    "workflow.current_phase": result.get("current_phase"),
                })

            logger.info(f"Workflow started: session_id={result['session_id']}")

            return result

        except Exception as e:
            logger.error(f"start_workflow failed: {e}", exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def get_current_phase(session_id: str) -> Dict[str, Any]:
        """
        Get current phase content and requirements.

        Retrieves the content for the current phase in the workflow,
        including requirements, commands, and artifacts from previous phases.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with current phase content and artifacts
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "get_current_phase",
                    "workflow.session_id": session_id,
                })

            logger.info(f"get_current_phase: session_id='{session_id}'")

            result = workflow_engine.get_current_phase(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.current_phase": result.get("current_phase"),
                    "workflow.target_file": result.get("target_file"),
                })

            logger.info(
                f"Returned phase {result['current_phase']} content for {session_id}"
            )

            return result

        except ValueError as e:
            logger.warning(f"get_current_phase: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"get_current_phase failed: {e}", exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def get_task(
        session_id: str, phase: int, task_number: int
    ) -> Dict[str, Any]:
        """
        Get full content for a specific task (horizontal scaling).

        Retrieves complete task content including execution steps and commands.
        Follows meta-framework principle: work on one task at a time.

        Args:
            session_id: Workflow session identifier
            phase: Phase number
            task_number: Task number within the phase

        Returns:
            Dictionary with complete task content and structured execution steps
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "get_task",
                    "workflow.session_id": session_id,
                    "workflow.phase": phase,
                    "workflow.task_number": task_number,
                })

            logger.info(
                f"get_task: session_id='{session_id}', phase={phase}, task={task_number}"
            )

            result = workflow_engine.get_task(session_id, phase, task_number)

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.task_name": result.get("task_name"),
                    "workflow.task_file": result.get("task_file"),
                    "workflow.steps_count": len(result.get("steps", [])),
                    "workflow.content_length": len(result.get("content", "")),
                })

            logger.info(
                f"Retrieved task {task_number} for phase {phase}: "
                f"{result.get('task_name')} with {len(result.get('steps', []))} steps"
            )

            return result

        except ValueError as e:
            logger.warning(f"get_task: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"get_task failed: {e}", exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def complete_phase(
        session_id: str, phase: int, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit evidence and attempt phase completion.

        Validates evidence against checkpoint criteria.
        If passed, advances to next phase and returns content.
        If failed, returns missing evidence and current phase content.

        Args:
            session_id: Workflow session identifier
            phase: Phase number being completed
            evidence: Evidence dictionary matching checkpoint criteria

        Returns:
            Dictionary with checkpoint result and next phase content if passed
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "complete_phase",
                    "workflow.session_id": session_id,
                    "workflow.phase": phase,
                    "workflow.evidence_fields": list(evidence.keys()),
                })

            logger.info(
                f"complete_phase: session_id='{session_id}', phase={phase}, "
                f"evidence_keys={list(evidence.keys())}"
            )

            result = workflow_engine.complete_phase(
                session_id=session_id, phase=phase, evidence=evidence
            )

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.checkpoint_passed": result.get("checkpoint_passed"),
                    "workflow.next_phase": result.get("next_phase"),
                    "workflow.missing_evidence": result.get("missing_evidence", []),
                })

            if result.get("checkpoint_passed"):
                logger.info(f"Phase {phase} completed for {session_id}")
            else:
                logger.warning(
                    f"Phase {phase} checkpoint failed: {result.get('missing_evidence')}"
                )

            return result

        except ValueError as e:
            logger.warning(f"complete_phase: {e}")
            return {"error": str(e), "checkpoint_passed": False}
        except Exception as e:
            logger.error(f"complete_phase failed: {e}", exc_info=True)
            return {"error": str(e), "checkpoint_passed": False}

    @mcp.tool()
    @tool_trace
    async def get_workflow_state(session_id: str) -> Dict[str, Any]:
        """
        Get complete workflow state for debugging/resume.

        Returns full workflow state including progress, completed phases,
        artifacts, and resume capability.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with complete workflow state
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "get_workflow_state",
                    "workflow.session_id": session_id,
                })

            logger.info(f"get_workflow_state: session_id='{session_id}'")

            result = workflow_engine.get_workflow_state(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.current_phase": result.get("current_phase"),
                    "workflow.completed_phases": result.get("completed_phases", []),
                    "workflow.is_complete": result.get("is_complete"),
                })

            logger.info(
                f"Returned state for {session_id}: phase {result['current_phase']}"
            )

            return result

        except ValueError as e:
            logger.warning(f"get_workflow_state: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"get_workflow_state failed: {e}", exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def create_workflow(
        name: str,
        workflow_type: str,
        phases: List[str],
        target_language: str = "python",
        quick_start: bool = True,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate new AI-assisted workflow framework using meta-framework principles.
        
        Creates a compliant framework structure with three-tier architecture,
        command language, validation gates, and ≤100 line task files.
        
        Args:
            name: Framework name (e.g., "api-documentation")
            workflow_type: Type of workflow (e.g., "documentation", "testing")
            phases: List of phase names (e.g., ["Analysis", "Generation", "Validation"])
            target_language: Target programming language (default: "python")
            quick_start: Use quick start template (minimal) (default: True)
            output_path: Optional custom output path (default: .agent-os/workflows/{name})
        
        Returns:
            Dictionary with framework details, file paths, and compliance report
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "create_workflow",
                    "framework.name": name,
                    "framework.type": workflow_type,
                    "framework.phases": len(phases),
                })
            
            logger.info(
                f"create_workflow: name='{name}', type='{workflow_type}', "
                f"phases={len(phases)}"
            )
            
            # Generate framework
            framework = framework_generator.generate_framework(
                name=name,
                workflow_type=workflow_type,
                phases=phases,
                target_language=target_language,
                quick_start=quick_start,
            )
            
            # Determine output path
            if output_path is None and base_path:
                output_path_obj = base_path / "workflows" / name
            elif output_path:
                output_path_obj = Path(output_path)
            else:
                output_path_obj = Path(".agent-os") / "workflows" / name
            
            # Save framework to disk
            framework.save(output_path_obj)
            
            # Validate compliance
            compliance = framework_generator.validate_compliance(framework)
            
            # Prepare response
            response = {
                "status": "success",
                "name": name,
                "workflow_type": workflow_type,
                "phases": phases,
                "output_path": str(output_path_obj),
                "files_created": len(framework.files),
                "file_list": list(framework.files.keys()),
                "compliance": compliance,
                "next_steps": [
                    f"Review generated framework at: {output_path_obj}",
                    f"Start workflow: Open {output_path_obj}/FRAMEWORK_ENTRY_POINT.md",
                    "Customize phase tasks as needed",
                ],
            }
            
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "framework.files_created": len(framework.files),
                    "framework.compliance_score": compliance.get("overall_score", 0),
                    "framework.output_path": str(output_path_obj),
                })
            
            logger.info(
                f"Framework '{name}' created: {len(framework.files)} files, "
                f"compliance score: {compliance.get('overall_score', 0)}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"create_workflow failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    @tool_trace
    async def current_date() -> Dict[str, Any]:
        """
        Get current date and time for preventing date errors in AI-generated content.
        
        AI assistants frequently make date mistakes (using wrong dates, inconsistent formats).
        This tool provides the reliable current date/time that should be used for:
        - Creating specifications with correct dates
        - Generating directory names with timestamps
        - Adding date headers to documentation
        - Any content requiring accurate current date
        
        Returns ISO 8601 formatted date/time information to ensure consistency.
        
        Returns:
            Dictionary with current date/time in multiple useful formats
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "current_date",
                })
            
            logger.info("current_date: Providing current date/time information")
            
            now = datetime.now()
            
            response = {
                "iso_date": now.strftime("%Y-%m-%d"),  # Primary format: 2025-10-06
                "iso_datetime": now.isoformat(),  # Full ISO: 2025-10-06T14:30:00.123456
                "day_of_week": now.strftime("%A"),  # Monday
                "month": now.strftime("%B"),  # October
                "year": now.year,
                "unix_timestamp": int(now.timestamp()),
                "formatted": {
                    "spec_directory": f"{now.strftime('%Y-%m-%d')}-",  # For .agent-os/specs/YYYY-MM-DD-name/
                    "header": f"**Date**: {now.strftime('%Y-%m-%d')}",  # For markdown headers
                    "full_readable": now.strftime("%A, %B %d, %Y"),  # Monday, October 6, 2025
                },
                "usage_note": (
                    "Use 'iso_date' for specs and documentation headers. "
                    "Use 'spec_directory' for .agent-os/specs/ folder names."
                ),
            }
            
            logger.info(
                f"Provided current date: {response['iso_date']} "
                f"({response['day_of_week']})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"current_date failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    return 7  # Seven tools registered


__all__ = ["register_workflow_tools"]
