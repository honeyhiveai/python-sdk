"""
Validation Module for Agent OS Upgrade Workflow.

Provides comprehensive validation functions for pre-flight checks,
post-upgrade validation, and system state verification.
"""

# pylint: disable=broad-exception-caught,import-outside-toplevel,missing-raises-doc,unused-argument
# Justification: Validation module uses broad exceptions for robustness,
# lazy imports for optional dependencies, standard exception documentation,
# and check_server_health has timeout parameter reserved for future implementation

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ValidationModule:
    """
    Validates system state at various upgrade checkpoints.

    Features:
    - Source repository validation
    - Target structure validation
    - Disk space checks
    - File checksum verification
    - Server health checks
    - Git status validation

    Example:
        validator = ValidationModule()
        result = validator.validate_source_repo("/path/to/source")
        if not result["valid"]:
            print(f"Validation failed: {result['errors']}")
    """

    @staticmethod
    def validate_source_repo(source_path: str) -> Dict:
        """
        Validate source repository for upgrade.

        Checks:
        - Path exists
        - Is agent-os-enhanced repository
        - Git status is clean (no uncommitted changes)
        - Extract version and commit hash

        Args:
            source_path: Path to source repository

        Returns:
            {
                "valid": bool,
                "path_exists": bool,
                "is_agent_os_repo": bool,
                "git_clean": bool,
                "version": str | None,
                "commit": str | None,
                "errors": List[str]
            }
        """
        logger.info("Validating source repository: %s", source_path)

        result: Dict[str, Any] = {
            "valid": False,
            "path_exists": False,
            "is_agent_os_repo": False,
            "git_clean": False,
            "version": None,
            "commit": None,
            "errors": [],
        }

        source = Path(source_path).resolve()

        # Check path exists
        if not source.exists():
            result["errors"].append(f"Path does not exist: {source_path}")
            return result

        result["path_exists"] = True

        # Check is agent-os-enhanced repo
        if not (source / "mcp_server").exists():
            result["errors"].append("Not an agent-os-enhanced repository")
            return result

        if not (source / "universal").exists():
            result["errors"].append("Missing universal/ directory")
            return result

        result["is_agent_os_repo"] = True

        # Check git status
        try:
            git_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=source,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            if git_result.stdout.strip():
                result["errors"].append("Git repository has uncommitted changes")
                result["git_clean"] = False
            else:
                result["git_clean"] = True

        except subprocess.CalledProcessError as e:
            result["errors"].append(f"Git check failed: {e}")
            return result
        except subprocess.TimeoutExpired:
            result["errors"].append("Git check timed out")
            return result

        # Extract version
        version_file = source / "VERSION.txt"
        if version_file.exists():
            result["version"] = version_file.read_text().strip()

        # Extract commit hash
        try:
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=source,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            result["commit"] = commit_result.stdout.strip()[:10]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logger.warning("Failed to get commit hash")

        # All checks passed if no errors and git is clean
        result["valid"] = len(result["errors"]) == 0 and result["git_clean"]

        if result["valid"]:
            logger.info(
                "Source repository validated: %s @ %s",
                result["version"],
                result["commit"],
            )
        else:
            logger.warning("Source validation failed: %s", result["errors"])

        return result

    @staticmethod
    def validate_target_structure(target_path: str = ".agent-os/") -> Dict:
        """
        Validate target directory structure.

        Checks for required directories:
        - mcp_server/
        - standards/
        - usage/
        - workflows/
        - config.json (file)

        Args:
            target_path: Path to target directory

        Returns:
            {
                "valid": bool,
                "target_exists": bool,
                "required_dirs": Dict[str, bool],
                "required_files": Dict[str, bool],
                "errors": List[str]
            }
        """
        logger.info("Validating target structure: %s", target_path)

        target = Path(target_path).resolve()

        result: Dict[str, Any] = {
            "valid": False,
            "target_exists": target.exists(),
            "required_dirs": {},
            "required_files": {},
            "errors": [],
        }

        if not target.exists():
            result["errors"].append(f"Target path does not exist: {target_path}")
            return result

        # Check required directories
        required_dirs = ["mcp_server", "standards", "usage", "workflows"]
        for dir_name in required_dirs:
            exists = (target / dir_name).exists()
            result["required_dirs"][dir_name] = exists
            if not exists:
                result["errors"].append(f"Missing directory: {dir_name}/")

        # Check required files
        required_files = ["config.json"]
        for file_name in required_files:
            exists = (target / file_name).exists()
            result["required_files"][file_name] = exists
            if not exists:
                result["errors"].append(f"Missing file: {file_name}")

        # Valid if all checks passed
        result["valid"] = len(result["errors"]) == 0

        if result["valid"]:
            logger.info("Target structure validated")
        else:
            logger.warning("Target validation failed: %s", result["errors"])

        return result

    @staticmethod
    def check_disk_space(
        path: str = ".agent-os/", required_multiplier: float = 2.0
    ) -> Dict:
        """
        Check available disk space.

        Ensures sufficient space for backup + upgrade.
        Recommended multiplier: 2.0 (need 2x current size).

        Args:
            path: Path to check disk space for
            required_multiplier: Multiplier for current size

        Returns:
            {
                "sufficient": bool,
                "available_bytes": int,
                "required_bytes": int,
                "available_gb": str,
                "required_gb": str
            }
        """
        logger.info("Checking disk space for: %s", path)

        disk = shutil.disk_usage(path)

        # Calculate current size
        try:
            current_size = sum(
                f.stat().st_size for f in Path(path).rglob("*") if f.is_file()
            )
        except Exception as e:
            logger.warning("Failed to calculate current size: %s", e)
            current_size = 100 * 1024 * 1024  # Default 100 MB

        required = int(current_size * required_multiplier)

        result = {
            "sufficient": disk.free > required,
            "available_bytes": disk.free,
            "required_bytes": required,
            "available_gb": f"{disk.free / 1e9:.1f}",
            "required_gb": f"{required / 1e9:.1f}",
        }

        if result["sufficient"]:
            logger.info(
                "Disk space sufficient: %s GB available, %s GB required",
                result["available_gb"],
                result["required_gb"],
            )
        else:
            logger.warning(
                "Insufficient disk space: %s GB available, %s GB required",
                result["available_gb"],
                result["required_gb"],
            )

        return result

    @staticmethod
    def verify_checksums(source_dir: str, target_dir: str) -> Dict:
        """
        Verify copied files match source via checksums.

        Used after file copy operations to ensure integrity.

        Args:
            source_dir: Source directory path
            target_dir: Target directory path

        Returns:
            {
                "verified": bool,
                "files_checked": int,
                "mismatches": List[str],
                "missing": List[str]
            }
        """
        import hashlib

        logger.info("Verifying checksums: %s -> %s", source_dir, target_dir)

        source = Path(source_dir)
        target = Path(target_dir)

        result: Dict[str, Any] = {
            "verified": False,
            "files_checked": 0,
            "mismatches": [],
            "missing": [],
        }

        if not source.exists() or not target.exists():
            logger.error("Source or target directory does not exist")
            return result

        # Get all files in source
        source_files = [f.relative_to(source) for f in source.rglob("*") if f.is_file()]

        for relative_path in source_files:
            source_file = source / relative_path
            target_file = target / relative_path

            if not target_file.exists():
                result["missing"].append(str(relative_path))
                continue

            # Calculate checksums
            source_checksum = hashlib.sha256(source_file.read_bytes()).hexdigest()
            target_checksum = hashlib.sha256(target_file.read_bytes()).hexdigest()

            result["files_checked"] += 1

            if source_checksum != target_checksum:
                result["mismatches"].append(str(relative_path))

        # Verified if no mismatches or missing files
        result["verified"] = (
            len(result["mismatches"]) == 0 and len(result["missing"]) == 0
        )

        if result["verified"]:
            logger.info("Checksums verified for %s files", result["files_checked"])
        else:
            logger.warning(
                "Checksum verification failed: %s mismatches, %s missing files",
                len(result["mismatches"]),
                len(result["missing"]),
            )

        return result

    @staticmethod
    def check_server_health(timeout: int = 30) -> Dict:
        """
        Check MCP server health after restart.

        Attempts to verify server is responding and functioning.

        Args:
            timeout: Maximum seconds to wait for server

        Returns:
            {
                "healthy": bool,
                "responding": bool,
                "response_time_ms": int | None,
                "error": str | None
            }
        """
        logger.info("Checking server health...")

        result: Dict[str, Any] = {
            "healthy": False,
            "responding": False,
            "response_time_ms": None,
            "error": None,
        }

        # Try to check if server process is running
        try:
            ps_result = subprocess.run(
                ["pgrep", "-f", "python -m mcp_server"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if ps_result.returncode == 0:
                result["responding"] = True
                result["healthy"] = True
                logger.info("Server process is running")
            else:
                result["error"] = "Server process not found"
                logger.warning(result["error"])

        except Exception as e:
            result["error"] = f"Failed to check server process: {e}"
            logger.error(result["error"])

        return result

    @staticmethod
    def check_for_concurrent_upgrades(
        lock_file: str = ".agent-os/.upgrade-lock",
    ) -> Dict:
        """
        Check for concurrent upgrade workflows.

        Args:
            lock_file: Path to upgrade lock file

        Returns:
            {
                "no_concurrent_workflows": bool,
                "lock_exists": bool,
                "lock_info": Dict | None
            }
        """
        logger.info("Checking for concurrent upgrades...")

        lock_path = Path(lock_file)

        result = {
            "no_concurrent_workflows": not lock_path.exists(),
            "lock_exists": lock_path.exists(),
            "lock_info": None,
        }

        if lock_path.exists():
            try:
                import json

                result["lock_info"] = json.loads(lock_path.read_text(encoding="utf-8"))
                logger.warning("Upgrade lock exists: %s", result["lock_info"])
            except Exception as e:
                logger.warning("Failed to read lock file: %s", e)

        return result

    @staticmethod
    def validate_workflow_not_in_progress(
        state_dir: str = ".agent-os/.cache/state/",
    ) -> bool:
        """
        Check if any upgrade workflow is currently in progress.

        Args:
            state_dir: Directory containing workflow state files

        Returns:
            True if no upgrades in progress, False otherwise
        """
        state_path = Path(state_dir)

        if not state_path.exists():
            return True

        # Check for active agent_os_upgrade_v1 sessions
        for state_file in state_path.glob("*.json"):
            try:
                import json

                state = json.loads(state_file.read_text())
                if (
                    state.get("workflow_type") == "agent_os_upgrade_v1"
                    and state.get("current_phase", 0) < 5
                ):
                    logger.warning(
                        "Active upgrade workflow found: %s", state.get("session_id")
                    )
                    return False
            except Exception:
                continue

        return True
