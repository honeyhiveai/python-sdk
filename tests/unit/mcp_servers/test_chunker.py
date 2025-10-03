"""
Unit tests for Agent OS Document Chunker.

Tests chunking logic, metadata extraction, and dynamic analysis.
100% AI-authored via human orchestration.
"""

# Import from .agent-os package
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".agent-os"))

# pylint: disable=wrong-import-position
from mcp_servers.chunker import (
    AgentOSChunker,
    ChunkMetadata,
    count_tokens,
    parse_markdown_headers,
)


class TestTokenCounting:
    """Test token counting accuracy."""

    def test_token_counting_basic(self):
        """Test basic token counting."""
        text = "This is a test"  # ~14 chars / 4 = 3-4 tokens
        tokens = count_tokens(text)
        assert 3 <= tokens <= 4

    def test_token_counting_long_text(self):
        """Test token counting on longer text."""
        text = "This is a test " * 100  # ~1500 chars = ~375 tokens
        tokens = count_tokens(text)
        assert 350 <= tokens <= 400  # Allow reasonable variance

    def test_token_counting_empty(self):
        """Test token counting on empty string."""
        assert count_tokens("") == 0

    def test_token_counting_with_newlines(self):
        """Test that newlines are counted."""
        text = "Line 1\nLine 2\nLine 3"
        tokens = count_tokens(text)
        assert tokens > 0


class TestMarkdownHeaderParsing:
    """Test markdown header parsing logic."""

    def test_parse_single_header(self):
        """Test parsing single header section."""
        content = """## Phase 1
Content for phase 1
"""
        sections = parse_markdown_headers(content)
        assert len(sections) == 1
        assert sections[0]["header"] == "Phase 1"
        assert "Content for phase 1" in sections[0]["content"]

    def test_parse_multiple_headers(self):
        """Test parsing multiple header sections."""
        content = """## Phase 1
Content for phase 1

### Subheader
Sub content

## Phase 2
Content for phase 2
"""
        sections = parse_markdown_headers(content)
        assert len(sections) == 3
        assert sections[0]["header"] == "Phase 1"
        assert sections[1]["header"] == "Subheader"
        assert sections[2]["header"] == "Phase 2"

    def test_header_level_detection(self):
        """Test that header levels are correctly identified."""
        content = """## Level 2
Content

### Level 3
More content
"""
        sections = parse_markdown_headers(content)
        assert sections[0]["level"] == 2
        assert sections[1]["level"] == 3

    def test_ignore_level_1_headers(self):
        """Test that # headers are ignored (only ## and ### processed)."""
        content = """# Title
Should be ignored

## Phase 1
Should be parsed
"""
        sections = parse_markdown_headers(content)
        assert len(sections) == 1
        assert sections[0]["header"] == "Phase 1"

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        sections = parse_markdown_headers("")
        assert len(sections) == 0

    def test_parse_no_headers(self):
        """Test parsing content with no headers."""
        content = "Just some text without headers"
        sections = parse_markdown_headers(content)
        assert len(sections) == 0


class TestChunkingLogic:
    """Test document chunking logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.chunker = AgentOSChunker()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_chunk_small_section(self):
        """Test that small sections become single chunks."""
        chunker = AgentOSChunker()
        content = """## Test Section
This is a small section with minimal content.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks = chunker.chunk_file(filepath)
            assert len(chunks) >= 1
            assert chunks[0].section_header == "Test Section"
            assert chunks[0].tokens < 500
        finally:
            filepath.unlink()

    def test_chunk_large_section_splits(self):
        """Test that large sections are split into multiple chunks."""
        chunker = AgentOSChunker()
        # Create content > 500 tokens with multiple paragraphs for splitting
        # ~400 chars = ~100 tokens
        paragraph = "This is a paragraph. " * 20
        # Create 6 paragraphs = ~600 tokens total (> 500, so should split)
        large_content = (
            f"{paragraph}\n\n{paragraph}\n\n{paragraph}\n\n"
            f"{paragraph}\n\n{paragraph}\n\n{paragraph}"
        )
        content = f"""## Large Section

{large_content}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks = chunker.chunk_file(filepath)
            # Should split into multiple chunks
            for chunk in chunks:
                assert chunk.tokens <= 500  # Respects MAX_CHUNK_TOKENS
        finally:
            filepath.unlink()

    def test_chunk_preserves_metadata(self):
        """Test that chunks preserve metadata correctly."""
        chunker = AgentOSChunker()
        content = """## Test Section
This section contains **CRITICAL** requirements.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks = chunker.chunk_file(filepath)
            assert len(chunks) >= 1
            assert chunks[0].metadata is not None
            assert isinstance(chunks[0].metadata, ChunkMetadata)
        finally:
            filepath.unlink()

    def test_chunk_id_generation(self):
        """Test that chunk IDs are generated consistently."""
        chunker = AgentOSChunker()
        content = """## Test Section
Same content every time.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks1 = chunker.chunk_file(filepath)
            chunks2 = chunker.chunk_file(filepath)
            # Same content should produce same chunk ID
            assert chunks1[0].chunk_id == chunks2[0].chunk_id
        finally:
            filepath.unlink()


class TestMetadataExtraction:
    """Test metadata extraction logic."""

    def test_extract_phase_number(self):
        """Test phase number extraction."""
        chunker = AgentOSChunker()
        content = "This is Phase 1 of the workflow."
        phase = chunker._extract_phase_number(content)
        assert phase == 1

    def test_extract_phase_number_multiple(self):
        """Test that first phase number is extracted."""
        chunker = AgentOSChunker()
        content = "Phase 1 before Phase 2"
        phase = chunker._extract_phase_number(content)
        assert phase == 1

    def test_extract_phase_number_none(self):
        """Test no phase number found."""
        chunker = AgentOSChunker()
        content = "No phase information here."
        phase = chunker._extract_phase_number(content)
        assert phase is None

    def test_detect_critical_emphasis(self):
        """Test critical emphasis detection."""
        chunker = AgentOSChunker()

        # Test uppercase emphasis
        assert chunker._has_critical_emphasis("**CRITICAL:** This is important")

        # Test emoji emphasis
        assert chunker._has_critical_emphasis("🚨 Warning: Critical issue")

        # Test requirement language with emphasis
        assert chunker._has_critical_emphasis("**This is REQUIRED**")

        # Test normal text
        assert not chunker._has_critical_emphasis("This is normal text.")

    def test_analyze_content_topics(self):
        """Test content topic analysis."""
        chunker = AgentOSChunker()

        # Test mocking topic
        content_mock = "Use unittest.mock to create test mocks."
        tags = chunker._analyze_content_topics(content_mock)
        assert "mocking" in tags

        # Test testing topic
        content_test = "Run pytest with fixtures and assertions."
        tags = chunker._analyze_content_topics(content_test)
        assert "testing" in tags

        # Test workflow topic
        content_workflow = "Complete Phase 1 checkpoint before proceeding."
        tags = chunker._analyze_content_topics(content_workflow)
        assert "workflow" in tags

    def test_extract_code_block_terms(self):
        """Test code block term extraction."""
        chunker = AgentOSChunker()
        content = """
Some text before

```python
import pytest
def test_example():
    assert True
```

Some text after
"""
        terms = chunker._extract_code_block_terms(content.lower())
        assert "import" in terms
        assert "pytest" in terms

    def test_extract_header_hierarchy(self):
        """Test header hierarchy extraction."""
        chunker = AgentOSChunker()
        content = """## Main Header
Content

### Subheader
More content
"""
        headers = chunker._extract_header_hierarchy(content)
        assert len(headers) >= 1
        assert "Main Header" in headers[0]

    def test_infer_framework_type(self):
        """Test framework type inference from path."""
        chunker = AgentOSChunker()

        # Test test framework detection
        path_parts = ("path", "to", "tests", "v3", "README.md")
        framework = chunker._infer_framework_type(path_parts, "")
        assert "test" in framework or framework == "test_v3"

        # Test production framework detection
        path_parts = ("path", "to", "production", "v2", "guide.md")
        framework = chunker._infer_framework_type(path_parts, "")
        assert "production" in framework or framework == "production_v2"

        # Test general detection
        path_parts = ("path", "to", "standards", "README.md")
        framework = chunker._infer_framework_type(path_parts, "")
        assert framework == "general"


class TestDirectoryChunking:
    """Test directory-level chunking."""

    def test_chunk_directory_recursive(self):
        """Test that directory chunking finds files recursively."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested structure
            subdir = temp_path / "subdir"
            subdir.mkdir()

            # Create markdown files
            (temp_path / "file1.md").write_text("## Section 1\nContent")
            (subdir / "file2.md").write_text("## Section 2\nMore content")

            chunker = AgentOSChunker()
            chunks = chunker.chunk_directory(temp_path)

            assert len(chunks) >= 2  # At least 2 chunks from 2 files

    def test_chunk_directory_skips_build_artifacts(self):
        """Test that build artifacts are skipped."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create build directory
            build_dir = temp_path / "_build"
            build_dir.mkdir()

            # Create files
            (temp_path / "file1.md").write_text("## Section 1\nContent")
            (build_dir / "file2.md").write_text("## Section 2\nShould skip")

            chunker = AgentOSChunker()
            chunks = chunker.chunk_directory(temp_path)

            # Should only get chunks from file1.md
            file_paths = [chunk.file_path for chunk in chunks]
            assert not any("_build" in path for path in file_paths)

    def test_chunk_directory_empty(self):
        """Test chunking empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            chunker = AgentOSChunker()
            chunks = chunker.chunk_directory(temp_path)
            assert len(chunks) == 0


class TestChunkIntegrity:
    """Test chunk data integrity."""

    def test_chunk_has_required_fields(self):
        """Test that chunks have all required fields."""
        chunker = AgentOSChunker()
        content = """## Test Section
Test content for chunk.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks = chunker.chunk_file(filepath)
            assert len(chunks) >= 1

            chunk = chunks[0]
            assert chunk.chunk_id is not None
            assert chunk.file_path is not None
            assert chunk.section_header is not None
            assert chunk.content is not None
            assert chunk.tokens > 0
            assert chunk.metadata is not None
        finally:
            filepath.unlink()

    def test_metadata_has_required_fields(self):
        """Test that metadata has all required fields."""
        chunker = AgentOSChunker()
        content = """## Test Section
Test content with metadata.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            chunks = chunker.chunk_file(filepath)
            metadata = chunks[0].metadata

            assert metadata.framework_type is not None
            assert isinstance(metadata.phase, (int, type(None)))
            assert metadata.category is not None
            assert isinstance(metadata.tags, list)
            assert isinstance(metadata.is_critical, bool)
            assert isinstance(metadata.parent_headers, list)
        finally:
            filepath.unlink()


# Test coverage target: 60%+ per project requirements
# This test suite provides comprehensive coverage of:
# - Token counting
# - Header parsing
# - Chunking logic
# - Metadata extraction
# - Directory operations
# - Data integrity
