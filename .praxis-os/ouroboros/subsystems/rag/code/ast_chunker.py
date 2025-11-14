"""AST-aware code chunking with import penalty.

This module provides language-agnostic AST-based code chunking using Tree-sitter.
Chunks are created at logical boundaries (functions, classes, control flow) and
include metadata for semantic search ranking (import ratio, token counts).

Architecture:
- Tree-sitter: Fast AST parsing with 40+ language grammars
- Config-driven: Language node types defined in mcp.yaml
- Import penalty: De-prioritize import-heavy chunks in search results
- Token-aware: Target 500 tokens per chunk for CodeBERT compatibility

Key Components:
- CodeChunk: Immutable dataclass representing a semantic code chunk
- UniversalASTChunker: Language-agnostic chunker using config-driven node types

Example:
    >>> from pathlib import Path
    >>> config = {
    ...     "language_configs": {
    ...         "python": {
    ...             "chunking": {
    ...                 "import_nodes": ["import_statement", "import_from_statement"],
    ...                 "definition_nodes": ["function_definition", "class_definition"],
    ...                 "split_boundary_nodes": ["if_statement", "for_statement"],
    ...                 "import_penalty": 0.3
    ...             }
    ...         }
    ...     }
    ... }
    >>> 
    >>> chunker = UniversalASTChunker(
    ...     language="python",
    ...     config=config,
    ...     base_path=Path("/project/root")
    ... )
    >>> 
    >>> chunks = chunker.chunk_file(Path("src/utils.py"))
    >>> for chunk in chunks:
    ...     print(f"{chunk.chunk_type}: {chunk.symbols} ({chunk.token_count} tokens)")

Mission: Enable semantic code search with AST-aware chunking and import penalty
         for more relevant search results.

Traceability:
    FR-001: AST-Aware Code Chunking
    FR-002: Import Penalty Mechanism
    FR-003: Token-Based Chunk Sizing
    FR-004: Configuration-Driven Language Support
    FR-009: Import Chunk Grouping
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CodeChunk:
    """Semantic code chunk with metadata for search ranking.
    
    Represents a logical unit of code (function, class, imports) extracted via
    AST parsing. Includes metadata for search relevance scoring:
    - Import ratio: Percentage of import statements (0.0-1.0)
    - Import penalty: Ranking multiplier to de-prioritize import-heavy chunks
    - Token count: Estimated tokens for CodeBERT embedding compatibility
    
    Attributes:
        content: Full text content of the chunk
        file_path: Absolute path to source file
        start_line: 1-indexed starting line number
        end_line: 1-indexed ending line number (inclusive)
        chunk_type: Type of chunk ("function", "class", "import", "module")
        symbols: List of function/class names defined in chunk
        import_ratio: Ratio of import lines to total lines (0.0-1.0)
        import_penalty: Multiplier for search ranking (0.3-1.0, lower = less relevant)
        token_count: Estimated token count for CodeBERT (target: ~500 tokens)
    
    Example:
        >>> chunk = CodeChunk(
        ...     content="def hello():\\n    print('world')",
        ...     file_path=Path("/project/utils.py"),
        ...     start_line=10,
        ...     end_line=11,
        ...     chunk_type="function",
        ...     symbols=["hello"],
        ...     import_ratio=0.0,
        ...     import_penalty=1.0,
        ...     token_count=12
        ... )
        >>> chunk.chunk_type
        'function'
        >>> chunk.symbols
        ['hello']
    
    Notes:
        - Immutable (frozen=True) for thread safety and caching
        - Import penalty typically 0.3 (configurable in mcp.yaml)
        - Token count estimated as len(content.split()) * 1.3 for CodeBERT
    """
    
    content: str
    file_path: Path
    start_line: int
    end_line: int
    chunk_type: str
    symbols: List[str]
    import_ratio: float
    import_penalty: float
    token_count: int


class UniversalASTChunker:
    """Language-agnostic AST-aware code chunker using configuration-driven node types.
    
    Chunks source code at logical AST boundaries (functions, classes, control flow)
    using Tree-sitter parsing. Node types are defined in mcp.yaml, enabling
    language support without code changes.
    
    Features:
    - Config-driven: Language node types loaded from mcp.yaml
    - Import grouping: Consecutive imports chunked together
    - Import penalty: De-prioritize import-heavy chunks in search
    - Token-aware: Target 500 tokens per chunk for CodeBERT
    - Graceful degradation: Parse failures logged, not raised
    
    Architecture:
    - Reuses Tree-sitter parsers from ASTExtractor (shared infrastructure)
    - Extracts node types from config (import_nodes, definition_nodes, split_boundary_nodes)
    - Applies configurable import_penalty multiplier (default: 0.3)
    - Estimates tokens for CodeBERT compatibility (max: 514 tokens)
    
    Example:
        >>> from pathlib import Path
        >>> config = {
        ...     "language_configs": {
        ...         "python": {
        ...             "chunking": {
        ...                 "import_nodes": ["import_statement", "import_from_statement"],
        ...                 "definition_nodes": ["function_definition", "class_definition"],
        ...                 "split_boundary_nodes": ["if_statement", "for_statement"],
        ...                 "import_penalty": 0.3
        ...             }
        ...         }
        ...     }
        ... }
        >>> 
        >>> chunker = UniversalASTChunker(
        ...     language="python",
        ...     config=config,
        ...     base_path=Path("/project")
        ... )
        >>> 
        >>> chunks = chunker.chunk_file(Path("src/utils.py"))
        >>> for chunk in chunks:
        ...     print(f"{chunk.chunk_type}: {len(chunk.content)} chars, {chunk.token_count} tokens")
    
    Attributes:
        language: Programming language name (e.g., "python", "typescript")
        base_path: Base directory for resolving relative paths
        import_nodes: Set of AST node types for imports/exports
        definition_nodes: Set of AST node types for functions/classes
        split_boundary_nodes: Set of AST node types for control flow splits
        import_penalty: Ranking multiplier for import-heavy chunks (0.0-1.0)
        target_tokens: Target token count per chunk (default: 500)
        parser: Tree-sitter parser instance (shared from ASTExtractor)
    
    Raises:
        ActionableError: If language config missing or parser unavailable
    """
    
    def __init__(self, language: str, config: Dict[str, Any], base_path: Path):
        """Initialize AST chunker for a specific language.
        
        Loads language-specific configuration from mcp.yaml and initializes
        Tree-sitter parser for AST parsing.
        
        Args:
            language: Language name (e.g., "python", "typescript", "go")
            config: Full code index config dict from mcp.yaml
                   Expected structure: {
                       "language_configs": {
                           "<language>": {
                               "chunking": {
                                   "import_nodes": [...],
                                   "definition_nodes": [...],
                                   "split_boundary_nodes": [...],
                                   "import_penalty": 0.3
                               }
                           }
                       }
                   }
            base_path: Base directory for resolving relative file paths
        
        Raises:
            ActionableError: If language config missing from mcp.yaml or
                           Tree-sitter parser cannot be loaded
        
        Example:
            >>> config = load_mcp_config()
            >>> chunker = UniversalASTChunker(
            ...     language="python",
            ...     config=config["indexes"]["code"],
            ...     base_path=Path("/project")
            ... )
        """
        self.language = language
        self.base_path = base_path
        
        # Extract language config from mcp.yaml structure
        if "language_configs" not in config:
            raise ActionableError(
                what_failed=f"Load language config for {language}",
                why_failed="No 'language_configs' section found in config",
                how_to_fix="Add 'language_configs' section to mcp.yaml with chunking config for this language"
            )
        
        if language not in config["language_configs"]:
            raise ActionableError(
                what_failed=f"Load language config for {language}",
                why_failed=f"Language '{language}' not found in language_configs",
                how_to_fix=f"Add '{language}' entry to mcp.yaml language_configs with chunking configuration"
            )
        
        lang_config = config["language_configs"][language]
        
        if "chunking" not in lang_config:
            raise ActionableError(
                what_failed=f"Load chunking config for {language}",
                why_failed="No 'chunking' section found in language config",
                how_to_fix=f"Add 'chunking' section to {language} config in mcp.yaml"
            )
        
        chunking = lang_config["chunking"]
        
        # Extract node type sets from config
        self.import_nodes: Set[str] = set(chunking.get("import_nodes", []))
        self.definition_nodes: Set[str] = set(chunking.get("definition_nodes", []))
        self.split_boundary_nodes: Set[str] = set(chunking.get("split_boundary_nodes", []))
        
        # Extract parameters with defaults
        self.import_penalty: float = chunking.get("import_penalty", 0.3)
        self.target_tokens: int = 500  # Target for CodeBERT (max: 514)
        
        # Initialize Tree-sitter parser (reuse from ASTExtractor infrastructure)
        try:
            from tree_sitter import Parser
            from tree_sitter_language_pack import get_language
            from typing import cast, Any
            
            # Cast to Any to bypass Literal type constraint (language is runtime-validated by get_language)
            lang = get_language(cast(Any, language))
            self.parser = Parser(lang)
            
            logger.info(
                "UniversalASTChunker initialized for %s: %d import nodes, %d definition nodes, %d split nodes",
                language,
                len(self.import_nodes),
                len(self.definition_nodes),
                len(self.split_boundary_nodes)
            )
            
        except ImportError as e:
            raise ActionableError(
                what_failed=f"Load Tree-sitter parser for {language}",
                why_failed="tree-sitter-language-pack not installed",
                how_to_fix="Install via: pip install 'tree-sitter-language-pack'"
            ) from e
        except KeyError as e:
            raise ActionableError(
                what_failed=f"Load Tree-sitter parser for {language}",
                why_failed=f"Language '{language}' not supported by tree-sitter-language-pack",
                how_to_fix=f"Supported languages: python, javascript, typescript, go, rust, java, c, cpp, c_sharp, ruby, php"
            ) from e
        except Exception as e:
            raise ActionableError(
                what_failed=f"Initialize Tree-sitter parser for {language}",
                why_failed=str(e),
                how_to_fix="Check tree-sitter-language-pack installation and language name spelling"
            ) from e
    
    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a source code file at AST boundaries.
        
        Parses the file with Tree-sitter and creates semantic chunks:
        - Groups all imports into a single chunk (first in list)
        - Creates individual chunks for each function/class definition
        - Returns empty list on parse failure (graceful degradation)
        
        Args:
            file_path: Path to source code file
        
        Returns:
            List of CodeChunk objects, with imports first, then definitions.
            Empty list if file cannot be parsed.
        
        Example:
            >>> chunks = chunker.chunk_file(Path("src/utils.py"))
            >>> len(chunks)
            5
            >>> chunks[0].chunk_type
            'import'
            >>> chunks[1].chunk_type
            'function'
            >>> chunks[2].chunk_type
            'class'
        
        Notes:
            - Parse failures are logged but not raised (graceful degradation)
            - Import chunk always appears first in the list (if imports exist)
            - Each function/class is a separate chunk (no mid-body splits)
            - Token counts estimated for CodeBERT compatibility (target: 500)
        """
        try:
            # Read file content
            if not file_path.exists():
                logger.warning("File not found: %s", file_path)
                return []
            
            code = file_path.read_text(encoding='utf-8')
            
            # Parse with Tree-sitter
            tree = self.parser.parse(bytes(code, 'utf-8'))
            root = tree.root_node
            
            # Collect nodes by type
            import_nodes = []
            definition_nodes = []
            
            # Traverse root children to classify nodes
            for node in root.children:
                if node.type in self.import_nodes:
                    import_nodes.append(node)
                elif node.type in self.definition_nodes:
                    definition_nodes.append(node)
            
            # Build chunks
            chunks: List[CodeChunk] = []
            
            # Group imports into single chunk (if any)
            if import_nodes:
                import_chunk = self._chunk_imports(import_nodes, code, file_path)
                if import_chunk:
                    chunks.append(import_chunk)
            
            # Chunk each definition individually
            for def_node in definition_nodes:
                def_chunk = self._chunk_definition(def_node, code, file_path)
                chunks.append(def_chunk)
            
            logger.info(
                "Chunked %s: %d chunks (%d imports, %d definitions)",
                file_path.name,
                len(chunks),
                1 if import_nodes else 0,
                len(definition_nodes)
            )
            
            return chunks
            
        except Exception as e:
            logger.warning(
                "Failed to chunk file %s: %s",
                file_path,
                str(e),
                exc_info=True
            )
            return []  # Graceful degradation on parse failure
    
    def _chunk_imports(self, nodes: List[Any], code: str, file_path: Path) -> Optional[CodeChunk]:
        """Group consecutive import statements into a single chunk.
        
        Collects all import/export nodes and creates a unified chunk with:
        - Combined content from all import statements
        - Extracted symbol names (what's being imported)
        - import_ratio = 1.0 (pure import chunk)
        - Applied import_penalty multiplier for search ranking
        
        Args:
            nodes: List of Tree-sitter AST nodes representing imports
            code: Full source code as string
            file_path: Path to source file
        
        Returns:
            CodeChunk with chunk_type="import", or None if no import nodes
        
        Example:
            >>> import_nodes = [node1, node2]  # import statements from AST
            >>> chunk = chunker._chunk_imports(import_nodes, code, file_path)
            >>> chunk.chunk_type
            'import'
            >>> chunk.import_ratio
            1.0
            >>> chunk.import_penalty
            0.3
        """
        if not nodes:
            return None
        
        # Get line range spanning all import nodes
        start_line = min(node.start_point[0] for node in nodes) + 1  # 1-indexed
        end_line = max(node.end_point[0] for node in nodes) + 1  # 1-indexed
        
        # Extract content for all import lines
        lines = code.split('\n')
        content = '\n'.join(lines[start_line - 1:end_line])
        
        # Extract imported symbols (module/function names)
        symbols: List[str] = []
        for node in nodes:
            # Walk node to find identifiers (imported names)
            def extract_symbols(n):
                if n.type == 'identifier' or n.type == 'dotted_name':
                    symbol = code[n.start_byte:n.end_byte]
                    if symbol and symbol not in symbols:
                        symbols.append(symbol)
                for child in n.children:
                    extract_symbols(child)
            
            extract_symbols(node)
        
        # Calculate token count
        token_count = self._estimate_tokens(content)
        
        return CodeChunk(
            content=content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            chunk_type="import",
            symbols=symbols,
            import_ratio=1.0,  # Pure import chunk
            import_penalty=self.import_penalty,  # Apply configured penalty
            token_count=token_count
        )
    
    def _chunk_definition(self, node: Any, code: str, file_path: Path) -> CodeChunk:
        """Extract function or class definition as a complete semantic unit.
        
        Creates a chunk from the entire definition body (no mid-function splits).
        Extracts the symbol name (function/class name) and determines chunk type.
        
        Args:
            node: Tree-sitter AST node (function_definition, class_definition, etc.)
            code: Full source code as string
            file_path: Path to source file
        
        Returns:
            CodeChunk with chunk_type="function" or "class"
        
        Example:
            >>> def_node = tree.root_node.children[0]  # function_definition node
            >>> chunk = chunker._chunk_definition(def_node, code, file_path)
            >>> chunk.chunk_type
            'function'
            >>> chunk.symbols
            ['my_function']
            >>> chunk.import_ratio
            0.0
        """
        # Extract line range (1-indexed)
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        
        # Extract content
        content = code[node.start_byte:node.end_byte]
        
        # Determine chunk type from node type
        node_type_lower = node.type.lower()
        if 'function' in node_type_lower or 'method' in node_type_lower:
            chunk_type = "function"
        elif 'class' in node_type_lower:
            chunk_type = "class"
        else:
            chunk_type = "definition"  # Generic fallback
        
        # Extract symbol name (function/class name)
        symbol_name = self._extract_symbol_name(node, code)
        symbols = [symbol_name] if symbol_name else []
        
        # Calculate token count
        token_count = self._estimate_tokens(content)
        
        # Detect large functions/classes (> target_tokens * 1.2)
        # TODO: Future enhancement - split at split_boundary_nodes (if/for/try statements)
        # For MVP, we keep large chunks intact. Rationale: Better to keep a complete
        # semantic unit (full function) than to arbitrarily split mid-function, which
        # would break the semantic integrity and hurt search relevance.
        if token_count > self.target_tokens * 1.2:
            logger.debug(
                "Large %s detected: %s (%d tokens > %d target) - keeping as single chunk",
                chunk_type,
                symbol_name or "anonymous",
                token_count,
                self.target_tokens
            )
        
        # Calculate import ratio (count import lines in content)
        import_ratio = self._calculate_import_ratio(content)
        
        # Apply import penalty if chunk has imports
        penalty = self._calculate_penalty(import_ratio)
        
        return CodeChunk(
            content=content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            chunk_type=chunk_type,
            symbols=symbols,
            import_ratio=import_ratio,
            import_penalty=penalty,
            token_count=token_count
        )
    
    def _extract_symbol_name(self, node: Any, code: str) -> Optional[str]:
        """Extract symbol name (function/class name) from AST node.
        
        Searches for identifier child nodes that represent the symbol name.
        
        Args:
            node: Tree-sitter AST node
            code: Full source code
        
        Returns:
            Symbol name string, or None if not found
        """
        # Common patterns: 
        # - function_definition -> identifier
        # - class_definition -> identifier
        # - method_definition -> property_identifier or identifier
        for child in node.children:
            if child.type in ('identifier', 'property_identifier', 'type_identifier'):
                return code[child.start_byte:child.end_byte]
        
        # Fallback: search recursively (but only 1 level deep)
        for child in node.children:
            if child.type == 'name':
                return code[child.start_byte:child.end_byte]
        
        return None
    
    def _calculate_import_ratio(self, content: str) -> float:
        """Calculate ratio of import lines to total lines in content.
        
        Args:
            content: Code content string
        
        Returns:
            Ratio from 0.0 to 1.0
        
        Example:
            >>> content = "import os\\nimport sys\\ndef foo():\\n    pass"
            >>> ratio = chunker._calculate_import_ratio(content)
            >>> ratio
            0.5
        """
        if not content:
            return 0.0
        
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        # Count lines that start with import keywords
        import_keywords = {'import ', 'from ', 'require(', 'include ', 'use '}
        import_count = sum(
            1 for line in lines
            if any(line.strip().startswith(kw) for kw in import_keywords)
        )
        
        return import_count / len(lines)
    
    def _calculate_penalty(self, import_ratio: float) -> float:
        """Calculate penalty multiplier based on import ratio.
        
        Chunks with >50% import statements receive the configured penalty
        multiplier (default: 0.3) to de-prioritize them in search results.
        Pure code chunks (no imports) receive no penalty (1.0).
        
        Args:
            import_ratio: Ratio of import lines (0.0 to 1.0)
        
        Returns:
            Penalty multiplier: 0.3 for import-heavy, 1.0 for code-heavy
        
        Example:
            >>> chunker._calculate_penalty(1.0)  # Pure imports
            0.3
            >>> chunker._calculate_penalty(0.0)  # Pure code
            1.0
            >>> chunker._calculate_penalty(0.6)  # Import-heavy
            0.3
            >>> chunker._calculate_penalty(0.4)  # Code-heavy
            1.0
        """
        if import_ratio > 0.5:
            return self.import_penalty  # Penalize import-heavy chunks
        else:
            return 1.0  # No penalty for code-heavy chunks
    
    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count for CodeBERT compatibility.
        
        Uses heuristic: ~4 characters per token for code.
        CodeBERT max: 514 tokens.
        
        Args:
            content: Code content string
        
        Returns:
            Estimated token count
        """
        # Simple heuristic: split on whitespace and estimate
        # Code typically has ~4 chars per token
        return len(content) // 4

