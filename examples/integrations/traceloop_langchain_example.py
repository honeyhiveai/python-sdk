#!/usr/bin/env python3
"""
LangChain + OpenLLMetry (Traceloop) Integration Example

Demonstrates how to integrate LangChain with HoneyHive using OpenLLMetry's
individual instrumentor package, following HoneyHive's "Bring Your Own
Instrumentor" architecture.

The same ``opentelemetry-instrumentation-langchain`` package also traces
LangGraph ``StateGraph`` workflows; see ``examples/integrations/langgraph_integration.py``.

Requirements:
- pip install honeyhive[traceloop-langchain] langchain-openai
- Set environment variables: HH_API_KEY, HH_PROJECT, OPENAI_API_KEY
"""

from __future__ import annotations

import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

from honeyhive import HoneyHiveTracer, enrich_span, trace
from honeyhive.models import EventType


def setup_tracing() -> tuple[HoneyHiveTracer, LangchainInstrumentor]:
    """Initialize HoneyHive tracer with OpenLLMetry LangChain instrumentor."""

    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")
    if not os.getenv("HH_PROJECT"):
        raise ValueError("HH_PROJECT environment variable is required")
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="traceloop_langchain_example",
        source=os.path.basename(__file__),
    )

    instrumentor = LangchainInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    print("✅ Tracing initialized with OpenLLMetry LangChain instrumentor")
    return tracer, instrumentor


def basic_langchain_example() -> str | None:
    """Basic LangChain chain usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic LangChain Example")
    print("-" * 40)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise assistant. Answer in one sentence."),
            ("user", "{question}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=100)
    chain = prompt | llm

    try:
        response = chain.invoke({"question": "Explain OpenLLMetry in one sentence."})
        print(f"✅ Response: {response.content}")
        return response.content
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {e}")
        return None


@trace(event_type=EventType.chain)
def advanced_langchain_workflow(document: str) -> dict[str, Any]:
    """Advanced workflow: summarize then analyze a document with LangChain."""

    print("\n🚀 Advanced Workflow: Document Analysis")
    print("-" * 40)

    enrich_span(
        metadata={
            "business.workflow": "document_analysis",
            "business.document_length": len(document),
            "langchain.strategy": "summarize_then_analyze",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=200)

    summary_prompt = ChatPromptTemplate.from_messages(
        [("user", "Provide a brief summary of this document:\n\n{document}")]
    )
    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "user",
                "Provide detailed analysis and insights for this document:\n\n{document}",
            )
        ]
    )

    try:
        print("📝 Step 1: Summarizing document...")
        summary = (summary_prompt | llm).invoke({"document": document}).content
        print(f"✅ Summary generated ({len(summary)} chars)")

        print("🔍 Step 2: Performing detailed analysis...")
        analysis = (analysis_prompt | llm).invoke({"document": document}).content
        print(f"✅ Analysis completed ({len(analysis)} chars)")

        enrich_span(
            metadata={
                "business.steps_completed": 2,
                "business.summary_length": len(summary),
                "business.analysis_length": len(analysis),
                "business.workflow_status": "completed",
            }
        )

        return {
            "document": document,
            "summary": summary,
            "analysis": analysis,
        }

    except Exception as e:  # noqa: BLE001
        enrich_span(
            metadata={
                "error.type": "workflow_error",
                "error.message": str(e),
                "business.workflow_status": "failed",
            }
        )
        print(f"❌ Workflow failed: {e}")
        raise


def main() -> int:
    """Main example function."""

    print("🧪 LangChain + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    tracer: HoneyHiveTracer | None = None
    instrumentor: LangchainInstrumentor | None = None

    try:
        tracer, instrumentor = setup_tracing()

        basic_langchain_example()

        sample_document = """
        Artificial Intelligence (AI) has revolutionized many industries in recent years.
        From healthcare to finance, AI applications are helping organizations make better
        decisions, automate processes, and improve customer experiences.
        """
        advanced_langchain_workflow(sample_document.strip())

        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        if instrumentor is not None:
            instrumentor.uninstrument()

    return 0


if __name__ == "__main__":
    exit(main())
