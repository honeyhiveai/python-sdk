"""
Backup Manager for Agent OS Upgrade Workflow.

Manages backup creation, verification, restoration, and archival operations.
Ensures safe rollback capability for upgrade workflows.
"""

# pylint: disable=broad-exception-caught,import-outside-toplevel,missing-raises-doc,too-many-locals
# Justification: Backup manager uses broad exceptions for robustness,
# lazy imports for optional dependencies, and verification logic requires many local
# variables for comprehensive validation (19 locals for metadata, hashes, files)

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupIntegrityError(Exception):
    """Raised when backup integrity verification fails."""


class BackupManager:
    """
    Manages backup creation and verification for safe upgrades.

    Features:
    - Timestamped backup creation
    - SHA256 checksum verification
    - Backup integrity validation
    - Safe restoration from backup
    - Old backup archival

    Example:
        manager = BackupManager()
        backup_info = manager.create_backup()
        # ... perform upgrade ...
        if upgrade_failed:
            manager.restore_from_backup(Path(backup_info["backup_path"]))
    """

    BACKUP_DIR = Path(".agent-os/.backups/")

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            base_path: Optional base path for .agent-os directory
                      (defaults to current directory)
        """
        self.base_path = base_path or Path.cwd()
        self.agent_os_dir = self.base_path / ".agent-os"
        self.backup_dir = self.base_path / self.BACKUP_DIR

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info("BackupManager initialized: %s", self.backup_dir)

    def create_backup(self) -> Dict:
        """
        Create timestamped backup with checksum manifest.

        Backs up:
        - mcp_server/ directory
        - config.json file
        - standards/ directory
        - usage/ directory
        - workflows/ directory
        - requirements.txt (snapshot of installed packages)

        Returns:
            {
                "backup_path": str,
                "backup_timestamp": str,
                "files_backed_up": int,
                "backup_size_bytes": int,
                "backup_manifest": str,
                "integrity_verified": bool,
                "lock_acquired": bool
            }

        Raises:
            IOError: If backup creation fails
        """
        logger.info("Creating backup...")

        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)

        # Backup critical directories and files
        directories = ["mcp_server", "standards", "usage", "workflows"]
        files = ["config.json"]

        total_size = 0
        file_count = 0

        # Backup directories
        for dir_name in directories:
            source = self.agent_os_dir / dir_name
            if source.exists():
                dest = backup_path / dir_name
                logger.debug("Backing up directory: %s -> %s", source, dest)
                shutil.copytree(source, dest)
                file_count += sum(1 for _ in dest.rglob("*") if _.is_file())
                total_size += sum(
                    f.stat().st_size for f in dest.rglob("*") if f.is_file()
                )

        # Backup individual files
        for file_name in files:
            source = self.agent_os_dir / file_name
            if source.exists():
                dest = backup_path / file_name
                logger.debug("Backing up file: %s -> %s", source, dest)
                shutil.copy2(source, dest)
                file_count += 1
                total_size += dest.stat().st_size

        # Create requirements snapshot (save currently installed packages)
        try:
            import subprocess

            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode == 0:
                req_snapshot = backup_path / "requirements-snapshot.txt"
                req_snapshot.write_text(result.stdout)
                file_count += 1
                total_size += req_snapshot.stat().st_size
                logger.debug("Created requirements snapshot: %s", req_snapshot)
        except Exception as e:
            logger.warning("Failed to create requirements snapshot: %s", e)

        # Generate checksum manifest
        manifest = self._generate_manifest(backup_path)
        manifest_path = backup_path / "MANIFEST.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Verify backup integrity immediately
        integrity_verified = self.verify_backup_integrity(backup_path)

        logger.info(
            "Backup created: %s (%s files, %.2f MB)",
            backup_path,
            file_count,
            total_size / 1024 / 1024,
        )

        return {
            "backup_path": str(backup_path),
            "backup_timestamp": timestamp,
            "files_backed_up": file_count,
            "backup_size_bytes": total_size,
            "backup_manifest": str(manifest_path),
            "integrity_verified": integrity_verified,
            "lock_acquired": True,  # Will be set by workflow engine
        }

    def _generate_manifest(self, backup_path: Path) -> Dict:
        """
        Generate SHA256 checksums for all files in backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            Manifest dictionary with file checksums
        """
        manifest: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
        }

        for file_path in backup_path.rglob("*"):
            if file_path.is_file() and file_path.name != "MANIFEST.json":
                relative_path = str(file_path.relative_to(backup_path))
                checksum = self._sha256_file(file_path)
                manifest["files"][relative_path] = checksum

        return manifest

    @staticmethod
    def _sha256_file(file_path: Path) -> str:
        """
        Calculate SHA256 hash of file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal SHA256 hash string
        """
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def verify_backup_integrity(self, backup_path: Path) -> bool:
        """
        Verify backup integrity using manifest checksums.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if all files match checksums, False otherwise
        """
        manifest_path = backup_path / "MANIFEST.json"

        if not manifest_path.exists():
            logger.error("Manifest not found: %s", manifest_path)
            return False

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            for relative_path, expected_checksum in manifest["files"].items():
                file_path = backup_path / relative_path

                if not file_path.exists():
                    logger.error("File missing from backup: %s", relative_path)
                    return False

                actual_checksum = self._sha256_file(file_path)
                if actual_checksum != expected_checksum:
                    logger.error(
                        "Checksum mismatch for %s: expected %s, got %s",
                        relative_path,
                        expected_checksum,
                        actual_checksum,
                    )
                    return False

            logger.info("Backup integrity verified: %s", backup_path)
            return True

        except Exception as e:
            logger.error("Failed to verify backup integrity: %s", e)
            return False

    def restore_from_backup(self, backup_path: Path) -> None:
        """
        Restore installation from backup.

        Used for rollback operation after failed upgrade.

        Args:
            backup_path: Path to backup directory

        Raises:
            BackupIntegrityError: If backup integrity check fails
            IOError: If restoration fails
        """
        logger.info("Restoring from backup: %s", backup_path)

        # Verify integrity first
        if not self.verify_backup_integrity(backup_path):
            raise BackupIntegrityError(
                f"Backup integrity check failed for {backup_path}"
            )

        # Restore directories
        directories = ["mcp_server", "standards", "usage", "workflows"]

        for dir_name in directories:
            source = backup_path / dir_name
            dest = self.agent_os_dir / dir_name

            if source.exists():
                # Remove existing directory if present
                if dest.exists():
                    logger.debug("Removing existing directory: %s", dest)
                    shutil.rmtree(dest)

                # Restore from backup
                logger.debug("Restoring directory: %s -> %s", source, dest)
                shutil.copytree(source, dest)

        # Restore individual files
        files = ["config.json"]

        for file_name in files:
            source = backup_path / file_name
            dest = self.agent_os_dir / file_name

            if source.exists():
                logger.debug("Restoring file: %s -> %s", source, dest)
                shutil.copy2(source, dest)

        logger.info("Restore from backup completed successfully")

    def archive_old_backups(self, keep: int = 3) -> Dict:
        """
        Archive old backups, keeping only the most recent N.

        Args:
            keep: Number of most recent backups to keep

        Returns:
            {
                "archived_count": int,
                "kept_backups": List[str]
            }
        """
        logger.info("Archiving old backups (keeping last %s)", keep)

        # Find all backup directories
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and not backup_dir.name.startswith("."):
                backups.append(backup_dir)

        # Sort by modification time (newest first)
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Keep only the most recent N backups
        kept_backups = backups[:keep]
        archived_backups = backups[keep:]

        archived_count = 0
        for backup_dir in archived_backups:
            try:
                logger.debug("Removing old backup: %s", backup_dir)
                shutil.rmtree(backup_dir)
                archived_count += 1
            except Exception as e:
                logger.warning("Failed to remove backup %s: %s", backup_dir, e)

        logger.info(
            "Archived %s old backups, kept %s recent backups",
            archived_count,
            len(kept_backups),
        )

        return {
            "archived_count": archived_count,
            "kept_backups": [str(b) for b in kept_backups],
        }

    def list_backups(self) -> List[Dict]:
        """
        List all available backups with metadata.

        Returns:
            List of backup info dictionaries
        """
        backups = []

        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and not backup_dir.name.startswith("."):
                manifest_path = backup_dir / "MANIFEST.json"

                backup_info = {
                    "path": str(backup_dir),
                    "timestamp": backup_dir.name,
                    "exists": True,
                }

                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        backup_info["file_count"] = len(manifest.get("files", {}))
                        backup_info["created_at"] = manifest.get("timestamp")
                    except Exception as e:
                        logger.warning(
                            "Failed to read manifest for %s: %s", backup_dir, e
                        )

                # Calculate total size
                try:
                    total_size = sum(
                        f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
                    )
                    backup_info["size_bytes"] = total_size
                except Exception as e:
                    logger.warning("Failed to calculate size for %s: %s", backup_dir, e)

                backups.append(backup_info)

        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: str(b["timestamp"]), reverse=True)

        return backups

    def get_latest_backup(self) -> Optional[Path]:
        """
        Get path to the most recent backup.

        Returns:
            Path to latest backup, or None if no backups exist
        """
        backups = self.list_backups()

        if not backups:
            return None

        return Path(backups[0]["path"])
