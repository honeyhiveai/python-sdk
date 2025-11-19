"""GraphIndex container: Orchestrates AST extraction and graph traversal.

This module provides the main GraphIndex class that implements the BaseIndex
interface and coordinates:
1. AST extraction (parsing with tree-sitter)
2. Graph traversal (recursive CTEs in DuckDB)
3. DuckDB schema management
4. Index building and updates

Architecture:
- ASTExtractor: Handles tree-sitter parsing and data extraction
- GraphTraversal: Handles DuckDB queries (find_callers, search_ast, etc.)
- DuckDBConnection: Thread-safe database connection management

This is the internal implementation for CodeIndex graph operations.
Use CodeIndex (parent container) as the public interface.
"""

import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import GraphConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, IndexBuildState, SearchResult
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_health_check,
)
from ouroboros.subsystems.rag.utils.duckdb_helpers import DuckDBConnection
from ouroboros.utils.errors import ActionableError, IndexError

from .ast import ASTExtractor
from .traversal import GraphTraversal

logger = logging.getLogger(__name__)


class GraphIndex(BaseIndex):
    """Unified AST + Call graph index using DuckDB.
    
    Combines structural code search (AST) with call graph traversal in a single
    DuckDB database. Orchestrates AST extraction and graph queries.
    
    Schema (DuckDB):
    1. ast_nodes: Structural code elements (functions, classes, methods)
    2. symbols: Callable symbols for graph analysis
    3. relationships: Call relationships between symbols
    
    Components:
    - ASTExtractor: Parse code and extract AST/symbols/relationships
    - GraphTraversal: Query graph using recursive CTEs
    
    Methods:
    - build(): Extract AST and build graph from source code
    - search(): Search symbols by name (BaseIndex interface)
    - search_ast(): Structural code search by pattern
    - find_callers(): Who calls this symbol? (reverse lookup)
    - find_dependencies(): What does this symbol call? (forward lookup)
    - find_call_paths(): How does X reach Y? (path finding)
    """
    
    def __init__(
        self, 
        config: GraphConfig, 
        base_path: Path, 
        languages: Optional[List[str]] = None,
        code_config: Optional[Dict[str, Any]] = None,
        db_path: Optional[Path] = None
    ):
        """Initialize Graph Index.
        
        Args:
            config: GraphConfig from MCPConfig
            base_path: Base path for resolving relative paths
            languages: List of programming languages to support (e.g., ["python", "typescript"])
            code_config: Optional full CodeIndexConfig dict for AST config (contains language_configs)
            db_path: Optional explicit database path (defaults to base_path/.cache/indexes/code/graph.duckdb)
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Use provided languages or default to Python
        if languages is None:
            languages = ["python"]
            logger.warning("No languages specified for GraphIndex, defaulting to ['python']")
        
        self.languages = languages
        
        # Resolve database path: explicit path or sane default
        if db_path is not None:
            self.db_path = db_path
        else:
            # Sane default: base_path/.cache/indexes/code/graph.duckdb (backward compatible)
            self.db_path = base_path / ".cache" / "indexes" / "code" / "graph.duckdb"
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection and components
        self.db_connection = DuckDBConnection(self.db_path)
        
        # Log ASTExtractor initialization parameters for debugging
        logger.info(
            "Initializing ASTExtractor: languages=%s, base_path=%s, code_config type=%s",
            languages,
            base_path,
            type(code_config).__name__ if code_config else None
        )
        
        self.ast_extractor = ASTExtractor(
            languages=languages,
            base_path=base_path,
            config=code_config  # Pass full config for language_configs extraction
        )
        self.traversal = GraphTraversal(self.db_connection)
        
        # Initialize schema
        self._initialize_schema()
        
        # Store source paths for targeted rebuilds (populated during build())
        self.source_paths: List[Path] = []
        
        # Build status tracking (ADDENDUM-2025-11-17: Build Status Integration)
        self._building = False
        self._build_lock = threading.Lock()
        
        # Register components for cascading health checks (fractal pattern)
        # See: specs/2025-11-08-cascading-health-check-architecture/
        self.components: Dict[str, ComponentDescriptor] = {
            "ast": ComponentDescriptor(
                name="ast",
                provides=["ast_nodes"],
                capabilities=["search_ast"],
                health_check=self._check_ast_health,
                build_status_check=self._stub_build_status,
                rebuild=self._rebuild_ast,
                dependencies=[],
            ),
            "graph": ComponentDescriptor(
                name="graph",
                provides=["symbols", "relationships"],
                capabilities=["find_callers", "find_dependencies", "find_call_paths"],
                health_check=self._check_graph_health,
                build_status_check=self._stub_build_status,
                rebuild=self._rebuild_graph,
                dependencies=[],
            ),
        }
        
        logger.info("GraphIndex initialized with component registry (ast, graph)")
    
    def _initialize_schema(self):
        """Create DuckDB tables and indexes if they don't exist.
        
        Creates three tables:
        1. ast_nodes: Structural code elements
        2. symbols: Callable code symbols (graph nodes)
        3. relationships: Call relationships (graph edges)
        
        Raises:
            IndexError: If schema creation fails
        """
        try:
            conn = self.db_connection.get_connection()
            
            # Table 1: AST nodes (structural search)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ast_nodes (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    symbol_name TEXT,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES ast_nodes(id)
                )
            """)
            
            # Indexes for AST queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_file_path ON ast_nodes(file_path)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_node_type ON ast_nodes(node_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_language ON ast_nodes(language)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_symbol_name ON ast_nodes(symbol_name)
            """)
            
            # Table 2: Symbols (call graph nodes)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    language TEXT NOT NULL
                )
            """)
            
            # Indexes for symbol queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols(type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_file_path ON symbols(file_path)
            """)
            
            # Table 3: Relationships (call graph edges)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY,
                    from_symbol_id INTEGER NOT NULL,
                    to_symbol_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    FOREIGN KEY (from_symbol_id) REFERENCES symbols(id),
                    FOREIGN KEY (to_symbol_id) REFERENCES symbols(id)
                )
            """)
            
            # Indexes for graph traversal
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_symbol_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_symbol_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type)
            """)
            
            logger.info("✅ DuckDB schema initialized (ast_nodes, symbols, relationships)")
            
            # Migration: Add multi-repo partitioning columns if they don't exist
            try:
                # Add partition, domain, repo_name columns to ast_nodes
                conn.execute("""
                    ALTER TABLE ast_nodes ADD COLUMN IF NOT EXISTS partition VARCHAR DEFAULT 'default'
                """)
                conn.execute("""
                    ALTER TABLE ast_nodes ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'code'
                """)
                conn.execute("""
                    ALTER TABLE ast_nodes ADD COLUMN IF NOT EXISTS repo_name VARCHAR DEFAULT 'default'
                """)
                conn.execute("""
                    ALTER TABLE ast_nodes ADD COLUMN IF NOT EXISTS metadata_json VARCHAR DEFAULT '{}'
                """)
                
                # Add partition, domain, repo_name columns to symbols
                conn.execute("""
                    ALTER TABLE symbols ADD COLUMN IF NOT EXISTS partition VARCHAR DEFAULT 'default'
                """)
                conn.execute("""
                    ALTER TABLE symbols ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'code'
                """)
                conn.execute("""
                    ALTER TABLE symbols ADD COLUMN IF NOT EXISTS repo_name VARCHAR DEFAULT 'default'
                """)
                conn.execute("""
                    ALTER TABLE symbols ADD COLUMN IF NOT EXISTS metadata_json VARCHAR DEFAULT '{}'
                """)
                
                # Add caller_partition, callee_partition columns to relationships
                conn.execute("""
                    ALTER TABLE relationships ADD COLUMN IF NOT EXISTS caller_partition VARCHAR DEFAULT 'default'
                """)
                conn.execute("""
                    ALTER TABLE relationships ADD COLUMN IF NOT EXISTS callee_partition VARCHAR DEFAULT 'default'
                """)
                
                # Create indexes on partition/domain columns for efficient filtering
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ast_partition_domain ON ast_nodes(partition, domain)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_symbols_partition_domain ON symbols(partition, domain)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_relationships_partitions ON relationships(caller_partition, callee_partition)
                """)
                
                logger.info("✅ Multi-repo partitioning columns added/verified")
                
            except Exception as migration_error:
                logger.warning(
                    "⚠️ Failed to add multi-repo columns (may already exist): %s",
                    str(migration_error)
                )
            
        except Exception as e:
            raise IndexError(
                what_failed="Initialize DuckDB schema",
                why_failed=str(e),
                how_to_fix="Check server logs. Database may be corrupted or locked."
            ) from e
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build graph index from source paths.
        
        Implementation:
        1. Parse files with tree-sitter (via ASTExtractor)
        2. Extract AST nodes, symbols, and relationships
        3. Insert into DuckDB tables
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building graph index from %d source paths", len(source_paths))
        
        # Set building flag (ADDENDUM-2025-11-17: Build Status Integration)
        with self._build_lock:
            self._building = True
        
        try:
            # Store source paths for targeted rebuilds
            self.source_paths = source_paths
            
            # Force rebuild: Delete database file and reinitialize
            # This is simpler, safer, and more reliable than trying to DELETE with FK constraints
            if force:
                logger.info("Deleting existing database file (force rebuild)")
                
                # Close existing connection
                self.db_connection.close()
                
                # Delete the database file
                if self.db_path.exists():
                    self.db_path.unlink()
                    logger.info("✅ Deleted database file: %s", self.db_path)
                
                # Reinitialize connection and schema
                from ouroboros.subsystems.rag.utils.duckdb_helpers import DuckDBConnection
                self.db_connection = DuckDBConnection(self.db_path)
                self._initialize_schema()
                logger.info("✅ Reinitialized database with fresh schema")
            
            conn = self.db_connection.get_connection()
            
            # Check if index already has data
            ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
            symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            
            if ast_count > 0 and symbol_count > 0 and not force:
                logger.info("Graph index already exists with %d AST nodes and %d symbols. Use force=True to rebuild.",
                           ast_count, symbol_count)
                return
            
            # Extract data from source files
            ast_nodes, symbols, relationships = self._extract_all_data(source_paths)
            
            if not ast_nodes and not symbols:
                raise ActionableError(
                    what_failed="Build graph index",
                    why_failed="No AST nodes or symbols found in source paths",
                    how_to_fix=f"Check that source paths contain code files for languages: {self.languages}. Ensure tree-sitter-languages is installed."
                )
            
            # Insert AST nodes
            if ast_nodes:
                logger.info("Inserting %d AST nodes into DuckDB...", len(ast_nodes))
                # DuckDB executemany for bulk insert
                conn.executemany(
                    "INSERT INTO ast_nodes (id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    ast_nodes
                )
            
            # Insert symbols
            if symbols:
                logger.info("Inserting %d symbols into DuckDB...", len(symbols))
                conn.executemany(
                    "INSERT INTO symbols (id, name, type, file_path, line_number, language) VALUES (?, ?, ?, ?, ?, ?)",
                    symbols
                )
            
            # Insert relationships
            if relationships:
                logger.info("Inserting %d relationships into DuckDB...", len(relationships))
                conn.executemany(
                    "INSERT INTO relationships (id, from_symbol_id, to_symbol_id, relationship_type) VALUES (?, ?, ?, ?)",
                    relationships
                )
            
            # CRITICAL: Checkpoint to flush WAL and make data visible
            # Without this, data stays in WAL and new connections may see stale data
            logger.info("Checkpointing to flush WAL...")
            conn.execute("CHECKPOINT")
            
            logger.info("✅ Graph index built: %d AST nodes, %d symbols, %d relationships",
                       len(ast_nodes), len(symbols), len(relationships))
        finally:
            # Clear building flag (ADDENDUM-2025-11-17: Build Status Integration)
            with self._build_lock:
                self._building = False
    
    def _extract_all_data(self, source_paths: List[Path]) -> tuple:
        """Extract AST nodes, symbols, and relationships from source code.
        
        Uses two-pass extraction to ensure cross-file relationships work correctly:
        1. Pass 1: Extract all symbols from all files (build complete symbol_map)
        2. Pass 2: Extract relationships using complete symbol_map
        
        Args:
            source_paths: Paths to scan for code files
            
        Returns:
            Tuple of (ast_nodes, symbols, relationships)
        """
        all_ast_nodes = []
        all_symbols = []
        all_relationships = []
        
        file_extensions = self.ast_extractor.get_file_extensions()
        
        # CRITICAL FIX: Query for max IDs to avoid collisions in multi-partition builds
        # In multi-partition scenarios, multiple partitions share the same database.
        # Each partition build must start IDs after existing data to prevent PK violations.
        conn = self.db_connection.get_connection()
        try:
            max_ast_id = conn.execute("SELECT COALESCE(MAX(id), -1) FROM ast_nodes").fetchone()[0]
            max_symbol_id = conn.execute("SELECT COALESCE(MAX(id), -1) FROM symbols").fetchone()[0]
            max_rel_id = conn.execute("SELECT COALESCE(MAX(id), -1) FROM relationships").fetchone()[0]
            
            ast_node_id = max_ast_id + 1
            symbol_id = max_symbol_id + 1
            rel_id = max_rel_id + 1
            
            logger.info("Starting ID generation from: ast_node=%d, symbol=%d, relationship=%d",
                       ast_node_id, symbol_id, rel_id)
        except Exception as e:
            logger.error("Failed to query max IDs (will start from 0): %s", e)
            ast_node_id = 0
            symbol_id = 0
            rel_id = 0
        
        # Collect all files to process
        files_to_process = []
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            if resolved_path.is_file():
                if resolved_path.suffix in file_extensions:
                    files_to_process.append(resolved_path)
            else:
                for ext in file_extensions:
                    for code_file in resolved_path.rglob(f"*{ext}"):
                        if self.ast_extractor.should_skip_path(code_file):
                            continue
                        files_to_process.append(code_file)
        
        # PASS 1: Extract AST nodes and symbols from ALL files
        # This builds a complete symbol_map before relationship extraction
        symbol_map = {}
        parsed_trees = []  # Cache parsed trees for pass 2
        
        logger.info("Pass 1: Extracting symbols from %d files...", len(files_to_process))
        
        for file_path in files_to_process:
            language = self.ast_extractor.detect_language(file_path)
            if not language:
                continue
            
            try:
                self.ast_extractor.ensure_parser(language)
                
                # Read and parse file
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_bytes = f.read().encode('utf-8')
                
                parser = self.ast_extractor._parsers[language]
                tree = parser.parse(code_bytes)
                root_node = tree.root_node
                
                # Extract AST nodes
                ast_nodes = self.ast_extractor._extract_ast_nodes(
                    root_node, str(file_path), language, ast_node_id
                )
                
                # Extract symbols
                symbols = self.ast_extractor._extract_symbols(
                    root_node, str(file_path), language, symbol_id, code_bytes
                )
                
                # Update symbol_map
                for symbol in symbols:
                    sym_id, name, _, sym_file, _, _ = symbol
                    symbol_map[(sym_file, name)] = sym_id
                
                # Store for pass 2
                all_ast_nodes.extend(ast_nodes)
                all_symbols.extend(symbols)
                parsed_trees.append((file_path, root_node, language, code_bytes))
                
                # Update IDs
                if ast_nodes:
                    ast_node_id = max(node[0] for node in ast_nodes) + 1
                if symbols:
                    symbol_id = max(sym[0] for sym in symbols) + 1
                
                logger.debug("Pass 1: %s - %d AST nodes, %d symbols",
                            file_path.name, len(ast_nodes), len(symbols))
                
            except Exception as e:
                logger.warning("Failed to parse %s: %s", file_path, e, exc_info=True)
                continue
        
        logger.info("Pass 1 complete: %d symbols extracted", len(all_symbols))
        
        # PASS 2: Extract relationships using complete symbol_map
        logger.info("Pass 2: Extracting relationships...")
        
        for file_path, root_node, language, code_bytes in parsed_trees:
            try:
                relationships = self.ast_extractor._extract_relationships(
                    root_node, str(file_path), language, rel_id, symbol_map, code_bytes
                )
                
                all_relationships.extend(relationships)
                
                # Update IDs
                if relationships:
                    rel_id = max(rel[0] for rel in relationships) + 1
                
                logger.debug("Pass 2: %s - %d relationships",
                            file_path.name, len(relationships))
                
            except Exception as e:
                logger.warning("Failed to extract relationships from %s: %s", file_path, e)
                continue
        
        logger.info("✅ Extracted: %d AST nodes, %d symbols, %d relationships",
                   len(all_ast_nodes), len(all_symbols), len(all_relationships))
        
        return all_ast_nodes, all_symbols, all_relationships
    
    # ========================================================================
    # BaseIndex Interface Methods
    # ========================================================================
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search symbols by name (BaseIndex interface).
        
        This is a basic symbol search for BaseIndex compatibility.
        For graph queries, use find_callers/find_dependencies/find_call_paths.
        For structural queries, use search_ast.
        
        Args:
            query: Symbol name or pattern to search
            n_results: Max results to return
            filters: Optional filters (type, file_path, language)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            IndexError: If search fails
        """
        try:
            # Delegate to traversal's symbol search
            results = self.traversal.search_symbols(query, n_results, filters)
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    content=result["content"],
                    file_path=result["file_path"],
                    relevance_score=1.0,
                    content_type="code",
                    metadata={
                        "language": result["language"],
                        "symbol_type": result["type"],
                        "line_number": result["line_number"],
                    },
                    chunk_id=str(result["id"]),
                    line_range=(result["line_number"], result["line_number"])
                ))
            
            return search_results
            
        except Exception as e:
            logger.error("Failed to search: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Search symbols",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def update(self, file_paths: List[Path]) -> None:
        """Update index for changed files.
        
        GraphIndex has 2 sub-components (fractal pattern):
        1. AST component: ast_nodes table 
        2. Graph component: symbols + relationships tables
        
        This method delegates incremental updates to BOTH sub-components,
        using the parse cache (if active) to avoid parsing twice.
        
        Fractal Delegation Pattern:
            - Checks for active parse cache via get_active_parse_cache()
            - For each file: parse once, update AST component, update graph component
            - Falls back to self-parsing if no cache available
        
        Args:
            file_paths: Paths to files that changed
        """
        if not file_paths:
            return
        
        logger.info("GraphIndex.update() updating %d files (AST + graph components)", len(file_paths))
        
        # Check for parse cache (fractal delegation pattern)
        from ouroboros.subsystems.rag.code.indexer import get_active_parse_cache
        parse_cache = get_active_parse_cache()
        
        cache_hits = 0
        cache_misses = 0
        files_updated = 0
        files_failed = 0
        
        conn = self.db_connection.get_connection()
        
        # Track IDs for new insertions
        try:
            max_ast_id = conn.execute("SELECT MAX(id) FROM ast_nodes").fetchone()[0] or 0
            max_symbol_id = conn.execute("SELECT MAX(id) FROM symbols").fetchone()[0] or 0
            max_rel_id = conn.execute("SELECT MAX(id) FROM relationships").fetchone()[0] or 0
        except Exception as e:
            logger.error("Failed to get max IDs: %s", str(e))
            max_ast_id = 0
            max_symbol_id = 0
            max_rel_id = 0
        
        ast_node_id = max_ast_id + 1
        symbol_id = max_symbol_id + 1
        rel_id = max_rel_id + 1
        
        # Build symbol map for relationship extraction
        # For incremental updates, we need the FULL symbol map (not just this file)
        symbol_map = {}
        try:
            all_symbols = conn.execute("SELECT id, file_path, name FROM symbols").fetchall()
            for sym_id, file_path, name in all_symbols:
                symbol_map[(file_path, name)] = sym_id
        except Exception as e:
            logger.warning("Failed to load symbol map: %s", str(e))
        
        for file_path in file_paths:
            try:
                # Skip if file doesn't exist (deleted)
                if not file_path.exists():
                    logger.info("File deleted, removing from index: %s", file_path)
                    self._delete_file_data(conn, file_path)
                    files_updated += 1
                    continue
                
                # Try to get cached parse result (parse-once optimization)
                ast_nodes = None
                graph_data = None
                
                if parse_cache:
                    cached = parse_cache.get_cached_parse(file_path)
                    if cached and "ast_nodes" in cached and "graph_data" in cached:
                        ast_nodes = cached["ast_nodes"]
                        graph_data = cached["graph_data"]
                        cache_hits += 1
                        logger.debug("Using cached parse for %s (AST + graph)", file_path.name)
                
                # Fallback: parse file ourselves if no cache
                if ast_nodes is None or graph_data is None:
                    language = self.ast_extractor.detect_language(file_path)
                    if not language:
                        logger.warning("Unknown language for %s, skipping", file_path)
                        files_failed += 1
                        continue
                    
                    self.ast_extractor.ensure_parser(language)
                    
                    with open(file_path, 'rb') as f:
                        code_bytes = f.read()
                    
                    parser = self.ast_extractor._parsers[language]
                    tree = parser.parse(code_bytes)
                    root_node = tree.root_node
                    
                    # Extract AST nodes
                    ast_nodes = self.ast_extractor._extract_ast_nodes(
                        root_node, str(file_path), language, ast_node_id
                    )
                    
                    # Extract symbols
                    symbols = self.ast_extractor._extract_symbols(
                        root_node, str(file_path), language, symbol_id, code_bytes
                    )
                    
                    # Update symbol_map with new symbols from this file
                    for symbol in symbols:
                        sym_id, name, _, sym_file, _, _ = symbol
                        symbol_map[(sym_file, name)] = sym_id
                    
                    # Extract relationships
                    relationships = self.ast_extractor._extract_relationships(
                        root_node, str(file_path), language, rel_id, symbol_map, code_bytes
                    )
                    
                    graph_data = {"symbols": symbols, "relationships": relationships}
                    cache_misses += 1
                
                # Delete old data for this file
                self._delete_file_data(conn, file_path)
                
                # Insert AST nodes (component 1)
                if ast_nodes:
                    conn.executemany(
                        "INSERT INTO ast_nodes (id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        ast_nodes
                    )
                    ast_node_id = max(node[0] for node in ast_nodes) + 1
                
                # Insert symbols (component 2a)
                if graph_data["symbols"]:
                    conn.executemany(
                        "INSERT INTO symbols (id, name, type, file_path, line_number, language) VALUES (?, ?, ?, ?, ?, ?)",
                        graph_data["symbols"]
                    )
                    symbol_id = max(sym[0] for sym in graph_data["symbols"]) + 1
                
                # Insert relationships (component 2b)
                if graph_data["relationships"]:
                    conn.executemany(
                        "INSERT INTO relationships (id, from_symbol_id, to_symbol_id, relationship_type) VALUES (?, ?, ?, ?)",
                        graph_data["relationships"]
                    )
                    rel_id = max(rel[0] for rel in graph_data["relationships"]) + 1
                
                files_updated += 1
                logger.debug(
                    "Updated %s: %d AST nodes, %d symbols, %d relationships",
                    file_path.name,
                    len(ast_nodes) if ast_nodes else 0,
                    len(graph_data["symbols"]) if graph_data["symbols"] else 0,
                    len(graph_data["relationships"]) if graph_data["relationships"] else 0
                )
            
            except Exception as e:
                files_failed += 1
                logger.error("Failed to update %s: %s", file_path, str(e), exc_info=True)
                continue
        
        # Checkpoint to flush WAL
        try:
            conn.execute("CHECKPOINT")
        except Exception as e:
            logger.warning("Failed to checkpoint: %s", str(e))
        
        # Log summary
        if parse_cache:
            logger.info(
                "✅ GraphIndex updated: %d files (%d succeeded, %d failed) - parse-once: %d cache hits, %d cache misses",
                len(file_paths), files_updated, files_failed, cache_hits, cache_misses
            )
        else:
            logger.info(
                "✅ GraphIndex updated: %d files (%d succeeded, %d failed)",
                len(file_paths), files_updated, files_failed
            )
    
    def _delete_file_data(self, conn, file_path: Path) -> None:
        """Delete all data for a file from AST and graph components.
        
        Args:
            conn: DuckDB connection
            file_path: File to delete data for
        """
        file_path_str = str(file_path)
        
        try:
            # Delete relationships first (has FKs to symbols)
            conn.execute(
                "DELETE FROM relationships WHERE from_symbol_id IN (SELECT id FROM symbols WHERE file_path = ?) OR to_symbol_id IN (SELECT id FROM symbols WHERE file_path = ?)",
                [file_path_str, file_path_str]
            )
            
            # Delete symbols
            conn.execute("DELETE FROM symbols WHERE file_path = ?", [file_path_str])
            
            # Delete AST nodes (handle self-referential FK by deleting children first)
            # Simplest: just delete all for this file (DuckDB should handle FK order)
            conn.execute("DELETE FROM ast_nodes WHERE file_path = ?", [file_path_str])
            
            logger.debug("Deleted old data for %s", file_path)
        
        except Exception as e:
            logger.warning("Failed to delete old data for %s: %s", file_path, str(e))
    
    def _stub_build_status(self) -> "BuildStatus":  # type: ignore[name-defined]
        """Stub build status check for components.
        
        Returns:
            BuildStatus indicating BUILT
        """
        from ouroboros.subsystems.rag.base import BuildStatus, IndexBuildState
        
        return BuildStatus(
            state=IndexBuildState.BUILT,
            message="Built",
            progress_percent=100.0,
        )
    
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
            return BuildStatus(
                state=IndexBuildState.BUILDING,
                message="Building graph index...",
                progress_percent=50.0,  # TODO: Track actual progress
                details={"component": "graph"}
            )
        
        # Check if index has data (has been built)
        try:
            conn = self.db_connection.get_connection()
            ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
            symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            
            if ast_count > 0 or symbol_count > 0:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message=f"Graph index built ({ast_count} AST nodes, {symbol_count} symbols)",
                    progress_percent=100.0,
                    details={"ast_nodes": ast_count, "symbols": symbol_count}
                )
        except Exception as e:
            logger.debug("Error checking graph data: %s", e)
        
        # No data found - not built yet
        return BuildStatus(
            state=IndexBuildState.NOT_BUILT,
            message="Graph index not yet built",
            progress_percent=0.0
        )
    
    def health_check(self) -> HealthStatus:
        """Dynamic health check using component registry (fractal pattern).
        
        Delegates to dynamic_health_check() which aggregates health from all
        registered components (AST, graph) without hardcoded if/else logic.
        
        This enables:
        - Component isolation: Each component reports its own health
        - Granular diagnostics: Know which specific component is broken
        - Targeted rebuilds: Rebuild only the broken component
        - Zero coupling: Parent doesn't know child implementation details
        
        Returns:
            HealthStatus: Aggregated health from all components with:
                - healthy (bool): True only if ALL components healthy
                - message (str): Summary (e.g., "2/2 components healthy")
                - details (dict): Contains:
                    - "components" (dict): Per-component health {name: HealthStatus}
                    - "capabilities" (dict): Capability map {capability: bool}
                    - "component_count" (int): Total components
                    - "healthy_count" (int): Healthy components
        
        Example Result:
            ```python
            HealthStatus(
                healthy=False,  # One component unhealthy
                message="1/2 components healthy",
                details={
                    "components": {
                        "ast": HealthStatus(healthy=False, message="AST empty: 0 nodes", ...),
                        "graph": HealthStatus(healthy=True, message="Graph healthy: 5 symbols", ...)
                    },
                    "capabilities": {
                        "search_ast": False,  # AST unhealthy
                        "find_callers": True,  # Graph healthy
                        ...
                    },
                    "component_count": 2,
                    "healthy_count": 1
                }
            )
            ```
        
        See Also:
            - specs/2025-11-08-cascading-health-check-architecture/
            - ADDENDUM-2025-11-17-build-status-integration.md
            - dynamic_health_check() in component_helpers.py
            - _check_ast_health() and _check_graph_health() for component implementations
        """
        # ADDENDUM-2025-11-17: Check build status first, skip validation if building
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
        return dynamic_health_check(self.components)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about graph index.
        
        Returns:
            Dict with ast_node_count, symbol_count, relationship_count
        """
        return self.traversal.get_stats()
    
    # ========================================================================
    # Extended Methods (Graph Operations)
    # ========================================================================
    
    def search_ast(
        self,
        pattern: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search AST nodes by pattern (structural search).
        
        Args:
            pattern: Node type or symbol name pattern
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type)
            
        Returns:
            List of AST node dicts
        """
        return self.traversal.search_ast(pattern, n_results, filters)
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth
            
        Returns:
            List of caller information with paths
        """
        return self.traversal.find_callers(symbol_name, max_depth)
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth
            
        Returns:
            List of dependency information with paths
        """
        return self.traversal.find_dependencies(symbol_name, max_depth)
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length
            
        Returns:
            List of call paths (each path is a list of symbol names)
        """
        return self.traversal.find_call_paths(from_symbol, to_symbol, max_depth)
    
    # ========================================================================
    # Component-specific health check and rebuild methods
    # (Stubs - will be implemented in Phase 1 Tasks 1.2-1.5)
    # ========================================================================
    
    def _check_ast_health(self) -> HealthStatus:
        """Check AST component health.
        
        Verifies:
        1. AST nodes table has data (count > 0)
        2. Can actually query the table (test query succeeds)
        
        Standard Details Contract:
            - data_present (bool): True if count > 0
            - query_works (bool): True if test query succeeds
            - count (int): Number of AST nodes
            - error (Optional[str]): Error message if exception caught
        
        Returns:
            HealthStatus: AST component health status
                - healthy=True if count > 0 and query works
                - healthy=False if count = 0 or exception occurred
        
        Note:
            Does NOT raise exceptions to caller. All errors are caught and
            returned as HealthStatus with healthy=False and error details.
        """
        try:
            conn = self.db_connection.get_connection()
            
            # Query 1: Count AST nodes
            count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
            
            # Query 2: Test query (verify we can actually read data)
            test = conn.execute("SELECT * FROM ast_nodes LIMIT 1").fetchone()
            query_works = test is not None if count > 0 else True  # Empty table is valid
            
            # Determine health status
            data_present = count > 0
            healthy = data_present and query_works
            
            # Build message
            if healthy:
                message = f"AST healthy: {count} nodes indexed"
            elif not data_present:
                message = f"AST empty: 0 nodes indexed"
            else:
                message = f"AST query failed: {count} nodes but test query returned None"
            
            return HealthStatus(
                healthy=healthy,
                message=message,
                details={
                    "data_present": data_present,
                    "query_works": query_works,
                    "count": count,
                    "error": None,
                },
            )
        
        except Exception as e:
            # Defensive: catch all exceptions, return error HealthStatus
            logger.error(f"AST health check raised exception: {type(e).__name__}: {e}", exc_info=True)
            return HealthStatus(
                healthy=False,
                message=f"AST health check failed: {type(e).__name__}: {str(e)}",
                details={
                    "data_present": False,
                    "query_works": False,
                    "count": 0,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
    
    def _check_graph_health(self) -> HealthStatus:
        """Check graph component health.
        
        Verifies:
        1. Symbols table has data (count > 0)
        2. Relationships table has data (count > 0)
        3. Can actually query both tables (test queries succeed)
        
        Standard Details Contract:
            - symbol_count (int): Number of symbols
            - relationship_count (int): Number of relationships
            - data_present (bool): True if both counts > 0
            - query_works (bool): True if test queries succeed
            - error (Optional[str]): Error message if exception caught
        
        Returns:
            HealthStatus: Graph component health status
                - healthy=True if both counts > 0 and queries work
                - healthy=False if any count = 0 or exception occurred
        
        Note:
            Does NOT raise exceptions to caller. All errors are caught and
            returned as HealthStatus with healthy=False and error details.
        """
        try:
            conn = self.db_connection.get_connection()
            
            # Query 1: Count symbols
            symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            
            # Query 2: Count relationships
            relationship_count = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            
            # Query 3: Test queries (verify we can actually read data)
            symbol_test = conn.execute("SELECT * FROM symbols LIMIT 1").fetchone()
            relationship_test = conn.execute("SELECT * FROM relationships LIMIT 1").fetchone()
            
            # Determine health status
            data_present = symbol_count > 0 and relationship_count > 0
            query_works = True  # If we got here, queries worked
            healthy = data_present and query_works
            
            # Build message
            if healthy:
                message = f"Graph healthy: {symbol_count} symbols, {relationship_count} relationships"
            elif symbol_count == 0 and relationship_count == 0:
                message = "Graph empty: 0 symbols, 0 relationships"
            elif symbol_count == 0:
                message = f"Graph incomplete: 0 symbols, {relationship_count} relationships"
            elif relationship_count == 0:
                message = f"Graph incomplete: {symbol_count} symbols, 0 relationships"
            else:
                message = "Graph query failed"
            
            return HealthStatus(
                healthy=healthy,
                message=message,
                details={
                    "symbol_count": symbol_count,
                    "relationship_count": relationship_count,
                    "data_present": data_present,
                    "query_works": query_works,
                    "error": None,
                },
            )
        
        except Exception as e:
            # Defensive: catch all exceptions, return error HealthStatus
            logger.error(f"Graph health check raised exception: {type(e).__name__}: {e}", exc_info=True)
            return HealthStatus(
                healthy=False,
                message=f"Graph health check failed: {type(e).__name__}: {str(e)}",
                details={
                    "symbol_count": 0,
                    "relationship_count": 0,
                    "data_present": False,
                    "query_works": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
    
    def _rebuild_ast(self) -> None:
        """Rebuild AST component only (targeted rebuild).
        
        This is a targeted rebuild that:
        1. Clears only the ast_nodes table (preserves symbols/relationships)
        2. Re-parses all source files using tree-sitter
        3. Re-inserts AST nodes
        4. Checkpoints WAL
        
        Use Case:
            Called when AST health check fails but graph is healthy. Enables
            fast recovery (rebuild AST in ~3s vs full rebuild ~30s = 10x speedup).
        
        Raises:
            ActionableError: If source paths not set (build() must be called first)
                           or if rebuild fails
        
        Note:
            File parse errors are logged but do NOT abort the rebuild. This
            ensures partial recovery even if some files are broken.
        """
        import time
        
        if not self.source_paths:
            raise ActionableError(
                what_failed="Rebuild AST component",
                why_failed="Source paths not set (build() has not been called yet)",
                how_to_fix="Call build(source_paths) first to populate source_paths, then retry rebuild"
            )
        
        start_time = time.time()
        logger.info("🔧 Rebuilding AST component (targeted rebuild)...")
        
        try:
            conn = self.db_connection.get_connection()
            
            # Step 1: Clear only ast_nodes table (preserve symbols/relationships)
            # Note: ast_nodes has self-referential FK (parent_id), so we DROP/CREATE
            # instead of DELETE to avoid FK violations
            logger.info("Dropping and recreating ast_nodes table...")
            
            conn.execute("DROP TABLE IF EXISTS ast_nodes")
            
            # Recreate ast_nodes table with same schema
            conn.execute("""
                CREATE TABLE ast_nodes (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    symbol_name TEXT,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES ast_nodes(id)
                )
            """)
            
            # Recreate indexes for AST queries
            conn.execute("CREATE INDEX idx_ast_file_path ON ast_nodes(file_path)")
            conn.execute("CREATE INDEX idx_ast_node_type ON ast_nodes(node_type)")
            conn.execute("CREATE INDEX idx_ast_language ON ast_nodes(language)")
            conn.execute("CREATE INDEX idx_ast_symbol_name ON ast_nodes(symbol_name)")
            
            logger.info("✅ ast_nodes table dropped and recreated (symbols/relationships preserved)")
            
            # Step 2: Extract AST nodes from all source files
            file_extensions = self.ast_extractor.get_file_extensions()
            files_to_process = []
            
            for source_path in self.source_paths:
                resolved_path = self.base_path / source_path
                
                if not resolved_path.exists():
                    logger.warning(f"Source path does not exist (skipping): {resolved_path}")
                    continue
                
                if resolved_path.is_file():
                    if resolved_path.suffix in file_extensions:
                        files_to_process.append(resolved_path)
                else:
                    for ext in file_extensions:
                        for code_file in resolved_path.rglob(f"*{ext}"):
                            if self.ast_extractor.should_skip_path(code_file):
                                continue
                            files_to_process.append(code_file)
            
            logger.info(f"Re-parsing {len(files_to_process)} files for AST extraction...")
            
            all_ast_nodes = []
            ast_node_id = 0
            parse_errors = 0
            
            for file_path in files_to_process:
                language = self.ast_extractor.detect_language(file_path)
                if not language:
                    continue
                
                try:
                    self.ast_extractor.ensure_parser(language)
                    
                    # Read and parse file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_bytes = f.read().encode('utf-8')
                    
                    parser = self.ast_extractor._parsers[language]
                    tree = parser.parse(code_bytes)
                    root_node = tree.root_node
                    
                    # Extract AST nodes only (skip symbols/relationships)
                    ast_nodes = self.ast_extractor._extract_ast_nodes(
                        root_node, str(file_path), language, ast_node_id
                    )
                    
                    all_ast_nodes.extend(ast_nodes)
                    ast_node_id += len(ast_nodes)
                
                except Exception as e:
                    # File parse errors are logged but do NOT abort rebuild
                    parse_errors += 1
                    logger.warning(
                        f"Failed to parse {file_path} (skipping): {type(e).__name__}: {e}"
                    )
                    continue
            
            # Step 3: Re-insert AST nodes
            if all_ast_nodes:
                logger.info(f"Re-inserting {len(all_ast_nodes)} AST nodes into DuckDB...")
                conn.executemany(
                    "INSERT INTO ast_nodes (id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    all_ast_nodes
                )
            else:
                logger.warning("No AST nodes extracted during rebuild (all files failed or no files found)")
            
            # Step 4: Checkpoint to flush WAL and make data visible
            logger.info("Checkpointing to flush WAL...")
            conn.execute("CHECKPOINT")
            
            # Log rebuild duration and results
            duration = time.time() - start_time
            logger.info(
                f"✅ AST rebuild complete: {len(all_ast_nodes)} nodes from {len(files_to_process)} files "
                f"({parse_errors} parse errors, skipped) in {duration:.2f}s"
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AST rebuild failed after {duration:.2f}s: {type(e).__name__}: {e}", exc_info=True)
            raise ActionableError(
                what_failed="Rebuild AST component",
                why_failed=f"{type(e).__name__}: {str(e)}",
                how_to_fix="Check server logs for details. Database may be corrupted or locked. Consider full rebuild with build(force=True)."
            ) from e
    
    def _rebuild_graph(self) -> None:
        """Rebuild graph component only (targeted rebuild).
        
        This is a targeted rebuild that:
        1. Clears symbols and relationships tables (preserves ast_nodes)
        2. Re-parses all source files using tree-sitter
        3. Re-extracts symbols and relationships
        4. Re-inserts both into DuckDB
        5. Checkpoints WAL
        
        Use Case:
            Called when graph health check fails but AST is healthy. Enables
            fast recovery (rebuild graph in ~3s vs full rebuild ~30s = 10x speedup).
        
        Raises:
            ActionableError: If source paths not set (build() must be called first)
                           or if rebuild fails
        
        Note:
            File parse errors are logged but do NOT abort the rebuild. This
            ensures partial recovery even if some files are broken.
        """
        import time
        
        if not self.source_paths:
            raise ActionableError(
                what_failed="Rebuild graph component",
                why_failed="Source paths not set (build() has not been called yet)",
                how_to_fix="Call build(source_paths) first to populate source_paths, then retry rebuild"
            )
        
        start_time = time.time()
        logger.info("🔧 Rebuilding graph component (targeted rebuild)...")
        
        try:
            conn = self.db_connection.get_connection()
            
            # Step 1: Clear symbols and relationships tables (preserve ast_nodes)
            # Note: relationships has FKs to symbols, so DROP/CREATE in correct order
            logger.info("Dropping and recreating symbols and relationships tables...")
            
            # Drop in reverse FK dependency order (relationships first)
            conn.execute("DROP TABLE IF EXISTS relationships")
            conn.execute("DROP TABLE IF EXISTS symbols")
            
            # Recreate symbols table
            conn.execute("""
                CREATE TABLE symbols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    language TEXT NOT NULL
                )
            """)
            
            # Recreate symbols indexes
            conn.execute("CREATE INDEX idx_symbols_name ON symbols(name)")
            conn.execute("CREATE INDEX idx_symbols_type ON symbols(type)")
            conn.execute("CREATE INDEX idx_symbols_file_path ON symbols(file_path)")
            
            # Recreate relationships table
            conn.execute("""
                CREATE TABLE relationships (
                    id INTEGER PRIMARY KEY,
                    from_symbol_id INTEGER NOT NULL,
                    to_symbol_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    FOREIGN KEY (from_symbol_id) REFERENCES symbols(id),
                    FOREIGN KEY (to_symbol_id) REFERENCES symbols(id)
                )
            """)
            
            # Recreate relationships indexes
            conn.execute("CREATE INDEX idx_relationships_from ON relationships(from_symbol_id)")
            conn.execute("CREATE INDEX idx_relationships_to ON relationships(to_symbol_id)")
            conn.execute("CREATE INDEX idx_relationships_type ON relationships(relationship_type)")
            
            logger.info("✅ symbols and relationships tables dropped and recreated (ast_nodes preserved)")
            
            # Step 2: Extract symbols and relationships from all source files
            file_extensions = self.ast_extractor.get_file_extensions()
            files_to_process = []
            
            for source_path in self.source_paths:
                resolved_path = self.base_path / source_path
                
                if not resolved_path.exists():
                    logger.warning(f"Source path does not exist (skipping): {resolved_path}")
                    continue
                
                if resolved_path.is_file():
                    if resolved_path.suffix in file_extensions:
                        files_to_process.append(resolved_path)
                else:
                    for ext in file_extensions:
                        for code_file in resolved_path.rglob(f"*{ext}"):
                            if self.ast_extractor.should_skip_path(code_file):
                                continue
                            files_to_process.append(code_file)
            
            logger.info(f"Re-parsing {len(files_to_process)} files for graph extraction...")
            
            # Use two-pass extraction (same as build())
            all_symbols = []
            all_relationships = []
            symbol_id = 0
            rel_id = 0
            parse_errors = 0
            
            # Pass 1: Extract symbols (build symbol_map)
            symbol_map = {}
            parsed_trees = []
            
            for file_path in files_to_process:
                language = self.ast_extractor.detect_language(file_path)
                if not language:
                    continue
                
                try:
                    self.ast_extractor.ensure_parser(language)
                    
                    # Read and parse file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_bytes = f.read().encode('utf-8')
                    
                    parser = self.ast_extractor._parsers[language]
                    tree = parser.parse(code_bytes)
                    root_node = tree.root_node
                    
                    # Extract symbols only (skip AST nodes)
                    symbols = self.ast_extractor._extract_symbols(
                        root_node, str(file_path), language, symbol_id, code_bytes
                    )
                    
                    # Update symbol_map for relationship extraction
                    for symbol in symbols:
                        sym_id, name, _, sym_file, _, _ = symbol
                        symbol_map[(sym_file, name)] = sym_id
                    
                    all_symbols.extend(symbols)
                    symbol_id += len(symbols)
                    
                    # Cache parsed tree for pass 2
                    parsed_trees.append((file_path, language, root_node, code_bytes))
                
                except Exception as e:
                    # File parse errors are logged but do NOT abort rebuild
                    parse_errors += 1
                    logger.warning(
                        f"Failed to parse {file_path} (skipping): {type(e).__name__}: {e}"
                    )
                    continue
            
            # Pass 2: Extract relationships using complete symbol_map
            logger.info(f"Extracting relationships from {len(parsed_trees)} parsed files...")
            
            for file_path, language, root_node, code_bytes in parsed_trees:
                try:
                    relationships = self.ast_extractor._extract_relationships(
                        root_node, str(file_path), language, rel_id, symbol_map, code_bytes
                    )
                    all_relationships.extend(relationships)
                    rel_id += len(relationships)
                except Exception as e:
                    logger.warning(
                        f"Failed to extract relationships from {file_path} (skipping): {type(e).__name__}: {e}"
                    )
                    continue
            
            # Step 3: Re-insert symbols
            if all_symbols:
                logger.info(f"Re-inserting {len(all_symbols)} symbols into DuckDB...")
                conn.executemany(
                    "INSERT INTO symbols (id, name, type, file_path, line_number, language) VALUES (?, ?, ?, ?, ?, ?)",
                    all_symbols
                )
            else:
                logger.warning("No symbols extracted during rebuild (all files failed or no files found)")
            
            # Step 4: Re-insert relationships
            if all_relationships:
                logger.info(f"Re-inserting {len(all_relationships)} relationships into DuckDB...")
                conn.executemany(
                    "INSERT INTO relationships (id, from_symbol_id, to_symbol_id, relationship_type) VALUES (?, ?, ?, ?)",
                    all_relationships
                )
            else:
                logger.info("No relationships extracted during rebuild (may be expected for simple code)")
            
            # Step 5: Checkpoint to flush WAL and make data visible
            logger.info("Checkpointing to flush WAL...")
            conn.execute("CHECKPOINT")
            
            # Log rebuild duration and results
            duration = time.time() - start_time
            logger.info(
                f"✅ Graph rebuild complete: {len(all_symbols)} symbols, {len(all_relationships)} relationships "
                f"from {len(files_to_process)} files ({parse_errors} parse errors, skipped) in {duration:.2f}s"
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Graph rebuild failed after {duration:.2f}s: {type(e).__name__}: {e}", exc_info=True)
            raise ActionableError(
                what_failed="Rebuild graph component",
                why_failed=f"{type(e).__name__}: {str(e)}",
                how_to_fix="Check server logs for details. Database may be corrupted or locked. Consider full rebuild with build(force=True)."
            ) from e

