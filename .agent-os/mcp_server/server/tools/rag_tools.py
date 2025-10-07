"""
RAG search tools for MCP server.

Provides search_standards tool for semantic search over Agent OS documentation.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# HoneyHive integration (optional)
try:
    from honeyhive.sdk.tracer import enrich_span
    HONEYHIVE_ENABLED = True
except ImportError:
    HONEYHIVE_ENABLED = False


def register_rag_tools(mcp: Any, rag_engine: Any) -> int:
    """
    Register RAG search tools with MCP server.
    
    :param mcp: FastMCP server instance
    :param rag_engine: RAGEngine instance for search
    :return: Number of tools registered
    """
    
    @mcp.tool()
    async def search_standards(
        query: str,
        n_results: int = 5,
        filter_phase: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic search over Agent OS documentation.

        Performs RAG-based semantic search to find relevant Agent OS content.
        Replaces reading entire framework documents with targeted retrieval.

        Args:
            query: Natural language question or topic
            n_results: Number of chunks to return (default 5)
            filter_phase: Optional phase number filter (1-8)
            filter_tags: Optional tags filter (e.g., ["mocking", "ast"])

        Returns:
            Dictionary with results, tokens, retrieval method, and timing
        """
        try:
            # Enrich HoneyHive span with MCP context
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "search_standards",
                    "mcp.query": query,
                    "mcp.n_results": n_results,
                    "mcp.filter_phase": filter_phase,
                    "mcp.filter_tags": filter_tags,
                })

            logger.info(
                f"search_standards: query='{query}', n_results={n_results}, "
                f"filter_phase={filter_phase}"
            )

            filters = {}
            if filter_phase is not None:
                filters["phase"] = filter_phase
            if filter_tags:
                filters["tags"] = filter_tags

            result = rag_engine.search(
                query=query, n_results=n_results, filters=filters
            )

            # Format response
            formatted_results = [
                {
                    "content": chunk.get("content", ""),
                    "file": chunk.get("file_path", ""),
                    "section": chunk.get("section_header", ""),
                    "relevance_score": score,
                    "tokens": chunk.get("tokens", 0),
                }
                for chunk, score in zip(result.chunks, result.relevance_scores)
            ]

            response = {
                "results": formatted_results,
                "total_tokens": result.total_tokens,
                "retrieval_method": result.retrieval_method,
                "query_time_ms": result.query_time_ms,
            }

            # Enrich span with results
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "result.chunks_returned": len(formatted_results),
                    "result.total_tokens": result.total_tokens,
                    "result.retrieval_method": result.retrieval_method,
                    "result.query_time_ms": result.query_time_ms,
                })

            logger.info(
                f"search_standards completed: {len(formatted_results)} results, "
                f"{result.total_tokens} tokens, {result.query_time_ms:.2f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"search_standards failed: {e}", exc_info=True)
            return {"error": str(e), "results": [], "total_tokens": 0}
    
    return 1  # One tool registered


__all__ = ["register_rag_tools"]
