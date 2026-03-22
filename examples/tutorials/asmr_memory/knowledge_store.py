"""
Knowledge Store - Structured Agent Findings Store

Pure structured storage with session-to-finding mappings.
No embeddings - all retrieval is done via agentic search.

This maps to the "Knowledge Store" component in the ASMR architecture diagram.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FindingCategory(str, Enum):
    """Six knowledge extraction vectors from the ASMR paper."""

    PERSONAL_INFO = "personal_info"
    PREFERENCES = "preferences"
    EVENTS = "events"
    TEMPORAL_DATA = "temporal_data"
    UPDATES = "updates"
    ASSISTANT_INFO = "assistant_info"


class FindingSource(str, Enum):
    """Which observer agent produced the finding."""

    FACT_HUNTER = "fact_hunter"
    CONTEXT_WEAVER = "context_weaver"
    TIMELINE_TRACKER = "timeline_tracker"


@dataclass
class Finding:
    """A single structured finding extracted by an observer agent."""

    id: str
    category: FindingCategory
    source_agent: FindingSource
    content: str
    session_ids: List[str]
    entities: List[str] = field(default_factory=list)
    timestamp: Optional[str] = None
    event_date: Optional[str] = None
    confidence: float = 1.0
    supersedes: Optional[str] = None  # ID of finding this updates/replaces
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "source_agent": self.source_agent.value,
            "content": self.content,
            "session_ids": self.session_ids,
            "entities": self.entities,
            "timestamp": self.timestamp,
            "event_date": self.event_date,
            "confidence": self.confidence,
            "supersedes": self.supersedes,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class KnowledgeStore:
    """In-memory structured knowledge store with session-to-finding mappings.

    Thread-safe storage for findings produced by observer agents.
    Supports querying by category, entity, session, and text search.
    """

    def __init__(self) -> None:
        self._findings: Dict[str, Finding] = {}
        self._session_index: Dict[str, List[str]] = {}  # session_id -> finding_ids
        self._entity_index: Dict[str, List[str]] = {}  # entity -> finding_ids
        self._category_index: Dict[str, List[str]] = {}  # category -> finding_ids
        self._lock = threading.Lock()
        self._finding_counter = 0

    def _next_id(self) -> str:
        self._finding_counter += 1
        return f"finding_{self._finding_counter:06d}"

    def add_finding(self, finding: Finding) -> str:
        """Add a finding to the store. Returns the finding ID."""
        with self._lock:
            if not finding.id:
                finding.id = self._next_id()

            self._findings[finding.id] = finding

            # Update session index
            for session_id in finding.session_ids:
                if session_id not in self._session_index:
                    self._session_index[session_id] = []
                self._session_index[session_id].append(finding.id)

            # Update entity index
            for entity in finding.entities:
                entity_key = entity.lower()
                if entity_key not in self._entity_index:
                    self._entity_index[entity_key] = []
                self._entity_index[entity_key].append(finding.id)

            # Update category index
            cat_key = finding.category.value
            if cat_key not in self._category_index:
                self._category_index[cat_key] = []
            self._category_index[cat_key].append(finding.id)

            return finding.id

    def add_findings_batch(self, findings: List[Finding]) -> List[str]:
        """Add multiple findings at once. Returns list of finding IDs."""
        ids = []
        for finding in findings:
            ids.append(self.add_finding(finding))
        return ids

    def get_finding(self, finding_id: str) -> Optional[Finding]:
        """Get a finding by ID."""
        return self._findings.get(finding_id)

    def get_by_session(self, session_id: str) -> List[Finding]:
        """Get all findings associated with a session."""
        finding_ids = self._session_index.get(session_id, [])
        return [self._findings[fid] for fid in finding_ids if fid in self._findings]

    def get_by_entity(self, entity: str) -> List[Finding]:
        """Get all findings mentioning an entity."""
        entity_key = entity.lower()
        finding_ids = self._entity_index.get(entity_key, [])
        return [self._findings[fid] for fid in finding_ids if fid in self._findings]

    def get_by_category(self, category: FindingCategory) -> List[Finding]:
        """Get all findings in a category."""
        finding_ids = self._category_index.get(category.value, [])
        return [self._findings[fid] for fid in finding_ids if fid in self._findings]

    def get_all(self) -> List[Finding]:
        """Get all findings in the store."""
        return list(self._findings.values())

    def get_all_findings(self) -> List[Finding]:
        """Get all findings in the store (alias for get_all)."""
        return self.get_all()

    def get_recent_findings(self, limit: int = 50) -> List[Finding]:
        """Get the most recent findings, ordered by creation time."""
        all_findings = list(self._findings.values())
        all_findings.sort(key=lambda f: f.created_at, reverse=True)
        return all_findings[:limit]

    def search_text(self, query: str) -> List[Finding]:
        """Simple text search across finding content."""
        query_lower = query.lower()
        results = []
        for finding in self._findings.values():
            if query_lower in finding.content.lower():
                results.append(finding)
        return results

    def get_superseded_chain(self, finding_id: str) -> List[Finding]:
        """Get the chain of findings that supersede each other (knowledge updates)."""
        chain = []
        current_id = finding_id
        visited = set()
        while current_id and current_id not in visited:
            visited.add(current_id)
            finding = self._findings.get(current_id)
            if finding:
                chain.append(finding)
                current_id = finding.supersedes
            else:
                break
        return chain

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_findings": len(self._findings),
            "total_sessions": len(self._session_index),
            "total_entities": len(self._entity_index),
            "categories": {cat: len(ids) for cat, ids in self._category_index.items()},
        }

    def to_context_string(self, findings: Optional[List[Finding]] = None) -> str:
        """Convert findings to a string suitable for LLM context injection."""
        if findings is None:
            findings = self.get_all_findings()

        if not findings:
            return "No knowledge findings available."

        lines = []
        for f in findings:
            line = f"[{f.category.value}] {f.content}"
            if f.timestamp:
                line += f" (recorded: {f.timestamp})"
            if f.event_date:
                line += f" (event date: {f.event_date})"
            if f.supersedes:
                line += " [UPDATED]"
            lines.append(line)

        return "\n".join(lines)

    def export_json(self) -> str:
        """Export the entire store as JSON."""
        return json.dumps(
            {
                "findings": [f.to_dict() for f in self._findings.values()],
                "stats": self.get_stats(),
            },
            indent=2,
        )
