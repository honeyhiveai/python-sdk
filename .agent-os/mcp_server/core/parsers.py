"""
Source parsers for dynamic workflow content.

Provides abstract interface and concrete implementations for parsing
external sources (like spec tasks.md files) into structured workflow data.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from mcp_server.models.workflow import DynamicPhase, DynamicTask


class ParseError(Exception):
    """Raised when source parsing fails."""
    
    pass


class SourceParser(ABC):
    """
    Abstract parser for dynamic workflow sources.
    
    Subclasses implement parsing for specific source formats
    (e.g., tasks.md files, Jira API, GitHub Issues, etc.).
    """
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse source into structured phase/task data.
        
        Args:
            source_path: Path to source file or directory
            
        Returns:
            List of DynamicPhase objects with populated tasks
            
        Raises:
            ParseError: If source is invalid or cannot be parsed
        """
        pass


class SpecTasksParser(SourceParser):
    """
    Parser for Agent OS spec tasks.md files.
    
    Extracts phases, tasks, acceptance criteria, dependencies,
    and validation gates from markdown-formatted specification files.
    
    Expected format:
        ### Phase N: Name
        **Goal:** Description
        **Estimated Duration:** X hours
        **Tasks:**
        - [ ] **Task N.M**: Name
          - **Estimated Time**: X hours
          - **Dependencies**: Task A, Task B
          - **Acceptance Criteria**:
            - [ ] Criterion 1
            - [ ] Criterion 2
        **Validation Gate:**
        - [ ] Gate criterion 1
        - [ ] Gate criterion 2
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse spec's tasks.md file into structured phases.
        
        Args:
            source_path: Path to tasks.md file
            
        Returns:
            List of DynamicPhase objects
            
        Raises:
            ParseError: If file format is invalid
        """
        if not source_path.exists():
            raise ParseError(f"Source file not found: {source_path}")
        
        if source_path.is_dir():
            # If directory provided, look for tasks.md
            source_path = source_path / "tasks.md"
            if not source_path.exists():
                raise ParseError(f"tasks.md not found in directory: {source_path.parent}")
        
        try:
            content = source_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParseError(f"Failed to read {source_path}: {e}")
        
        if not content.strip():
            raise ParseError(f"Source file is empty: {source_path}")
        
        # Split into phase sections
        phase_sections = self._split_phases(content)
        
        if not phase_sections:
            raise ParseError(f"No phases found in {source_path}")
        
        phases = []
        for section in phase_sections:
            try:
                phase = self._parse_phase_section(section)
                phases.append(phase)
            except Exception as e:
                raise ParseError(f"Failed to parse phase section: {e}")
        
        return phases
    
    def _split_phases(self, content: str) -> List[str]:
        """
        Split content by ### Phase headers.
        
        Args:
            content: Full markdown content
            
        Returns:
            List of phase section strings
        """
        # Match ### Phase N: Name headers
        phase_pattern = r'^### Phase (\d+):'
        
        sections = []
        current_section = []
        in_phase = False
        
        for line in content.split('\n'):
            if re.match(phase_pattern, line):
                if current_section and in_phase:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_phase = True
            elif in_phase:
                current_section.append(line)
        
        # Add last section
        if current_section and in_phase:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _parse_phase_section(self, section: str) -> DynamicPhase:
        """
        Parse single phase section into DynamicPhase.
        
        Args:
            section: Phase section markdown
            
        Returns:
            DynamicPhase object
        """
        lines = section.split('\n')
        
        # Extract phase header
        header_match = re.match(r'^### Phase (\d+): (.+)$', lines[0])
        if not header_match:
            raise ValueError(f"Invalid phase header: {lines[0]}")
        
        phase_number = int(header_match.group(1))
        phase_name = header_match.group(2).strip()
        
        # Extract goal/description
        description = self._extract_field(section, r'\*\*Goal:\*\*\s*(.+)')
        if not description:
            description = f"Phase {phase_number} objectives"
        
        # Extract estimated duration
        estimated_duration = self._extract_field(section, r'\*\*Estimated Duration:\*\*\s*(.+)')
        if not estimated_duration:
            estimated_duration = "Variable"
        
        # Extract tasks
        tasks = self._extract_tasks(section, phase_number)
        
        # Extract validation gate
        validation_gate = self._extract_validation_gate(section)
        
        return DynamicPhase(
            phase_number=phase_number,
            phase_name=phase_name,
            description=description,
            estimated_duration=estimated_duration,
            tasks=tasks,
            validation_gate=validation_gate,
        )
    
    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """
        Extract single field value from text.
        
        Args:
            text: Text to search
            pattern: Regex pattern with one capture group
            
        Returns:
            Extracted value or None
        """
        match = re.search(pattern, text, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _extract_tasks(self, section: str, phase_number: int) -> List[DynamicTask]:
        """
        Extract all tasks from phase section.
        
        Args:
            section: Phase section markdown
            phase_number: Phase number for task ID context
            
        Returns:
            List of DynamicTask objects
        """
        tasks = []
        
        # Find task list section
        lines = section.split('\n')
        in_tasks = False
        current_task_lines = []
        
        for i, line in enumerate(lines):
            # Check if we're entering tasks section
            if re.match(r'\*\*Tasks:\*\*', line):
                in_tasks = True
                continue
            
            # Check if we're leaving tasks section
            if in_tasks and re.match(r'\*\*Validation Gate:', line):
                if current_task_lines:
                    task = self._parse_task(current_task_lines, phase_number)
                    if task:
                        tasks.append(task)
                    current_task_lines = []  # Clear so we don't parse twice
                break
            
            # Collect task lines
            if in_tasks:
                # New task starts with - [ ] **Task
                if re.match(r'^- \[ \] \*\*Task', line):
                    if current_task_lines:
                        task = self._parse_task(current_task_lines, phase_number)
                        if task:
                            tasks.append(task)
                    current_task_lines = [line]
                elif current_task_lines:
                    current_task_lines.append(line)
        
        # Parse last task if any
        if current_task_lines:
            task = self._parse_task(current_task_lines, phase_number)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _parse_task(self, task_lines: List[str], phase_number: int) -> Optional[DynamicTask]:
        """
        Parse task from collected lines.
        
        Args:
            task_lines: Lines belonging to this task
            phase_number: Phase number for validation
            
        Returns:
            DynamicTask object or None if parsing fails
        """
        if not task_lines:
            return None
        
        task_text = '\n'.join(task_lines)
        
        # Extract task header: - [ ] **Task N.M**: Name
        header_match = re.match(r'^- \[ \] \*\*Task ([0-9.]+)\*\*:\s*(.+)$', task_lines[0])
        if not header_match:
            return None
        
        task_id = header_match.group(1).strip()
        task_name = header_match.group(2).strip()
        
        # Validate task_id matches phase
        if not task_id.startswith(f"{phase_number}."):
            # Task ID doesn't match phase, but we'll use it anyway
            pass
        
        # Extract description (task name is the description in simple format)
        description = task_name
        
        # Extract estimated time
        estimated_time = self._extract_field(task_text, r'\*\*Estimated Time\*\*:\s*(.+)')
        if not estimated_time:
            estimated_time = "Variable"
        
        # Extract dependencies
        dependencies = self._extract_dependencies(task_text)
        
        # Extract acceptance criteria
        acceptance_criteria = self._extract_acceptance_criteria(task_text)
        
        return DynamicTask(
            task_id=task_id,
            task_name=task_name,
            description=description,
            estimated_time=estimated_time,
            dependencies=dependencies,
            acceptance_criteria=acceptance_criteria,
        )
    
    def _extract_dependencies(self, task_text: str) -> List[str]:
        """
        Extract task dependencies.
        
        Args:
            task_text: Task markdown text
            
        Returns:
            List of dependency task IDs
        """
        dep_match = re.search(r'\*\*Dependencies\*\*:\s*(.+)', task_text)
        if not dep_match:
            return []
        
        dep_text = dep_match.group(1).strip()
        
        # Check for "None"
        if dep_text.lower() in ['none', 'n/a', '-']:
            return []
        
        # Split by comma, semicolon, or "and"
        deps = re.split(r',\s*|;\s*|\s+and\s+', dep_text)
        
        # Extract task IDs (e.g., "Task 1.1" -> "1.1")
        task_ids = []
        for dep in deps:
            # Match Task N.M pattern
            id_match = re.search(r'(?:Task\s+)?([0-9.]+)', dep)
            if id_match:
                task_ids.append(id_match.group(1))
        
        return task_ids
    
    def _extract_acceptance_criteria(self, task_text: str) -> List[str]:
        """
        Extract acceptance criteria checklist.
        
        Args:
            task_text: Task markdown text
            
        Returns:
            List of criterion strings
        """
        criteria = []
        
        # Find acceptance criteria section
        lines = task_text.split('\n')
        in_criteria = False
        
        for line in lines:
            if re.match(r'\s*-\s*\*\*Acceptance Criteria\*\*:', line):
                in_criteria = True
                continue
            
            if in_criteria:
                # Check for nested checkbox item
                criterion_match = re.match(r'\s*-\s*\[ \]\s*(.+)', line)
                if criterion_match:
                    criteria.append(criterion_match.group(1).strip())
                # Stop at next major section or outdent
                elif line.strip() and not line.startswith('  '):
                    break
        
        return criteria
    
    def _extract_validation_gate(self, section: str) -> List[str]:
        """
        Extract validation gate criteria.
        
        Args:
            section: Phase section markdown
            
        Returns:
            List of gate criterion strings
        """
        criteria = []
        
        # Find validation gate section
        lines = section.split('\n')
        in_gate = False
        
        for line in lines:
            if re.match(r'\*\*Validation Gate:\*\*', line):
                in_gate = True
                continue
            
            if in_gate:
                # Check for checkbox item
                criterion_match = re.match(r'^-\s*\[ \]\s*(.+)', line)
                if criterion_match:
                    criteria.append(criterion_match.group(1).strip())
                # Stop at next phase or major section
                elif line.strip().startswith('###') or line.strip().startswith('##'):
                    break
        
        return criteria


__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
]
