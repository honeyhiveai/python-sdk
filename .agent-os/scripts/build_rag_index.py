"""
RAG Index Builder - LanceDB Implementation.

Builds vector index from Agent OS standards using LanceDB for semantic search.
Switched from ChromaDB to LanceDB for:
- Better metadata filtering (WHERE clauses at DB level)
- Cleaner hot reload (no singleton client conflicts)
- Incremental updates (update vs full rebuild)

100% AI-authored via human orchestration.
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import lancedb
import pyarrow as pa

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp_servers.chunker import AgentOSChunker, DocumentChunk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class IndexBuilder:
    """Builds and maintains LanceDB vector index for Agent OS standards."""

    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        embedding_provider: str = "local",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize index builder.

        Args:
            index_path: Path to store vector index (LanceDB directory)
            standards_path: Path to Agent OS standards directory
            embedding_provider: Provider for embeddings ("local" default/free or "openai" costs money)
            embedding_model: Model to use (all-MiniLM-L6-v2 for local, text-embedding-3-small for openai)
        """
        self.index_path = index_path
        self.standards_path = standards_path
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        
        # Initialize embedding model
        if self.embedding_provider == "local":
            logger.info("Using local embeddings (sentence-transformers) - FREE & OFFLINE")
            from sentence_transformers import SentenceTransformer
            self.local_model = SentenceTransformer(embedding_model)
        else:
            self.local_model = None

        # Ensure paths exist
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize LanceDB connection
        logger.info(f"Initializing LanceDB at {index_path}")
        self.db = lancedb.connect(str(index_path))
        logger.info("LanceDB initialized successfully")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (384 dimensions for local, 1536 for openai)

        Raises:
            Exception: If embedding generation fails
        """
        if self.embedding_provider == "local":
            try:
                # Local embeddings using sentence-transformers
                # Returns 384-dimensional vector
                embedding = self.local_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Failed to generate local embedding: {e}")
                raise
        elif self.embedding_provider == "openai":
            try:
                import openai
                # OpenAI embeddings (requires API key, costs money)
                response = openai.embeddings.create(
                    model=self.embedding_model, input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Failed to generate OpenAI embedding: {e}")
                raise
        else:
            raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    def build_index(self, force: bool = False, incremental: bool = True) -> Dict[str, Any]:
        """
        Build vector index from Agent OS files.

        Steps:
        1. Check if rebuild needed (unless force=True)
        2. Determine build strategy (full vs incremental)
        3. Find files to process
        4. Chunk files and generate embeddings
        5. Update/create LanceDB table
        6. Save metadata

        Args:
            force: Force full rebuild even if index is fresh
            incremental: Use incremental updates (only process changed files)

        Returns:
            Build statistics dictionary

        Raises:
            Exception: If build fails
        """
        logger.info("Starting RAG index build")
        start_time = datetime.now()

        # Check if rebuild needed
        if not force and self._is_index_fresh():
            logger.info("Index is fresh, skipping rebuild (use --force to rebuild)")
            return {"status": "skipped", "reason": "index_fresh"}
        
        # Determine build strategy
        table_exists = "agent_os_standards" in self.db.table_names()
        use_incremental = incremental and table_exists and not force
        
        if use_incremental:
            logger.info("📝 Using incremental update (only processing changed files)")
            changed_files = self._get_changed_files()
            
            if not changed_files:
                logger.info("No files changed, index is up to date")
                return {"status": "skipped", "reason": "no_changes"}
            
            logger.info(f"Found {len(changed_files)} changed files")
            files_to_process = changed_files
            
            # Open existing table
            table = self.db.open_table("agent_os_standards")
            
            # Delete old chunks for changed files
            logger.info("🗑️  Removing old chunks for changed files...")
            for md_file in changed_files:
                rel_path = str(md_file.relative_to(self.standards_path))
                try:
                    table.delete(f"file_path = '{rel_path}'")
                    logger.debug(f"Deleted chunks for {rel_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete chunks for {rel_path}: {e}")
        else:
            if force:
                logger.info("🔄 Force rebuild requested - processing all files")
            else:
                logger.info("🔄 Initial build - processing all files")
            files_to_process = list(self.standards_path.rglob("*.md"))

        # Initialize chunker
        chunker = AgentOSChunker()

        # Chunk files (all or changed)
        logger.info(f"Processing {len(files_to_process)} markdown files")
        all_chunks = []
        for idx, filepath in enumerate(files_to_process, 1):
            try:
                logger.info(f"[{idx}/{len(files_to_process)}] Chunking {filepath.name}")
                chunks = chunker.chunk_file(filepath)
                all_chunks.extend(chunks)
                logger.debug(f"  Generated {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to chunk {filepath}: {e}")
                # Continue processing other files
                continue

        logger.info(f"Generated {len(all_chunks)} chunks from {len(files_to_process)} files")

        # Convert chunks to LanceDB format with embeddings
        logger.info("Generating embeddings for all chunks...")
        records = []
        for idx, chunk in enumerate(all_chunks, 1):
            if idx % 100 == 0:
                logger.info(f"  Embedding chunk {idx}/{len(all_chunks)}")
            
            try:
                # Generate embedding
                embedding = self.generate_embedding(chunk.content)
                
                # Create record with embedding and metadata
                record = {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "vector": embedding,
                    "file_path": chunk.file_path,
                    "section_header": chunk.section_header,
                    "parent_headers": json.dumps(chunk.metadata.parent_headers),
                    "token_count": chunk.tokens,
                    "phase": chunk.metadata.phase if chunk.metadata.phase else 0,
                    "framework_type": chunk.metadata.framework_type or "",
                    "category": chunk.metadata.category or "",
                    "is_critical": chunk.metadata.is_critical,
                    "tags": json.dumps(chunk.metadata.tags),
                }
                records.append(record)
                
            except Exception as e:
                logger.error(f"Failed to embed chunk {idx}: {e}")
                continue

        logger.info(f"Successfully created {len(records)} records with embeddings")

        # Update or create table
        if use_incremental:
            # Add new records to existing table
            logger.info(f"➕ Adding {len(records)} new/updated records to existing table...")
            table.add(records)
            total_chunks = table.count_rows()
            logger.info(f"✅ Table updated - now contains {total_chunks} total records")
        else:
            # Full rebuild - drop and recreate table
            try:
                if table_exists:
                    logger.info("Dropping existing table for full rebuild")
                    self.db.drop_table("agent_os_standards")
            except Exception as e:
                logger.warning(f"Could not drop existing table: {e}")
            
            logger.info(f"Creating new table with {len(records)} records...")
            table = self.db.create_table("agent_os_standards", records)
            total_chunks = len(records)
            logger.info(f"✅ Table created with {total_chunks} records")

        # Save metadata with file modification times
        build_time = datetime.now()
        elapsed = (build_time - start_time).total_seconds()
        
        # Collect all file mtimes for change detection
        file_mtimes = {}
        for md_file in self.standards_path.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.standards_path))
            file_mtimes[rel_path] = md_file.stat().st_mtime
        
        metadata = {
            "build_time": build_time.isoformat(),
            "source_files": len(file_mtimes),
            "total_chunks": total_chunks,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "build_duration_seconds": elapsed,
            "build_type": "incremental" if use_incremental else "full",
            "files_mtimes": file_mtimes,
        }
        
        metadata_file = self.index_path / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        logger.info(f"Metadata saved to {metadata_file}")

        build_type = "incremental update" if use_incremental else "full build"
        logger.info(f"✅ Index {build_type} complete in {elapsed:.1f}s")
        return {
            "status": "success",
            "chunks": total_chunks,
            "files": len(file_mtimes),
            "files_processed": len(files_to_process),
            "duration_seconds": elapsed,
            "build_type": "incremental" if use_incremental else "full",
        }

    def _get_changed_files(self) -> List[Path]:
        """
        Get list of files that changed since last build.

        Returns:
            List of file paths that need reprocessing
        """
        metadata_file = self.index_path / "metadata.json"
        
        # No metadata = all files are "changed"
        if not metadata_file.exists():
            return list(self.standards_path.rglob("*.md"))
        
        try:
            metadata = json.loads(metadata_file.read_text())
            file_mtimes = metadata.get("files_mtimes", {})
            
            changed_files = []
            current_files = set()
            
            for md_file in self.standards_path.rglob("*.md"):
                rel_path = str(md_file.relative_to(self.standards_path))
                current_files.add(rel_path)
                current_mtime = md_file.stat().st_mtime
                
                # File is new or modified
                if rel_path not in file_mtimes or file_mtimes[rel_path] != current_mtime:
                    changed_files.append(md_file)
            
            # Log deleted files (in old metadata but not in current files)
            deleted_files = set(file_mtimes.keys()) - current_files
            if deleted_files:
                logger.info(f"Detected {len(deleted_files)} deleted files")
            
            return changed_files
            
        except Exception as e:
            logger.warning(f"Error detecting changed files: {e}")
            # Fall back to full rebuild
            return list(self.standards_path.rglob("*.md"))

    def _is_index_fresh(self) -> bool:
        """
        Check if index needs rebuild.

        Returns:
            True if index is fresh and doesn't need rebuild
        """
        metadata_file = self.index_path / "metadata.json"
        
        # No metadata = needs build
        if not metadata_file.exists():
            return False
        
        # Check if table exists
        if "agent_os_standards" not in self.db.table_names():
            return False
        
        try:
            # Read metadata
            metadata = json.loads(metadata_file.read_text())
            build_time = datetime.fromisoformat(metadata["build_time"])
            
            # Check if any source files are newer than build
            for md_file in self.standards_path.rglob("*.md"):
                file_mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if file_mtime > build_time:
                    logger.debug(f"File {md_file.name} modified after build")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not check index freshness: {e}")
            return False


def main():
    """CLI entry point for index builder."""
    parser = argparse.ArgumentParser(
        description="Build RAG vector index from Agent OS standards"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force full rebuild even if index exists and is fresh",
    )
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable incremental updates (force full rebuild)",
    )

    parser.add_argument(
        "--provider",
        default="local",
        choices=["local", "openai"],
        help="Embedding provider: 'local' (FREE, offline, default) or 'openai' (~3-5%% better, costs money)",
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Embedding model (defaults: all-MiniLM-L6-v2 for local, text-embedding-3-small for openai)",
    )

    parser.add_argument(
        "--index-path",
        type=Path,
        default=None,
        help="Path to store vector index (default: .agent-os/.cache/vector_index)",
    )

    parser.add_argument(
        "--standards-path",
        type=Path,
        default=None,
        help="Path to Agent OS standards (default: .agent-os/standards)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    index_path = args.index_path or (repo_root / ".agent-os" / ".cache" / "vector_index")
    standards_path = args.standards_path or (repo_root / ".agent-os" / "standards")

    # Validate standards path exists
    if not standards_path.exists():
        logger.error(f"Standards path does not exist: {standards_path}")
        logger.info("Please specify --standards-path or run from repository root")
        sys.exit(1)

    # Check OpenAI API key if using OpenAI
    if args.provider == "openai":
        import os

        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set")
            logger.info("Switching to local embeddings (free, offline)")
            args.provider = "local"

    try:
        # Determine model based on provider if not specified
        if args.model is None:
            if args.provider == "local":
                args.model = "all-MiniLM-L6-v2"
            else:
                args.model = "text-embedding-3-small"
        
        # Build index
        builder = IndexBuilder(
            index_path=index_path,
            standards_path=standards_path,
            embedding_provider=args.provider,
            embedding_model=args.model,
        )

        result = builder.build_index(
            force=args.force,
            incremental=not args.no_incremental,
        )

        if result["status"] == "success":
            logger.info("✅ Index built successfully!")
            sys.exit(0)
        elif result["status"] == "skipped":
            logger.info("✅ Index is already fresh!")
            sys.exit(0)
        else:
            logger.error(f"❌ Index build failed: {result}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error during index build: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
