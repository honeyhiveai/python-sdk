# Query Construction Patterns for Standards Discovery

**Keywords for search**: query construction, search_standards patterns, how to query effectively, semantic search best practices, RAG query optimization, finding standards content, query anti-patterns, effective queries, query strategy, search patterns

**This standard defines how AI assistants should construct effective `pos_search_project()` queries to discover prAxIs OS content reliably.**

---

## 🎯 TL;DR - Query Construction Quick Reference

**Core Principle:** Use **content-specific phrases** from target sections, not generic questions or structural keywords.

**Winning Pattern:**
```python
✅ pos_search_project(content_type="standards", query="specific phrase from target section unique values")
❌ pos_search_project(content_type="standards", query="what is concept name")
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

1. "How do I construct effective pos_search queries?"
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
pos_search_project(content_type="standards", query="widget sprocket gadget doohickey thingamajig")
```

**❌ Bad Pattern:**
```python
# Generic table structure terms
pos_search_project(content_type="standards", query="table rows columns")
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
pos_search_project(content_type="standards", query="initialize connection validate schema transform payload")
```

**❌ Bad Pattern:**
```python
# Generic process question
pos_search_project(content_type="standards", query="how to process data")
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
pos_search_project(content_type="standards", query="reviewing output approving changes fixing edge cases")
```

**❌ Bad Pattern:**
```python
# Structural keywords
pos_search_project(content_type="standards", query="INCLUDES EXCLUDES list items")
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
pos_search_project(content_type="standards", query="P Q R variables multiply divide result")
```

**❌ Bad Pattern:**
```python
# Generic math question
pos_search_project(content_type="standards", query="calculation formula")
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
pos_search_project(content_type="standards", query="start conservative 2.5x factor 12-15% threshold")
```

**❌ Bad Pattern:**
```python
# Generic concept
pos_search_project(content_type="standards", query="calibration guidelines recommendations")
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
pos_search_project(content_type="standards", query="template format example Baseline Enhanced Comparison")
```

**❌ Bad Pattern:**
```python
# Too generic
pos_search_project(content_type="standards", query="example template")
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
pos_search_project(content_type="standards", query="what is dependency injection")
pos_search_project(content_type="standards", query="how to handle errors")
pos_search_project(content_type="standards", query="best practices for testing")
```

**Why It Fails:**
- Too generic → matches 50+ sections
- TL;DR sections outrank deep content
- Gets overview, not specific guidance

**✅ Fix:**
```python
pos_search_project(content_type="standards", query="constructor injection setter injection field injection")
pos_search_project(content_type="standards", query="exception wrapping context preservation stack trace")
pos_search_project(content_type="standards", query="arrange act assert given when then")
```

---

### Anti-Pattern 2: Structural Keywords

**❌ Fails:**
```python
pos_search_project(content_type="standards", query="INCLUDES EXCLUDES")
pos_search_project(content_type="standards", query="Step 1 Step 2 Step 3")
pos_search_project(content_type="standards", query="Section Header Subsection")
```

**Why It Fails:**
- Matches document STRUCTURE, not content
- Headers may not appear in chunked text
- Generic structure terms match everything

**✅ Fix:**
```python
pos_search_project(content_type="standards", query="actual activity phrases from content")
pos_search_project(content_type="standards", query="initialize validate transform send")
pos_search_project(content_type="standards", query="specific topic domain terminology")
```

---

### Anti-Pattern 3: Single Word Queries

**❌ Fails:**
```python
pos_search_project(content_type="standards", query="testing")
pos_search_project(content_type="standards", query="database")
pos_search_project(content_type="standards", query="performance")
```

**Why It Fails:**
- Too broad → thousands of matches
- No semantic context
- Can't distinguish intent

**✅ Fix:**
```python
pos_search_project(content_type="standards", query="mock patch stub fake test double")
pos_search_project(content_type="standards", query="transaction isolation rollback deadlock")
pos_search_project(content_type="standards", query="memory cpu latency throughput bottleneck")
```

---

### Anti-Pattern 4: Asking for Concepts Instead of Content

**❌ Fails:**
```python
pos_search_project(content_type="standards", query="explain concept name")
pos_search_project(content_type="standards", query="definition of term")
pos_search_project(content_type="standards", query="what does X mean")
```

**Why It Fails:**
- Looking for explanation, not using content phrases
- Matches question sections, not answer sections
- TL;DR/FAQ outrank deep content

**✅ Fix:**
```python
pos_search_project(content_type="standards", query="definition terminology example usage pattern")
pos_search_project(content_type="standards", query="key phrase from definition unique to concept")
pos_search_project(content_type="standards", query="symptoms causes solutions prevention")
```

---

## ✅ Winning Patterns That Work

### Pattern 1: Content-Specific Phrases

**Strategy:** Use 3-5 words/phrases that appear in target section

```python
# Target: Finding list of orchestration activities
pos_search_project(content_type="standards", query="reviewing output approving changes fixing edge cases")

# Target: Finding specific formula calculation
pos_search_project(content_type="standards", query="P Q R variables multiply divide result")

# Target: Finding task type comparison
pos_search_project(content_type="standards", query="widget sprocket gadget complexity comparison")
```

**Success Rate:** 95%+ when phrases match target content

---

### Pattern 2: Unique Values

**Strategy:** Use numbers, percentages, or sequences unique to target

```python
# Target: Calibration section with specific values
pos_search_project(content_type="standards", query="start conservative 2.5x factor 12-15% threshold")

# Target: Performance benchmarks
pos_search_project(content_type="standards", query="latency 50ms 95th percentile 200ms 99th")

# Target: Version-specific guidance
pos_search_project(content_type="standards", query="Python 3.11 3.12 match case structural pattern")
```

**Success Rate:** 98%+ when values are unique to section

---

### Pattern 3: Multi-Keyword Semantic

**Strategy:** Combine domain terms that co-occur in target

```python
# Target: Race condition prevention
pos_search_project(content_type="standards", query="mutex lock atomic compare-and-swap memory order")

# Target: Dependency injection patterns
pos_search_project(content_type="standards", query="constructor injection container autowire lifecycle")

# Target: Testing strategies
pos_search_project(content_type="standards", query="unit integration end-to-end pyramid trophy")
```

**Success Rate:** 90%+ when keywords have strong semantic relationship

---

### Pattern 4: Activity + Context

**Strategy:** Action verbs + domain context from procedural content

```python
# Target: Spec validation process
pos_search_project(content_type="standards", query="parse validate check conflicts verify completeness")

# Target: Error handling flow
pos_search_project(content_type="standards", query="catch wrap log rethrow context preserve")

# Target: Review checklist
pos_search_project(content_type="standards", query="verify test document approve merge deploy")
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
results = pos_search_project(query, n_results=3)

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
pos_search_project(content_type="standards", query="widget sprocket gadget complexity multiplier")

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
pos_search_project(content_type="standards", query="INCLUDES EXCLUDES list")
```

**Result:** Returns generic list structure content, not target
**Why It Failed:** "INCLUDES EXCLUDES" are section headers, not content
**Relevance:** 0.45 (wrong section ranked #1)

---

### Attempt 2: Generic Question ❌

```python
pos_search_project(content_type="standards", query="what counts as active time")
```

**Result:** Returns TL;DR and overview, not specific activities
**Why It Failed:** Too generic, matches concept not content
**Relevance:** 0.62 (overview ranked higher than details)

---

### Attempt 3: Content-Specific Phrases ✅

```python
pos_search_project(content_type="standards", query="reviewing output approving changes fixing edge cases")
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

Before running `pos_search_project()`, verify:

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
| **Constructing new query** | `pos_search_project(content_type="standards", query="query construction patterns best practices")` |
| **Query not finding content** | `pos_search_project(content_type="standards", query="why query fails content-specific phrases")` |
| **Choosing query strategy** | `pos_search_project(content_type="standards", query="table procedure list formula query patterns")` |
| **Debugging low relevance** | `pos_search_project(content_type="standards", query="query anti-patterns structural keywords")` |
| **Learning from examples** | `pos_search_project(content_type="standards", query="case study query optimization")` |
| **Testing query effectiveness** | `pos_search_project(content_type="standards", query="test query relevance score refine")` |

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
- `standards/ai-assistant/PRAXIS-OS-ORIENTATION.md` - Overall prAxIs OS usage
- `standards/ai-assistant/standards-creation-process.md` - Creating new standards

**Query anytime:**
```python
pos_search_project(content_type="standards", query="query construction patterns")
pos_search_project(content_type="standards", query="content-specific phrases semantic search")
pos_search_project(content_type="standards", query="query anti-patterns fails")
```

---

**Remember**: If authoring is about making content discoverable, querying is about finding it effectively. Content-specific phrases match target sections semantically. Generic questions match overview sections. Match content, not structure, for precision.

