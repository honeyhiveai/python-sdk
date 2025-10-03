#!/usr/bin/env python3
"""
RAG Validation Script
Tests retrieval accuracy with comprehensive query set.

100% AI-authored via human orchestration.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.rag_engine import RAGEngine
from scripts.build_rag_index import IndexBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Comprehensive test query set (50 queries)
TEST_QUERIES = [
    # Test Generation Framework V3 - Phase-specific queries (8 queries)
    {
        "query": "Phase 1 method verification requirements",
        "expected_keywords": ["phase 1", "method", "verification", "ast"],
        "expected_phase": 1,
        "description": "Phase 1 specific content",
    },
    {
        "query": "Phase 2 logging analysis checkpoint criteria",
        "expected_keywords": ["phase 2", "logging", "checkpoint"],
        "expected_phase": 2,
        "description": "Phase 2 checkpoint requirements",
    },
    {
        "query": "Phase 3 mocking boundary determination",
        "expected_keywords": ["phase 3", "mocking", "boundary"],
        "expected_phase": 3,
        "description": "Phase 3 mocking guidance",
    },
    {
        "query": "Phase 4 AST analysis implementation",
        "expected_keywords": ["phase 4", "ast", "analysis"],
        "expected_phase": 4,
        "description": "Phase 4 AST requirements",
    },
    {
        "query": "Phase 5 coverage strategy planning",
        "expected_keywords": ["phase 5", "coverage", "strategy"],
        "expected_phase": 5,
        "description": "Phase 5 coverage planning",
    },
    {
        "query": "Phase 6 test generation readiness",
        "expected_keywords": ["phase 6", "generation", "readiness"],
        "expected_phase": 6,
        "description": "Phase 6 pre-generation",
    },
    {
        "query": "Phase 7 test execution and metrics",
        "expected_keywords": ["phase 7", "execution", "metrics"],
        "expected_phase": 7,
        "description": "Phase 7 post-generation",
    },
    {
        "query": "Phase 8 framework validation requirements",
        "expected_keywords": ["phase 8", "validation", "framework"],
        "expected_phase": 8,
        "description": "Phase 8 validation",
    },
    # Testing Standards (5 queries)
    {
        "query": "unit testing best practices",
        "expected_keywords": ["unit", "test", "practice"],
        "description": "Unit testing guidance",
    },
    {
        "query": "integration testing standards",
        "expected_keywords": ["integration", "test", "standard"],
        "description": "Integration test requirements",
    },
    {
        "query": "test fixture patterns and usage",
        "expected_keywords": ["fixture", "pattern", "test"],
        "description": "Fixture standards",
    },
    {
        "query": "test execution commands",
        "expected_keywords": ["test", "execution", "command", "tox"],
        "description": "Test running commands",
    },
    {
        "query": "debugging methodology for tests",
        "expected_keywords": ["debug", "test", "methodology"],
        "description": "Test debugging guidance",
    },
    # Mocking and AST (5 queries)
    {
        "query": "how to determine mocking boundaries",
        "expected_keywords": ["mocking", "boundary", "determine"],
        "description": "Mocking boundary analysis",
    },
    {
        "query": "AST analysis for test generation",
        "expected_keywords": ["ast", "analysis", "test"],
        "description": "AST usage in testing",
    },
    {
        "query": "when to mock internal methods",
        "expected_keywords": ["mock", "internal", "method"],
        "description": "Internal method mocking",
    },
    {
        "query": "external dependency mocking patterns",
        "expected_keywords": ["external", "dependency", "mock"],
        "description": "External mocking patterns",
    },
    {
        "query": "avoiding over-mocking in tests",
        "expected_keywords": ["over", "mock", "avoid"],
        "description": "Over-mocking prevention",
    },
    # Code Quality and Standards (5 queries)
    {
        "query": "pylint configuration and rules",
        "expected_keywords": ["pylint", "rule", "configuration"],
        "description": "Pylint standards",
    },
    {
        "query": "code style guidelines",
        "expected_keywords": ["code", "style", "guideline"],
        "description": "Code style requirements",
    },
    {
        "query": "type hinting requirements",
        "expected_keywords": ["type", "hint", "annotation"],
        "description": "Type annotation standards",
    },
    {
        "query": "docstring documentation standards",
        "expected_keywords": ["docstring", "documentation"],
        "description": "Docstring requirements",
    },
    {
        "query": "code quality metrics",
        "expected_keywords": ["quality", "metric", "coverage"],
        "description": "Quality measurement",
    },
    # Git and Development Workflow (5 queries)
    {
        "query": "git workflow and branching strategy",
        "expected_keywords": ["git", "workflow", "branch"],
        "description": "Git workflow guidance",
    },
    {
        "query": "pre-commit hook requirements",
        "expected_keywords": ["pre", "commit", "hook"],
        "description": "Pre-commit standards",
    },
    {
        "query": "changelog update requirements",
        "expected_keywords": ["changelog", "update", "requirement"],
        "description": "CHANGELOG standards",
    },
    {
        "query": "commit message format",
        "expected_keywords": ["commit", "message", "format"],
        "description": "Commit message guidelines",
    },
    {
        "query": "release process steps",
        "expected_keywords": ["release", "process", "step"],
        "description": "Release procedures",
    },
    # Documentation (5 queries)
    {
        "query": "sphinx documentation generation",
        "expected_keywords": ["sphinx", "documentation", "generation"],
        "description": "Sphinx docs",
    },
    {
        "query": "mermaid diagram standards",
        "expected_keywords": ["mermaid", "diagram"],
        "description": "Diagram guidelines",
    },
    {
        "query": "documentation templates",
        "expected_keywords": ["documentation", "template"],
        "description": "Doc templates",
    },
    {
        "query": "API documentation requirements",
        "expected_keywords": ["api", "documentation"],
        "description": "API docs standards",
    },
    {
        "query": "documentation quality standards",
        "expected_keywords": ["documentation", "quality"],
        "description": "Doc quality requirements",
    },
    # Performance and Security (5 queries)
    {
        "query": "performance optimization guidelines",
        "expected_keywords": ["performance", "optimization"],
        "description": "Performance standards",
    },
    {
        "query": "security best practices",
        "expected_keywords": ["security", "practice"],
        "description": "Security guidelines",
    },
    {
        "query": "credential management",
        "expected_keywords": ["credential", "management", "security"],
        "description": "Credential handling",
    },
    {
        "query": "environment variable configuration",
        "expected_keywords": ["environment", "variable", "config"],
        "description": "Env var standards",
    },
    {
        "query": "secure configuration practices",
        "expected_keywords": ["secure", "configuration"],
        "description": "Config security",
    },
    # AI Assistant and Code Generation (7 queries)
    {
        "query": "AI assistant compliance requirements",
        "expected_keywords": ["ai", "assistant", "compliance"],
        "description": "AI assistant standards",
    },
    {
        "query": "test generation acknowledgment contract",
        "expected_keywords": ["acknowledgment", "contract", "test"],
        "description": "Test gen contract",
    },
    {
        "query": "production code generation patterns",
        "expected_keywords": ["production", "code", "generation"],
        "description": "Production code gen",
    },
    {
        "query": "pre-generation checklist requirements",
        "expected_keywords": ["pre", "generation", "checklist"],
        "description": "Pre-gen checklist",
    },
    {
        "query": "code generation quality targets",
        "expected_keywords": ["code", "generation", "quality"],
        "description": "Code gen quality",
    },
    {
        "query": "AI assistant error handling",
        "expected_keywords": ["ai", "error", "handling"],
        "description": "AI error handling",
    },
    {
        "query": "forbidden AI assistant operations",
        "expected_keywords": ["forbidden", "ai", "operation"],
        "description": "AI prohibitions",
    },
    # Cross-cutting Concerns (5 queries)
    {
        "query": "tech stack requirements",
        "expected_keywords": ["tech", "stack", "requirement"],
        "description": "Technology standards",
    },
    {
        "query": "environment setup instructions",
        "expected_keywords": ["environment", "setup"],
        "description": "Environment configuration",
    },
    {
        "query": "best practices overview",
        "expected_keywords": ["best", "practice"],
        "description": "General best practices",
    },
    {
        "query": "specification writing standards",
        "expected_keywords": ["specification", "standard"],
        "description": "Spec writing guidance",
    },
    {
        "query": "Agent OS standards overview",
        "expected_keywords": ["agent", "os", "standard"],
        "description": "Agent OS overview",
    },
]


class RAGValidator:
    """Validates RAG retrieval accuracy."""

    def __init__(self, engine: RAGEngine):
        """
        Initialize validator.

        Args:
            engine: RAG engine to validate
        """
        self.engine = engine
        self.results = []

    def validate_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single test query.

        Args:
            test_case: Test case dictionary with query and expectations

        Returns:
            Result dictionary with pass/fail and metrics
        """
        query = test_case["query"]
        expected_keywords = test_case["expected_keywords"]
        expected_phase = test_case.get("expected_phase")
        description = test_case.get("description", "")

        logger.debug(f"Testing: {description}")
        logger.debug(f"Query: {query}")

        # Build filters if phase expected
        filters = {"phase": expected_phase} if expected_phase else None

        # Execute search
        try:
            result = self.engine.search(query, n_results=5, filters=filters)

            # Check if any chunks returned
            if len(result.chunks) == 0:
                logger.warning(f"No results for query: {query}")
                return {
                    "query": query,
                    "description": description,
                    "passed": False,
                    "reason": "no_results",
                    "expected_keywords": expected_keywords,
                    "found_keywords": [],
                    "relevance_scores": [],
                }

            # Analyze chunks for keyword presence
            found_keywords = []
            all_content = " ".join(
                [chunk["content"].lower() for chunk in result.chunks]
            )

            for keyword in expected_keywords:
                if keyword.lower() in all_content:
                    found_keywords.append(keyword)

            # Calculate match rate
            keyword_match_rate = len(found_keywords) / len(expected_keywords)

            # Pass if >= 50% keywords found (lenient for validation)
            passed = keyword_match_rate >= 0.5

            return {
                "query": query,
                "description": description,
                "passed": passed,
                "keyword_match_rate": keyword_match_rate,
                "expected_keywords": expected_keywords,
                "found_keywords": found_keywords,
                "relevance_scores": result.relevance_scores,
                "retrieval_method": result.retrieval_method,
                "query_time_ms": result.query_time_ms,
                "total_tokens": result.total_tokens,
                "chunks_returned": len(result.chunks),
            }

        except Exception as e:
            logger.error(f"Query failed: {query} - {e}")
            return {
                "query": query,
                "description": description,
                "passed": False,
                "reason": "error",
                "error": str(e),
            }

    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all test queries.

        Returns:
            Summary dictionary with overall metrics
        """
        logger.info(f"Validating {len(TEST_QUERIES)} test queries...")
        logger.info("=" * 60)

        passed_count = 0
        failed_count = 0

        for idx, test_case in enumerate(TEST_QUERIES, 1):
            result = self.validate_query(test_case)
            self.results.append(result)

            if result["passed"]:
                passed_count += 1
                status = "✅ PASS"
            else:
                failed_count += 1
                status = "❌ FAIL"

            logger.info(
                f"[{idx}/{len(TEST_QUERIES)}] {status} - {result['description']}"
            )

            if not result["passed"]:
                logger.info(f"  Query: {result['query']}")
                if "reason" in result:
                    logger.info(f"  Reason: {result['reason']}")
                if "keyword_match_rate" in result:
                    logger.info(
                        f"  Keyword match: {result['keyword_match_rate']:.1%}"
                    )

        # Calculate overall accuracy
        accuracy = passed_count / len(TEST_QUERIES)

        logger.info("=" * 60)
        logger.info(f"Validation Complete!")
        logger.info(f"  Total queries: {len(TEST_QUERIES)}")
        logger.info(f"  Passed: {passed_count}")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Accuracy: {accuracy:.1%}")
        logger.info("=" * 60)

        # Calculate additional metrics
        avg_query_time = sum(
            r.get("query_time_ms", 0) for r in self.results if "query_time_ms" in r
        ) / len([r for r in self.results if "query_time_ms" in r])

        avg_tokens = sum(
            r.get("total_tokens", 0) for r in self.results if "total_tokens" in r
        ) / len([r for r in self.results if "total_tokens" in r])

        summary = {
            "total_queries": len(TEST_QUERIES),
            "passed": passed_count,
            "failed": failed_count,
            "accuracy": accuracy,
            "meets_target": accuracy >= 0.90,  # 90% target
            "avg_query_time_ms": avg_query_time,
            "avg_tokens_per_query": avg_tokens,
            "validated_at": datetime.now().isoformat(),
        }

        return summary

    def save_results(self, output_path: Path) -> None:
        """
        Save validation results to JSON.

        Args:
            output_path: Path to save results
        """
        output_data = {"results": self.results}

        output_path.write_text(json.dumps(output_data, indent=2))
        logger.info(f"Results saved to {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate RAG retrieval accuracy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--index-path",
        type=Path,
        default=None,
        help="Path to vector index (default: .agent-os/.cache/vector_index)",
    )

    parser.add_argument(
        "--standards-path",
        type=Path,
        default=None,
        help="Path to Agent OS standards (default: .agent-os/standards)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to save validation results JSON",
    )

    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build index before validation if missing",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    index_path = args.index_path or (repo_root / ".agent-os" / ".cache" / "vector_index")
    standards_path = args.standards_path or (repo_root / ".agent-os" / "standards")

    # Check if index exists
    if not index_path.exists() or not (index_path / "chroma.sqlite3").exists():
        if args.build_index:
            logger.info("Index not found, building...")
            builder = IndexBuilder(index_path, standards_path)
            builder.build_index(force=True)
        else:
            logger.error(f"Index not found at {index_path}")
            logger.info("Run with --build-index to build index first")
            logger.info("Or run: python .agent-os/scripts/build_rag_index.py")
            sys.exit(1)

    # Initialize RAG engine
    try:
        engine = RAGEngine(index_path, standards_path)
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")
        sys.exit(1)

    # Validate
    validator = RAGValidator(engine)
    summary = validator.validate_all()

    # Save results if requested
    if args.output:
        validator.save_results(args.output)

    # Exit with appropriate code
    if summary["meets_target"]:
        logger.info("✅ RAG accuracy target met (90%+)")
        sys.exit(0)
    else:
        logger.warning(f"❌ RAG accuracy below target: {summary['accuracy']:.1%}")
        logger.warning("Consider tuning chunking parameters or embedding strategy")
        sys.exit(1)


if __name__ == "__main__":
    main()

