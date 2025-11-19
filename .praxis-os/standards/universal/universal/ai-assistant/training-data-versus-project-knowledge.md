# Training Data vs Project Knowledge

## 🎯 Purpose

Define the critical distinction between "knowing ABOUT things from training data" versus "knowing THIS PROJECT's implementation" to prevent agents from making false confidence assumptions that lead to incorrect implementations.

**Key Distinction:** You have general knowledge from training. You do NOT have knowledge of THIS PROJECT until you query/read it. These are completely different things.

---

## 🚨 Training Data vs Project Knowledge Quick Reference (TL;DR)

**The Critical Mistake:**
```
❌ Agent: "I know how authentication works from training data"
❌ Agent: "I'll implement using standard patterns"
❌ Agent: *writes code based on assumptions*
❌ Result: Wrong patterns, wrong conventions, wrong architecture
```

**The Correct Approach:**
```
✅ Agent: "I know authentication EXISTS from training data"
✅ Agent: "I DON'T know how THIS PROJECT does auth"
✅ Agent: search_standards("how does authentication work in this project")
✅ Agent: grep("auth", path="src/")  # Find actual auth code
✅ Agent: read_file("src/auth/...")  # Read THIS PROJECT's implementation
✅ Result: Code that matches THIS PROJECT's patterns
```

**Core Principle: Training Data = General Concepts, NOT Specific Implementation**

You know:
- ✅ That authentication exists
- ✅ Common authentication patterns (JWT, OAuth, sessions)
- ✅ General security principles
- ✅ How to write Python/JS/Go code

You DON'T know (until you search/read):
- ❌ How THIS PROJECT structures auth
- ❌ What THIS PROJECT's naming conventions are
- ❌ Which auth library THIS PROJECT uses
- ❌ Where THIS PROJECT stores auth logic
- ❌ What THIS PROJECT's patterns are
- ❌ How THIS PROJECT's tests are structured

**MANDATORY: Assume you're wrong about project details until verified**

---

## 🔍 The Network Security Engineer Analogy

**How prAxIs OS mirrors professional troubleshooting workflows:**

Imagine you're a network security engineer doing front-line support at a hosting company:

1. **Landing Page (Environment Guidelines)** → **prAxIs OS Base Standards**
   - High-level details about how the system works
   - Explicit callouts and critical patterns
   - Entry point for understanding the environment

2. **System Layouts** → **Universal CS Standards (Shipped to All Projects)**
   - Common patterns that apply across projects
   - Language-agnostic best practices
   - Helps you work in any project using prAxIs OS

3. **Customer-Specific Configurations** → **Project-Specific Standards (Added Over Time)**
   - Standards you and the user create together
   - Durable, persistent knowledge about THIS PROJECT
   - Turns you into a specialist on THIS PROJECT

4. **External Discovery** → **Internet Searches & User Questions**
   - Current information not yet in standards
   - Real-time updates (APIs, libraries, tools)
   - Human-in-the-loop for clarification

5. **Deep Code Reading** → **Network Device Parsing (Last Resort)**
   - Only when standards don't cover it
   - Detailed implementation inspection
   - Slow, but necessary for novel problems

6. **Training Data** → **Outdated Manual (Should Be Last Resort)**
   - Frozen point in time (you don't know when)
   - Like asking a 5-year-old manual for current configurations
   - Makes NO sense as first source of truth

**The Critical Insight:**

Training data is a **frozen point in time**. You don't know when it was frozen. It could be 6 months old, 2 years old, or from before a major API change. Using it as your first source is like trusting a 5-year-old network diagram to fix a current issue.

**The Correct Discovery Hierarchy:**

```
1. Standards (prAxIs OS base → Universal CS → Project-specific)
   ↓ (if not found)
2. External Discovery (web_search for current info)
   ↓ (if still unclear)
3. User Questions (human in the loop)
   ↓ (if needed)
4. Code Reading (deep dive into implementation)
   ↓ (last resort)
5. Training Data (use with heavy skepticism, verify with current sources)
```

**Why This Hierarchy Matters:**

- ✅ Standards = Current, project-specific, verified knowledge
- ✅ External Discovery = Up-to-date information (APIs, libraries, tools)
- ✅ User Questions = Human expertise and project context
- ✅ Code Reading = Ground truth, but slow
- ❌ Training Data = Unknown freshness, generic patterns, frozen knowledge

**The Rule:**

> **Training data should NEVER be your first source. It's a last resort, and even then, verify with current sources.**

---

## 🎓 The Genius College Graduate Analogy

**Understanding Training Data Limitations:**

Training data makes you the equivalent of a **genius college graduate**:
- ✅ Strong foundation in computer science fundamentals
- ✅ Understands general patterns and concepts
- ✅ Can read and write code in multiple languages
- ✅ Knows common algorithms, data structures, best practices
- ✅ Familiar with frameworks, libraries, and tools

**But NOT an expert on anything by itself:**

Every project is unique and has its own take on its problem space. Universal patterns you distill from training data will cause you to take bad actions because:

- ❌ Each project has unique constraints and requirements
- ❌ Each project has evolved its own conventions over time
- ❌ Each project makes trade-offs specific to its context
- ❌ Generic patterns ≠ Project-specific implementation

**The Critical Insight:**

> **Training data gives you the foundation to understand things quickly, but it does NOT make you an expert on THIS PROJECT. You become an expert through discovery: standards, code reading, user questions, and current information sources.**

**Real-World Parallel:**

A brilliant computer science graduate fresh out of MIT:
- ✅ Can understand any codebase quickly (strong foundation)
- ✅ Knows general patterns (MVC, REST, OOP, etc.)
- ❌ Doesn't know THIS COMPANY's specific conventions
- ❌ Doesn't know THIS PROJECT's unique architecture decisions
- ❌ Doesn't know THIS TEAM's coding style preferences

**They become an expert by:**
1. Reading company documentation and standards
2. Studying existing codebases
3. Asking senior engineers questions
4. Learning from current team practices
5. Understanding project-specific constraints

**You should do the same:**
1. Query standards (prAxIs OS → Universal CS → Project-specific)
2. Read existing code
3. Ask user questions
4. Search for current information (web_search)
5. Only then reference training data (with skepticism)

**The Mental Model:**

```
Training Data = Foundation (college education)
                ↓
Discovery Process = Becoming Expert (on-the-job learning)
                ↓
THIS PROJECT = Unique Implementation (requires discovery)
```

---

1. Why do I keep implementing things wrong even though I "know" the concept?
2. When should I trust my training data knowledge vs query/read?
3. How do I distinguish between general knowledge and project-specific knowledge?
4. What's the difference between "knowing about X" and "knowing how THIS PROJECT does X"?
5. Why can't I just apply standard patterns I learned in training?
6. How do I prevent false confidence from training data?
7. When should I search/read vs use training knowledge?
8. What does "you don't know THIS PROJECT" actually mean?
9. How do I catch myself making training-data assumptions?
10. Why does "I know how X works" lead to wrong implementations?
11. What should I do when something seems familiar from training?
12. How do I avoid "lala land" assumptions about the codebase?
13. What's the correct order for discovering information about a project?
14. Why shouldn't training data be my first source of information?
15. How does the Network Security Engineer analogy apply to prAxIs OS?
16. What's the information discovery hierarchy?
17. Why is training data "frozen in time" a problem?
18. How does the "genius college graduate" analogy apply to training data?
19. Why does training data give foundation but not expertise?
20. What's the difference between foundational knowledge and project expertise?

---

## 🚫 The Problem

**Agents fall into "I know this" mode based on training data pattern recognition:**

### Failure Pattern 1: False Confidence
```
User: "Add a new API endpoint"
Agent: *recognizes "API endpoint" from training data*
Agent: "I know how APIs work!" 
Agent: *writes code using generic REST patterns*
Reality: THIS PROJECT uses GraphQL, not REST
Result: ❌ Complete rewrite needed
```

### Failure Pattern 2: Assumed Conventions
```
User: "Update the User model"
Agent: *recognizes "model" from training data*
Agent: "Models go in models.py with class definitions"
Agent: *creates models.py*
Reality: THIS PROJECT uses TypeORM entities in src/entities/
Result: ❌ Wrong location, wrong patterns
```

### Failure Pattern 3: Generic Library Usage
```
User: "Add logging"
Agent: *recognizes "logging" from training data*
Agent: "I'll use the standard logging library"
Agent: *imports logging*
Reality: THIS PROJECT uses Winston with custom formatters
Result: ❌ Inconsistent logging, doesn't match existing code
```

### Failure Pattern 4: Assumed Architecture
```
User: "Add database migration"
Agent: *recognizes "migration" from training data*
Agent: "I'll create a migration in db/migrations/"
Agent: *creates migration file*
Reality: THIS PROJECT uses Prisma with different migration workflow
Result: ❌ Migration doesn't work, wrong format
```

---

## ✅ The Solution

### Rule 1: Training Data = Concepts Only, NOT Implementation

**What training data tells you:**
- Concepts exist (auth, APIs, databases)
- General patterns are common (MVC, REST, etc.)
- Best practices in abstract
- How languages work in general

**What training data CANNOT tell you:**
- How THIS PROJECT structures things
- What THIS PROJECT's conventions are
- Which libraries THIS PROJECT uses
- Where THIS PROJECT puts files
- How THIS PROJECT's existing code works

### Rule 2: Always Verify Project-Specific Details

**Before ANY implementation, verify:**

```bash
# 1. Search for project patterns
search_standards("how to add X in this project")

# 2. Find existing examples
grep("similar_feature", path="src/")

# 3. Read actual implementation
read_file("src/path/to/existing_example.py")

# 4. Check project structure
list_dir("src/")

# 5. Look for configuration
read_file("package.json")  # or requirements.txt, go.mod, etc.
```

### Rule 3: "I Know X" → "Let Me Verify How THIS PROJECT Does X"

**Mental Model Shift:**

| ❌ Wrong Thinking | ✅ Right Thinking |
|------------------|------------------|
| "I know auth" | "I know auth exists; let me see how THIS PROJECT does it" |
| "I'll use standard patterns" | "Let me find THIS PROJECT's patterns" |
| "This looks like a REST API" | "Let me verify what THIS PROJECT uses" |
| "Models go in models/" | "Where does THIS PROJECT put models?" |
| "I'll import logging" | "What logging library does THIS PROJECT use?" |

### Rule 4: Recognition ≠ Knowledge

**When you recognize something from training:**

```python
# ❌ WRONG: Act on recognition
def handle_recognition():
    recognize("This looks familiar")
    assume("I know how this works")
    implement("Based on training patterns")
    # Result: Probably wrong for THIS PROJECT

# ✅ RIGHT: Use recognition as a query trigger
def handle_recognition():
    recognize("This looks familiar from training")
    trigger_query("Let me verify THIS PROJECT's approach")
    search_standards("how does this work here")
    grep("existing_examples")
    read_actual_code()
    implement("Based on THIS PROJECT's patterns")
    # Result: Matches project conventions
```

### Rule 5: Assume You're Wrong Until Verified

**Default mental state:**

```
"I think I know how this works from training data...
 BUT I'm probably wrong about THIS PROJECT's specifics.
 Let me search/read to verify before implementing."
```

**NOT:**

```
"I know how this works from training data.
 I'll just implement it."
```

---

## 🔧 Practical Application

### Scenario 1: Adding a New Feature

**❌ Training Data Approach (WRONG):**
```
User: "Add user authentication"
Agent: *thinks: "I know auth, I'll use JWT"*
Agent: *implements JWT from training patterns*
Result: Project uses OAuth2, complete rewrite needed
```

**✅ Project Knowledge Approach (RIGHT):**
```
User: "Add user authentication"
Agent: *thinks: "Auth exists as concept, but how does THIS PROJECT do it?"*
Agent: search_standards("authentication patterns in this project")
Agent: grep("auth", path="src/")
Agent: read_file("src/auth/existing_auth.ts")
Agent: *implements matching existing patterns*
Result: Consistent with project architecture
```

### Scenario 2: Fixing a Bug

**❌ Training Data Approach (WRONG):**
```
User: "Fix the database connection error"
Agent: *thinks: "I know how DB connections work"*
Agent: *implements generic connection pooling from training*
Result: Doesn't work with THIS PROJECT's ORM
```

**✅ Project Knowledge Approach (RIGHT):**
```
User: "Fix the database connection error"
Agent: *thinks: "DB connections exist, but what does THIS PROJECT use?"*
Agent: grep("database.*connection", path="src/")
Agent: read_file("src/config/database.ts")
Agent: search_standards("database configuration patterns")
Agent: *fixes using THIS PROJECT's actual DB setup*
Result: Bug fixed, matches project patterns
```

### Scenario 3: Adding Tests

**❌ Training Data Approach (WRONG):**
```
User: "Add tests for the new feature"
Agent: *thinks: "I know testing patterns"*
Agent: *writes tests using Jest patterns from training*
Result: Project uses Vitest with different setup
```

**✅ Project Knowledge Approach (RIGHT):**
```
User: "Add tests for the new feature"
Agent: *thinks: "Testing exists, but how does THIS PROJECT test?"*
Agent: list_dir("tests/")
Agent: read_file("tests/example.test.ts")
Agent: grep("describe\\(", path="tests/")
Agent: read_file("package.json")  # Check test runner
Agent: *writes tests matching THIS PROJECT's patterns*
Result: Tests run, match existing test style
```

### Scenario 4: Information Discovery Hierarchy in Action

**❌ Wrong Order (Training Data First):**
```
User: "Add OAuth2 authentication"
Agent: *thinks: "I know OAuth2 from training data"*
Agent: *implements using training patterns*
Agent: *uses outdated library from training*
Result: Wrong implementation, outdated approach, doesn't match project
```

**✅ Correct Order (Following Discovery Hierarchy):**
```
User: "Add OAuth2 authentication"

Step 1: Standards (prAxIs OS base → Universal CS → Project-specific)
  → search_standards("authentication patterns in this project")
  → search_standards("OAuth2 implementation")
  → Finds: Project uses Auth0, custom middleware pattern

Step 2: External Discovery (if standards don't cover current API)
  → web_search("Auth0 latest API changes 2025")
  → Discovers: New token refresh endpoint

Step 3: User Questions (if unclear)
  → Ask: "Should we use Auth0's new refresh endpoint or existing pattern?"

Step 4: Code Reading (to understand existing implementation)
  → read_file("src/auth/existing_auth.ts")
  → Understands: Current patterns, middleware structure

Step 5: Training Data (last resort, verify with current sources)
  → NOT used as first source
  → Only referenced to understand general OAuth2 concepts
  → Verified against current Auth0 docs

Result: Implementation matches project patterns, uses current APIs, verified approach
```

---

## 🔄 Self-Correction Pattern

**When you catch yourself assuming:**

1. **Stop:** "Wait, am I assuming based on training data?"
2. **Question:** "Do I actually know how THIS PROJECT does this?"
3. **Verify:** Query/search/read actual project code
4. **Implement:** Based on verified project patterns

**Red Flag Phrases (Internal Monologue):**
- "I know how this works" → ⚠️ Stop, verify
- "This is standard" → ⚠️ Standard WHERE? Not necessarily here
- "I'll use typical patterns" → ⚠️ Typical for WHAT? Not this project
- "This looks like X" → ⚠️ Looks like ≠ Is
- "I've seen this before" → ⚠️ Seen WHERE? Not in this codebase

---

## 📋 Decision Checklist

Before implementing anything, verify:

**Information Discovery Order:**
- [ ] Have I checked standards FIRST (prAxIs OS → Universal CS → Project-specific)?
- [ ] If standards don't cover it, have I searched externally (web_search) for current info?
- [ ] If still unclear, have I asked the user questions?
- [ ] If needed, have I read the actual code?
- [ ] Am I using training data as LAST RESORT (not first source)?

**Project-Specific Verification:**
- [ ] Have I searched for THIS PROJECT's approach?
- [ ] Have I grep'd for existing examples?
- [ ] Have I read actual code from THIS PROJECT?
- [ ] Have I verified the libraries THIS PROJECT uses?
- [ ] Have I checked THIS PROJECT's file structure?
- [ ] Am I implementing based on THIS PROJECT's patterns (not training data)?
- [ ] Have I questioned my assumptions from training data?

**If ANY box is unchecked → You're probably about to implement wrong**

---

## 🎯 Success Metrics

**You're doing it right when:**
- ✅ Every implementation matches existing code style
- ✅ You use the same libraries as the rest of the project
- ✅ Your code fits naturally in the existing structure
- ✅ Tests follow the same patterns as existing tests
- ✅ You rarely need major rewrites after code review

**You're doing it wrong when:**
- ❌ Code reviews consistently say "we don't do it that way"
- ❌ Your implementations use different libraries than existing code
- ❌ Your file structure doesn't match the rest of the project
- ❌ Your code style is inconsistent with existing code
- ❌ You frequently need to rewrite after "discovering" project conventions

---

## 🔗 Related Standards

- **[Agent Decision Protocol](./agent-decision-protocol.md)** - Query: "decision protocol generic knowledge"
- **[Query Construction Patterns](./query-construction-patterns.md)** - Query: "how to construct effective queries"
- **[prAxIs OS Orientation](./AGENT-OS-ORIENTATION.md)** - Query: "orientation project-specific knowledge"

---

## 🔍 When to Query This Standard

Query when you:
- Feel confident you "know" how something works
- Recognize a pattern from training data
- About to implement based on "standard" approaches
- Catch yourself saying "I'll just use typical patterns"
- Start implementing without verifying project approach
- Notice your code doesn't match existing project style

**Keywords for search**: training data assumptions, generic knowledge, project-specific patterns, false confidence, verify before implementing, this project not training data, assumed conventions, recognition not knowledge, generic patterns wrong project, information discovery hierarchy, network security engineer analogy, training data frozen point in time, discovery order, standards first training data last, outdated manual frozen knowledge, genius college graduate analogy, foundation vs expertise, training data foundation not expertise, foundational knowledge vs project expertise

---

**Last Updated:** 2025-11-01
**Version:** 2.1 (Added Genius College Graduate analogy to complement Network Security Engineer analogy)
**Context:** Addresses agents falling back to training data instead of verifying THIS PROJECT's actual implementation. Now includes explicit discovery hierarchy, Network Security Engineer workflow analogy, and Genius College Graduate foundation vs expertise analogy.

