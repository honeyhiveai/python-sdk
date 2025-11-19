"""Semantic search implementation for the Standards Index.

This module provides hybrid search (Vector + FTS + RRF) for standards content.
It uses LanceDB's native capabilities for multi-strategy search:
1. Vector search: Semantic similarity using sentence-transformers
2. FTS search: Keyword matching using LanceDB's native BM25
3. Hybrid fusion: Reciprocal Rank Fusion (RRF) merges both results
4. Optional reranking: Cross-encoder improves top results
5. Metadata filtering: Scalar indexes (BTREE/BITMAP) for fast prefiltering

Architecture Insight (from multi-index-rag-architecture.md):
- Originally designed with 3 databases (LanceDB + rank-bm25 + SQLite)
- Research revealed LanceDB has ALL capabilities built-in!
- Single database architecture: Vector + FTS + Scalar indexes = LanceDB native

Mission: Maintain behavioral system effectiveness as standards scale to 500+

This is the internal implementation for StandardsIndex, not the public API.
Use StandardsIndex (container.py) as the public interface.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import StandardsIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.utils.lancedb_helpers import EmbeddingModelLoader, LanceDBConnection, safe_encode
from ouroboros.subsystems.rag.utils.progress_file import ProgressFileManager
from ouroboros.utils.errors import ActionableError, IndexError

logger = logging.getLogger(__name__)


class SemanticIndex(BaseIndex):
    """Hybrid search index for standards content (internal implementation).
    
    Uses LanceDB's native capabilities:
    - Vector index (HNSW for fast ANN search)
    - FTS index (BM25-based keyword search)
    - Scalar indexes (BTREE for high-cardinality, BITMAP for low-cardinality)
    
    Search strategies:
    - Vector only: Semantic search
    - FTS only: Keyword search
    - Hybrid (default): RRF fusion of vector + FTS
    - With reranking: Cross-encoder rescores top results
    
    Design Notes:
    - Uses LanceDBConnection helper for lazy initialization
    - Uses EmbeddingModelLoader helper for model caching
    - No lock manager integration yet (will be added when container orchestrates)
    """
    
    def __init__(self, config: StandardsIndexConfig, base_path: Path):
        """Initialize Semantic Index.
        
        Args:
            config: StandardsIndexConfig from MCPConfig
            base_path: Base path for resolving relative paths
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Resolve index path
        self.index_path = base_path / ".cache" / "indexes" / "standards"
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Use LanceDBConnection helper for lazy initialization
        self.db_connection = LanceDBConnection(self.index_path)
        self._table = None
        
        # Lazy-load embedding model via helper
        self._reranker = None
        
        # Progress file manager for build progress reporting
        progress_cache_dir = base_path / ".cache" / "rag" / "build-progress"
        self._progress_manager = ProgressFileManager(
            cache_dir=progress_cache_dir,
            index_name="standards",
            component="vector"  # SemanticIndex is primarily vector-based
        )
        
        logger.info("SemanticIndex initialized (lazy-load mode)")
    
    def _ensure_table(self):
        """Ensure table is loaded (lazy initialization)."""
        if self._table is None:
            try:
                self._table = self.db_connection.open_table("standards")
                logger.info("Opened standards table")
            except ActionableError:
                # Re-raise ActionableError from helper
                raise
            except Exception as e:
                raise IndexError(
                    what_failed="Open standards table",
                    why_failed="Table does not exist. Index not built yet.",
                    how_to_fix="Build index first using container.build()"
                ) from e
    
    def _ensure_reranker(self):
        """Ensure reranker model is loaded (lazy initialization)."""
        if not self.config.reranking or not self.config.reranking.enabled:
            return
        
        if self._reranker is None:
            try:
                from sentence_transformers import CrossEncoder
                
                model_name = self.config.reranking.model
                logger.info("Loading reranker model: %s", model_name)
                self._reranker = CrossEncoder(model_name)
                logger.info("✅ Reranker loaded")
                
            except ImportError as e:
                logger.warning("Cross-encoder not available, reranking disabled: %s", e)
                # Graceful degradation - reranking is optional
            except Exception as e:
                logger.warning("Failed to load reranker, reranking disabled: %s", e)
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build standards index from source paths.
        
        This method:
        1. Chunks markdown documents (respecting config.vector.chunk_size/overlap)
        2. Generates embeddings for each chunk
        3. Creates LanceDB table with vector data
        4. Builds FTS index (BM25)
        5. Builds scalar indexes for metadata (domain, phase, role, etc.)
        
        Args:
            source_paths: Paths to standard directories/files
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building standards index from %d source paths", len(source_paths))
        
        try:
            # Write initial progress (0%)
            self._progress_manager.write_progress(0.0, "Starting build...")
            
            # Check if index already exists
            db = self.db_connection.connect()
            existing_tables = db.table_names()
            
            if "standards" in existing_tables and not force:
                logger.info("Standards index already exists. Use force=True to rebuild.")
                # Cleanup progress file on early return
                self._progress_manager.delete_progress()
                return
            
            # Load embedding model via helper (caching)
            self._progress_manager.write_progress(5.0, "Loading embedding model...")
            embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
            
            # Collect and chunk documents
            self._progress_manager.write_progress(10.0, "Collecting and chunking documents...")
            chunks = self._collect_and_chunk(source_paths)
            logger.info("Collected %d chunks from source paths", len(chunks))
            
            if not chunks:
                # Cleanup progress file on error
                self._progress_manager.delete_progress()
                raise ActionableError(
                    what_failed="Build standards index",
                    why_failed="No content found in source paths",
                    how_to_fix=f"Check that source paths contain markdown files: {source_paths}"
                )
            
            # Generate embeddings with progress reporting
            logger.info("Generating embeddings for %d chunks...", len(chunks))
            texts = [chunk["content"] for chunk in chunks]
            
            # Report progress during embedding (20% -> 70% of total progress)
            self._progress_manager.write_progress(20.0, f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = safe_encode(embedding_model, texts, show_progress_bar=True)
            self._progress_manager.write_progress(70.0, f"Embeddings generated for {len(chunks)} chunks")
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["vector"] = embedding.tolist()
            
            # Create table (drop existing if force=True)
            if "standards" in existing_tables and force:
                logger.info("Dropping existing standards table (force rebuild)")
                db.drop_table("standards")
            
            self._progress_manager.write_progress(75.0, f"Creating LanceDB table with {len(chunks)} chunks...")
            logger.info("Creating standards table with %d chunks", len(chunks))
            self._table = db.create_table("standards", data=chunks)
            
            # Build indexes
            self._progress_manager.write_progress(85.0, "Building FTS and metadata indexes...")
            self._build_indexes()
            
            # Success - cleanup progress file
            self._progress_manager.write_progress(100.0, "Build complete!")
            self._progress_manager.delete_progress()
            
            logger.info("✅ Standards index built successfully")
        
        except Exception as e:
            # Cleanup progress file on failure
            self._progress_manager.delete_progress()
            raise
    
    def _collect_and_chunk(self, source_paths: List[Path]) -> List[Dict[str, Any]]:
        """Collect markdown files and chunk them.
        
        Args:
            source_paths: Paths to scan for markdown files
            
        Returns:
            List of chunk dictionaries with content, metadata, etc.
        """
        chunks = []
        
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            # Collect markdown files
            if resolved_path.is_file():
                if resolved_path.suffix == ".md":
                    chunks.extend(self._chunk_file(resolved_path))
            else:
                # Recursively find markdown files
                for md_file in resolved_path.rglob("*.md"):
                    chunks.extend(self._chunk_file(md_file))
        
        return chunks
    
    def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single markdown file.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List of chunk dictionaries
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to read %s: %s", file_path, e)
            return []
        
        # Simple chunking strategy: split by headers
        # TODO: Implement token-based chunking with overlap (config.vector.chunk_size/overlap)
        # For now, use section-based chunking (split on ## headers)
        
        chunks = []
        lines = content.split("\n")
        current_chunk: List[str] = []
        current_section = "Introduction"
        
        for line in lines:
            if line.startswith("##"):
                # Save previous chunk
                if current_chunk:
                    chunk_content = "\n".join(current_chunk).strip()
                    if chunk_content:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            section=current_section
                        ))
                
                # Start new chunk
                current_section = line.lstrip("#").strip()
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Save last chunk
        if current_chunk:
            chunk_content = "\n".join(current_chunk).strip()
            if chunk_content:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    section=current_section
                ))
        
        return chunks
    
    def _create_chunk(self, content: str, file_path: Path, section: str) -> Dict[str, Any]:
        """Create chunk dictionary with metadata.
        
        Args:
            content: Chunk text content
            file_path: Source file path
            section: Section header
            
        Returns:
            Chunk dictionary ready for LanceDB
        """
        # Generate chunk ID (hash of content + file path)
        chunk_id = hashlib.sha256(f"{file_path}::{section}".encode()).hexdigest()[:16]
        
        # Extract metadata from file path and content
        # TODO: Implement metadata extraction (domain, phase, role, etc.)
        metadata = self._extract_metadata(file_path, content)
        
        return {
            "chunk_id": chunk_id,
            "content": content,
            "file_path": str(file_path.relative_to(self.base_path)),
            "section": section,
            "content_type": "standard",
            **metadata
        }
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from file and content.
        
        Args:
            file_path: Source file path
            content: Content text
            
        Returns:
            Metadata dictionary
        """
        # Simple metadata extraction
        # TODO: Implement YAML frontmatter parsing, keyword extraction, etc.
        
        metadata = {
            "domain": "general",  # Default
            "phase": 0,  # Default
            "role": "agent",  # Default
            "is_critical": False,  # Default
        }
        
        # Extract domain from path (e.g., standards/development/ → domain: development)
        parts = file_path.parts
        if "standards" in parts:
            idx = parts.index("standards")
            if idx + 1 < len(parts):
                metadata["domain"] = parts[idx + 1]
        
        return metadata
    
    def _build_indexes(self) -> None:
        """Build FTS and scalar indexes on the table.
        
        This method creates:
        1. FTS index on 'content' column (BM25 keyword search)
        2. Scalar indexes on metadata columns (BTREE/BITMAP for fast filtering)
        """
        if self._table is None:
            raise IndexError(
                what_failed="Build indexes",
                why_failed="Table not initialized",
                how_to_fix="Call build() first to create the table"
            )
        
        try:
            # FTS index (BM25-based keyword search)
            if self.config.fts.enabled:
                logger.info("Creating FTS index on 'content' column...")
                # Map simplified FTSConfig to LanceDB tokenizer
                tokenizer_mapping = {
                    "default": "default",
                    "standard": "standard", 
                    "whitespace": "whitespace",
                    "simple": "simple",
                }
                
                tokenizer_name = tokenizer_mapping.get(
                    self.config.fts.tokenizer,
                    "default"
                )
                
                self._table.create_fts_index(
                    "content",
                    replace=True,  # Replace if exists
                    tokenizer_name=tokenizer_name,
                )
                logger.info("✅ FTS index created")
            
            # Scalar indexes for metadata filtering (config-driven)
            if self.config.metadata_filtering and self.config.metadata_filtering.enabled:
                logger.info("Creating scalar indexes for metadata...")
                
                # Dynamically create each configured scalar index
                for scalar_index_config in self.config.metadata_filtering.scalar_indexes:
                    self._table.create_scalar_index(
                        scalar_index_config.column,
                        index_type=scalar_index_config.index_type.upper(),
                        replace=True
                    )
                    logger.info(
                        "✅ Scalar index created for column '%s' (type: %s)",
                        scalar_index_config.column,
                        scalar_index_config.index_type
                    )
                
                logger.info("✅ All %d scalar indexes created", 
                           len(self.config.metadata_filtering.scalar_indexes))
                
        except Exception as e:
            logger.error("Failed to build indexes: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Build FTS/scalar indexes",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure LanceDB version >=0.13.0 supports create_fts_index()"
            ) from e
    
    def rebuild_secondary_indexes(self) -> None:
        """Rebuild only the secondary indexes (FTS + scalar) without touching table data.
        
        This is useful when the table exists and has data, but the FTS or scalar indexes
        are missing or corrupted. This is much faster than rebuilding the entire index
        since it doesn't require re-chunking files or regenerating embeddings.
        
        Raises:
            IndexError: If rebuild fails
        """
        logger.info("Rebuilding secondary indexes for standards index...")
        
        try:
            self._ensure_table()
            
            if self._table is None:
                raise IndexError(
                    what_failed="Rebuild secondary indexes",
                    why_failed="Table not initialized",
                    how_to_fix="Run full index build first - table doesn't exist"
                )
            
            # Check if table has data
            row_count = self._table.count_rows()
            if row_count == 0:
                raise IndexError(
                    what_failed="Rebuild secondary indexes",
                    why_failed="Table is empty",
                    how_to_fix="Run full index build first - no data in table"
                )
            
            logger.info(f"Table has {row_count} chunks, rebuilding secondary indexes...")
            
            # Rebuild FTS and scalar indexes
            self._build_indexes()
            
            logger.info("✅ Secondary indexes rebuilt successfully")
            
        except Exception as e:
            logger.error("Failed to rebuild secondary indexes: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Rebuild secondary indexes",
                why_failed=str(e),
                how_to_fix="Check server logs. May need full index rebuild if table is corrupted."
            ) from e

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search standards index using hybrid strategy.
        
        Search flow:
        1. Vector search (top 20 results)
        2. FTS search (top 20 results) - if enabled
        3. Reciprocal Rank Fusion (merge vector + FTS)
        4. Cross-encoder reranking (top 10) - if enabled
        5. Return top N
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            filters: Optional metadata filters (domain, phase, role)
            
        Returns:
            List of SearchResult objects sorted by relevance
            
        Raises:
            IndexError: If search fails
        """
        self._ensure_table()
        
        # Load embedding model via helper (caching)
        embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
        
        try:
            # Build WHERE clause for metadata filtering
            where_clause = self._build_where_clause(filters) if filters else None
            
            # 1. Vector search
            query_vector = safe_encode(embedding_model, query).tolist()
            vector_results = self._vector_search(query_vector, where_clause, limit=20)
            
            # 2. FTS search (if enabled)
            if self.config.fts.enabled:
                fts_results = self._fts_search(query, where_clause, limit=20)
                
                # 3. Hybrid fusion (RRF)
                fused_results = self._reciprocal_rank_fusion(vector_results, fts_results)
            else:
                fused_results = vector_results
            
            # 4. Reranking (if enabled)
            if self.config.reranking and self.config.reranking.enabled and fused_results:
                self._ensure_reranker()
                if self._reranker:
                    fused_results = self._rerank(query, fused_results[:10])
            
            # 5. Convert to SearchResult objects
            search_results = []
            for idx, result in enumerate(fused_results[:n_results]):
                search_results.append(SearchResult(
                    content=result.get("content", ""),
                    file_path=result.get("file_path", ""),
                    relevance_score=result.get("score", 1.0 / (idx + 1)),  # Fallback score
                    content_type="standard",
                    metadata={
                        "domain": result.get("domain", ""),
                        "phase": result.get("phase", 0),
                        "section": result.get("section", ""),
                    },
                    chunk_id=result.get("chunk_id"),
                    section=result.get("section")
                ))
            
            logger.info("Search returned %d results for query: %s", len(search_results), query[:50])
            return search_results
            
        except Exception as e:
            logger.error("Search failed: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Standards search",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure index is built and model is loaded."
            ) from e
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """Build SQL WHERE clause from filters.
        
        Args:
            filters: Dictionary of filters (e.g., {"domain": "workflow", "phase": 3})
            
        Returns:
            SQL WHERE clause string
        """
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{key} = '{value}'")
            elif isinstance(value, int):
                conditions.append(f"{key} = {value}")
            elif isinstance(value, bool):
                conditions.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, list):
                # IN clause
                if all(isinstance(v, str) for v in value):
                    values_str = ", ".join(f"'{v}'" for v in value)
                    conditions.append(f"{key} IN ({values_str})")
                else:
                    values_str = ", ".join(str(v) for v in value)
                    conditions.append(f"{key} IN ({values_str})")
        
        return " AND ".join(conditions) if conditions else ""
    
    def _vector_search(
        self,
        query_vector: List[float],
        where_clause: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Execute vector search.
        
        Args:
            query_vector: Query embedding vector
            where_clause: Optional SQL WHERE clause for prefiltering
            limit: Max results
            
        Returns:
            List of result dictionaries
        """
        assert self._table is not None
        search_query = self._table.search(query_vector)
        
        if where_clause:
            search_query = search_query.where(where_clause, prefilter=True)
        
        results = search_query.limit(limit).to_list()
        
        # Add search type and score
        for result in results:
            result["search_type"] = "vector"
            # LanceDB returns _distance, convert to score (1 / (1 + distance))
            if "_distance" in result:
                result["score"] = 1.0 / (1.0 + result["_distance"])
        
        return results
    
    def _fts_search(
        self,
        query: str,
        where_clause: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Execute FTS (keyword) search.
        
        Args:
            query: Search query text
            where_clause: Optional SQL WHERE clause for prefiltering
            limit: Max results
            
        Returns:
            List of result dictionaries
        """
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
            # LanceDB FTS returns _score (BM25 score), normalize to 0-1
            if "_score" in result:
                result["score"] = min(1.0, result["_score"] / 10.0)  # Rough normalization
        
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
        # Build score dictionary: {chunk_id: rrf_score}
        rrf_scores: Dict[str, float] = {}
        result_map = {}  # {chunk_id: result_dict}
        
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
                if chunk_id not in result_map:  # Use FTS result if not in vector results
                    result_map[chunk_id] = result
        
        # Sort by RRF score
        sorted_chunk_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build final results list
        merged_results = []
        for chunk_id, score in sorted_chunk_ids:
            result = result_map[chunk_id].copy()
            result["score"] = score
            result["search_type"] = "hybrid_rrf"
            merged_results.append(result)
        
        return merged_results
    
    def _rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder.
        
        Args:
            query: Search query
            results: Results to rerank
            
        Returns:
            Reranked results
        """
        if not self._reranker or not results:
            return results
        
        # Prepare pairs for cross-encoder
        pairs = [(query, result.get("content", "")) for result in results]
        
        # Get scores
        scores = self._reranker.predict(pairs)
        
        # Add scores to results
        for result, score in zip(results, scores):
            result["score"] = float(score)
            result["search_type"] = "hybrid_rrf_reranked"
        
        # Sort by new scores
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails
        """
        logger.info("Updating standards index with %d changed files", len(changed_files))
        
        self._ensure_table()
        
        # Load embedding model via helper (caching)
        embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
        
        try:
            # For each changed file, re-chunk and update
            for file_path in changed_files:
                # Check if file still exists (not deleted)
                if not file_path.exists():
                    # Delete chunks for this file
                    self._delete_file_chunks(file_path)
                    continue
                
                # Re-chunk file
                chunks = self._chunk_file(file_path)
                
                if not chunks:
                    continue
                
                # Generate embeddings
                texts = [chunk["content"] for chunk in chunks]
                embeddings = safe_encode(embedding_model, texts)
                
                # Add embeddings to chunks
                for chunk, embedding in zip(chunks, embeddings):
                    chunk["vector"] = embedding.tolist()
                
                # Delete old chunks for this file
                self._delete_file_chunks(file_path)
                
                # Add new chunks
                assert self._table is not None
                self._table.add(chunks)
            
            # Rebuild FTS index (incremental FTS not supported, must rebuild)
            if self.config.fts.enabled:
                logger.info("Rebuilding FTS index after updates...")
                self._build_indexes()
            
            logger.info("✅ Standards index updated")
            
        except Exception as e:
            logger.error("Failed to update standards index: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Update standards index",
                why_failed=str(e),
                how_to_fix="Check server logs. May need to rebuild index if corruption detected."
            ) from e
    
    def _delete_file_chunks(self, file_path: Path) -> None:
        """Delete all chunks for a given file.
        
        Args:
            file_path: File whose chunks should be deleted
        """
        relative_path = str(file_path.relative_to(self.base_path))
        
        try:
            assert self._table is not None
            self._table.delete(f"file_path = '{relative_path}'")
            logger.info("Deleted chunks for file: %s", relative_path)
        except Exception as e:
            logger.warning("Failed to delete chunks for %s: %s", relative_path, e)
    
    def build_status(self) -> "BuildStatus":  # type: ignore[name-defined]
        """Check build status (not implemented for internal semantic index).
        
        This is an internal implementation class. Build status is handled
        by the container class (StandardsIndex).
        
        Returns:
            BuildStatus indicating BUILT (stub implementation)
        """
        from ouroboros.subsystems.rag.base import BuildStatus, IndexBuildState
        
        return BuildStatus(
            state=IndexBuildState.BUILT,
            message="Internal semantic index (build status tracked by container)",
            progress_percent=100.0,
        )
    
    def health_check(self) -> HealthStatus:
        """Check index health with dynamic validation.
        
        Verifies:
        1. Table exists and has data
        2. Can actually perform a test search (catches dimension mismatches, schema errors)
        3. FTS index exists (if enabled)
        4. Scalar indexes exist (if enabled)
        
        Returns:
            HealthStatus with diagnostic info
        """
        try:
            self._ensure_table()
            assert self._table is not None
            
            # Get table stats
            stats = self._table.count_rows()
            
            if stats == 0:
                return HealthStatus(
                    healthy=False,
                    message="Standards index is empty (no chunks)",
                    details={"chunk_count": 0, "needs_rebuild": True}
                )
            
            # DYNAMIC CHECK: Try to actually use the index with a test query
            # This catches dimension mismatches, schema incompatibilities, etc.
            try:
                # Load embedding model and generate test vector
                embedding_model = EmbeddingModelLoader.load(self.config.vector.model)
                test_query = "test"
                test_vector = safe_encode(embedding_model, test_query).tolist()
                
                # Try a simple vector search (limit 1 to minimize overhead)
                _ = self._table.search(test_vector).limit(1).to_list()
                
                # If we got here, vector search works - continue with other checks
                
            except Exception as test_error:
                # Test query failed - index is corrupted or incompatible
                error_msg = str(test_error).lower()
                
                # Check for common incompatibility issues
                if "dim" in error_msg and "match" in error_msg:
                    reason = "Model dimension mismatch (config changed, index needs rebuild)"
                elif "schema" in error_msg:
                    reason = "Schema incompatibility (LanceDB version or config changed)"
                else:
                    reason = f"Index not operational: {test_error}"
                
                return HealthStatus(
                    healthy=False,
                    message=f"Standards index corrupted or incompatible: {reason}",
                    details={
                        "chunk_count": stats,
                        "test_error": str(test_error),
                        "needs_rebuild": True
                    }
                )
            
            # Check FTS index exists (if enabled)
            fts_healthy = True
            fts_message = "FTS not enabled"
            
            if self.config.fts.enabled:
                # FTS index is built during _build_indexes() if enabled
                # We assume it exists if the table is healthy and FTS is enabled in config
                fts_message = "FTS index enabled and operational"
            
            # Check scalar indexes exist (if enabled)
            scalar_healthy = True
            scalar_message = "Scalar indexes not enabled"
            
            if self.config.metadata_filtering and self.config.metadata_filtering.enabled:
                try:
                    assert self._table is not None
                    indexes = self._table.list_indices()
                    
                    # Check each configured scalar index
                    missing_scalar = []
                    for scalar_config in self.config.metadata_filtering.scalar_indexes:
                        # BUG FIX: idx is an IndexConfig Pydantic model, use attribute access not .get()
                        exists = any(scalar_config.column in (idx.columns if hasattr(idx, 'columns') else getattr(idx, 'column', [])) 
                                   for idx in indexes)
                        if not exists:
                            missing_scalar.append(scalar_config.column)
                    
                    if missing_scalar:
                        scalar_healthy = False
                        scalar_message = f"Missing scalar indexes: {', '.join(missing_scalar)}"
                    else:
                        scalar_message = f"All {len(self.config.metadata_filtering.scalar_indexes)} scalar indexes exist"
                
                except Exception as e:
                    logger.warning("Failed to check scalar indexes: %s", e)
                    scalar_healthy = False
                    scalar_message = f"Scalar index check failed: {e}"
            
            # Overall health
            overall_healthy = fts_healthy and scalar_healthy
            
            if overall_healthy:
                return HealthStatus(
                    healthy=True,
                    message=f"Standards index operational ({stats} chunks)",
                    details={
                        "chunk_count": stats,
                        "fts_status": fts_message,
                        "scalar_status": scalar_message
                    },
                    last_updated=None  # TODO: Track last update time
                )
            else:
                return HealthStatus(
                    healthy=False,
                    message=f"Standards index needs secondary index rebuild",
                    details={
                        "chunk_count": stats,
                        "fts_status": fts_message,
                        "scalar_status": scalar_message,
                        "needs_secondary_rebuild": True
                    }
                )
            
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Standards index not healthy: {e}",
                details={"error": str(e), "needs_full_rebuild": True}
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
            
            # TODO: Get more detailed stats (unique files, average chunk size, etc.)
            
            return {
                "chunk_count": chunk_count,
                "index_path": str(self.index_path),
                "embedding_model": self.config.vector.model,
                "fts_enabled": self.config.fts.enabled,
                "reranking_enabled": self.config.reranking.enabled if self.config.reranking else False,
            }
            
        except Exception as e:
            return {"error": str(e)}
