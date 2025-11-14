"""
pos_filesystem: Unified file operations tool.

Provides a single consolidated tool for all filesystem operations:
- read, write, append: Content operations
- delete, move, copy: File management
- list, exists, stat, glob: Discovery operations
- mkdir, rmdir: Directory operations

Security Features:
- Path validation (prevents directory traversal)
- Gitignore respect (prevents modifying ignored files)
- Safe defaults (no recursive delete without explicit flag)
- Permission validation (actionable error messages)

Architecture:
    AI Agent → pos_filesystem (Tools Layer)
        ↓
    Security Validation (path traversal, gitignore)
        ↓
    Python pathlib + shutil
        ↓
    Filesystem

Traceability:
    FR-008: pos_filesystem - File Operations Tool
"""

# pylint: disable=broad-exception-caught
# Justification: File operations tool must catch all exceptions to return
# structured error responses to AI agents, preventing tool crashes

import fnmatch
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from ouroboros.tools.base import ActionDispatchMixin

logger = logging.getLogger(__name__)


class FilesystemTool(ActionDispatchMixin):
    """
    Unified filesystem operations tool using ActionDispatchMixin pattern.
    
    Provides secure file operations with path validation and gitignore respect.
    """
    
    def __init__(self, mcp: Any, workspace_root: Path):
        """Initialize with workspace root for path validation."""
        super().__init__(mcp)
        self.workspace_root = workspace_root
        
        # Define action handlers
        self.handlers = {
            "read": self._handle_read,
            "write": self._handle_write,
            "append": self._handle_append,
            "delete": self._handle_delete,
            "move": self._handle_move,
            "copy": self._handle_copy,
            "list": self._handle_list,
            "exists": self._handle_exists,
            "stat": self._handle_stat,
            "glob": self._handle_glob,
            "mkdir": self._handle_mkdir,
            "rmdir": self._handle_rmdir,
        }
    
    @property
    def tool(self):
        """Return the MCP tool decorator wrapper."""
        @self.mcp.tool()
        async def pos_filesystem(
            action: Literal[
                # Content operations
                "read",
                "write",
                "append",
                # File management
                "delete",
                "move",
                "copy",
                # Discovery
                "list",
                "exists",
                "stat",
                "glob",
                # Directory operations
                "mkdir",
                "rmdir",
            ],
            path: str,
            content: Optional[str] = None,
            destination: Optional[str] = None,
            recursive: bool = False,
            follow_symlinks: bool = False,
            encoding: str = "utf-8",
            create_parents: bool = False,
            override_gitignore: bool = False,
        ) -> Dict[str, Any]:
            """
            Unified file operations with safe defaults.
            
            Provides comprehensive filesystem operations with security validation:
            - Path traversal prevention (no "..", no absolute paths outside workspace)
            - Gitignore respect (won't modify ignored files without override)
            - Safe defaults (no recursive delete without explicit flag)
            - Actionable error messages with remediation guidance
            
            Actions:
                Content Operations:
                    - read: Read file contents (encoding configurable)
                    - write: Write content to file (creates if not exists)
                    - append: Append content to file (creates if not exists)
                
                File Management:
                    - delete: Delete file or directory (requires recursive=True for dirs)
                    - move: Move/rename file or directory
                    - copy: Copy file or directory
                
                Discovery:
                    - list: List directory contents (recursive optional)
                    - exists: Check if path exists
                    - stat: Get file/directory metadata (size, modified time, etc.)
                    - glob: Search for files matching pattern
                
                Directory Operations:
                    - mkdir: Create directory (create_parents for nested dirs)
                    - rmdir: Remove empty directory
            
            Args:
                action: File operation to perform (required)
                path: File or directory path (required, relative to workspace)
                content: Content to write/append (for write, append actions)
                destination: Destination path (for move, copy actions)
                recursive: Enable recursive operations (delete dirs, list subdirs)
                follow_symlinks: Follow symbolic links
                encoding: Text encoding (default: utf-8)
                create_parents: Create parent directories if needed (mkdir, write)
                override_gitignore: Allow operations on gitignored files
                
            Returns:
                Dictionary with:
                - status: "success" or "error"
                - action: Echoed action parameter
                - path: Resolved path
                - data: Action-specific result data
                
            Examples:
                >>> # Read file
                >>> pos_filesystem(
                ...     action="read",
                ...     path="src/module.py"
                ... )
                
                >>> # Write file with parent creation
                >>> pos_filesystem(
                ...     action="write",
                ...     path="output/results.txt",
                ...     content="Hello, World!",
                ...     create_parents=True
                ... )
                
                >>> # List directory recursively
                >>> pos_filesystem(
                ...     action="list",
                ...     path="src/",
                ...     recursive=True
                ... )
                
                >>> # Delete directory (requires recursive flag)
                >>> pos_filesystem(
                ...     action="delete",
                ...     path="tmp/",
                ...     recursive=True
                ... )
            
            Raises:
                ValueError: If action is invalid or required parameters missing
                
            Traceability:
                FR-008: pos_filesystem - File Operations Tool
            """
            # Validate required parameters
            if not path:
                raise ValueError("path parameter is required")
            
            # Security: Validate and resolve path
            try:
                resolved_path = self._validate_and_resolve_path(path)
            except ValueError as e:
                raise ValueError(
                    f"{e}. Provide a relative path within the workspace. "
                    "Absolute paths and '..' are not allowed for security."
                )
            
            # Security: Check gitignore (for modify operations)
            if not override_gitignore and action in ("write", "append", "delete", "move"):
                if self._is_gitignored(resolved_path):
                    raise ValueError(
                        f"File is gitignored: {path}. "
                        "Use override_gitignore=True to modify gitignored files, "
                        "or remove from .gitignore"
                    )
            
            # Dispatch to handler
            result = await self.dispatch(
                action,
                self.handlers,  # type: ignore[arg-type]
                path=resolved_path,
                content=content,
                destination=destination,
                recursive=recursive,
                follow_symlinks=follow_symlinks,
                encoding=encoding,
                create_parents=create_parents,
            )
            
            # Add relative path to result
            if "path" not in result:
                result["path"] = str(resolved_path.relative_to(self.workspace_root))
            
            return result
        
        return pos_filesystem
    
    # ========================================================================
    # Security Validation
    # ========================================================================
    
    def _validate_and_resolve_path(self, path: str) -> Path:
        """
        Validate and resolve path, preventing directory traversal attacks.
        
        Args:
            path: User-provided path (relative or absolute)
            
        Returns:
            Resolved absolute path within workspace
            
        Raises:
            ValueError: If path is invalid or outside workspace
        """
        # Convert to Path object
        path_obj = Path(path)
        
        # Security: Reject absolute paths starting with /
        if path_obj.is_absolute():
            # Allow if it's already within workspace
            try:
                path_obj.relative_to(self.workspace_root)
                return path_obj.resolve()
            except ValueError:
                raise ValueError(
                    f"Absolute path outside workspace: {path}"
                )
        
        # Resolve relative to workspace
        resolved = (self.workspace_root / path_obj).resolve()
        
        # Security: Ensure resolved path is within workspace (prevents ".." attacks)
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(
                f"Path traversal detected: {path} resolves outside workspace"
            )
        
        return resolved
    
    def _is_gitignored(self, path: Path) -> bool:
        """
        Check if path is gitignored.
        
        Args:
            path: Absolute path to check
            
        Returns:
            True if path is gitignored, False otherwise
        """
        gitignore_file = self.workspace_root / ".gitignore"
        if not gitignore_file.exists():
            return False
        
        try:
            relative_path = path.relative_to(self.workspace_root)
            path_str = str(relative_path)
            
            # Read .gitignore patterns
            with open(gitignore_file, "r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            
            # Simple pattern matching
            for pattern in patterns:
                # Remove trailing slash
                pattern = pattern.rstrip("/")
                
                # Exact match
                if path_str == pattern:
                    return True
                
                # Directory match
                if path_str.startswith(f"{pattern}/"):
                    return True
                
                # Wildcard match (basic)
                if "*" in pattern:
                    if fnmatch.fnmatch(path_str, pattern):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning("Error checking gitignore for %s: %s", path, e)
            return False
    
    # ========================================================================
    # Action Handlers
    # ========================================================================
    
    def _handle_read(self, path: Path, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """Read file contents."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        try:
            content = path.read_text(encoding=encoding)
            return {
                "content": content,
                "size": len(content),
                "encoding": encoding,
            }
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Failed to decode file with encoding {encoding}: {e}. "
                "Try a different encoding or read as binary."
            )
    
    def _handle_write(
        self, path: Path, content: Optional[str], encoding: str = "utf-8", 
        create_parents: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Write content to file."""
        if content is None:
            raise ValueError("write action requires content parameter")
        
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding=encoding)
        
        return {
            "bytes_written": len(content.encode(encoding)),
        }
    
    def _handle_append(
        self, path: Path, content: Optional[str], encoding: str = "utf-8",
        create_parents: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Append content to file."""
        if content is None:
            raise ValueError("append action requires content parameter")
        
        if create_parents and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "a", encoding=encoding) as f:
            f.write(content)
        
        return {
            "bytes_appended": len(content.encode(encoding)),
        }
    
    def _handle_delete(self, path: Path, recursive: bool = False, **kwargs) -> Dict[str, Any]:
        """Delete file or directory."""
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        if path.is_dir():
            if not recursive:
                raise ValueError(
                    f"Cannot delete directory without recursive=True: {path}. "
                    "Use recursive=True to delete directories and their contents."
                )
            shutil.rmtree(path)
            return {
                "deleted": "directory",
                "recursive": True,
            }
        else:
            path.unlink()
            return {
                "deleted": "file",
            }
    
    def _handle_move(self, path: Path, destination: Optional[str], **kwargs) -> Dict[str, Any]:
        """Move/rename file or directory."""
        if not destination:
            raise ValueError("move action requires destination parameter")
        
        dest_path = self._validate_and_resolve_path(destination)
        
        if not path.exists():
            raise FileNotFoundError(f"Source not found: {path}")
        
        shutil.move(str(path), str(dest_path))
        
        return {
            "source": str(path.relative_to(self.workspace_root)),
            "destination": str(dest_path.relative_to(self.workspace_root)),
        }
    
    def _handle_copy(
        self, path: Path, destination: Optional[str], recursive: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Copy file or directory."""
        if not destination:
            raise ValueError("copy action requires destination parameter")
        
        dest_path = self._validate_and_resolve_path(destination)
        
        if not path.exists():
            raise FileNotFoundError(f"Source not found: {path}")
        
        if path.is_dir():
            if not recursive:
                raise ValueError(
                    f"Cannot copy directory without recursive=True: {path}. "
                    "Use recursive=True to copy directories and their contents."
                )
            shutil.copytree(str(path), str(dest_path))
            return {
                "copied": "directory",
                "recursive": True,
            }
        else:
            shutil.copy2(str(path), str(dest_path))
            return {
                "copied": "file",
            }
    
    def _handle_list(self, path: Path, recursive: bool = False, **kwargs) -> Dict[str, Any]:
        """List directory contents."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        entries = []
        
        if recursive:
            for item in path.rglob("*"):
                entries.append({
                    "path": str(item.relative_to(path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
        else:
            for item in path.iterdir():
                entries.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
        
        return {
            "entries": entries,
            "count": len(entries),
            "recursive": recursive,
        }
    
    def _handle_exists(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Check if path exists."""
        exists = path.exists()
        
        result: Dict[str, Any] = {
            "exists": exists,
        }
        
        if exists:
            result["type"] = "directory" if path.is_dir() else "file"
        
        return result
    
    def _handle_stat(self, path: Path, follow_symlinks: bool = False, **kwargs) -> Dict[str, Any]:
        """Get file/directory metadata."""
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat_info = path.stat() if follow_symlinks else path.lstat()
        
        return {
            "type": "directory" if path.is_dir() else "file",
            "size": stat_info.st_size,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "accessed": stat_info.st_atime,
            "permissions": oct(stat_info.st_mode)[-3:],
            "is_symlink": path.is_symlink(),
        }
    
    def _handle_glob(self, path: Path, recursive: bool = False, **kwargs) -> Dict[str, Any]:
        """Search for files matching pattern."""
        # path is the glob pattern
        pattern = str(path.relative_to(self.workspace_root))
        
        if recursive:
            matches = list(self.workspace_root.rglob(pattern))
        else:
            matches = list(self.workspace_root.glob(pattern))
        
        results = [
            {
                "path": str(match.relative_to(self.workspace_root)),
                "type": "directory" if match.is_dir() else "file",
            }
            for match in matches
        ]
        
        return {
            "pattern": pattern,
            "matches": results,
            "count": len(results),
        }
    
    def _handle_mkdir(self, path: Path, create_parents: bool = False, **kwargs) -> Dict[str, Any]:
        """Create directory."""
        if path.exists():
            raise FileExistsError(f"Directory already exists: {path}")
        
        path.mkdir(parents=create_parents, exist_ok=False)
        
        return {
            "created": str(path.relative_to(self.workspace_root)),
            "parents_created": create_parents,
        }
    
    def _handle_rmdir(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Remove empty directory."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        try:
            path.rmdir()  # Only removes empty directories
        except OSError:
            raise ValueError(
                f"Directory is not empty: {path}. "
                "Use action='delete' with recursive=True to remove non-empty directories."
            )
        
        return {
            "removed": str(path.relative_to(self.workspace_root)),
        }


def register_filesystem_tool(mcp: Any, workspace_root: Path) -> int:
    """
    Register pos_filesystem tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        workspace_root: Workspace root directory for path validation
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-008: pos_filesystem tool registration
    """
    # Create tool instance
    tool_instance = FilesystemTool(mcp=mcp, workspace_root=workspace_root)
    
    # Register the tool (accessing the @mcp.tool() decorated function)
    _ = tool_instance.tool
    
    logger.info("✅ Registered pos_filesystem tool (12 actions) using ActionDispatchMixin")
    return 1  # One tool registered


__all__ = ["register_filesystem_tool", "FilesystemTool"]

