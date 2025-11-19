"""
Markdown AST traversal utilities.

Functions for navigating mistletoe Document structures and extracting
headers, lists, and other markdown elements.

Target: ~200 lines
"""

from typing import List, Optional

from mistletoe import Document
from mistletoe.block_token import Heading, List as MarkdownList, ListItem, Paragraph
from mistletoe.span_token import LineBreak, RawText, Strong


def get_text_content(node) -> str:
    """
    Extract all text content from an AST node and its children.

    Recursively traverses the AST and concatenates text content
    while preserving structure (paragraphs, line breaks).

    Args:
        node: Mistletoe AST node

    Returns:
        Concatenated text content with preserved structure

    Examples:
        >>> from mistletoe import Document
        >>> doc = Document("# Hello\\nWorld")
        >>> get_text_content(doc)
        "Hello\\nWorld"
    """
    if not node:
        return ""

    if isinstance(node, RawText):
        return str(node.content)

    if isinstance(node, LineBreak):
        return "\n"

    if isinstance(node, ListItem):
        return extract_list_item_text(node)

    if hasattr(node, "children") and node.children is not None:
        # Strong nodes: just return first child's content
        if isinstance(node, Strong) and node.children:
            # Convert to list if needed to access first element
            children_list = list(node.children)
            if children_list:
                return get_text_content(children_list[0])

        parts = []
        for child in node.children:
            text = get_text_content(child)
            if text:
                parts.append(text)
        # For paragraph nodes, inline elements join without newlines
        return "".join(parts)

    return str(node)


def extract_list_item_text(node: ListItem) -> str:
    """
    Extract text from a ListItem node with proper structure.

    Handles nested lists and paragraphs within list items,
    preserving checkbox markers and indentation.

    Args:
        node: ListItem AST node

    Returns:
        Extracted text with structure preserved
    """
    parts: List[str] = []
    inline_buffer: List[str] = []
    checkbox_marker = get_checkbox_marker(node)

    for child in node.children if node.children else []:
        if isinstance(child, MarkdownList):
            # Flush inline buffer before nested list
            checkbox_marker = flush_inline_buffer(
                inline_buffer, checkbox_marker, parts
            )
            inline_buffer = []
            # Extract nested list items
            for nested_item in child.children if child.children else []:
                nested_text = get_text_content(nested_item)
                if nested_text:
                    parts.append(nested_text)
        elif isinstance(child, Paragraph):
            # Flush inline buffer before paragraph
            checkbox_marker = flush_inline_buffer(
                inline_buffer, checkbox_marker, parts
            )
            inline_buffer = []
            text = get_text_content(child)
            if text:
                parts.append(text)
        else:
            # Accumulate inline content
            text = get_text_content(child)
            if text:
                inline_buffer.append(text)

    # Flush remaining inline content
    flush_inline_buffer(inline_buffer, checkbox_marker, parts)
    return "\n".join(parts)


def get_checkbox_marker(node: ListItem) -> str:
    """
    Get checkbox marker for a list item.

    Args:
        node: ListItem AST node

    Returns:
        Checkbox marker string ("- [x] " or "- [ ] ") or empty string

    Examples:
        >>> marker = get_checkbox_marker(some_list_item)
        "- [ ] "
    """
    if not hasattr(node, "checked"):
        return ""
    checked_val = getattr(node, "checked", None)
    if checked_val is None:
        return ""
    return "- [x] " if checked_val else "- [ ] "


def flush_inline_buffer(
    inline_buffer: list, checkbox_marker: str, parts: list
) -> str:
    """
    Flush inline buffer to parts list and return updated checkbox marker.

    Args:
        inline_buffer: List of inline text fragments
        checkbox_marker: Current checkbox marker
        parts: List to append flushed content to

    Returns:
        Updated checkbox marker (empty string if used)
    """
    if not inline_buffer:
        return checkbox_marker

    content = "".join(inline_buffer)
    if checkbox_marker and not parts:
        parts.append(checkbox_marker + content)
        return ""  # Marker used
    parts.append(content)
    return checkbox_marker


def extract_checklist_items(node) -> List[str]:
    """
    Extract checklist items from a node's children.

    Finds all checkbox list items ("- [ ] item") and extracts their text.

    Args:
        node: AST node to search

    Returns:
        List of checklist item strings (without checkboxes)

    Examples:
        >>> items = extract_checklist_items(some_node)
        ["Complete task 1", "Complete task 2"]
    """
    items = []
    text = get_text_content(node)

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            item = stripped[5:].strip()
            if item:
                items.append(item)
        elif stripped.startswith("[ ]"):
            # Handle cases where dash is missing (nested items)
            item = stripped[3:].strip()
            if item:
                items.append(item)

    return items


def find_headers(doc: Document, level: Optional[int] = None) -> List[Heading]:
    """
    Find all headers in document, optionally filtered by level.

    Args:
        doc: Mistletoe Document
        level: Optional header level to filter (1-6, where 1 is #)

    Returns:
        List of Heading nodes

    Examples:
        >>> headers = find_headers(doc, level=2)  # Find all ## headers
    """
    headers = []

    def traverse(node):
        if isinstance(node, Heading):
            if level is None or node.level == level:
                headers.append(node)

        if hasattr(node, "children") and node.children:
            for child in node.children:
                traverse(child)

    children = doc.children or []
    for child in children:
        traverse(child)

    return headers


__all__ = [
    "get_text_content",
    "extract_list_item_text",
    "get_checkbox_marker",
    "flush_inline_buffer",
    "extract_checklist_items",
    "find_headers",
]
