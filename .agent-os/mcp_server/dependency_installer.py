"""
Dependency Installer for Agent OS Upgrade Workflow.

Manages Python dependency installation and post-install steps.
"""

# pylint: disable=broad-exception-caught,missing-raises-doc
# Justification: Installer uses broad exceptions for robustness,
# standard exception documentation in docstrings

import logging
import subprocess
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class DependencyInstaller:
    """
    Installs Python dependencies and handles post-install steps.

    Features:
    - Install dependencies from requirements.txt
    - Detect packages needing post-install (playwright, etc.)
    - Execute post-install steps
    - Capture structured results

    Example:
        installer = DependencyInstaller()
        result = installer.install_dependencies("requirements.txt")
        if result["success"]:
            post_install = installer.run_post_install_steps(
                installer.detect_post_install_steps("requirements.txt")
            )
    """

    @staticmethod
    def install_dependencies(requirements_file: str) -> Dict:
        """
        Install dependencies from requirements.txt.

        Args:
            requirements_file: Path to requirements.txt

        Returns:
            {
                "success": bool,
                "packages_installed": int,
                "output": str,
                "errors": List[str]
            }
        """
        logger.info("Installing dependencies from: %s", requirements_file)

        req_path = Path(requirements_file)

        if not req_path.exists():
            return {
                "success": False,
                "packages_installed": 0,
                "output": "",
                "errors": [f"Requirements file not found: {requirements_file}"],
            }

        try:
            result = subprocess.run(
                ["pip", "install", "-r", requirements_file],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                check=False,
            )

            # Count installed packages from output
            packages_installed = result.stdout.count("Successfully installed")

            success = result.returncode == 0

            if success:
                logger.info(
                    "Dependencies installed successfully: %s packages",
                    packages_installed,
                )
            else:
                logger.error("Dependency installation failed: %s", result.stderr)

            return {
                "success": success,
                "packages_installed": packages_installed,
                "output": result.stdout,
                "errors": [result.stderr] if not success else [],
            }

        except subprocess.TimeoutExpired:
            error = "Dependency installation timed out after 5 minutes"
            logger.error(error)
            return {
                "success": False,
                "packages_installed": 0,
                "output": "",
                "errors": [error],
            }
        except Exception as e:
            logger.error("Failed to install dependencies: %s", e)
            return {
                "success": False,
                "packages_installed": 0,
                "output": "",
                "errors": [str(e)],
            }

    @staticmethod
    def detect_post_install_steps(requirements_file: str) -> List[Dict]:
        """
        Scan requirements.txt for packages needing post-install.

        Known patterns:
        - playwright → playwright install chromium

        Args:
            requirements_file: Path to requirements.txt

        Returns:
            List of post-install step dictionaries:
            [{
                "package": str,
                "command": str,
                "description": str
            }]
        """
        logger.info("Detecting post-install steps from: %s", requirements_file)

        req_path = Path(requirements_file)

        if not req_path.exists():
            return []

        steps = []

        try:
            content = req_path.read_text(encoding="utf-8")

            # Check for playwright
            if "playwright" in content.lower():
                steps.append(
                    {
                        "package": "playwright",
                        "command": "playwright install chromium",
                        "description": "Install Chromium browser for Playwright",
                    }
                )
                logger.info("Detected post-install step: playwright install chromium")

            # Add more patterns as needed

        except Exception as e:
            logger.warning("Failed to detect post-install steps: %s", e)

        return steps

    @staticmethod
    def run_post_install_steps(steps: List[Dict]) -> List[Dict]:
        """
        Execute post-install steps.

        Args:
            steps: List of post-install step dictionaries

        Returns:
            List of results:
            [{
                "command": str,
                "status": "success" | "failed",
                "output": str,
                "size_downloaded": str | None
            }]
        """
        results = []

        for step in steps:
            command = step["command"]
            logger.info("Running post-install step: %s", command)

            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout
                    check=False,
                )

                # Extract size information if available
                size_downloaded = None
                if "playwright install" in command:
                    # Try to extract download size from output
                    for line in result.stdout.split("\n"):
                        if "MB" in line or "downloaded" in line.lower():
                            size_downloaded = line.strip()
                            break

                status = "success" if result.returncode == 0 else "failed"

                results.append(
                    {
                        "command": command,
                        "status": status,
                        "output": result.stdout,
                        "size_downloaded": size_downloaded,
                    }
                )

                if status == "success":
                    logger.info("Post-install step completed: %s", command)
                else:
                    logger.error(
                        "Post-install step failed: %s\n%s", command, result.stderr
                    )

            except subprocess.TimeoutExpired:
                logger.error("Post-install step timed out: %s", command)
                results.append(
                    {
                        "command": command,
                        "status": "failed",
                        "output": "Timed out after 5 minutes",
                        "size_downloaded": None,
                    }
                )
            except Exception as e:
                logger.error("Failed to run post-install step %s: %s", command, e)
                results.append(
                    {
                        "command": command,
                        "status": "failed",
                        "output": str(e),
                        "size_downloaded": None,
                    }
                )

        return results
