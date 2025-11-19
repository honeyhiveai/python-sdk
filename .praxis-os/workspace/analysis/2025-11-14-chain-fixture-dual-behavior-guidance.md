# CHAIN Fixture Dual Behavior - Boss Guidance

**Date:** 2025-11-14  
**Status:** 🎯 **OFFICIAL GUIDANCE FROM BOSS**  
**Context:** Coordination between python-sdk and hive-kube fixture work

---

## 📋 Boss Guidance (Direct Quote)

> **"tool like content for chain types"**
> 
> **"if there's any kind of data that looks like model messages it should be placed in inputs chat history or outputs accordingly"**

**Source:** Joshua Paul → Dhruv Singh, 6:09 PM

---

## 🎯 Translation: Dual Behavior Pattern

### **CHAIN Event Structure:**

✅ **Use TOOL-LIKE flexible structure** (NOT MODEL-like chat format)

```json
{
  "event_type": "chain",
  "inputs": {
    "query": "What's the weather?",        // ✅ Structured input
    "parameters": {...}                    // ✅ Chain parameters
  },
  "outputs": {
    "result": "It's 72°F!",               // ✅ Structured output
    "status": "success"                    // ✅ Chain status
  }
}
```

❌ **DO NOT force entire chain into chat format:**

```json
{
  "inputs": {
    "chat_history": [...]  // ❌ Forces everything into chat
  },
  "outputs": {
    "role": "assistant",   // ❌ Chain is NOT a model
    "content": "..."
  }
}
```

---

## 🔄 Dual Behavior: When Model Messages Are Present

**IF** the chain contains model messages, include them as **FIELDS within the flexible structure:**

```json
{
  "event_type": "chain",
  "inputs": {
    "query": "What's the weather?",        // ✅ Structured agent input
    "chat_history": [                      // ✅ Model messages as a FIELD
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  },
  "outputs": {
    "result": "It's 72°F!",               // ✅ Structured agent result
    "conversation": [                      // ✅ Model messages as a FIELD
      {"role": "user", "content": "What's the weather?"},
      {"role": "assistant", "content": "It's 72°F!"}
    ]
  }
}
```

---

## 🎯 Key Principles

1. ✅ **CHAIN structure** = Flexible (like TOOL), NOT chat format
2. ✅ **Model messages** = Go in fields (`chat_history`, `conversation`) WITHIN structure
3. ❌ **DO NOT** force entire chain into `outputs.role/content`
4. ✅ **Preserve structured data** (query, result, status, metadata, etc.)

---

## 📦 Pydantic AI Fixture Status

**Python-SDK has 3 CHAIN fixtures that need review:**
- `pydantic_ai_anthropic_agent_001.json`
- `pydantic_ai_openai_agent_with_tools_001.json`
- `pydantic_ai_agent_multi_turn_conversation_001.json`

**Current Status:** Recently changed to chat format (WRONG per boss guidance)

**Action Required:** Hive-kube team will handle fixture corrections based on this guidance

---

## ✅ What Python-SDK Has Updated

1. ✅ **Standard updated** (`.praxis-os/standards/development/integrations/honeyhive-event-schema.md` v1.2)
   - CHAIN events use flexible structure
   - Model messages as fields within structure
   - Clear examples and anti-patterns

2. ✅ **Token/Metrics mapping** (from earlier today)
   - Token counts → `metadata.*`
   - Cost/timing → `metrics.*`

---

## 🤝 Coordination Plan

**Python-SDK:**
- ✅ Standard updated with boss guidance
- ⏸️ Awaiting hive-kube fixture corrections

**Hive-Kube:**
- 🔄 Will review and correct 3 Pydantic AI CHAIN fixtures
- 🔄 Will apply dual behavior pattern
- 🔄 Python-SDK will review after corrections

---

## 📞 Contact

If questions arise, coordinate through:
- Python-SDK session (this conversation)
- Hive-kube session (parallel work)

**Target:** Monday delivery - fixtures as specifications for ingestion service implementation

---

**🎯 Remember:** Fixtures are specifications. If they fail in hive-kube tests, that's expected - the ingestion service needs to be updated to meet the specification, not the other way around.

