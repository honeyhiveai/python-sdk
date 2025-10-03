"""
Unit tests for RAG Engine.

Tests semantic search, grep fallback, caching, and filtering.
100% AI-authored via human orchestration.
"""

# Import from .agent-os package
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".agent-os"))

# pylint: disable=wrong-import-position,no-member,unexpected-keyword-arg
from mcp_servers.rag_engine import RAGEngine, SearchResult


class TestRAGEngineInitialization:
    """Test RAG engine initialization."""

    def test_init_with_invalid_index(self):
        """Test initialization with non-existent index."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "nonexistent"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            # Should initialize but vector search unavailable
            assert not engine.vector_search_available

    def test_init_with_valid_paths(self):
        """Test initialization with valid paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            index_path.mkdir()
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            # Should initialize
            assert engine.index_path == index_path
            assert engine.standards_path == standards_path


class TestSearchTermExtraction:
    """Test search term extraction."""

    def test_extract_search_terms_basic(self):
        """Test basic term extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            query = "Phase 1 method verification requirements"
            terms = engine._extract_search_terms(query)

            assert "phase" in terms
            assert "method" in terms
            assert "verification" in terms
            assert "requirements" in terms

    def test_extract_search_terms_filters_stop_words(self):
        """Test that stop words are filtered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            query = "what is the test framework"
            terms = engine._extract_search_terms(query)

            # Stop words should be filtered
            assert "what" not in terms
            assert "the" not in terms

            # Content words should remain
            assert "test" in terms
            assert "framework" in terms

    def test_extract_search_terms_handles_punctuation(self):
        """Test that punctuation is handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            query = "test, framework: validation?"
            terms = engine._extract_search_terms(query)

            assert "test" in terms
            assert "framework" in terms
            assert "validation" in terms


class TestCacheManagement:
    """Test query caching."""

    def test_cache_key_generation(self):
        """Test cache key generation is consistent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            key1 = engine._generate_cache_key("test query", 5, None)
            key2 = engine._generate_cache_key("test query", 5, None)

            assert key1 == key2

    def test_cache_key_different_for_different_queries(self):
        """Test cache keys differ for different queries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            key1 = engine._generate_cache_key("query 1", 5, None)
            key2 = engine._generate_cache_key("query 2", 5, None)

            assert key1 != key2

    def test_cache_result_and_check(self):
        """Test caching and retrieving results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path, cache_ttl_seconds=10)

            # Create a result
            result = SearchResult(
                chunks=[{"content": "test"}],
                total_tokens=10,
                retrieval_method="vector",
                query_time_ms=50.0,
                relevance_scores=[0.95],
                cache_hit=False,
            )

            # Cache it
            cache_key = "test_key"
            engine._cache_result(cache_key, result)

            # Check cache
            cached_result = engine._check_cache(cache_key)
            assert cached_result is not None
            assert cached_result.cache_hit is True
            assert len(cached_result.chunks) == 1

    def test_cache_expiration(self):
        """Test that cache expires after TTL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            # Short TTL for testing
            engine = RAGEngine(index_path, standards_path, cache_ttl_seconds=1)

            result = SearchResult(
                chunks=[{"content": "test"}],
                total_tokens=10,
                retrieval_method="vector",
                query_time_ms=50.0,
                relevance_scores=[0.95],
            )

            cache_key = "test_key"
            engine._cache_result(cache_key, result)

            # Should be cached immediately
            assert engine._check_cache(cache_key) is not None

            # Wait for expiration
            time.sleep(1.1)

            # Should be expired
            assert engine._check_cache(cache_key) is None

    def test_cache_cleanup(self):
        """Test cache cleanup removes expired entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path, cache_ttl_seconds=1)

            result = SearchResult(
                chunks=[],
                total_tokens=0,
                retrieval_method="vector",
                query_time_ms=0.0,
                relevance_scores=[],
            )

            # Add entries
            for i in range(10):
                engine._cache_result(f"key_{i}", result)

            assert len(engine._query_cache) == 10

            # Wait for expiration
            time.sleep(1.1)

            # Trigger cleanup
            engine._cleanup_cache()

            # All should be removed
            assert len(engine._query_cache) == 0


class TestWhereClauseBuilder:
    """Test metadata filter building."""

    def test_build_where_clause_empty(self):
        """Test building where clause with no filters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            where = engine._build_where_clause(None)
            assert where is None

    def test_build_where_clause_phase_filter(self):
        """Test building where clause with phase filter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            where = engine._build_where_clause({"phase": 1})
            assert where is not None
            assert where["phase"] == 1

    def test_build_where_clause_critical_filter(self):
        """Test building where clause with critical filter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            where = engine._build_where_clause({"is_critical": True})
            assert where is not None
            assert where["is_critical"] is True

    def test_build_where_clause_multiple_filters(self):
        """Test building where clause with multiple filters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            where = engine._build_where_clause(
                {"phase": 1, "is_critical": True, "framework": "test_v3"}
            )

            assert where is not None
            assert where["phase"] == 1
            assert where["is_critical"] is True
            assert where["framework_type"] == "test_v3"


class TestResultProcessing:
    """Test result processing and ranking."""

    def test_process_results_basic(self):
        """Test basic result processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            # Mock ChromaDB results
            results = {
                "documents": [["doc1", "doc2"]],
                "metadatas": [
                    [
                        {
                            "file_path": "file1.md",
                            "section_header": "Section 1",
                            "is_critical": False,
                        },
                        {
                            "file_path": "file2.md",
                            "section_header": "Section 2",
                            "is_critical": False,
                        },
                    ]
                ],
                "distances": [[0.1, 0.2]],
            }

            chunks = engine._process_results(results, n_results=2)

            assert len(chunks) == 2
            assert chunks[0]["content"] == "doc1"
            assert chunks[1]["content"] == "doc2"

    def test_process_results_critical_boosting(self):
        """Test that critical content gets score boost."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            results = {
                "documents": [["critical doc", "normal doc"]],
                "metadatas": [
                    [
                        {
                            "file_path": "file1.md",
                            "section_header": "Section 1",
                            "is_critical": True,
                        },
                        {
                            "file_path": "file2.md",
                            "section_header": "Section 2",
                            "is_critical": False,
                        },
                    ]
                ],
                "distances": [[0.5, 0.5]],  # Same distance
            }

            chunks = engine._process_results(results, n_results=2)

            # Critical content should have higher score
            assert chunks[0]["is_critical"] is True
            assert chunks[0]["score"] > chunks[1]["score"]

    def test_process_results_deduplication(self):
        """Test deduplication by file_path + section_header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            results = {
                "documents": [["doc1", "doc1_duplicate", "doc2"]],
                "metadatas": [
                    [
                        {
                            "file_path": "file1.md",
                            "section_header": "Section 1",
                            "is_critical": False,
                        },
                        {
                            "file_path": "file1.md",
                            "section_header": "Section 1",  # Duplicate
                            "is_critical": False,
                        },
                        {
                            "file_path": "file2.md",
                            "section_header": "Section 2",
                            "is_critical": False,
                        },
                    ]
                ],
                "distances": [[0.1, 0.15, 0.2]],
            }

            chunks = engine._process_results(results, n_results=3)

            # Should deduplicate
            assert len(chunks) == 2
            assert chunks[0]["content"] == "doc1"  # Keep first
            assert chunks[1]["content"] == "doc2"


class TestHealthCheck:  # pylint: disable=too-few-public-methods
    """Test health check functionality."""

    def test_health_check_no_vector_search(self):
        """Test health check when vector search unavailable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "nonexistent"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            health = engine.health_check()

            assert health["vector_search_available"] is False
            assert health["grep_fallback_available"] is True
            assert "cache_size" in health


@patch("mcp_servers.rag_engine.openai")
class TestGrepFallback:
    """Test grep fallback search."""

    def test_grep_fallback_basic(self, mock_openai):  # pylint: disable=unused-argument
        """Test basic grep fallback."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "nonexistent"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            # Create test file
            test_file = standards_path / "test.md"
            test_file.write_text("This is a test document with phase 1 content.")

            engine = RAGEngine(index_path, standards_path)

            result = engine._grep_fallback("phase test", n_results=5, filters=None)

            assert result.retrieval_method == "grep_fallback"
            assert len(result.chunks) > 0

    def test_grep_fallback_no_results(
        self, mock_openai
    ):  # pylint: disable=unused-argument
        """Test grep fallback with no matches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "nonexistent"
            standards_path = Path(temp_dir) / "standards"
            standards_path.mkdir()

            engine = RAGEngine(index_path, standards_path)

            result = engine._grep_fallback(
                "nonexistent_term_xyz", n_results=5, filters=None
            )

            assert result.retrieval_method == "grep_fallback"
            assert len(result.chunks) == 0


# Test coverage target: 60%+ per project requirements
# This test suite provides comprehensive coverage of:
# - Initialization
# - Search term extraction
# - Cache management
# - Filter building
# - Result processing
# - Health checks
# - Grep fallback
