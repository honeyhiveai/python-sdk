"""
current_date: Reliable date/time tool for AI assistants.

Provides current date and time to prevent date errors in AI-generated content.
AI assistants frequently make date mistakes (using wrong dates, inconsistent formats).
This tool provides reliable, correctly-formatted dates.

Use cases:
- Creating specifications with correct dates
- Generating directory names with timestamps
- Adding date headers to documentation
- Any content requiring accurate current date

Architecture:
    AI Agent → current_date (Tools Layer)
        ↓
    System datetime (no dependencies)

Traceability:
    FR-010: current_date - Date/Time Tool
"""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def register_current_date_tool(mcp: Any) -> int:
    """
    Register current_date tool with MCP server.
    
    Provides reliable current date/time for AI assistants to prevent
    date-related errors in generated content.
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-010: current_date tool registration
    """
    
    @mcp.tool()
    async def current_date() -> Dict[str, Any]:
        """
        Get current date and time for preventing date errors in AI content.
        
        AI assistants frequently make date mistakes (using wrong dates,
        inconsistent formats). This tool provides the reliable current
        date/time that should be used for:
        - Creating specifications with correct dates
        - Generating directory names with timestamps
        - Adding date headers to documentation
        - Any content requiring accurate current date
        
        Returns ISO 8601 formatted date/time information to ensure consistency.
        
        Returns:
            Dictionary with current date/time in multiple useful formats:
            - iso_date: Primary format (YYYY-MM-DD)
            - iso_datetime: Full ISO 8601 timestamp
            - day_of_week: Human-readable day name
            - month: Human-readable month name
            - year: Current year
            - unix_timestamp: Unix epoch timestamp
            - formatted: Pre-formatted strings for common use cases
            - usage_note: Guidance on which format to use
        
        Examples:
            >>> result = await current_date()
            >>> print(result["iso_date"])  # 2025-11-05
            >>> print(result["formatted"]["spec_directory"])  # 2025-11-05-
            >>> print(result["day_of_week"])  # Tuesday
        
        Traceability:
            FR-010: current_date - Date/Time Tool
        """
        now = datetime.now()
        
        return {
            "iso_date": now.strftime("%Y-%m-%d"),  # Primary format: 2025-11-05
            "iso_datetime": now.isoformat(),  # Full ISO: 2025-11-05T14:30:00.123456
            "day_of_week": now.strftime("%A"),  # Tuesday
            "month": now.strftime("%B"),  # November
            "year": now.year,
            "unix_timestamp": int(now.timestamp()),
            "formatted": {
                # For .praxis-os/specs/YYYY-MM-DD-name/
                "spec_directory": f"{now.strftime('%Y-%m-%d')}-",
                # For markdown headers
                "header": f"**Date**: {now.strftime('%Y-%m-%d')}",
                "readable": now.strftime("%B %d, %Y"),  # November 05, 2025
            },
            "usage_note": (
                "Use 'iso_date' (YYYY-MM-DD) for all specifications, "
                "directories, and headers per prAxIs OS date policy"
            ),
        }
    
    logger.info("✅ Registered current_date tool")
    return 1  # One tool registered


__all__ = ["register_current_date_tool"]

