"""
Custom Hatch build hook for version-based package builds.

Note: The actual exclusion of _v0/ or _v1/ is done by scripts/filter_wheel.py
as a post-processing step, since hatchling's exclude mechanism doesn't work
well with build hooks for wheel targets.

This hook is kept for potential future use and compatibility.
"""

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class VersionExclusionHook(BuildHookInterface):
    """Build hook placeholder for version-based builds."""

    PLUGIN_NAME = "version-exclusion"

    def initialize(self, version: str, build_data: dict) -> None:
        """Initialize the build hook (placeholder)."""
        pass
