"""AST extraction using tree-sitter.

This module handles parsing source code files and extracting:
1. AST nodes: Structural syntax elements (functions, classes, control flow)
2. Symbols: Callable code elements (functions, methods, classes)
3. Relationships: Call graph edges (who calls what)

Architecture:
- tree-sitter-languages: Auto-installed parsers for multiple languages
- Parser caching: Load parsers once per language
- Multi-pass extraction: Parse once, extract nodes/symbols/relationships

Mission: Enable structural code analysis and call graph traversal.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class ASTExtractor:
    """Extract AST nodes, symbols, and relationships from source code.
    
    Uses tree-sitter for parsing and walking ASTs. Supports multiple languages
    with automatic parser installation.
    
    Attributes:
        languages: List of languages to support (e.g., ["python", "javascript"])
        base_path: Base path for resolving relative file paths
        _parsers: Cached tree-sitter parsers (language -> Parser)
    """
    
    def __init__(self, languages: List[str], base_path: Path):
        """Initialize AST extractor.
        
        Args:
            languages: List of language names (e.g., ["python", "typescript"])
            base_path: Base path for resolving relative paths
        """
        self.languages = languages
        self.base_path = base_path
        self._parsers: Dict[str, Any] = {}  # Language -> tree-sitter Parser
        
        logger.info("ASTExtractor initialized for languages: %s", languages)
    
    def ensure_parser(self, language: str):
        """Ensure tree-sitter parser is loaded for a language.
        
        Auto-loads and caches tree-sitter parsers. Uses tree-sitter-languages
        for automatic parser installation.
        
        Args:
            language: Language name (e.g., "python", "typescript", "javascript")
            
        Raises:
            ActionableError: If parser cannot be loaded
        """
        if language not in self._parsers:
            try:
                from tree_sitter import Language, Parser
                from tree_sitter_language_pack import get_language
                from typing import cast, Any
                
                # Get language grammar and create parser
                # Cast to Any to handle get_language's strict Literal type signature
                # Runtime will validate if language is supported
                lang = get_language(cast(Any, language))
                parser = Parser(lang)
                
                self._parsers[language] = parser
                logger.info("✅ Loaded tree-sitter parser for %s", language)
                
            except ImportError as e:
                raise ActionableError(
                    what_failed=f"Load tree-sitter parser for {language}",
                    why_failed="tree-sitter-language-pack not installed",
                    how_to_fix="Install via: pip install 'tree-sitter-language-pack'"
                ) from e
            except KeyError as e:
                raise ActionableError(
                    what_failed=f"Load tree-sitter parser for {language}",
                    why_failed=f"Language '{language}' not supported by tree-sitter-language-pack",
                    how_to_fix=f"Supported languages: python, javascript, typescript, go, rust, java, c, cpp, c_sharp, ruby, php, html, css, json, yaml. Check language name spelling."
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed=f"Load tree-sitter parser for {language}",
                    why_failed=str(e),
                    how_to_fix=f"Check tree-sitter-language-pack installation and language name"
                ) from e
    
    def extract_from_file(
        self,
        file_path: Path,
        language: str,
        ast_node_id: int,
        symbol_id: int,
        rel_id: int,
        symbol_map: Dict[Tuple[str, str], int]
    ) -> Tuple[List[Tuple], List[Tuple], List[Tuple]]:
        """Extract AST nodes, symbols, and relationships from a single file.
        
        Multi-pass extraction:
        1. Parse file with tree-sitter
        2. Walk AST and extract significant nodes
        3. Extract callable symbols (functions, classes, methods)
        4. Extract call expressions (relationships)
        
        Args:
            file_path: Path to source file
            language: Language name
            ast_node_id: Starting ID for AST nodes
            symbol_id: Starting ID for symbols
            rel_id: Starting ID for relationships
            symbol_map: Map of (file_path, symbol_name) -> symbol_id for relationship building
            
        Returns:
            Tuple of (ast_nodes, symbols, relationships)
        """
        self.ensure_parser(language)
        
        try:
            # Read file contents
            with open(file_path, 'r', encoding='utf-8') as f:
                code_bytes = f.read().encode('utf-8')
            
            # Parse with tree-sitter
            parser = self._parsers[language]
            tree = parser.parse(code_bytes)
            root_node = tree.root_node
            
            # Extract AST nodes (structural elements)
            ast_nodes = self._extract_ast_nodes(
                root_node, str(file_path), language, ast_node_id
            )
            
            # Extract symbols (callable elements)
            symbols = self._extract_symbols(
                root_node, str(file_path), language, symbol_id, code_bytes
            )
            
            # Update symbol_map with new symbols
            for symbol in symbols:
                sym_id, name, _, sym_file, _, _ = symbol
                symbol_map[(sym_file, name)] = sym_id
            
            # Extract relationships (call graph)
            relationships = self._extract_relationships(
                root_node, str(file_path), language, rel_id, symbol_map, code_bytes
            )
            
            return ast_nodes, symbols, relationships
            
        except Exception as e:
            logger.warning("Failed to parse %s: %s", file_path, e)
            return [], [], []
    
    def _extract_ast_nodes(
        self,
        root_node: Any,
        file_path: str,
        language: str,
        start_id: int
    ) -> List[Tuple]:
        """Extract significant AST nodes from tree-sitter tree.
        
        Extracts structural elements:
        - Functions, methods, async functions
        - Classes, interfaces, enums
        - Control flow (if, for, while, try/catch)
        - Imports, exports
        
        Args:
            root_node: Root node of tree-sitter AST
            file_path: Path to source file
            language: Language name
            start_id: Starting ID for nodes
            
        Returns:
            List of (id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id)
        """
        ast_nodes = []
        node_id = start_id
        
        # Node types we care about (language-agnostic where possible)
        significant_types = self._get_significant_node_types(language)
        
        # BFS traversal to extract nodes
        stack: List[Tuple[Any, Optional[int]]] = [(root_node, None)]  # (node, parent_id)
        
        while stack:
            node, parent_id = stack.pop(0)
            
            if node.type in significant_types:
                # Extract symbol name if available
                symbol_name = self._extract_node_symbol_name(node, language)
                
                ast_nodes.append((
                    node_id,
                    file_path,
                    language,
                    node.type,
                    symbol_name,
                    node.start_point[0] + 1,  # Line numbers start at 1
                    node.end_point[0] + 1,
                    parent_id
                ))
                
                current_parent: Optional[int] = node_id
                node_id += 1
            else:
                current_parent = parent_id
            
            # Add children to stack
            for child in node.children:
                stack.append((child, current_parent))
        
        return ast_nodes
    
    def _extract_symbols(
        self,
        root_node: Any,
        file_path: str,
        language: str,
        start_id: int,
        code_bytes: bytes
    ) -> List[Tuple]:
        """Extract callable symbols (functions, classes, methods).
        
        Symbols are the "nodes" in the call graph. Extract:
        - Functions (top-level and nested)
        - Methods (class methods)
        - Classes (constructors are callable)
        
        Args:
            root_node: Root node of tree-sitter AST
            file_path: Path to source file
            language: Language name
            start_id: Starting ID for symbols
            code_bytes: Source code bytes (for extracting text)
            
        Returns:
            List of (id, name, type, file_path, line_number, language)
        """
        symbols = []
        symbol_id = start_id
        
        # Symbol types per language
        symbol_types = self._get_symbol_node_types(language)
        
        # Walk AST and extract symbols
        stack = [root_node]
        
        while stack:
            node = stack.pop(0)
            
            if node.type in symbol_types:
                name = self._extract_node_symbol_name(node, language, code_bytes)
                
                if name:
                    symbol_type = self._map_node_type_to_symbol_type(node.type, language)
                    
                    symbols.append((
                        symbol_id,
                        name,
                        symbol_type,
                        file_path,
                        node.start_point[0] + 1,
                        language
                    ))
                    
                    symbol_id += 1
            
            # Add children
            stack.extend(node.children)
        
        return symbols
    
    def _extract_relationships(
        self,
        root_node: Any,
        file_path: str,
        language: str,
        start_id: int,
        symbol_map: Dict[Tuple[str, str], int],
        code_bytes: bytes
    ) -> List[Tuple]:
        """Extract call graph relationships (function calls, method calls).
        
        Relationships are the "edges" in the call graph. Extract:
        - Function calls
        - Method calls
        - Constructor calls (new, instantiation)
        
        Uses depth-first traversal to maintain function scope context.
        
        Args:
            root_node: Root node of tree-sitter AST
            file_path: Path to source file
            language: Language name
            start_id: Starting ID for relationships
            symbol_map: Map of (file_path, symbol_name) -> symbol_id
            code_bytes: Source code bytes
            
        Returns:
            List of (id, from_symbol_id, to_symbol_id, relationship_type)
        """
        relationships = []
        rel_id_counter = [start_id]  # Use list to allow mutation in nested function
        
        # Get relevant node types
        call_types = self._get_call_node_types(language)
        symbol_types = self._get_symbol_node_types(language)
        
        def extract_from_node(node: Any, current_symbol_id: Optional[int] = None) -> None:
            """Recursively extract relationships using DFS to maintain scope."""
            nonlocal rel_id_counter
            
            # Check if this node defines a new symbol (function/class/method)
            if node.type in symbol_types:
                name = self._extract_node_symbol_name(node, language, code_bytes)
                if name and (file_path, name) in symbol_map:
                    # Enter new scope - this becomes the current symbol
                    new_symbol_id = symbol_map[(file_path, name)]
                    
                    # Recursively process children in this new scope
                    for child in node.children:
                        extract_from_node(child, new_symbol_id)
                    return  # Don't process children again
            
            # Check if this is a call node
            if node.type in call_types and current_symbol_id is not None:
                called_name = self._extract_call_target(node, language, code_bytes)
                
                if called_name:
                    # Try to find target symbol in map
                    target_symbol_id = None
                    
                    # First try same file
                    if (file_path, called_name) in symbol_map:
                        target_symbol_id = symbol_map[(file_path, called_name)]
                    else:
                        # Try to find in any file (for cross-file calls)
                        for (_, sym_name), sym_id in symbol_map.items():
                            if sym_name == called_name:
                                target_symbol_id = sym_id
                                break
                    
                    if target_symbol_id and target_symbol_id != current_symbol_id:
                        # Record relationship (don't record self-calls)
                        relationships.append((
                            rel_id_counter[0],
                            current_symbol_id,
                            target_symbol_id,
                            "calls"
                        ))
                        rel_id_counter[0] += 1
            
            # Recursively process children in current scope
            for child in node.children:
                extract_from_node(child, current_symbol_id)
        
        # Start extraction from root
        extract_from_node(root_node, None)
        
        return relationships
    
    def _get_significant_node_types(self, language: str) -> set:
        """Get significant AST node types for a language."""
        # Python
        if language == "python":
            return {
                "function_definition",
                "async_function_definition",
                "class_definition",
                "if_statement",
                "for_statement",
                "while_statement",
                "try_statement",
                "with_statement",
                "import_statement",
                "import_from_statement",
            }
        
        # JavaScript/TypeScript
        if language in ["javascript", "typescript", "tsx", "jsx"]:
            return {
                "function_declaration",
                "function",
                "arrow_function",
                "method_definition",
                "class_declaration",
                "if_statement",
                "for_statement",
                "while_statement",
                "try_statement",
                "import_statement",
                "export_statement",
            }
        
        # Default: common patterns
        return {
            "function_definition",
            "function_declaration",
            "class_definition",
            "class_declaration",
        }
    
    def _get_symbol_node_types(self, language: str) -> set:
        """Get symbol node types (callable elements) for a language."""
        if language == "python":
            return {
                "function_definition",
                "async_function_definition",
                "class_definition",
            }
        
        if language in ["javascript", "typescript", "tsx", "jsx"]:
            return {
                "function_declaration",
                "function",
                "arrow_function",
                "method_definition",
                "class_declaration",
            }
        
        return {
            "function_definition",
            "function_declaration",
            "class_definition",
            "class_declaration",
        }
    
    def _get_call_node_types(self, language: str) -> set:
        """Get call node types (function/method calls) for a language."""
        if language == "python":
            return {
                "call",  # function_name()
            }
        
        if language in ["javascript", "typescript", "tsx", "jsx"]:
            return {
                "call_expression",  # function_name()
                "new_expression",   # new ClassName()
            }
        
        return {
            "call",
            "call_expression",
        }
    
    def _extract_node_symbol_name(self, node: Any, language: str, code_bytes: Optional[bytes] = None) -> Optional[str]:
        """Extract symbol name from node.
        
        Different node types store names in different child nodes.
        
        Args:
            node: tree-sitter node
            language: Language name
            code_bytes: Source code bytes (optional, for extracting text)
            
        Returns:
            Symbol name or None
        """
        # Python
        if language == "python":
            if node.type in ["function_definition", "async_function_definition", "class_definition"]:
                for child in node.children:
                    if child.type == "identifier":
                        if code_bytes:
                            return code_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        return None
        
        # JavaScript/TypeScript
        if language in ["javascript", "typescript", "tsx", "jsx"]:
            if node.type in ["function_declaration", "class_declaration"]:
                for child in node.children:
                    if child.type == "identifier":
                        if code_bytes:
                            return code_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        return None
            
            if node.type in ["function", "arrow_function", "method_definition"]:
                # May be anonymous or have name in different places
                for child in node.children:
                    if child.type in ["identifier", "property_identifier"]:
                        if code_bytes:
                            return code_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        return None
        
        return None
    
    def _extract_call_target(self, node: Any, language: str, code_bytes: bytes) -> Optional[str]:
        """Extract the name of the function/method being called.
        
        Handles both simple calls (func()) and chained attribute calls (obj.attr.method()).
        
        Args:
            node: Call node
            language: Language name
            code_bytes: Source code bytes
            
        Returns:
            Called function/method name or None
        """
        # Python: call node has a "function" child
        if language == "python":
            for child in node.children:
                if child.type == "identifier":
                    # Simple function call: func()
                    return code_bytes[child.start_byte:child.end_byte].decode('utf-8')
                elif child.type == "attribute":
                    # Method call: obj.method() or obj.attr.method()
                    # Walk down nested attributes to find the final identifier
                    current = child
                    while current.type == "attribute":
                        # attribute node: [object, ".", identifier]
                        # The last child is the identifier we want
                        last_child = current.children[-1] if current.children else None
                        if last_child and last_child.type == "identifier":
                            return code_bytes[last_child.start_byte:last_child.end_byte].decode('utf-8')
                        # Check if first child is nested attribute
                        if current.children and current.children[0].type == "attribute":
                            current = current.children[0]
                        else:
                            break
        
        # JavaScript/TypeScript: call_expression has "function" or "member_expression"
        if language in ["javascript", "typescript", "tsx", "jsx"]:
            for child in node.children:
                if child.type == "identifier":
                    return code_bytes[child.start_byte:child.end_byte].decode('utf-8')
                elif child.type == "member_expression":
                    # For obj.method() or obj.attr.method(), get the final property
                    current = child
                    while current.type == "member_expression":
                        # member_expression: [object, ".", property_identifier]
                        last_child = current.children[-1] if current.children else None
                        if last_child and last_child.type == "property_identifier":
                            return code_bytes[last_child.start_byte:last_child.end_byte].decode('utf-8')
                        # Check if first child is nested member_expression
                        if current.children and current.children[0].type == "member_expression":
                            current = current.children[0]
                        else:
                            break
        
        return None
    
    def _map_node_type_to_symbol_type(self, node_type: str, language: str) -> str:
        """Map tree-sitter node type to symbol type (function, class, method)."""
        if "class" in node_type:
            return "class"
        elif "method" in node_type:
            return "method"
        else:
            return "function"
    
    def get_file_extensions(self) -> List[str]:
        """Get file extensions for configured languages."""
        extension_map = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".mjs", ".cjs"],
            "typescript": [".ts", ".tsx"],
            "jsx": [".jsx"],
            "tsx": [".tsx"],
            "go": [".go"],
            "rust": [".rs"],
            "java": [".java"],
            "c": [".c", ".h"],
            "cpp": [".cpp", ".hpp", ".cc", ".hh", ".cxx"],
            "csharp": [".cs"],
            "ruby": [".rb"],
            "php": [".php"],
        }
        
        extensions = []
        for lang in self.languages:
            lang_lower = lang.lower()
            if lang_lower in extension_map:
                extensions.extend(extension_map[lang_lower])
        
        return extensions
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect language from file extension.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Language name or None if not supported
        """
        suffix = file_path.suffix.lower()
        
        # Map extension to language
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php",
        }
        
        lang = ext_to_lang.get(suffix)
        
        # Only return if language is in configured languages
        if lang and lang in self.languages:
            return lang
        
        return None
    
    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped during indexing.
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be skipped
        """
        skip_patterns = [
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".git",
            ".cache",
            "coverage",
            ".pytest_cache",
            ".mypy_cache",
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)

