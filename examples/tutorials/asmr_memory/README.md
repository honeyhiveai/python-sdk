# ASMR Memory System on HoneyHive

A reference implementation of the **ASMR (Agentic Structured Memory and Recall)** system
built on top of HoneyHive APIs, demonstrating how HoneyHive's tracing and observability
platform supports sophisticated agentic memory architectures.

Based on [Supermemory's research](https://supermemory.ai/research/) achieving ~99% on the
LongMemEval benchmark.

## Architecture

The ASMR system has four stages, all fully traced through HoneyHive:

### 1. Data Ingestion - Parallel Knowledge Extraction

Three observer agents process conversation histories in parallel (round-robin distribution):

- **Fact Hunter** - Named entity recognition, explicit facts, relationships
- **Context Weaver** - Pattern recognition, implications, cross-session correlations
- **Timeline Tracker** - Temporal analysis, event chronology, knowledge updates

Each agent extracts structured findings across six knowledge vectors:
Personal Info, Preferences, Events, Temporal Data, Updates, Assistant Info.

### 2. Knowledge Store

Pure structured storage (no embeddings, no vector DB) with:
- Session-to-finding mappings
- Entity index for fast lookup
- Category-based organization
- Knowledge update chains (supersedes tracking)

### 3. Active Search Orchestration

Three search agents process user queries against the knowledge store:

- **Direct Seeker** - Exact match, literal facts, recent-first prioritization
- **Inference Engine** - Implication analysis, related context, supporting evidence
- **Temporal Reasoner** - Timeline reasoning, duration, state changes, recency

### 4. Decision Forest & Consensus

- **12-way parallel inference**: Each variant uses a different reasoning perspective
- **Consensus aggregator**: Majority voting + domain-weighted trust (temperature=0)

## HoneyHive Tracing

Every component is instrumented with HoneyHive span management:

```
asmr_full_pipeline (chain)
├── asmr_ingest (chain)
│   └── parallel_knowledge_extraction (chain)
│       ├── fact_hunter_agent (tool)
│       ├── context_weaver_agent (tool)
│       └── timeline_tracker_agent (tool)
└── asmr_query (chain)
    ├── agentic_search_orchestration (chain)
    │   ├── direct_seeker_agent (tool)
    │   ├── inference_engine_agent (tool)
    │   └── temporal_reasoner_agent (tool)
    └── decision_forest_and_consensus (chain)
        ├── parallel_inference_forest (chain)
        │   ├── variant_fact_checker (model)
        │   ├── variant_contextual_analyst (model)
        │   ├── ... (12 variants total)
        │   └── variant_holistic_reasoner (model)
        └── consensus_aggregation (model)
```

## Quick Start

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export HH_API_KEY="hh_..."
export HH_PROJECT="your-project"
export HH_API_URL="https://api.honeyhive.ai"  # optional

# Run the example
python -m examples.tutorials.asmr_memory.example
```

## Programmatic Usage

```python
from examples.tutorials.asmr_memory.asmr import ASMRMemory

# Initialize
memory = ASMRMemory(
    api_key="hh_...",
    project="my-project",
    openai_api_key="sk-...",
)

# Ingest conversation sessions
sessions = [
    {
        "session_id": "s1",
        "timestamp": "2024-01-15T10:00:00Z",
        "messages": [
            {"role": "user", "content": "I live in San Francisco."},
            {"role": "assistant", "content": "Great city!"},
        ],
    },
]
memory.ingest(sessions)

# Query the memory
result = memory.query("Where does the user live?")
print(result["final_answer"])   # "San Francisco"
print(result["confidence"])     # 0.95
```

## File Structure

```
asmr_memory/
├── __init__.py           # Package init
├── asmr.py               # Main orchestrator (ASMRMemory class)
├── knowledge_store.py     # Structured findings store
├── observer_agents.py     # 3 parallel observer agents for ingestion
├── search_agents.py       # 3 search agents for retrieval
├── consensus.py           # 12-way decision forest + consensus
├── example.py             # Runnable example with sample data
└── README.md              # This file
```

## Key Design Decisions

1. **No embeddings**: Following the ASMR paper, all retrieval is done via agentic
   search (LLM-powered) rather than vector similarity. No vector DB dependency.

2. **Structured storage**: Findings are stored as typed objects with metadata,
   not raw text chunks.

3. **Full observability**: Every LLM call, every agent decision, every pipeline stage
   is traced through HoneyHive. Inspect the full execution in the HoneyHive UI.

4. **Modular architecture**: Each component (observers, store, search, consensus) is
   independent and can be swapped or extended.

5. **Round-robin distribution**: Sessions are distributed across observer agents to
   ensure balanced workload and diverse extraction perspectives.
