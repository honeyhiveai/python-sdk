"""
Validation corpus for tasks.md parser.

Extracts patterns from all tasks.md files and validates parser correctness.
"""

import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Type

# Add project root to path for imports
# This script should be run from project root with: PYTHONPATH=.praxis-os/ouroboros:. python3 validate_corpus.py
try:
    from ouroboros.subsystems.workflow.parsers.markdown.spec_tasks import SpecTasksParser
    from ouroboros.subsystems.workflow.parsers.markdown import pattern_discovery
    from mistletoe import Document
    PARSER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import parser modules: {e}")
    print("Running in analysis-only mode")
    print("To enable parser tests, run from project root with: PYTHONPATH=.praxis-os/ouroboros:. python3 validate_corpus.py")
    SpecTasksParser: Optional[Any] = None  # type: ignore[no-redef]
    PARSER_AVAILABLE = False


def analyze_tasks_file(file_path: Path) -> Dict:
    """Analyze a single tasks.md file for patterns."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        headers = []
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headers.append({
                    'level': level,
                    'text': text,
                    'text_lower': text.lower(),
                    'line': i + 1
                })
        
        # Extract phase headers
        phase_headers = []
        metadata_headers = []
        
        for h in headers:
            text_lower = h['text_lower']
            level_value = h['level']
            # Handle level which can be int | str | Any
            header_level: int = int(level_value) if isinstance(level_value, (int, str)) and str(level_value).isdigit() else 0
            
            # Phase headers: level 2, matches "Phase N:"
            if header_level == 2 and isinstance(text_lower, str) and re.match(r'^phase\s+\d+\s*:', text_lower):
                phase_headers.append(h['text'])
            # Metadata sections
            elif isinstance(text_lower, str) and any(kw in text_lower for kw in ['tasks', 'acceptance', 'validation', 'gate', 'dependencies', 'execution order', 'risk', 'success']):
                metadata_headers.append(h['text'])
        
        return {
            'file': str(file_path),
            'phase_headers': phase_headers,
            'metadata_headers': metadata_headers,
            'total_headers': len(headers),
            'phase_count': len(phase_headers),
            'has_phase_0': any('phase 0' in str(ph).lower() for ph in phase_headers),
            'content': content,
        }
    except Exception as e:
        return {'file': str(file_path), 'error': str(e)}


def test_parser_on_file(file_path: Path, parser: SpecTasksParser) -> Dict:
    """Test parser on a single file."""
    try:
        phases = parser.parse(file_path)
        return {
            'file': str(file_path),
            'success': True,
            'phase_count': len(phases),
            'phase_numbers': [p.phase_number for p in phases],
            'has_phase_0': any(p.phase_number == 0 for p in phases),
            'error': None,
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'success': False,
            'phase_count': 0,
            'phase_numbers': [],
            'has_phase_0': False,
            'error': str(e),
        }


def build_corpus() -> Tuple[List[Dict], Dict]:
    """Build validation corpus from all tasks.md files."""
    spec_dirs = [
        Path('.praxis-os/specs'),
        Path('../python-sdk/.agent-os/specs')
    ]
    
    all_files: List[Path] = []
    for spec_dir in spec_dirs:
        if spec_dir.exists():
            all_files.extend(spec_dir.rglob('tasks.md'))
    
    print(f"Found {len(all_files)} tasks.md files\n")
    
    # Analyze each file
    results = []
    for file_path in all_files:
        result = analyze_tasks_file(file_path)
        results.append(result)
    
    # Extract patterns
    all_phase_patterns = []
    all_metadata_patterns = []
    phase_0_files = []
    valid_files = []
    
    for result in results:
        if 'error' not in result:
            valid_files.append(result)
            all_phase_patterns.extend(result['phase_headers'])
            all_metadata_patterns.extend(result['metadata_headers'])
            if result['has_phase_0']:
                phase_0_files.append(result['file'])
    
    # Build pattern statistics
    patterns = {
        'phase_header_levels': Counter(),
        'phase_patterns': Counter(),
        'metadata_keywords': Counter(),
        'phase_0_count': len(phase_0_files),
    }
    
    # Analyze phase header patterns
    for ph in all_phase_patterns:
        ph_lower = ph.lower()
        # Extract level (assuming level 2)
        patterns['phase_header_levels'][2] += 1  # type: ignore[index]
        # Extract pattern
        if re.match(r'^phase\s+\d+\s*:', ph_lower):
            patterns['phase_patterns']['Phase N:'] += 1  # type: ignore[index]
    
    # Analyze metadata keywords
    for mh in all_metadata_patterns:
        mh_lower = mh.lower()
        words = set(mh_lower.split())
        metadata_keywords = {'tasks', 'acceptance', 'criteria', 'validation', 'gate', 
                            'dependencies', 'execution', 'order', 'risk', 'success', 
                            'estimated', 'duration', 'detailed', 'breakdown'}
        for kw in metadata_keywords:
            if kw in words:
                patterns['metadata_keywords'][kw] += 1  # type: ignore[index]
    
    return valid_files, patterns


def print_corpus_summary(files: List[Dict], patterns: Dict):
    """Print corpus summary."""
    print("=" * 80)
    print("VALIDATION CORPUS SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal files: {len(files)}")
    print(f"Files with Phase 0: {patterns['phase_0_count']}")
    print(f"Total phase headers: {sum(f['phase_count'] for f in files)}")
    print(f"Total metadata headers: {sum(len(f['metadata_headers']) for f in files)}")
    
    print(f"\nPhase Header Levels:")
    for level, count in patterns['phase_header_levels'].most_common():
        print(f"  Level {level}: {count}")
    
    print(f"\nPhase Patterns:")
    for pattern, count in patterns['phase_patterns'].most_common():
        print(f"  {pattern}: {count}")
    
    print(f"\nTop Metadata Keywords:")
    for kw, count in patterns['metadata_keywords'].most_common(10):
        print(f"  {kw}: {count}")
    
    print(f"\nPhase Header Examples:")
    all_phases = []
    for f in files:
        all_phases.extend(f['phase_headers'])
    for i, ph in enumerate(all_phases[:10], 1):
        print(f"  {i}. {ph}")
    
    print(f"\nMetadata Header Examples:")
    all_metadata = []
    for f in files:
        all_metadata.extend(f['metadata_headers'])
    for i, mh in enumerate(all_metadata[:15], 1):
        print(f"  {i}. {mh}")


def test_parser_corpus(files: List[Dict]):
    """Test parser against corpus."""
    if not PARSER_AVAILABLE:
        print("\nParser not available - skipping tests")
        print("Run with: PYTHONPATH=.praxis-os/ouroboros:. python3 validate_corpus.py")
        return
    
    print("\n" + "=" * 80)
    print("PARSER VALIDATION TESTS")
    print("=" * 80)
    
    parser = SpecTasksParser()
    
    results = []
    for file_info in files:
        file_path = Path(file_info['file'])
        result = test_parser_on_file(file_path, parser)
        results.append(result)
        
        if result['success']:
            expected_phases = file_info['phase_count']
            actual_phases = result['phase_count']
            match = "✓" if expected_phases == actual_phases else "⚠"
            phase0_note = " [Phase 0]" if result['has_phase_0'] else ""
            print(f"{match} {file_path.parent.name}: {actual_phases} phases (expected {expected_phases}){phase0_note}")
        else:
            print(f"✗ {file_path.parent.name}: ERROR - {result['error']}")
    
    # Summary
    print(f"\n=== VALIDATION SUMMARY ===")
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Successful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    
    if failed:
        print(f"\nFailed files:")
        for r in failed:
            print(f"  {Path(r['file']).parent.name}: {r['error']}")
    
    # Phase count accuracy
    phase_match = 0
    for r in successful:
        file_info = next(f for f in files if f['file'] == r['file'])
        if r['phase_count'] == file_info['phase_count']:
            phase_match += 1
    
    print(f"\nPhase count accuracy: {phase_match}/{len(successful)} ({phase_match/len(successful)*100:.1f}%)")


def main():
    """Main entry point."""
    files, patterns = build_corpus()
    print_corpus_summary(files, patterns)
    test_parser_corpus(files)


if __name__ == '__main__':
    main()

