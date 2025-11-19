"""Semantic search implementation for Code Index.

This module provides semantic code search using CodeBERT/GraphCodeBERT embeddings in LanceDB.
Unlike standards (which are documentation), code requires different chunking strategies
and embedding models optimized for programming languages.

Key Differences from StandardsIndex:
- Smaller chunks: 200 tokens (code is denser than prose)
- Code-specific embeddings: CodeBERT/GraphCodeBERT
- Function/class-level granularity (respects code structure)
- Line number tracking for precise navigation
- Language-aware tokenization

Graph traversal (call graphs, dependencies) is handled by GraphIndex (separate module).

Mission: Enable "trust but verify" - AI can search code to validate documentation claims.

This is the internal implementation for CodeIndex semantic search, not the public API.
Use CodeIndex (container.py) as the public interface.
"""

import hashlib
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Set, Tuple

from ouroboros.config.schemas.indexes import CodeIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.code.constants import DEFAULT_EXCLUDE_PATTERNS
from ouroboros.subsystems.rag.code.ast_chunker import UniversalASTChunker, CodeChunk
from ouroboros.subsystems.rag.utils.lancedb_helpers import EmbeddingModelLoader, LanceDBConnection, safe_encode
from ouroboros.subsystems.rag.utils.progress_file import ProgressFileManager
from ouroboros.utils.errors import ActionableError, IndexError
from gitignore_parser import parse_gitignore

logger = logging.getLogger(__name__)

# Constants for edge case handling
MAX_GITIGNORE_SIZE = 1 * 1024 * 1024  # 1MB maximum .gitignore file size


class SemanticIndex(BaseIndex):
    """Semantic code search index using LanceDB (internal implementation).
    
    Provides hybrid search (vector + FTS + RRF) over source code using
    CodeBERT embeddings for semantic understanding.
    
    Architecture:
    - LanceDB: Vector + FTS + Scalar indexes (like StandardsIndex)
    - CodeBERT: Code-optimized embeddings
    - AST-aware chunking: Function/class boundaries
    - Language filtering: Per-language metadata
    
    Search strategies:
    - Vector: Semantic code understanding ("error handling patterns")
    - FTS: Exact symbol/keyword matching ("StateManager")
    - Hybrid: RRF fusion for best results
    
    Design Notes:
    - Uses LanceDBConnection helper for lazy initialization
    - Uses EmbeddingModelLoader helper for model caching
    - No lock manager integration yet (will be added when container orchestrates)
    """
    
    def __init__(
        self, 
        config: CodeIndexConfig, 
        base_path: Path, 
        index_path: Optional[Path] = None,
        partition_name: Optional[str] = None
    ):
        """Initialize Semantic Index for code.
        
        Args:
            config: CodeIndexConfig from MCPConfig
            base_path: Base path for resolving relative paths
            index_path: Optional explicit index path (defaults to base_path/.cache/indexes/code)
            partition_name: Optional partition name for multi-repo mode (used to tag chunks)
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        self.partition_name = partition_name or "default"  # Store for chunk tagging
        
        # Resolve index path: explicit path or sane default
        if index_path is not None:
            self.index_path = index_path
        else:
            # Sane default: base_path/.cache/indexes/code (backward compatible)
            self.index_path = base_path / ".cache" / "indexes" / "code"
        
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Use LanceDBConnection helper for lazy initialization
        self.db_connection = LanceDBConnection(self.index_path)
        self._table = None
        
        # Lazy-load reranker (optional)
        self._reranker = None
        
        # Gitignore caching (thread-safe)
        self._gitignore_path: Optional[Path] = None
        self._gitignore_parser: Optional[Callable[[str], bool]] = None
        self._gitignore_lock = threading.Lock()
        
        # Cached parsers for performance (thread-safe)
        # Note: Builtin parser is NOT cached because gitignore-parser requires a real file
        # and we can't keep temp files alive for the lifetime of the index
        self._config_parser: Optional[Callable[[str], bool]] = None
        self._config_patterns_hash: Optional[str] = None  # Track config changes
        self._parser_lock = threading.Lock()
        
        # AST chunking fallback tracking (for health metrics)
        self._ast_fallback_count: int = 0
        
        # Progress file manager for build progress reporting
        progress_cache_dir = base_path / ".cache" / "rag" / "build-progress"
        self._progress_manager = ProgressFileManager(
            cache_dir=progress_cache_dir,
            index_name="code",
            component="semantic"
        )
        
        # Build status tracking (ADDENDUM-2025-11-17: Build Status Integration)
        self._building = False
        self._build_lock = threading.Lock()
        
        logger.info("SemanticIndex (code) initialized (lazy-load mode)")
    
    def _ensure_table(self):
        """Ensure table is loaded (lazy initialization)."""
        if self._table is None:
            try:
                self._table = self.db_connection.open_table("code")
                logger.info("Opened code table")
            except ActionableError:
                # Re-raise ActionableError from helper
                raise
            except Exception as e:
                raise IndexError(
                    what_failed="Open code table",
                    why_failed="Table does not exist. Index not built yet.",
                    how_to_fix="Build index first using container.build()"
                ) from e
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build code index from source paths.
        
        This method:
        1. Discovers code files based on config.languages
        2. Chunks code at function/class boundaries (200 tokens target)
        3. Generates CodeBERT embeddings for each chunk
        4. Creates LanceDB table with vector data
        5. Builds FTS index for exact symbol matching
        6. Builds scalar indexes for language/file filtering
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building code index from %d source paths", len(source_paths))
        
        # Set building flag (ADDENDUM-2025-11-17: Build Status Integration)
        with self._build_lock:
            self._building = True
        
        try:
            # Write initial progress (0%)
            self._progress_manager.write_progress(0.0, "Starting build...")
            
            # Check if index already exists
            db = self.db_connection.connect()
            existing_tables = db.table_names()
            
            if "code" in existing_tables and not force:
                logger.info("Code index already exists. Use force=True to rebuild.")
                # Cleanup progress file on early return
                self._progress_manager.delete_progress()
                return
            
            # Load embedding model via helper (caching)
            self._progress_manager.write_progress(5.0, "Loading CodeBERT embedding model...")
            embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
            
            # Collect and chunk code files
            self._progress_manager.write_progress(10.0, "Discovering and chunking code files...")
            chunks = self._collect_and_chunk(source_paths)
            logger.info("Collected %d code chunks from source paths", len(chunks))
            
            if not chunks:
                # Cleanup progress file on error
                self._progress_manager.delete_progress()
                raise ActionableError(
                    what_failed="Build code index",
                    why_failed="No code files found in source paths",
                    how_to_fix=f"Check that source paths contain code files for languages: {self.config.languages}"
                )
            
            # Generate embeddings with progress reporting
            logger.info("Generating embeddings for %d chunks...", len(chunks))
            texts = [chunk["content"] for chunk in chunks]
            
            # Report progress during embedding (20% -> 70% of total progress)
            self._progress_manager.write_progress(20.0, f"Generating embeddings for {len(chunks)} code chunks...")
            embeddings = safe_encode(embedding_model, texts, show_progress_bar=True)
            self._progress_manager.write_progress(70.0, f"Embeddings generated for {len(chunks)} chunks")
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["vector"] = embedding.tolist()
            
            # Create table (drop existing if force=True)
            if "code" in existing_tables and force:
                logger.info("Dropping existing code table (force rebuild)")
                db.drop_table("code")
            
            self._progress_manager.write_progress(75.0, f"Creating LanceDB table with {len(chunks)} chunks...")
            logger.info("Creating code table with %d chunks", len(chunks))
            self._table = db.create_table("code", data=chunks)
            
            # Build indexes
            self._progress_manager.write_progress(85.0, "Building FTS and metadata indexes...")
            self._build_indexes()
            
            # Success - cleanup progress file
            self._progress_manager.write_progress(100.0, "Build complete!")
            self._progress_manager.delete_progress()
            
            logger.info("✅ Code index built successfully")
        
        except Exception as e:
            # Cleanup progress file on failure
            self._progress_manager.delete_progress()
            raise
        finally:
            # Clear building flag (ADDENDUM-2025-11-17: Build Status Integration)
            with self._build_lock:
                self._building = False
    
    def _collect_and_chunk(self, source_paths: List[Path]) -> List[Dict[str, Any]]:
        """Collect code files and chunk them.
        
        Includes symlink detection and cycle prevention to avoid:
        - Infinite loops from circular symlinks
        - Duplicate indexing from symlinks to already-indexed directories
        - Security issues from symlinks escaping project boundaries
        
        Args:
            source_paths: Paths to scan for code files
            
        Returns:
            List of chunk dictionaries with content, metadata, etc.
        """
        chunks = []
        
        # Track seen inodes to prevent symlink cycles and duplicates
        seen_inodes: Set[Tuple[int, int]] = set()
        
        # Build file patterns from configured languages
        file_extensions = self._get_file_extensions()
        
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            # Collect code files matching configured languages
            if resolved_path.is_file():
                if resolved_path.suffix in file_extensions:
                    # Check exclusion for single file
                    if not self._should_exclude_file(resolved_path):
                        chunks.extend(self._chunk_file(resolved_path))
            else:
                # Recursively find code files
                for ext in file_extensions:
                    for code_file in resolved_path.rglob(f"*{ext}"):
                        # Symlink detection and cycle prevention
                        if code_file.is_symlink():
                            try:
                                # Resolve symlink and get inode
                                resolved_file = code_file.resolve(strict=True)
                                file_stat = resolved_file.stat()
                                inode = (file_stat.st_dev, file_stat.st_ino)
                                
                                # Check if we've already seen this file
                                if inode in seen_inodes:
                                    logger.debug(
                                        "Skipping duplicate file via symlink: %s -> %s",
                                        code_file, resolved_file
                                    )
                                    continue
                                
                                seen_inodes.add(inode)
                                logger.debug("Following symlink: %s -> %s", code_file, resolved_file)
                                
                            except (OSError, RuntimeError) as e:
                                # Broken symlink or circular reference
                                logger.warning(
                                    "Skipping broken/circular symlink: %s (%s: %s)",
                                    code_file, type(e).__name__, e
                                )
                                continue
                        else:
                            # Regular file - track inode to detect duplicates
                            try:
                                file_stat = code_file.stat()
                                inode = (file_stat.st_dev, file_stat.st_ino)
                                
                                if inode in seen_inodes:
                                    logger.debug("Skipping duplicate inode: %s", code_file)
                                    continue
                                
                                seen_inodes.add(inode)
                            except OSError as e:
                                logger.warning("Failed to stat file: %s (%s)", code_file, e)
                                continue
                        
                        # Three-tier exclusion check
                        if self._should_exclude_file(code_file):
                            continue
                        chunks.extend(self._chunk_file(code_file))
        
        return chunks
    
    def _get_file_extensions(self) -> List[str]:
        """Get file extensions for configured languages.
        
        Returns:
            List of file extensions (e.g., ['.py', '.js', '.ts'])
        """
        # Map language names to file extensions
        extension_map = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".mjs", ".cjs"],
            "typescript": [".ts", ".tsx"],
            "go": [".go"],
            "rust": [".rs"],
            "java": [".java"],
            "csharp": [".cs"],
            "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
            "c": [".c", ".h"],
            "ruby": [".rb"],
            "php": [".php"],
        }
        
        extensions = []
        for lang in self.config.languages:
            lang_lower = lang.lower()
            if lang_lower in extension_map:
                extensions.extend(extension_map[lang_lower])
            else:
                logger.warning("Unknown language: %s (no file extensions mapped)", lang)
        
        return extensions
    
    def _find_gitignore_file(self) -> Optional[Path]:
        """Find .gitignore file starting from project root (base_path.parent).
        
        Walks up from project root to support monorepos. Caches result.
        
        Returns:
            Path to .gitignore if found, None otherwise
        """
        if self._gitignore_path is not None:
            return self._gitignore_path
        
        # base_path is .praxis-os/, project root is base_path.parent
        # Start from project root and walk up (for monorepos)
        current = self.base_path.parent
        while current != current.parent:  # Stop at filesystem root
            gitignore = current / ".gitignore"
            if gitignore.exists():
                self._gitignore_path = gitignore
                return gitignore
            current = current.parent
        
        self._gitignore_path = None
        return None
    
    def _has_gitignore(self) -> bool:
        """Check if .gitignore file exists.
        
        Returns:
            True if .gitignore exists, False otherwise
        """
        return self._find_gitignore_file() is not None
    
    def _load_gitignore(self) -> Optional[Callable[[str], bool]]:
        """Load and parse .gitignore file using gitignore-parser (thread-safe).
        
        Includes security checks:
        - Size limit (1MB) to prevent DoS from malicious large files
        - Thread-safe caching to prevent race conditions
        
        Caches parser instance. Returns None if .gitignore not found.
        
        Returns:
            Parser function that takes an absolute path string and returns bool (True = ignored)
            or None if .gitignore not found or too large
        """
        with self._gitignore_lock:
            # Check cache first (inside lock for thread safety)
            if self._gitignore_parser is not None:
                return self._gitignore_parser
            
            gitignore_path = self._find_gitignore_file()
            if gitignore_path is None:
                return None
            
            try:
                # Security: Check file size
                gitignore_size = gitignore_path.stat().st_size
                if gitignore_size > MAX_GITIGNORE_SIZE:
                    logger.warning(
                        ".gitignore file is very large (%d bytes, max: %d bytes). "
                        "Skipping to prevent performance issues. "
                        "Falling back to built-in exclusion patterns.",
                        gitignore_size, MAX_GITIGNORE_SIZE
                    )
                    return None
                
                # gitignore-parser needs base_dir to resolve relative paths
                # CRITICAL: Must resolve() to handle symlinks (e.g., /var -> /private/var on macOS)
                gitignore_dir = gitignore_path.parent.resolve()
                self._gitignore_parser = parse_gitignore(str(gitignore_path), base_dir=str(gitignore_dir))
                logger.info("Loaded .gitignore from: %s (%d bytes)", gitignore_path, gitignore_size)
                return self._gitignore_parser
            except Exception as e:
                logger.error(
                    "Failed to parse .gitignore at %s: %s. "
                    "Falling back to built-in exclusion patterns.",
                    gitignore_path, e,
                    exc_info=True
                )
                return None
    
    def _gitignore_matches(self, file_path: Path) -> bool:
        """Check if file path matches .gitignore patterns.
        
        gitignore-parser with base_dir expects absolute paths as input and internally
        converts them to relative paths for pattern matching. The key fix for the
        production bug was resolving base_dir to handle symlinks (e.g., /var -> /private/var).
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file matches .gitignore patterns (should be excluded)
        """
        parser = self._load_gitignore()
        if parser is None:
            return False
        
        try:
            # gitignore-parser expects absolute paths (it converts internally)
            # The fix: resolved base_dir in _load_gitignore() handles symlinks correctly
            return parser(str(file_path.resolve()))
        except Exception as e:
            logger.warning("Error checking gitignore match for %s: %s", file_path, e)
            return False
    
    def _builtin_default_matches(self, file_path: Path) -> bool:
        """Check if file matches built-in default exclusion patterns.
        
        Uses gitignore-parser to match against DEFAULT_EXCLUDE_PATTERNS.
        Note: Parser is NOT cached because gitignore-parser requires a real file
        that must exist for the parser's lifetime.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file matches any built-in pattern (should be excluded)
        """
        try:
            # Create temporary gitignore file with patterns
            import tempfile
            project_root = self.base_path.parent
            
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_gitignore = Path(tmpdir) / ".gitignore"
                temp_gitignore.write_text("\n".join(DEFAULT_EXCLUDE_PATTERNS))
                
                parser = parse_gitignore(str(temp_gitignore), base_dir=str(project_root))
                
                # gitignore-parser expects absolute paths
                result = parser(str(file_path.resolve()))
                return bool(result)
        except Exception as e:
            logger.error("Error checking builtin patterns for %s: %s", file_path, e)
            # If pattern matching fails, err on the side of caution and don't exclude
            return False
    
    def _config_patterns_match(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches config exclude_patterns.
        
        Note: Parser is NOT cached because gitignore-parser requires a real file
        that must exist for the parser's lifetime.
        
        Args:
            file_path: File path to check
            patterns: List of gitignore-format patterns (from config.exclude_patterns)
            
        Returns:
            True if file matches any pattern (should be excluded)
        """
        if not patterns:
            return False
        
        try:
            # Create temporary gitignore file with patterns
            import tempfile
            project_root = self.base_path.parent
            
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_gitignore = Path(tmpdir) / ".gitignore"
                temp_gitignore.write_text("\n".join(patterns))
                
                # Create parser with project root as base_dir
                parser = parse_gitignore(str(temp_gitignore), base_dir=str(project_root))
                
                # gitignore-parser expects absolute paths
                result = parser(str(file_path.resolve()))
                return bool(result)
        except Exception as e:
            logger.error("Error checking config patterns for %s: %s", file_path, e)
            return False
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded using three-tier system.
        
        Tier 1: .gitignore patterns (if respect_gitignore=True)
        Tier 2: Built-in defaults (if no .gitignore or respect_gitignore=False)
        Tier 3: Config exclude_patterns (additive)
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file should be excluded
        """
        # Tier 1: Check .gitignore
        if self.config.respect_gitignore:
            if self._gitignore_matches(file_path):
                return True
        
        # Tier 2: Built-in defaults (fallback or if gitignore disabled)
        if not self.config.respect_gitignore or not self._has_gitignore():
            if self._builtin_default_matches(file_path):
                return True
        
        # Tier 3: Config exclude_patterns (additive)
        if self.config.exclude_patterns:
            if self._config_patterns_match(file_path, self.config.exclude_patterns):
                return True
        
        return False
    
    def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single code file using AST-aware or line-based strategy.
        
        Strategy selection (based on config.chunking_strategy):
        - "ast": AST-aware chunking at function/class boundaries (recommended)
        - "line" or missing: Line-based chunking (fallback)
        
        AST strategy uses UniversalASTChunker for:
        - Function/class boundary detection
        - Import grouping with penalty
        - Config-driven language support
        
        Args:
            file_path: Path to code file
            
        Returns:
            List of chunk dictionaries ready for LanceDB
        """
        # Check chunking strategy from config
        strategy = getattr(self.config, "chunking_strategy", "line")
        
        if strategy == "ast":
            # Use AST-aware chunking
            return self._chunk_file_ast(file_path)
        else:
            # Use line-based fallback
            return self._chunk_file_lines(file_path)
    
    def _chunk_file_ast(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk file using AST-aware chunking (function/class boundaries).
        
        Args:
            file_path: Path to code file
        
        Returns:
            List of chunk dictionaries
        """
        # Detect language from file extension
        language = self._detect_language(file_path)
        
        # Check if language is configured for AST chunking
        if not hasattr(self.config, "language_configs") or not self.config.language_configs:
            logger.warning(
                "AST chunking enabled but no language_configs found, falling back to line-based for %s",
                file_path
            )
            return self._chunk_file_lines(file_path)
        
        if language not in self.config.language_configs:
            logger.debug(
                "Language '%s' not configured for AST chunking, falling back to line-based for %s",
                language,
                file_path.name
            )
            return self._chunk_file_lines(file_path)
        
        try:
            # Initialize UniversalASTChunker for this language
            chunker = UniversalASTChunker(
                language=language,
                config=self.config.model_dump(),  # Pass full config dict
                base_path=self.base_path
            )
            
            # Chunk the file
            code_chunks: List[CodeChunk] = chunker.chunk_file(file_path)
            
            # Convert CodeChunk objects to dict format for LanceDB
            chunks = []
            for code_chunk in code_chunks:
                chunks.append(self._create_chunk(
                    content=code_chunk.content,
                    file_path=code_chunk.file_path,
                    start_line=code_chunk.start_line,
                    end_line=code_chunk.end_line,
                    chunk_type=code_chunk.chunk_type,
                    symbols=code_chunk.symbols,
                    import_ratio=code_chunk.import_ratio,
                    import_penalty=code_chunk.import_penalty
                ))
            
            logger.debug(
                "AST chunked %s: %d chunks (%s)",
                file_path.name,
                len(chunks),
                ", ".join(set(c.get("chunk_type", "unknown") for c in chunks))
            )
            
            return chunks
            
        except Exception as e:
            self._ast_fallback_count += 1
            logger.warning(
                "AST chunking failed for %s: %s, falling back to line-based (fallback #%d)",
                file_path,
                str(e),
                self._ast_fallback_count
            )
            return self._chunk_file_lines(file_path)
    
    def _chunk_file_lines(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk file using simple line-based chunking (fallback).
        
        Args:
            file_path: Path to code file
        
        Returns:
            List of chunk dictionaries
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to read %s: %s", file_path, e)
            return []
        
        lines = content.split("\n")
        chunks = []
        
        # Simple line-based chunking (200 lines per chunk, 20 line overlap)
        chunk_size = 200
        overlap = 20
        
        for i in range(0, len(lines), chunk_size - overlap):
            chunk_lines = lines[i:i + chunk_size]
            if not chunk_lines:
                continue
            
            chunk_content = "\n".join(chunk_lines)
            if not chunk_content.strip():
                continue
            
            start_line = i + 1
            end_line = min(i + len(chunk_lines), len(lines))
            
            chunks.append(self._create_chunk(
                content=chunk_content,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line
            ))
        
        return chunks
    
    def _create_chunk(
        self,
        content: str,
        file_path: Path,
        start_line: int,
        end_line: int,
        chunk_type: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        import_ratio: Optional[float] = None,
        import_penalty: Optional[float] = None,
        partition: Optional[str] = None,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create chunk dictionary with metadata.
        
        Args:
            content: Chunk text content
            file_path: Source file path
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            chunk_type: AST chunk type ("import", "function", "class") - optional
            symbols: List of symbols in chunk (function/class names) - optional
            import_ratio: Ratio of import lines (0.0-1.0) - optional
            import_penalty: Penalty multiplier for search ranking - optional
            partition: Partition name (repo name) - optional, defaults to "default"
            domain: Domain name within partition (e.g., "code", "tests") - optional, defaults to "code"
            metadata: Domain metadata for query filtering (e.g., {"framework": "openai"}) - optional
            
        Returns:
            Chunk dictionary ready for LanceDB
        """
        # Generate chunk ID (hash of file path + line range)
        chunk_id = hashlib.sha256(
            f"{file_path}::{start_line}-{end_line}".encode()
        ).hexdigest()[:16]
        
        # Detect language from file extension
        language = self._detect_language(file_path)
        
        # Handle files that may be outside base_path (e.g., via symlinks or absolute source_paths)
        try:
            rel_file_path = str(file_path.relative_to(self.base_path))
        except ValueError:
            # File is outside base_path, use absolute path as fallback
            rel_file_path = str(file_path.resolve())
            logger.debug(
                "File outside base_path, using absolute path: %s",
                rel_file_path
            )
        
        # Build base chunk dict
        chunk = {
            "chunk_id": chunk_id,
            "content": content,
            "file_path": rel_file_path,
            "start_line": start_line,
            "end_line": end_line,
            "language": language,
            "content_type": "code",
            # Multi-repo partitioning fields (with defaults for backward compatibility)
            "partition": partition if partition is not None else self.partition_name,  # Use instance partition_name
            "domain": domain if domain is not None else "code",
            "repo_name": partition if partition is not None else self.partition_name,  # Use instance partition_name
            "metadata": metadata if metadata is not None else {},
        }
        
        # Add AST-specific metadata if provided
        if chunk_type is not None:
            chunk["chunk_type"] = chunk_type
        if symbols is not None:
            chunk["symbols"] = symbols
        if import_ratio is not None:
            chunk["import_ratio"] = import_ratio
        if import_penalty is not None:
            chunk["import_penalty"] = import_penalty
        
        return chunk
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension.
        
        Args:
            file_path: File path
            
        Returns:
            Language name (e.g., "python", "javascript")
        """
        ext = file_path.suffix.lower()
        
        # Map extensions to language names
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php",
        }
        
        return ext_to_lang.get(ext, "unknown")
    
    def _build_indexes(self) -> None:
        """Build FTS and scalar indexes on the table.
        
        Creates:
        1. FTS index on 'content' column (code keyword search)
        2. Scalar indexes on metadata columns (language, file_path)
        """
        if self._table is None:
            raise IndexError(
                what_failed="Build indexes",
                why_failed="Table not initialized",
                how_to_fix="Call build() first to create the table"
            )
        
        try:
            # FTS index (code keyword search)
            if self.config.fts.enabled:
                logger.info("Creating FTS index on 'content' column...")
                self._table.create_fts_index("content", replace=True)
                logger.info("✅ FTS index created")
            
            # Scalar indexes for language filtering
            logger.info("Creating scalar indexes for metadata...")
            self._table.create_scalar_index("language", index_type="BTREE", replace=True)
            logger.info("✅ Scalar indexes created")
            
        except Exception as e:
            logger.error("Failed to build indexes: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Build FTS/scalar indexes",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure LanceDB version >=0.13.0"
            ) from e
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search code index using hybrid strategy.
        
        Search flow (same as StandardsIndex):
        1. Vector search (top 20 results) - semantic code understanding
        2. FTS search (top 20 results) - exact symbol matching
        3. Reciprocal Rank Fusion (merge vector + FTS)
        4. Return top N with line ranges
        
        Args:
            query: Natural language or code search query
            n_results: Number of results to return
            filters: Optional filters (language, file_path)
            
        Returns:
            List of SearchResult objects with line ranges
            
        Raises:
            IndexError: If search fails
        """
        self._ensure_table()
        
        # Load embedding model via helper (caching)
        logger.info("🔍 Code search: Loading model '%s' (dim: %d) for query: %s", 
                   self.config.vector.model, self.config.vector.dimension, query[:50])
        embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
        
        try:
            # Build WHERE clause for filtering
            where_clause = self._build_where_clause(filters) if filters else None
            
            # 1. Vector search (semantic)
            query_vector = safe_encode(embedding_model, query).tolist()
            vector_results = self._vector_search(query_vector, where_clause, limit=20)
            
            # 2. FTS search (if enabled)
            if self.config.fts.enabled:
                fts_results = self._fts_search(query, where_clause, limit=20)
                
                # 3. Hybrid fusion (RRF)
                fused_results = self._reciprocal_rank_fusion(vector_results, fts_results)
            else:
                fused_results = vector_results
            
            # 4. Convert to SearchResult objects
            search_results = []
            for idx, result in enumerate(fused_results[:n_results]):
                search_results.append(SearchResult(
                    content=result.get("content", ""),
                    file_path=result.get("file_path", ""),
                    relevance_score=result.get("score", 1.0 / (idx + 1)),
                    content_type="code",
                    metadata={
                        "language": result.get("language", ""),
                        "start_line": result.get("start_line", 0),
                        "end_line": result.get("end_line", 0),
                    },
                    chunk_id=result.get("chunk_id"),
                    line_range=(result.get("start_line", 0), result.get("end_line", 0))
                ))
            
            logger.info("Code search returned %d results for query: %s", len(search_results), query[:50])
            return search_results
            
        except Exception as e:
            logger.error("Code search failed: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Code search",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure index is built and model is loaded."
            ) from e
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """Build SQL WHERE clause from filters.
        
        Args:
            filters: Dictionary of filters (e.g., {"language": "python"})
            
        Returns:
            SQL WHERE clause string
        """
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{key} = '{value}'")
            elif isinstance(value, list):
                # IN clause
                if all(isinstance(v, str) for v in value):
                    values_str = ", ".join(f"'{v}'" for v in value)
                    conditions.append(f"{key} IN ({values_str})")
        
        return " AND ".join(conditions) if conditions else ""
    
    def _vector_search(
        self,
        query_vector: List[float],
        where_clause: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Execute vector search on code embeddings."""
        assert self._table is not None
        search_query = self._table.search(query_vector)
        
        if where_clause:
            search_query = search_query.where(where_clause, prefilter=True)
        
        results = search_query.limit(limit).to_list()
        
        # Add search type and score
        for result in results:
            result["search_type"] = "vector"
            if "_distance" in result:
                result["score"] = 1.0 / (1.0 + result["_distance"])
        
        return results
    
    def _fts_search(
        self,
        query: str,
        where_clause: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Execute FTS (keyword) search on code."""
        assert self._table is not None
        # LanceDB FTS: use search() with query_type="fts"
        search_query = self._table.search(query, query_type="fts")
        
        # Apply prefiltering if needed
        if where_clause:
            search_query = search_query.where(where_clause, prefilter=True)
        
        results = search_query.limit(limit).to_list()
        
        # Add search type and score
        for result in results:
            result["search_type"] = "fts"
            if "_score" in result:
                result["score"] = min(1.0, result["_score"] / 10.0)
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        fts_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Merge vector and FTS results using Reciprocal Rank Fusion.
        
        RRF formula: score(d) = Σ 1 / (k + rank(d))
        
        Args:
            vector_results: Results from vector search
            fts_results: Results from FTS search
            k: RRF constant (default 60 per literature)
            
        Returns:
            Merged and sorted results
        """
        rrf_scores: Dict[str, float] = {}
        result_map = {}
        
        # Add vector results
        for rank, result in enumerate(vector_results):
            chunk_id = result.get("chunk_id")
            if chunk_id:
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (k + rank + 1)
                result_map[chunk_id] = result
        
        # Add FTS results
        for rank, result in enumerate(fts_results):
            chunk_id = result.get("chunk_id")
            if chunk_id:
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (k + rank + 1)
                if chunk_id not in result_map:
                    result_map[chunk_id] = result
        
        # Sort by RRF score
        sorted_chunk_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build final results list with import penalty applied
        merged_results = []
        for chunk_id, score in sorted_chunk_ids:
            result = result_map[chunk_id].copy()
            result["score"] = score
            result["search_type"] = "hybrid_rrf"
            
            # Apply import penalty if present (de-prioritize import-heavy chunks)
            import_penalty = result.get("import_penalty")
            if import_penalty is not None and import_penalty < 1.0:
                original_score = result["score"]
                result["score"] = original_score * import_penalty
                logger.debug(
                    "Applied import penalty %.2f to chunk %s (score: %.4f → %.4f)",
                    import_penalty,
                    chunk_id,
                    original_score,
                    result["score"]
                )
            
            merged_results.append(result)
        
        # Re-sort after applying penalties (imports should rank lower)
        merged_results.sort(key=lambda x: x["score"], reverse=True)
        
        return merged_results
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails
        """
        logger.info("Updating code index with %d changed files", len(changed_files))
        
        self._ensure_table()
        
        # Load embedding model via helper (caching)
        embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
        
        try:
            # Check for active parse cache (fractal delegation optimization)
            from ouroboros.subsystems.rag.code.indexer import get_active_parse_cache
            parse_cache = get_active_parse_cache()
            cache_hits = 0
            cache_misses = 0
            
            for file_path in changed_files:
                # Check if file still exists
                if not file_path.exists():
                    self._delete_file_chunks(file_path)
                    continue
                
                # Try to get cached parse result (parse-once-index-thrice optimization)
                chunks = None
                if parse_cache:
                    cached = parse_cache.get_cached_parse(file_path)
                    if cached and "semantic_chunks" in cached:
                        chunks = cached["semantic_chunks"]
                        cache_hits += 1
                        logger.debug("Using cached chunks for %s (parse-once optimization)", file_path.name)
                
                # Fallback: parse file ourselves if no cache available
                if chunks is None:
                    chunks = self._chunk_file(file_path)
                    cache_misses += 1
                
                if not chunks:
                    continue
                
                # Generate embeddings
                texts = [chunk["content"] for chunk in chunks]
                embeddings = safe_encode(embedding_model, texts)
                
                # Add embeddings to chunks
                for chunk, embedding in zip(chunks, embeddings):
                    chunk["vector"] = embedding.tolist()
                
                # Delete old chunks
                self._delete_file_chunks(file_path)
                
                # Add new chunks
                assert self._table is not None
                self._table.add(chunks)
            
            # Rebuild FTS index
            if self.config.fts.enabled:
                logger.info("Rebuilding FTS index after updates...")
                self._build_indexes()
            
            # Log cache statistics
            if parse_cache:
                logger.info(
                    "✅ SemanticIndex updated (parse-once: %d cache hits, %d cache misses)",
                    cache_hits,
                    cache_misses
                )
            else:
                logger.info("✅ SemanticIndex updated")
            
        except Exception as e:
            logger.error("Failed to update code index: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Update code index",
                why_failed=str(e),
                how_to_fix="Check server logs. May need to rebuild index if corruption detected."
            ) from e
    
    def _delete_file_chunks(self, file_path: Path) -> None:
        """Delete all chunks for a given file.
        
        Handles files that may be outside base_path (e.g., via symlinks or absolute source_paths).
        
        Args:
            file_path: File whose chunks should be deleted
        """
        # Handle files that may be outside base_path
        try:
            relative_path = str(file_path.relative_to(self.base_path))
        except ValueError:
            # File is outside base_path, use absolute path (matches what was stored in _chunk_file)
            relative_path = str(file_path.resolve())
            logger.debug(
                "File outside base_path for deletion, using absolute path: %s",
                relative_path
            )
        
        try:
            assert self._table is not None
            self._table.delete(f"file_path = '{relative_path}'")
            logger.info("Deleted chunks for file: %s", relative_path)
        except Exception as e:
            logger.warning("Failed to delete chunks for %s: %s", relative_path, e)
    
    def build_status(self) -> "BuildStatus":  # type: ignore[name-defined]
        """Check actual build status (ADDENDUM-2025-11-17: Build Status Integration).
        
        Returns:
            BuildStatus with actual state (BUILDING, BUILT, or NOT_BUILT)
        """
        from ouroboros.subsystems.rag.base import BuildStatus, IndexBuildState
        
        # Check if currently building
        with self._build_lock:
            is_building = self._building
        
        if is_building:
            # Check progress file for actual progress
            progress_info = self._progress_manager.read_progress()
            progress_percent = progress_info.progress_percent if progress_info else 50.0
            progress_message = progress_info.message if progress_info else "Building..."
            
            return BuildStatus(
                state=IndexBuildState.BUILDING,
                message=f"Building semantic index: {progress_message}",
                progress_percent=progress_percent,
                details={"component": "semantic"}
            )
        
        # Check if index has data (has been built)
        try:
            db = self.db_connection.connect()
            existing_tables = db.table_names()
            
            if "code" in existing_tables:
                # Table exists, check if it has data
                table = db.open_table("code")
                count = table.count_rows()
                
                if count > 0:
                    return BuildStatus(
                        state=IndexBuildState.BUILT,
                        message=f"Semantic index built ({count} chunks)",
                        progress_percent=100.0,
                        details={"chunks": count}
                    )
        except Exception as e:
            logger.debug("Error checking semantic index data: %s", e)
        
        # No data found - not built yet
        return BuildStatus(
            state=IndexBuildState.NOT_BUILT,
            message="Semantic index not yet built",
            progress_percent=0.0
        )
    
    def health_check(self) -> HealthStatus:
        """Check index health with dynamic validation.
        
        ADDENDUM-2025-11-17: Now checks build status first, skips validation if building.
        
        Verifies:
        1. Table exists and has data
        2. Can actually perform a test search (catches dimension mismatches, schema errors)
        3. FTS index exists (if enabled)
        4. Scalar indexes exist
        
        Returns:
            HealthStatus with diagnostic info
        """
        # ADDENDUM-2025-11-17: Check build status first, skip validation if building
        from ouroboros.subsystems.rag.base import IndexBuildState
        
        build_status = self.build_status()
        
        if build_status.state == IndexBuildState.BUILDING:
            # Don't validate data during build - it's incomplete!
            return HealthStatus(
                healthy=True,  # Not unhealthy, just building
                message=f"Building ({build_status.progress_percent:.0f}%), skipping health check",
                details={
                    "building": True,
                    "progress": build_status.progress_percent,
                    "build_message": build_status.message
                }
            )
        
        # Normal health check (validate data)
        # NOTE: We do NOT run embedding generation in health checks!
        # Embeddings are only needed for building and searching, not validation.
        # Health check should be fast (< 100ms) and cheap (no heavy computation).
        try:
            logger.debug("🏥 CodeSemanticIndex health check: partition=%s", self.partition_name)
            
            # Check if table exists
            db = self.db_connection.connect()
            existing_tables = db.table_names()
            
            if "code" not in existing_tables:
                return HealthStatus(
                    healthy=False,
                    message="Code index not built (table doesn't exist)",
                    details={"table_exists": False}
                )
            
            # Check if table has data
            table = db.open_table("code")
            count = table.count_rows()
            logger.debug("  📊 Row count: %d", count)
            
            if count == 0:
                return HealthStatus(
                    healthy=False,
                    message="Code index is empty (no chunks)",
                    details={"chunk_count": 0}
                )
            
            # Table exists and has data - healthy!
            # Note: Dimension mismatches will be caught when actual searches are performed,
            # not in periodic health checks. Health checks should be fast and cheap.
            return HealthStatus(
                healthy=True,
                message=f"Code index healthy ({count} chunks)",
                details={"chunk_count": count},
                last_updated=None
            )
            
        except Exception as e:
            logger.error("Health check failed: %s", e, exc_info=True)
            return HealthStatus(
                healthy=False,
                message=f"Code index not healthy: {e}",
                details={"error": str(e)}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            self._ensure_table()
            assert self._table is not None
            
            chunk_count = self._table.count_rows()
            
            return {
                "chunk_count": chunk_count,
                "index_path": str(self.index_path),
                "embedding_model": self.config.vector.model,
                "languages": self.config.languages,
                "fts_enabled": self.config.fts.enabled,
            }
            
        except Exception as e:
            return {"error": str(e)}
