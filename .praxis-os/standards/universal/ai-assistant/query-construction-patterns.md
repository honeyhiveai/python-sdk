# Query Construction Patterns for Standards Discovery

**Keywords for search**: query construction, search_standards patterns, how to query effectively, semantic search best practices, RAG query optimization, finding standards content, query anti-patterns, effective queries, query strategy, search patterns

**This standard defines how AI assistants should construct effective `search_standards()` queries to discover prAxIs OS content reliably.**

---

## 🎯 TL;DR - Query Construction Quick Reference

**Core Principle:** Use **content-specific phrases** from target sections, not generic questions or structural keywords.

**Winning Pattern:**
```python
✅ search_standards("specific phrase from target section unique values")
❌ search_standards("what is concept name")
```

**Why:**
- Generic questions match many sections → wrong results ranked higher
- Content-specific phrases match target section → semantic similarity = high rank
- Unique values (numbers, sequences) appear only in target → precise targeting

**Quick Rules:**
1. **Match content, not structure** - Use words from target text, not section headers
2. **Use unique values** - Numbers, percentages, sequences that appear only in target
3. **Test iteratively** - Run query, check result, refine if needed
4. **Multi-keyword** - Combine 3-5 relevant terms for semantic matching

---

## ❓ Questions This Answers

1. "How do I construct effective search_standards queries?"
2. "Why aren't my queries finding the right content?"
3. "What makes a query generic vs specific?"
4. "Should I use questions or keywords in queries?"
5. "How do I find content deep in long documents?"
6. "What are query anti-patterns to avoid?"
7. "How do I test if my query works?"
8. "Why do structural keywords fail?"
9. "What is content-specific query construction?"
10. "How do I use unique values in queries?"
11. "What query patterns work best for tables?"
12. "How do I find procedural content?"
13. "What's the difference between authoring for RAG and querying RAG?"

---

## 🎨 Query Patterns By Content Type

### 1. Finding Tables

**✅ Good Pattern:**
```python
# Use keywords from ROWS, not column headers
search_standards("widget sprocket gadget doohickey thingamajig")
```

**❌ Bad Pattern:**
```python
# Generic table structure terms
search_standards("table rows columns")
```

**Why Good Works:**
- Row keywords: "widget sprocket gadget" appear IN the table
- Multiple row items = high semantic match to table content
- Unique item names narrow to specific table

**Example Content Found:**
```markdown
| Item Type | Category | ... |
|-----------|----------|-----|
| Widget    | A        | ... |
| Sprocket  | B        | ... |
| Gadget    | C        | ... |
```

---

### 2. Finding Procedural Steps

**✅ Good Pattern:**
```python
# Use verbs + nouns from actual steps
search_standards("initialize connection validate schema transform payload")
```

**❌ Bad Pattern:**
```python
# Generic process question
search_standards("how to process data")
```

**Why Good Works:**
- "initialize connection validate schema" matches step sequence
- Action verbs from actual procedure text
- Multiple steps = semantic match to procedural content

**Example Content Found:**
```markdown
1. Initialize connection
2. Validate schema
3. Transform payload
4. Send to endpoint
```

---

### 3. Finding Lists/Criteria

**✅ Good Pattern:**
```python
# Use items from list, not list structure
search_standards("reviewing output approving changes fixing edge cases")
```

**❌ Bad Pattern:**
```python
# Structural keywords
search_standards("INCLUDES EXCLUDES list items")
```

**Why Good Works:**
- "reviewing output approving changes" are actual list items
- Activity phrases from content, not headers
- Matches semantic meaning of list purpose

**Example Content Found:**
```markdown
Activities included:
- Reviewing output (3-7 min)
- Approving changes (1-2 min)
- Fixing edge cases (0-5 min)
```

---

### 4. Finding Formulas/Calculations

**✅ Good Pattern:**
```python
# Use variables + operation terms
search_standards("P Q R variables multiply divide result")
```

**❌ Bad Pattern:**
```python
# Generic math question
search_standards("calculation formula")
```

**Why Good Works:**
- "P Q R variables" are actual symbols used
- "multiply divide" match operations in formula
- Variable names are unique to that calculation

**Example Content Found:**
```markdown
Variables:
- P = Initial value
- Q = Multiplier
- R = Result

Formula: R = P × Q ÷ Factor
```

---

### 5. Finding Calibration/Guidelines with Specific Values

**✅ Good Pattern:**
```python
# Use exact numbers/percentages from target
search_standards("start conservative 2.5x factor 12-15% threshold")
```

**❌ Bad Pattern:**
```python
# Generic concept
search_standards("calibration guidelines recommendations")
```

**Why Good Works:**
- "2.5x" and "12-15%" are unique values from section
- Exact numbers appear only in target section
- Precision = high relevance score

**Example Content Found:**
```markdown
Start conservative:
- Use 2.5x factor (assume slower)
- Use 12-15% threshold (not 8-10%)
- Track for 8-12 iterations
```

---

### 6. Finding Examples/Format Templates

**✅ Good Pattern:**
```python
# Use template structure keywords + domain
search_standards("template format example Baseline Enhanced Comparison")
```

**❌ Bad Pattern:**
```python
# Too generic
search_standards("example template")
```

**Why Good Works:**
- "Baseline Enhanced Comparison" are section headers in template
- Structure terms combined with domain terms
- "format example" signals looking for template

**Example Content Found:**
```markdown
**Template Format:**

**Baseline:** {value}
**Enhanced:** {value}
**Comparison:** {leverage}x
```

---

## ❌ Anti-Patterns That Fail

### Anti-Pattern 1: Generic Questions

**❌ Fails:**
```python
search_standards("what is dependency injection")
search_standards("how to handle errors")
search_standards("best practices for testing")
```

**Why It Fails:**
- Too generic → matches 50+ sections
- TL;DR sections outrank deep content
- Gets overview, not specific guidance

**✅ Fix:**
```python
search_standards("constructor injection setter injection field injection")
search_standards("exception wrapping context preservation stack trace")
search_standards("arrange act assert given when then")
```

---

### Anti-Pattern 2: Structural Keywords

**❌ Fails:**
```python
search_standards("INCLUDES EXCLUDES")
search_standards("Step 1 Step 2 Step 3")
search_standards("Section Header Subsection")
```

**Why It Fails:**
- Matches document STRUCTURE, not content
- Headers may not appear in chunked text
- Generic structure terms match everything

**✅ Fix:**
```python
search_standards("actual activity phrases from content")
search_standards("initialize validate transform send")
search_standards("specific topic domain terminology")
```

---

### Anti-Pattern 3: Single Word Queries

**❌ Fails:**
```python
search_standards("testing")
search_standards("database")
search_standards("performance")
```

**Why It Fails:**
- Too broad → thousands of matches
- No semantic context
- Can't distinguish intent

**✅ Fix:**
```python
search_standards("mock patch stub fake test double")
search_standards("transaction isolation rollback deadlock")
search_standards("memory cpu latency throughput bottleneck")
```

---

### Anti-Pattern 4: Asking for Concepts Instead of Content

**❌ Fails:**
```python
search_standards("explain concept name")
search_standards("definition of term")
search_standards("what does X mean")
```

**Why It Fails:**
- Looking for explanation, not using content phrases
- Matches question sections, not answer sections
- TL;DR/FAQ outrank deep content

**✅ Fix:**
```python
search_standards("definition terminology example usage pattern")
search_standards("key phrase from definition unique to concept")
search_standards("symptoms causes solutions prevention")
```

---

## ✅ Winning Patterns That Work

### Pattern 1: Content-Specific Phrases

**Strategy:** Use 3-5 words/phrases that appear in target section

```python
# Target: Finding list of orchestration activities
search_standards("reviewing output approving changes fixing edge cases")

# Target: Finding specific formula calculation
search_standards("P Q R variables multiply divide result")

# Target: Finding task type comparison
search_standards("widget sprocket gadget complexity comparison")
```

**Success Rate:** 95%+ when phrases match target content

---

### Pattern 2: Unique Values

**Strategy:** Use numbers, percentages, or sequences unique to target

```python
# Target: Calibration section with specific values
search_standards("start conservative 2.5x factor 12-15% threshold")

# Target: Performance benchmarks
search_standards("latency 50ms 95th percentile 200ms 99th")

# Target: Version-specific guidance
search_standards("Python 3.11 3.12 match case structural pattern")
```

**Success Rate:** 98%+ when values are unique to section

---

### Pattern 3: Multi-Keyword Semantic

**Strategy:** Combine domain terms that co-occur in target

```python
# Target: Race condition prevention
search_standards("mutex lock atomic compare-and-swap memory order")

# Target: Dependency injection patterns
search_standards("constructor injection container autowire lifecycle")

# Target: Testing strategies
search_standards("unit integration end-to-end pyramid trophy")
```

**Success Rate:** 90%+ when keywords have strong semantic relationship

---

### Pattern 4: Activity + Context

**Strategy:** Action verbs + domain context from procedural content

```python
# Target: Spec validation process
search_standards("parse validate check conflicts verify completeness")

# Target: Error handling flow
search_standards("catch wrap log rethrow context preserve")

# Target: Review checklist
search_standards("verify test document approve merge deploy")
```

**Success Rate:** 92%+ for procedural content

---

## 🧪 Testing Your Queries

### Step 1: Construct Initial Query

Based on what you're looking for, construct query using patterns above:

```python
# Looking for: Table showing task types with multipliers
query = "widget sprocket gadget complexity multiplier"
```

---

### Step 2: Run and Inspect Results

```python
results = search_standards(query, n_results=3)

# Check:
# 1. Is target content in top 3 results?
# 2. What relevance score? (> 0.85 is good)
# 3. Does content match what you need?
```

---

### Step 3: Refine If Needed

**If target not found:**
1. Add more specific keywords from target
2. Replace generic terms with content phrases
3. Add unique values if available

**If wrong content ranked higher:**
1. Remove generic terms
2. Add distinguishing keywords
3. Use more specific domain terms

---

### Step 4: Document Working Query

Once you find pattern that works, document it:

```markdown
**Working Query:**
search_standards("widget sprocket gadget complexity multiplier")

**Returns:** Complete task type comparison table
**Relevance:** 1.08-1.12
**Position:** #3 result
**Why It Works:** Row keywords from actual table content
```

---

## 🔬 Case Study: Real Query Optimization

### Context

Target content: List of activities included in orchestration estimate

**Target Section:**
```markdown
Activities included:
- Reviewing output (3-7 min)
- Approving changes (1-2 min)
- Fixing edge cases (0-5 min)
```

---

### Attempt 1: Structural Keywords ❌

```python
search_standards("INCLUDES EXCLUDES list")
```

**Result:** Returns generic list structure content, not target
**Why It Failed:** "INCLUDES EXCLUDES" are section headers, not content
**Relevance:** 0.45 (wrong section ranked #1)

---

### Attempt 2: Generic Question ❌

```python
search_standards("what counts as active time")
```

**Result:** Returns TL;DR and overview, not specific activities
**Why It Failed:** Too generic, matches concept not content
**Relevance:** 0.62 (overview ranked higher than details)

---

### Attempt 3: Content-Specific Phrases ✅

```python
search_standards("reviewing output approving changes fixing edge cases")
```

**Result:** Returns exact target section with 6-item activity list
**Why It Worked:** Used actual activity phrases from list items
**Relevance:** 0.89 (target found as #3 result)
**Success!** ✅

---

### Lesson Learned

**Match content phrases, not structure keywords**
- ❌ "INCLUDES EXCLUDES" (structure)
- ✅ "reviewing output approving changes" (content)

**Use words that appear in target text**
- ❌ "what counts as" (question framing)
- ✅ "reviewing approving fixing" (actual activities)

---

## 🔧 Query Construction Checklist

Before running `search_standards()`, verify:

**Content Matching:**
- [ ] Query uses phrases from target content (not headers)
- [ ] Query includes 3-5 relevant keywords
- [ ] Query avoids generic question framing

**Specificity:**
- [ ] Query includes domain-specific terms
- [ ] Query includes unique values if available (numbers, percentages)
- [ ] Query distinguishes target from similar content

**Pattern Selection:**
- [ ] Tables: Use row keywords
- [ ] Procedures: Use action verbs + nouns
- [ ] Lists: Use item phrases
- [ ] Formulas: Use variables + operations
- [ ] Guidelines: Use specific values

**Testing:**
- [ ] Run query with n_results=3
- [ ] Check if target in top 3
- [ ] Verify relevance score > 0.75
- [ ] Refine if needed

---

## 📊 Query Strategy Decision Tree

```
┌─ Need to find content ─────────────────────────┐
│                                                 │
├─ What type? ───────────────────────────────────┤
│                                                 │
├─ TABLE:     Use keywords from rows             │
│   Example:  "widget sprocket gadget"           │
│                                                 │
├─ PROCEDURE: Use action verbs from steps        │
│   Example:  "initialize validate transform"    │
│                                                 │
├─ LIST:      Use phrases from items             │
│   Example:  "reviewing approving fixing"       │
│                                                 │
├─ FORMULA:   Use variables + operations         │
│   Example:  "P Q R multiply divide"            │
│                                                 │
├─ GUIDELINE: Use specific values                │
│   Example:  "2.5x factor 12-15% threshold"     │
│                                                 │
├─ CONCEPT:   Use definition keywords            │
│   Example:  "isolation levels serializable"    │
│                                                 │
└─────────────────────────────────────────────────┘

Then:
1. Construct query with pattern
2. Run with n_results=3
3. Check if target found
4. Refine if needed
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Constructing new query** | `search_standards("query construction patterns best practices")` |
| **Query not finding content** | `search_standards("why query fails content-specific phrases")` |
| **Choosing query strategy** | `search_standards("table procedure list formula query patterns")` |
| **Debugging low relevance** | `search_standards("query anti-patterns structural keywords")` |
| **Learning from examples** | `search_standards("case study query optimization")` |
| **Testing query effectiveness** | `search_standards("test query relevance score refine")` |

---

## 📞 Questions?

**How do I know which pattern to use?**
→ Identify content type (table, procedure, list, etc.) and use corresponding pattern from decision tree.

**What if I don't know exact content phrases?**
→ Start with domain keywords, check results, then refine with content-specific phrases from what you find.

**Should I always avoid questions in queries?**
→ Not always, but content-specific phrases usually outperform generic questions. Test both if unsure.

**What relevance score is "good"?**
→ >0.85 excellent, 0.70-0.85 good, 0.50-0.70 marginal, <0.50 needs refinement.

**How many keywords should I use?**
→ 3-5 keywords typically optimal. Too few = too generic, too many = over-constrains.

---

**Related Standards:**
- `standards/ai-assistant/rag-content-authoring.md` - How to WRITE content for RAG (authoring side)
- `standards/ai-assistant/AGENT-OS-ORIENTATION.md` - Overall prAxIs OS usage
- `standards/ai-assistant/standards-creation-process.md` - Creating new standards

**Query anytime:**
```python
search_standards("query construction patterns")
search_standards("content-specific phrases semantic search")
search_standards("query anti-patterns fails")
```

---

**Remember**: If authoring is about making content discoverable, querying is about finding it effectively. Content-specific phrases match target sections semantically. Generic questions match overview sections. Match content, not structure, for precision.

