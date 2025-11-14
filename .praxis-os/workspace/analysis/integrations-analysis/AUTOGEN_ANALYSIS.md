# Microsoft AutoGen Analysis Report

**Date:** 2025-10-15  
**Analyst:** AI Assistant  
**Analysis Version:** Based on SDK_ANALYSIS_METHODOLOGY.md v1.3  
**SDK Version Analyzed:** v0.7.5 (main branch)

---

## Phase 1: Initial Discovery

### Phase 1.1: Repository Metadata Analysis ✅

**SDK Overview:**
- **Name:** AutoGen
- **Type:** Multi-agent AI application framework
- **Version:** 0.7.5
- **Python Requirement:** >=3.10
- **License:** MIT (code), CC-BY-4.0 (docs)
- **Maintainer:** Microsoft
- **Repository:** https://github.com/microsoft/autogen

**Architecture:**
AutoGen uses a **layered monorepo** with three main Python packages:

1. **autogen-core** (v0.7.5)
   - Foundational interfaces and agent runtime
   - Message passing, event-driven agents
   - Local and distributed runtime
   - **Key dependency:** `opentelemetry-api>=1.34.1` ✅
   - Other deps: pydantic, protobuf, pillow, typing-extensions

2. **autogen-agentchat** (v0.7.5)
   - High-level API for multi-agent applications
   - Built on top of autogen-core
   - Agents: AssistantAgent, team patterns
   - Dependencies: autogen-core only

3. **autogen-ext** (v0.7.5)
   - Extensions library for LLM clients and capabilities
   - **LLM Client Support (optional dependencies):**
     - `openai>=1.93` (with tiktoken, aiofiles)
     - `anthropic>=0.48`
     - `azure-ai-inference>=1.0.0b9`
     - `ollama>=0.4.7`
     - `google-genai>=1.0.0` (Gemini)
     - `semantic-kernel>=1.17.1` (multiple providers)
     - `langchain_core~=0.3.3`
   - Additional capabilities: Docker, gRPC, MCP servers, web surfer, etc.

**Key Findings:**
- ✅ **autogen-core depends on `opentelemetry-api>=1.34.1`** - Built-in OTel support!
- ✅ Multiple LLM provider support (OpenAI, Anthropic, Azure, Ollama, Gemini)
- ✅ Both Python and .NET implementations
- ✅ Cross-language support via gRPC and protobuf
- ⚠️ Note in README: "if you are new to AutoGen, please checkout Microsoft Agent Framework" - AutoGen is in maintenance mode (bug fixes only)

**Documentation:**
- Primary docs: https://microsoft.github.io/autogen/
- AgentChat guide: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/
- Discord community: https://aka.ms/autogen-discord
- Blog: https://devblogs.microsoft.com/autogen/

**Installation:**
```bash
# AgentChat + OpenAI
pip install -U "autogen-agentchat" "autogen-ext[openai]"

# AutoGen Studio (GUI)
pip install -U "autogenstudio"
```

**Development Dependencies (from root pyproject.toml):**
- ✅ **`opentelemetry-instrumentation-openai`** in dev dependencies!
- Testing: pytest, pytest-asyncio, pytest-cov, pytest-xdist
- Type checking: pyright==1.1.389, mypy==1.13.0
- Linting: ruff==0.4.8

---

## Analysis Status

- [x] Phase 1.1: Repository Metadata Analysis
- [ ] Phase 1.2: File Structure Mapping
- [ ] Phase 1.3: Entry Point Discovery
- [ ] Phase 1.5: Existing Instrumentor Discovery (CRITICAL)
- [ ] Phase 2: LLM Client Discovery
- [ ] Phase 3: Observability System Analysis
- [ ] Phase 4: Architecture Deep Dive
- [ ] Phase 5: Instrumentation Strategy & Testing
- [ ] Phase 6: Documentation & Delivery

---


