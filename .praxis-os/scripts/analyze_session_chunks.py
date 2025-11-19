#!/usr/bin/env python3
"""
Analyze Session Chunks

Reads all chunks from a chunked session file and extracts key information:
- User messages and requests
- Agent tool uses and outcomes
- Key decisions and turning points
- Problems encountered and solutions
- Final outcomes

Usage:
    python scripts/analyze_session_chunks.py <chunks_directory>
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def extract_user_messages(content: str) -> List[str]:
    """Extract user messages from chunk content."""
    messages = []
    # Look for user message markers
    pattern = r"\*\*User:\*\*\s*(?:<task>)?(.*?)(?:</task>)?(?=\*\*Assistant:\*\*|\*\*User:\*\*|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        msg = match.strip()
        if msg and len(msg) > 10:  # Filter out very short matches
            messages.append(msg[:500])  # First 500 chars
    return messages


def extract_tool_uses(content: str) -> List[Dict[str, str]]:
    """Extract tool uses from chunk content."""
    tools = []
    # Look for tool use patterns
    tool_pattern = r"<([a-z_]+)>.*?</\1>"
    matches = re.findall(
        r"<(use_mcp_tool|execute_command|read_file|write_to_file|replace_in_file|search_files|list_files|ask_followup_question|attempt_completion)>",
        content,
    )

    for match in matches:
        # Get some context around the tool
        idx = content.find(f"<{match}>")
        if idx != -1:
            context = content[max(0, idx - 100) : min(len(content), idx + 500)]
            tools.append({"tool": match, "context": context[:300]})

    return tools


def extract_key_phrases(content: str) -> List[str]:
    """Extract potentially important phrases."""
    phrases = []

    # Look for error patterns
    errors = re.findall(
        r"(?:error|Error|ERROR|failed|Failed|issue|Issue)[:\s]+([^\n]{20,100})",
        content,
        re.IGNORECASE,
    )
    phrases.extend([f"ERROR: {e.strip()}" for e in errors[:3]])

    # Look for success patterns
    successes = re.findall(
        r"(?:success|Success|completed|Completed|✓|✅)[:\s]+([^\n]{20,100})",
        content,
        re.IGNORECASE,
    )
    phrases.extend([f"SUCCESS: {s.strip()}" for s in successes[:3]])

    # Look for key decisions
    decisions = re.findall(
        r"(?:decision|Decision|approach|Approach|strategy|Strategy)[:\s]+([^\n]{20,100})",
        content,
        re.IGNORECASE,
    )
    phrases.extend([f"DECISION: {d.strip()}" for d in decisions[:2]])

    return phrases


def analyze_chunks(chunks_dir: Path) -> Dict[str, Any]:
    """Analyze all chunks and extract key information."""

    chunks_dir = Path(chunks_dir)
    if not chunks_dir.exists():
        raise FileNotFoundError(f"Chunks directory not found: {chunks_dir}")

    # Get all chunk files
    chunk_files = sorted(chunks_dir.glob("chunk_*.md"))

    if not chunk_files:
        raise ValueError(f"No chunk files found in {chunks_dir}")

    print(f"Analyzing {len(chunk_files)} chunks...")
    print()

    analysis = {
        "total_chunks": len(chunk_files),
        "user_messages": [],
        "tool_uses": {},
        "key_events": [],
        "errors": [],
        "successes": [],
    }

    for i, chunk_file in enumerate(chunk_files):
        print(f"Processing chunk {i}/{len(chunk_files)}...", end="\r")

        try:
            content = chunk_file.read_text(encoding="utf-8")

            # Extract user messages
            messages = extract_user_messages(content)
            if messages:
                for msg in messages:
                    analysis["user_messages"].append({"chunk": i, "message": msg})

            # Extract tool uses
            tools = extract_tool_uses(content)
            for tool_info in tools:
                tool_name = tool_info["tool"]
                if tool_name not in analysis["tool_uses"]:
                    analysis["tool_uses"][tool_name] = 0
                analysis["tool_uses"][tool_name] += 1

            # Extract key phrases
            phrases = extract_key_phrases(content)
            for phrase in phrases:
                if phrase.startswith("ERROR"):
                    analysis["errors"].append({"chunk": i, "text": phrase})
                elif phrase.startswith("SUCCESS"):
                    analysis["successes"].append({"chunk": i, "text": phrase})
                else:
                    analysis["key_events"].append({"chunk": i, "text": phrase})

        except Exception as e:
            print(f"\nError processing {chunk_file}: {e}")
            continue

    print("\nAnalysis complete!")
    return analysis


def print_analysis(analysis: Dict[str, Any], output_file: str = None):
    """Print or save the analysis results."""

    lines = []

    lines.append("=" * 80)
    lines.append("SESSION ANALYSIS")
    lines.append("=" * 80)
    lines.append("")

    lines.append(f"Total Chunks: {analysis['total_chunks']}")
    lines.append("")

    # Tool usage summary
    lines.append("TOOL USAGE SUMMARY")
    lines.append("-" * 80)
    for tool, count in sorted(
        analysis["tool_uses"].items(), key=lambda x: x[1], reverse=True
    ):
        lines.append(f"  {tool}: {count} times")
    lines.append("")

    # User messages (show first 10 and last 5)
    lines.append("USER MESSAGES (Key Interactions)")
    lines.append("-" * 80)
    messages = analysis["user_messages"]

    if len(messages) > 15:
        for msg in messages[:10]:
            lines.append(f"\n[Chunk {msg['chunk']}]")
            lines.append(msg["message"][:300])

        lines.append("\n... [middle messages omitted] ...\n")

        for msg in messages[-5:]:
            lines.append(f"\n[Chunk {msg['chunk']}]")
            lines.append(msg["message"][:300])
    else:
        for msg in messages:
            lines.append(f"\n[Chunk {msg['chunk']}]")
            lines.append(msg["message"][:300])
    lines.append("")

    # Errors
    if analysis["errors"]:
        lines.append("\nERRORS ENCOUNTERED")
        lines.append("-" * 80)
        for error in analysis["errors"][:10]:
            lines.append(f"[Chunk {error['chunk']}] {error['text']}")
        lines.append("")

    # Successes
    if analysis["successes"]:
        lines.append("\nSUCCESSES")
        lines.append("-" * 80)
        for success in analysis["successes"][:10]:
            lines.append(f"[Chunk {success['chunk']}] {success['text']}")
        lines.append("")

    # Key events
    if analysis["key_events"]:
        lines.append("\nKEY EVENTS/DECISIONS")
        lines.append("-" * 80)
        for event in analysis["key_events"][:10]:
            lines.append(f"[Chunk {event['chunk']}] {event['text']}")
        lines.append("")

    lines.append("=" * 80)

    output = "\n".join(lines)

    if output_file:
        Path(output_file).write_text(output, encoding="utf-8")
        print(f"\nAnalysis saved to: {output_file}")
    else:
        print(output)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: python scripts/analyze_session_chunks.py <chunks_directory> [output_file]"
        )
        print()
        print("Example:")
        print(
            "  python scripts/analyze_session_chunks.py other-sessions/cline_task_oct-11-2025_1-16-57-pm_chunks"
        )
        print(
            "  python scripts/analyze_session_chunks.py other-sessions/cline_task_oct-11-2025_1-16-57-pm_chunks analysis.txt"
        )
        sys.exit(1)

    chunks_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        analysis = analyze_chunks(chunks_dir)
        print_analysis(analysis, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
