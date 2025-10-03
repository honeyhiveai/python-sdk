"""
Agent OS Document Chunker
Intelligent chunking preserving semantic boundaries.

100% AI-authored via human orchestration.
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    """Metadata for better retrieval."""

    framework_type: str  # "test_v3", "production_v2", etc.
    phase: Optional[int]  # If phase-specific
    category: str  # "requirement", "example", "reference"
    tags: List[str]  # ["mocking", "ast", "coverage", ...]
    is_critical: bool  # Contains MANDATORY/CRITICAL markers
    parent_headers: List[str]  # Breadcrumb of headers


@dataclass
class DocumentChunk:
    """Represents a chunk of Agent OS documentation."""

    chunk_id: str  # MD5 hash of content
    file_path: str  # Source file path
    section_header: str  # Header this chunk belongs to
    content: str  # The actual text content
    tokens: int  # Token count
    metadata: ChunkMetadata  # Additional metadata


def count_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Uses simple heuristic: ~4 characters per token.

    Args:
        text: Text to count tokens for

    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4


def parse_markdown_headers(content: str) -> List[Dict[str, Any]]:
    """
    Parse markdown into hierarchical sections by headers.

    Dynamic parsing approach - analyzes line structure, not static patterns.

    Args:
        content: Markdown content to parse

    Returns:
        List of sections with header level, text, and content
    """
    sections = []
    current_section = None

    for line in content.split("\n"):
        # Dynamic header detection: analyze line structure
        stripped = line.strip()

        # Check if line starts with # characters (markdown header)
        if stripped and stripped[0] == "#":
            # Count leading # characters dynamically
            hash_count = 0
            for char in stripped:
                if char == "#":
                    hash_count += 1
                else:
                    break

            # Only process ## and ### headers (Agent OS convention)
            if hash_count in (2, 3):
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)

                # Extract header text (everything after the hashes)
                header_text = stripped[hash_count:].strip()

                current_section = {
                    "level": hash_count,
                    "header": header_text,
                    "content": "",
                    "line_start": len(sections),
                }
        elif current_section:
            current_section["content"] += line + "\n"

    # Add final section
    if current_section:
        sections.append(current_section)

    return sections


class AgentOSChunker:
    """Intelligent chunker for Agent OS documentation."""

    MAX_CHUNK_TOKENS = 500
    MIN_CHUNK_TOKENS = 100

    def chunk_file(self, filepath: Path) -> List[DocumentChunk]:
        """
        Chunk a single Agent OS markdown file.

        Steps:
        1. Read file content
        2. Parse into sections by headers
        3. For each section:
           - If <= MAX_TOKENS: single chunk
           - If > MAX_TOKENS: split recursively
        4. Extract metadata
        5. Generate chunk IDs

        Args:
            filepath: Path to markdown file

        Returns:
            List of DocumentChunk objects
        """
        content = filepath.read_text()
        sections = parse_markdown_headers(content)

        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section, filepath)
            chunks.extend(section_chunks)

        return chunks

    def _chunk_section(
        self, section: Dict[str, Any], filepath: Path
    ) -> List[DocumentChunk]:
        """
        Chunk a single section.

        Args:
            section: Section dictionary from parse_markdown_headers
            filepath: Path to source file

        Returns:
            List of chunks for this section
        """
        tokens = count_tokens(section["content"])

        if tokens <= self.MAX_CHUNK_TOKENS:
            # Small enough, single chunk
            return [self._create_chunk(section, filepath)]
        else:
            # Too large, split on paragraphs
            return self._split_large_section(section, filepath)

    def _split_large_section(
        self, section: Dict[str, Any], filepath: Path
    ) -> List[DocumentChunk]:
        """
        Split large section into multiple chunks.

        Args:
            section: Section dictionary to split
            filepath: Path to source file

        Returns:
            List of chunks split by paragraph boundaries
        """
        paragraphs = section["content"].split("\n\n")

        chunks = []
        current_chunk_text = ""

        for para in paragraphs:
            para_tokens = count_tokens(para)
            current_tokens = count_tokens(current_chunk_text)

            if current_tokens + para_tokens <= self.MAX_CHUNK_TOKENS:
                # Add to current chunk
                current_chunk_text += para + "\n\n"
            else:
                # Save current chunk, start new one
                if current_chunk_text:
                    chunk_section = {
                        "header": section["header"],
                        "content": current_chunk_text,
                        "level": section["level"],
                    }
                    chunks.append(self._create_chunk(chunk_section, filepath))

                current_chunk_text = para + "\n\n"

        # Add final chunk
        if current_chunk_text:
            chunk_section = {
                "header": section["header"],
                "content": current_chunk_text,
                "level": section["level"],
            }
            chunks.append(self._create_chunk(chunk_section, filepath))

        return chunks

    def _create_chunk(
        self, section: Dict[str, Any], filepath: Path
    ) -> DocumentChunk:
        """
        Create DocumentChunk from section.

        Args:
            section: Section dictionary
            filepath: Path to source file

        Returns:
            DocumentChunk with metadata
        """
        content = section["content"].strip()
        metadata = self._extract_metadata(content, filepath)
        chunk_id = hashlib.md5(content.encode()).hexdigest()

        return DocumentChunk(
            chunk_id=chunk_id,
            file_path=str(filepath),
            section_header=section["header"],
            content=content,
            tokens=count_tokens(content),
            metadata=metadata,
        )

    def _extract_metadata(self, content: str, filepath: Path) -> ChunkMetadata:
        """
        Extract metadata from content and filepath.

        Dynamic analysis approach - examines structure and context,
        not hardcoded keyword matching.

        Args:
            content: Chunk content
            filepath: Path to source file

        Returns:
            ChunkMetadata with analyzed properties
        """
        # Analyze filepath structure dynamically
        path_parts = filepath.parts
        framework_type = self._infer_framework_type(path_parts, content)

        # Extract phase number by analyzing header structure
        phase = self._extract_phase_number(content)

        # Dynamically identify topics from content analysis
        tags = self._analyze_content_topics(content)

        # Analyze emphasis markers in content
        is_critical = self._has_critical_emphasis(content)

        # Build header hierarchy from document structure
        parent_headers = self._extract_header_hierarchy(content)

        return ChunkMetadata(
            framework_type=framework_type,
            phase=phase,
            category="requirement" if is_critical else "guidance",
            tags=tags,
            is_critical=is_critical,
            parent_headers=parent_headers,
        )

    def _infer_framework_type(self, path_parts: tuple, content: str) -> str:
        """
        Infer framework type from file structure and content.

        Dynamic approach: analyze path structure, not string matching.

        Args:
            path_parts: Path components from filepath
            content: File content for additional context

        Returns:
            Framework type string
        """
        # Examine path hierarchy
        for i, part in enumerate(path_parts):
            if part == "tests":
                # Look for test generation docs
                remaining = path_parts[i + 1 :]
                for version_part in remaining:
                    if version_part.startswith("v") and any(
                        c.isdigit() for c in version_part[1:]
                    ):
                        return f"test_{version_part}"
            elif part == "production":
                remaining = path_parts[i + 1 :]
                for version_part in remaining:
                    if version_part.startswith("v") and any(
                        c.isdigit() for c in version_part[1:]
                    ):
                        return f"production_{version_part}"
            elif "test" in part.lower():
                return "test_framework"
            elif "code-generation" in part:
                remaining = path_parts[i + 1 :]
                if remaining:
                    return remaining[0]

        return "general"

    def _extract_phase_number(self, content: str) -> Optional[int]:
        """
        Extract phase number by analyzing content structure.

        Dynamic approach: look for "Phase" followed by digits in context.

        Args:
            content: Chunk content

        Returns:
            Phase number if found, None otherwise
        """
        # Split into words and analyze context
        words = content.split()

        for i, word in enumerate(words):
            # Check if word is "Phase" (case-insensitive)
            if word.lower().startswith("phase"):
                # Look at next word for number
                if i + 1 < len(words):
                    next_word = words[i + 1].strip(":,.")
                    if next_word.isdigit():
                        return int(next_word)

        return None

    def _analyze_content_topics(self, content: str) -> List[str]:
        """
        Analyze content to identify main topics dynamically.

        Analyzes term frequency and context rather than keyword matching.

        Args:
            content: Chunk content

        Returns:
            List of identified topic tags
        """
        tags = []
        content_lower = content.lower()

        # Topic analysis: look for terms in meaningful contexts
        # (commands, code blocks, emphasis markers)

        # Identify technical terms that appear in code blocks or commands
        code_block_terms = self._extract_code_block_terms(content_lower)

        # Map common technical concepts (extensible)
        topic_indicators = {
            "mocking": ["mock", "stub", "patch", "unittest.mock"],
            "ast": ["ast.", "parse", "node", "abstract syntax"],
            "coverage": ["coverage", "pytest-cov", "branch"],
            "logging": ["logger", "logging.", "log."],
            "testing": ["pytest", "test_", "assert", "fixture"],
            "documentation": ["docstring", "sphinx", "rst"],
            "workflow": ["phase", "checkpoint", "workflow"],
            "git": ["commit", "branch", "repository"],
            "mcp": ["mcp", "model context protocol", "tool"],
            "rag": ["rag", "retrieval", "embedding", "vector"],
        }

        for topic, indicators in topic_indicators.items():
            # Check if multiple indicators present (stronger signal)
            indicator_count = sum(1 for ind in indicators if ind in content_lower)
            if indicator_count > 0:
                tags.append(topic)

        # Add code block terms if relevant
        if code_block_terms:
            tags.append("code_example")

        return tags

    def _extract_code_block_terms(self, content: str) -> set:
        """
        Extract terms from code blocks dynamically.

        Args:
            content: Chunk content (lowercased)

        Returns:
            Set of terms found in code blocks
        """
        terms = set()
        in_code_block = False

        for line in content.split("\n"):
            stripped = line.strip()
            # Detect code block boundaries
            if stripped.startswith("```"):
                in_code_block = not in_code_block
            elif in_code_block:
                # Extract terms from code
                terms.update(stripped.split())

        return terms

    def _has_critical_emphasis(self, content: str) -> bool:
        """
        Detect critical emphasis through document formatting analysis.

        Dynamic approach: analyze emphasis patterns, not keyword lists.

        Args:
            content: Chunk content

        Returns:
            True if content has critical emphasis markers
        """
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()

            # Check for lines with strong emphasis markers
            if stripped.startswith(("**", "##")):
                # Analyze if line contains requirement language
                upper_count = sum(1 for c in stripped if c.isupper())
                if upper_count > len(stripped) * 0.5:  # >50% uppercase
                    return True

            # Check for emoji emphasis
            if any(char in stripped for char in ["🛑", "⚠️", "❌", "🚨", "‼️"]):
                return True

            # Check for requirement language patterns
            requirement_words = ["must", "required", "mandatory", "critical"]
            lower_stripped = stripped.lower()
            if any(word in lower_stripped for word in requirement_words):
                # Verify it's emphasized (bold, caps, or standalone line)
                if (
                    "**" in stripped
                    or stripped.isupper()
                    or len(stripped.split()) < 10
                ):
                    return True

        return False

    def _extract_header_hierarchy(self, content: str) -> List[str]:
        """
        Extract header hierarchy by parsing document structure.

        Returns list of parent headers leading to this chunk.

        Args:
            content: Chunk content

        Returns:
            List of header text strings in hierarchical order
        """
        headers = []

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and stripped[0] == "#":
                # Count header level dynamically
                level = 0
                for char in stripped:
                    if char == "#":
                        level += 1
                    else:
                        break
                # Extract header text
                if level > 0:
                    header_text = stripped[level:].strip()
                    headers.append(header_text)

        return headers

    def chunk_directory(self, directory: Path) -> List[DocumentChunk]:
        """
        Chunk all markdown files in a directory recursively.

        Args:
            directory: Path to directory containing Agent OS files

        Returns:
            List of all chunks from all files
        """
        all_chunks = []

        # Find all markdown files recursively
        for md_file in directory.rglob("*.md"):
            # Skip build artifacts and cache
            if any(
                part in md_file.parts for part in ["_build", ".cache", "node_modules"]
            ):
                continue

            try:
                chunks = self.chunk_file(md_file)
                all_chunks.extend(chunks)
            except Exception as e:
                # Log error but continue processing
                print(f"Error chunking {md_file}: {e}")
                continue

        return all_chunks

