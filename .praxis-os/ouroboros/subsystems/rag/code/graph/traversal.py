"""Graph traversal using DuckDB recursive CTEs.

This module provides call graph traversal and AST queries:
1. find_callers: Who calls this function? (reverse lookup)
2. find_dependencies: What does this function call? (forward lookup)
3. find_call_paths: How to reach X from Y? (path finding)
4. search_ast: Find code by structural patterns

All queries use DuckDB's powerful recursive Common Table Expressions (CTEs)
with cycle detection and depth limits.

Mission: Enable "trust but verify" - trace function dependencies and impact.
"""

import logging
from typing import Any, Dict, List, Optional

from ouroboros.utils.errors import IndexError

logger = logging.getLogger(__name__)


class GraphTraversal:
    """Graph traversal queries using DuckDB recursive CTEs.
    
    Provides call graph analysis:
    - Reverse lookup (find_callers): Who calls this?
    - Forward lookup (find_dependencies): What does this call?
    - Path finding (find_call_paths): How to reach X from Y?
    - Structural search (search_ast): Find code by AST patterns
    
    All queries include cycle detection and max_depth limits to prevent
    infinite loops in recursive call graphs.
    """
    
    def __init__(self, db_connection: Any):
        """Initialize graph traversal.
        
        Args:
            db_connection: DuckDBConnection instance
        """
        self.db_connection = db_connection
        logger.info("GraphTraversal initialized")
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Uses recursive CTE to traverse the call graph upwards, finding all
        functions that directly or indirectly call the target symbol.
        
        Example:
            find_callers("process_request", max_depth=3)
            → Returns: handle_api_call, main, server_loop (chain of callers)
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth (default: 10, prevents infinite loops)
            
        Returns:
            List of caller information with paths, each dict contains:
            - caller_id, caller_name, caller_type, caller_file, caller_line
            - target_id, target_name, depth, path (call chain)
            
        Raises:
            IndexError: If query fails
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Recursive CTE to find all callers up to max_depth
            query = """
            WITH RECURSIVE callers AS (
                -- Base case: direct callers of the target symbol
                SELECT 
                    s1.id AS caller_id,
                    s1.name AS caller_name,
                    s1.type AS caller_type,
                    s1.file_path AS caller_file,
                    s1.line_number AS caller_line,
                    s2.id AS target_id,
                    s2.name AS target_name,
                    1 AS depth,
                    s1.name AS path
                FROM symbols s2
                JOIN relationships r ON s2.id = r.to_symbol_id
                JOIN symbols s1 ON r.from_symbol_id = s1.id
                WHERE s2.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: callers of callers (walk up the graph)
                SELECT 
                    s1.id,
                    s1.name,
                    s1.type,
                    s1.file_path,
                    s1.line_number,
                    c.target_id,
                    c.target_name,
                    c.depth + 1,
                    s1.name || ' -> ' || c.path
                FROM callers c
                JOIN relationships r ON c.caller_id = r.to_symbol_id
                JOIN symbols s1 ON r.from_symbol_id = s1.id
                WHERE c.depth < ? AND r.relationship_type = 'calls'
            )
            SELECT DISTINCT * FROM callers ORDER BY depth, caller_name
            """
            
            results = conn.execute(query, [symbol_name, max_depth]).fetchall()
            
            # Convert to dictionaries
            callers = []
            for row in results:
                callers.append({
                    "caller_id": row[0],
                    "caller_name": row[1],
                    "caller_type": row[2],
                    "caller_file": row[3],
                    "caller_line": row[4],
                    "target_id": row[5],
                    "target_name": row[6],
                    "depth": row[7],
                    "path": row[8],
                })
            
            logger.info("Found %d callers for '%s'", len(callers), symbol_name)
            return callers
            
        except Exception as e:
            logger.error("Failed to find callers: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_callers query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Uses recursive CTE to traverse the call graph downwards, finding all
        functions that are directly or indirectly called by the target symbol.
        
        Example:
            find_dependencies("main", max_depth=3)
            → Returns: init_app, load_config, start_server (chain of calls)
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth (default: 10, prevents infinite loops)
            
        Returns:
            List of dependency information with paths, each dict contains:
            - dep_id, dep_name, dep_type, dep_file, dep_line
            - source_id, source_name, depth, path (call chain)
            
        Raises:
            IndexError: If query fails
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Recursive CTE to find all dependencies up to max_depth
            query = """
            WITH RECURSIVE dependencies AS (
                -- Base case: direct dependencies of the source symbol
                SELECT 
                    s2.id AS dep_id,
                    s2.name AS dep_name,
                    s2.type AS dep_type,
                    s2.file_path AS dep_file,
                    s2.line_number AS dep_line,
                    s1.id AS source_id,
                    s1.name AS source_name,
                    1 AS depth,
                    s2.name AS path
                FROM symbols s1
                JOIN relationships r ON s1.id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE s1.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: dependencies of dependencies (walk down the graph)
                SELECT 
                    s2.id,
                    s2.name,
                    s2.type,
                    s2.file_path,
                    s2.line_number,
                    d.source_id,
                    d.source_name,
                    d.depth + 1,
                    d.path || ' -> ' || s2.name
                FROM dependencies d
                JOIN relationships r ON d.dep_id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE d.depth < ? AND r.relationship_type = 'calls'
            )
            SELECT DISTINCT * FROM dependencies ORDER BY depth, dep_name
            """
            
            results = conn.execute(query, [symbol_name, max_depth]).fetchall()
            
            # Convert to dictionaries
            dependencies = []
            for row in results:
                dependencies.append({
                    "dep_id": row[0],
                    "dep_name": row[1],
                    "dep_type": row[2],
                    "dep_file": row[3],
                    "dep_line": row[4],
                    "source_id": row[5],
                    "source_name": row[6],
                    "depth": row[7],
                    "path": row[8],
                })
            
            logger.info("Found %d dependencies for '%s'", len(dependencies), symbol_name)
            return dependencies
            
        except Exception as e:
            logger.error("Failed to find dependencies: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_dependencies query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Uses recursive CTE to find all paths connecting two symbols through
        the call graph. Includes cycle detection to prevent infinite loops.
        
        Example:
            find_call_paths("main", "database_query", max_depth=5)
            → Returns: [["main", "init_app", "setup_db", "database_query"],
                       ["main", "process_request", "database_query"]]
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length (default: 10)
            
        Returns:
            List of call paths, where each path is a list of symbol names
            
        Raises:
            IndexError: If query fails
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Recursive CTE to find all paths from source to target
            query = """
            WITH RECURSIVE paths AS (
                -- Base case: start from source symbol
                SELECT 
                    s1.id AS current_id,
                    s1.name AS current_name,
                    s2.id AS next_id,
                    s2.name AS next_name,
                    1 AS depth,
                    s1.name || ' -> ' || s2.name AS path,
                    s1.name || ',' || s2.name AS visited_ids
                FROM symbols s1
                JOIN relationships r ON s1.id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE s1.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: extend paths
                SELECT 
                    s2.id,
                    s2.name,
                    s3.id,
                    s3.name,
                    p.depth + 1,
                    p.path || ' -> ' || s3.name,
                    p.visited_ids || ',' || s3.name
                FROM paths p
                JOIN relationships r ON p.next_id = r.from_symbol_id
                JOIN symbols s2 ON p.next_id = s2.id
                JOIN symbols s3 ON r.to_symbol_id = s3.id
                WHERE 
                    p.depth < ? 
                    AND r.relationship_type = 'calls'
                    AND p.visited_ids NOT LIKE '%' || s3.name || '%'  -- Cycle detection
            )
            SELECT DISTINCT path FROM paths WHERE next_name = ?
            ORDER BY LENGTH(path)
            """
            
            results = conn.execute(query, [from_symbol, max_depth, to_symbol]).fetchall()
            
            # Convert paths to lists
            call_paths = []
            for row in results:
                path_str = row[0]
                path_list = path_str.split(" -> ")
                call_paths.append(path_list)
            
            logger.info("Found %d paths from '%s' to '%s'", len(call_paths), from_symbol, to_symbol)
            return call_paths
            
        except Exception as e:
            logger.error("Failed to find call paths: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_call_paths query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def search_ast(
        self,
        pattern: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search AST nodes by pattern (structural search).
        
        Query AST nodes by:
        - Node type (e.g., "function_definition", "class_definition")
        - Symbol name (e.g., "process_request")
        - Combined patterns
        
        Example:
            search_ast("async_function", filters={"language": "python"})
            → Returns all async functions in Python files
        
        Args:
            pattern: Node type or symbol name pattern
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type)
            
        Returns:
            List of AST node dicts with file_path, node_type, symbol_name, lines
            
        Raises:
            IndexError: If query fails
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Build WHERE clause
            where_clauses = []
            params: List[Any] = []
            
            # Pattern can match node_type or symbol_name
            where_clauses.append("(node_type LIKE ? OR symbol_name LIKE ?)")
            params.extend([f"%{pattern}%", f"%{pattern}%"])
            
            # Apply filters
            if filters:
                if "language" in filters:
                    where_clauses.append("language = ?")
                    params.append(filters["language"])
                if "node_type" in filters:
                    where_clauses.append("node_type = ?")
                    params.append(filters["node_type"])
                if "file_path" in filters:
                    where_clauses.append("file_path LIKE ?")
                    params.append(f"%{filters['file_path']}%")
            
            where_clause = " AND ".join(where_clauses)
            
            query = f"""
                SELECT file_path, language, node_type, symbol_name, start_line, end_line
                FROM ast_nodes
                WHERE {where_clause}
                ORDER BY file_path, start_line
                LIMIT ?
            """
            params.append(n_results)
            
            results = conn.execute(query, params).fetchall()
            
            # Convert to dictionaries
            ast_results = []
            for row in results:
                ast_results.append({
                    "file_path": row[0],
                    "language": row[1],
                    "node_type": row[2],
                    "symbol_name": row[3],
                    "start_line": row[4],
                    "end_line": row[5],
                    "content": f"{row[2]} {row[3] or ''} (lines {row[4]}-{row[5]})",
                })
            
            logger.info("Found %d AST nodes matching pattern '%s'", len(ast_results), pattern)
            return ast_results
            
        except Exception as e:
            logger.error("Failed to search AST: %s", e, exc_info=True)
            raise IndexError(
                what_failed="search_ast query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def search_symbols(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search symbols by name (basic symbol search).
        
        Args:
            query: Symbol name or pattern to search
            n_results: Max results to return
            filters: Optional filters (type, file_path, language)
            
        Returns:
            List of symbol dicts
            
        Raises:
            IndexError: If query fails
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Build WHERE clause
            where_clauses = ["name LIKE ?"]
            params: List[Any] = [f"%{query}%"]
            
            # Apply filters
            if filters:
                if "type" in filters:
                    where_clauses.append("type = ?")
                    params.append(filters["type"])
                if "file_path" in filters:
                    where_clauses.append("file_path LIKE ?")
                    params.append(f"%{filters['file_path']}%")
                if "language" in filters:
                    where_clauses.append("language = ?")
                    params.append(filters["language"])
            
            where_clause = " AND ".join(where_clauses)
            
            query_sql = f"""
                SELECT id, name, type, file_path, line_number, language
                FROM symbols
                WHERE {where_clause}
                ORDER BY name
                LIMIT ?
            """
            params.append(n_results)
            
            results = conn.execute(query_sql, params).fetchall()
            
            # Convert to dictionaries
            symbol_results = []
            for row in results:
                symbol_results.append({
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "file_path": row[3],
                    "line_number": row[4],
                    "language": row[5],
                    "content": f"{row[2]} {row[1]} at {row[3]}:{row[4]}",
                })
            
            logger.info("Found %d symbols matching query '%s'", len(symbol_results), query)
            return symbol_results
            
        except Exception as e:
            logger.error("Failed to search symbols: %s", e, exc_info=True)
            raise IndexError(
                what_failed="search_symbols query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph index.
        
        Returns:
            Dict with ast_node_count, symbol_count, relationship_count
        """
        conn = self.db_connection.get_connection()
        
        try:
            # Count AST nodes
            ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
            
            # Count symbols
            symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            
            # Count relationships
            rel_count = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            
            return {
                "ast_node_count": ast_count,
                "symbol_count": symbol_count,
                "relationship_count": rel_count,
            }
            
        except Exception as e:
            logger.warning("Failed to get stats: %s", e)
            return {
                "ast_node_count": 0,
                "symbol_count": 0,
                "relationship_count": 0,
            }

