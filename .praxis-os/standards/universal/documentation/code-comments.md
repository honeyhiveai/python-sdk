# Code Comments - Universal Documentation Practice

**Timeless principles for writing helpful code comments.**

---

## 🎯 TL;DR - Code Comments Quick Reference

**Keywords for search**: code comments, comment best practices, when to comment, comment styles, docstrings, JSDoc, Javadoc, TODO comments, FIXME, comment anti-patterns, self-documenting code

**Core Principle:** Comments should explain WHY, not WHAT. Code explains WHAT.

**When to Comment:**
- ✅ **Complex logic** - Explain the algorithm/approach
- ✅ **Non-obvious decisions** - Why you chose this solution
- ✅ **Performance optimizations** - Why this unusual approach
- ✅ **Business rules** - Domain logic that isn't obvious from code
- ✅ **Workarounds** - Why you're working around a bug/limitation
- ✅ **Security concerns** - Why certain checks are necessary
- ✅ **Public APIs** - Function/class documentation for users

**When NOT to Comment:**
- ❌ **Obvious code** - `i++  // increment i`
- ❌ **Bad variable names** - Fix the name instead
- ❌ **Commented-out code** - Delete it (use version control)
- ❌ **Outdated comments** - Update or remove them

**Comment Styles:**
1. **Single-line** - `// Quick explanation`
2. **Multi-line** - Block comments for longer explanations
3. **Documentation** - JSDoc, docstrings, Javadoc (public API)
4. **Special tags** - `TODO`, `FIXME`, `HACK`, `NOTE`

**Documentation Comments (Public APIs):**
```
/**
 * Brief description of function
 * 
 * @param {type} name - Parameter description
 * @returns {type} Return value description
 * @throws {ErrorType} When this error occurs
 * @example
 * functionName(example)
 */
```

**Best Practices:**
- Write comments for your future self (6 months later)
- Update comments when code changes
- Explain "why" not "what"
- Use self-documenting code first, comments second
- Keep comments near the code they describe

**Anti-Patterns:**
- Commented-out code
- Misleading/outdated comments
- Comments that restate code
- Wall of comments (refactor instead)

---

## ❓ Questions This Answers

1. "When should I write code comments?"
2. "What makes a good comment?"
3. "Should I comment obvious code?"
4. "What's the difference between TODO and FIXME?"
5. "How do I write documentation comments?"
6. "What's JSDoc/docstring/Javadoc?"
7. "When should I NOT comment?"
8. "How do I maintain comments?"
9. "What are comment anti-patterns?"
10. "Should I keep commented-out code?"
11. "How do I comment complex algorithms?"
12. "What comment style should I use?"

---

## What Are Code Comments?

Code comments are human-readable explanations embedded in source code.

**Key principle:** Comments should explain WHY, not WHAT. Code explains WHAT.

---

## What Is the Golden Rule for Comments?

The golden rule separates helpful comments from noise. Understanding this principle improves all your commenting decisions.

```
// Good comment: Explains WHY
// Use binary search because list is sorted and contains 10M+ items
index = binary_search(sorted_list, target)

// Bad comment: Restates code (obvious)
// Search the list for target
index = binary_search(sorted_list, target)

// No comment: Code is self-explanatory
index = binary_search(sorted_list, target)
```

**Ask yourself:** Does this comment add information that code doesn't already convey?

---

## When Should I Write Comments?

Effective commenting requires judging when comments add value versus when they create noise. These guidelines help you decide.

### ✅ DO Comment

#### 1. Complex Logic (WHY)

**Good:**
```
// Calculate compound interest using continuous compounding formula
// (more accurate for high-frequency compounding than discrete formula)
final_amount = principal * exp(rate * time)
```

#### 2. Non-Obvious Decisions (WHY)

**Good:**
```
// Sleep before retry to avoid thundering herd on service recovery
sleep(exponential_backoff(attempt))
retry()
```

#### 3. Workarounds and Hacks (WHY + Context)

**Good:**
```
// WORKAROUND: Python 3.8 has bug in asyncio.gather with timeout
// https://bugs.python.org/issue12345
// Remove this when we upgrade to Python 3.9+
results = await custom_gather_with_timeout(tasks, timeout=30)
```

#### 4. Performance Optimizations (WHY)

**Good:**
```
// Cache result for 5 minutes to reduce DB load
// Measured: 1000 req/s without cache vs 10000 req/s with cache
@cache(ttl=300)
def get_user_profile(user_id):
    return database.query(...)
```

#### 5. Edge Cases and Gotchas (WARNING)

**Good:**
```
// WARNING: This function is NOT thread-safe. Use lock if calling from
// multiple threads, or switch to thread_safe_version()
def update_cache(key, value):
    self.cache[key] = value
```

#### 6. Business Logic Context (WHY)

**Good:**
```
// Per IRS regulations, income above $200k is taxed at 35%
if income > 200_000:
    tax_rate = 0.35
```

#### 7. TODOs and FIXMEs (ACTION NEEDED)

**Good:**
```
// TODO(alice): Refactor this to use async/await when we upgrade to Python 3.10
// FIXME: Race condition if two requests modify same user simultaneously
// HACK: Hardcoded for demo, replace with config in production
```

---

### ❌ DON'T Comment

#### 1. Obvious Code (Code Speaks for Itself)

**Bad:**
```
// Increment counter by 1
counter += 1

// Check if user is admin
if user.role == "admin":
```

**Fix:** No comment needed. Code is self-explanatory.

#### 2. Redundant Information

**Bad:**
```
// UserService class
class UserService:
    """UserService class for managing users."""
```

**Fix:** Either remove or add value.
```
class UserService:
    """Handles user lifecycle: creation, authentication, permissions."""
```

#### 3. Commented-Out Code (DELETE IT)

**Bad:**
```
def calculate_total(items):
    total = sum(item.price for item in items)
    # total = total * 0.9  // Old discount logic
    # if user.is_premium:
    #     total = total * 0.95
    return total
```

**Fix:** Delete it. Use version control if you need history.

#### 4. Changelog in Comments (Use Git)

**Bad:**
```
// 2025-01-15: Changed tax rate from 0.3 to 0.35 (Alice)
// 2025-02-20: Added discount calculation (Bob)
// 2025-03-10: Fixed bug with negative prices (Charlie)
```

**Fix:** Delete. This is what `git log` is for.

---

## What Comment Styles Should I Use?

Different comment styles serve different purposes. Choose the right style for your comment's intent.

### 1. Function/Method Documentation

**Format:** Docstring at function start.

```
def calculate_payment_schedule(
    principal: float,
    annual_rate: float,
    months: int
) -> List[Payment]:
    """
    Calculate monthly payment schedule for a loan.
    
    Uses standard amortization formula with monthly compounding.
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate (e.g., 0.05 for 5%)
        months: Number of monthly payments
    
    Returns:
        List of Payment objects with date, principal, and interest
    
    Raises:
        ValueError: If principal <= 0, rate < 0, or months <= 0
    
    Example:
        >>> schedule = calculate_payment_schedule(100000, 0.05, 360)
        >>> len(schedule)
        360
        >>> schedule[0].payment
        536.82
    """
    if principal <= 0 or months <= 0:
        raise ValueError("Principal and months must be positive")
    
    # Implementation...
```

**What to document:**
- **Purpose:** What does it do?
- **Parameters:** What inputs? What format/units?
- **Return value:** What does it return? What format?
- **Exceptions:** What can go wrong?
- **Examples:** How to use it?

---

### 2. Inline Comments

**Format:** Comment above or beside code.

```
// Good: Comment above (multi-line explanation)
// We use SHA-256 instead of MD5 because MD5 is cryptographically broken.
// SHA-256 provides 256-bit security and is still considered secure as of 2025.
hash_value = sha256(data)

// Good: Comment beside (brief clarification)
timeout = 30  // seconds, not milliseconds
```

---

### 3. Section Headers

**Format:** Separate code sections with headers.

```
def complex_workflow():
    # ========================================
    # Step 1: Validate Input
    # ========================================
    if not validate_input(data):
        raise ValidationError()
    
    # ========================================
    # Step 2: Process Data
    # ========================================
    processed = transform(data)
    
    # ========================================
    # Step 3: Save Results
    # ========================================
    database.save(processed)
```

**When to use:** Long functions with multiple logical sections.  
**Better approach:** Refactor into separate functions instead.

---

### 4. File/Module Headers

**Format:** Comment at top of file.

```
"""
User authentication and authorization module.

This module handles:
- User login/logout
- Password hashing and verification
- JWT token generation and validation
- Role-based access control (RBAC)

Security considerations:
- Passwords are hashed with bcrypt (12 rounds)
- Tokens expire after 1 hour
- Rate limiting: 5 failed login attempts per 15 minutes

Author: Engineering Team
License: MIT
"""

import bcrypt
import jwt
```

---

## What Special Comment Tags Exist?

Special tags create searchable markers for specific types of comments. Use them consistently for easier codebase navigation.

### Standard Tags

```
// TODO: Something needs to be done
// FIXME: Known bug that needs fixing
// HACK: Temporary workaround (technical debt)
// NOTE: Important information
// WARNING: Dangerous or surprising behavior
// OPTIMIZE: Performance could be improved
// DEPRECATED: This code will be removed
```

### Enhanced Tags (Include Metadata)

```
// TODO(alice): Refactor to use new API (deadline: 2025-12-01)
// FIXME(bob): Race condition in concurrent access (issue #123)
// HACK(charlie): Hardcoded timeout, replace with config (tech-debt-456)
```

---

## How Do I Write Comments for Different Audiences?

Comments serve different audiences with different needs. Tailor your comments to who will read them.

### For Future You (6 Months Later)

```
// This uses a weak reference to avoid circular dependency between
// User and Session. If we used a strong reference, neither would be
// garbage collected. Took 2 days to debug this memory leak.
self.session = weakref.ref(session)
```

### For Other Developers

```
// API rate limit is 100 req/min. We batch requests and cache results
// for 5 minutes to stay under limit. Don't remove caching without
// increasing rate limit with provider.
@cache(ttl=300)
def fetch_external_data():
    ...
```

### For Domain Experts

```
// Net Present Value (NPV) calculation using discount rate
// Formula: NPV = Σ(Cash_Flow_t / (1 + r)^t)
// Where r = discount rate, t = time period
// Reference: https://en.wikipedia.org/wiki/Net_present_value
npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
```

---

## How Do I Maintain Comments?

Comments that don't match the code are worse than no comments. Treat comments as code that needs maintenance.

### Problem: Stale Comments

**Bad:**
```
// Return user's email address
def get_user_info(user_id):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,     // Comment is stale! Now returns more
        "address": user.address
    }
```

**Fix:** Update comment when code changes.
```
// Return user's contact information (email, phone, address)
def get_user_info(user_id):
    ...
```

**Better:** Write test that enforces the contract.
```
def test_get_user_info_returns_contact_info():
    user_info = get_user_info(123)
    assert "email" in user_info
    assert "phone" in user_info
    assert "address" in user_info
```

---

## When Should I Use Code Examples vs Comments?

Working code examples often communicate better than prose explanations. Choose the right approach for your situation.

### Instead of Complex Comments, Write Clear Code

**Bad:**
```
// Check if user is active and either admin or has premium subscription
if u.s == 1 and (u.r == 0 or u.p == 1):
```

**Good (Self-Documenting Code):**
```
if user.is_active and (user.is_admin or user.has_premium_subscription):
```

**No comment needed!** Code explains itself.

---

## What Are Language-Specific Comment Styles?

Each language has conventions for documentation comments. Follow your language's standards for tool compatibility.

### Python
```
# Single-line comment

"""
Multi-line docstring
(PEP 257 standard)
"""

def function(arg):
    """Docstring here."""
    pass
```

### Java
```
// Single-line comment

/**
 * JavaDoc comment
 * @param arg Description
 * @return Description
 */
public void function(String arg) {
    // Implementation
}
```

### JavaScript
```
// Single-line comment

/**
 * JSDoc comment
 * @param {string} arg - Description
 * @returns {number} Description
 */
function calculate(arg) {
    // Implementation
}
```

### Go
```
// Single-line comment

// Function documentation comment
// (GoDoc standard: start with function name)
// Calculate returns the result of calculation.
func Calculate(arg int) int {
    // Implementation
}
```

---

## What Comment Anti-Patterns Should I Avoid?

These common commenting mistakes create confusion and maintenance burden. Recognize and eliminate them.

### Anti-Pattern 1: Commenting Everything

❌ Every line has a comment.

```
// Create new user instance
user = User()
// Set user name
user.name = "Alice"
// Set user email
user.email = "alice@example.com"
// Save user to database
database.save(user)
```

**Fix:** Only comment non-obvious parts.

### Anti-Pattern 2: Lying Comments

❌ Comment says one thing, code does another.

```
// Calculate average
total = sum(values) // Wrong! This is sum, not average
```

**Fix:** Update comment or code to match.

### Anti-Pattern 3: Commenting Bad Code

❌ Using comments to explain messy code.

```
// x is temporary variable for storing intermediate result
// y is the final result after applying discount
// z is used to check if we need to apply tax
x = calculate(data)
y = x * 0.9
z = check_tax(y)
```

**Fix:** Clean up code instead.
```
price_before_discount = calculate(data)
price_after_discount = price_before_discount * 0.9
needs_tax = check_tax(price_after_discount)
```

---

## What Are Comment Best Practices?

Follow these practices to write comments that help rather than hinder code understanding.

### Do Write Comments For:
1. **Why**, not **what** (code explains what)
2. Complex algorithms and business logic
3. Non-obvious decisions and workarounds
4. Performance optimizations
5. Edge cases and gotchas
6. Function/class documentation (public APIs)

### Don't Write Comments For:
1. Obvious code (self-explanatory)
2. Redundant information
3. Commented-out code (delete it)
4. Changelogs (use git)
5. Variable names (use descriptive names instead)

### Maintain Comments:
1. Update when code changes
2. Delete stale comments
3. Review comments during code review
4. Prefer self-documenting code over comments

---

## What Is the Comment Quality Checklist?

Use this checklist to review comments before committing code.

Before committing, ask:

- [ ] Does this comment explain WHY, not WHAT?
- [ ] Would code be unclear without this comment?
- [ ] Is the comment accurate and up-to-date?
- [ ] Could I improve code clarity instead of adding comment?
- [ ] Does comment add information beyond what code conveys?

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Writing comments** | `pos_search_project(content_type="standards", query="code comments")` |
| **Comment best practices** | `pos_search_project(content_type="standards", query="comment best practices")` |
| **Deciding to comment** | `pos_search_project(content_type="standards", query="when to comment")` |
| **Documentation comments** | `pos_search_project(content_type="standards", query="docstrings JSDoc")` |
| **TODO vs FIXME** | `pos_search_project(content_type="standards", query="TODO FIXME")` |
| **Commented-out code** | `pos_search_project(content_type="standards", query="commented out code")` |
| **Maintaining comments** | `pos_search_project(content_type="standards", query="maintain comments")` |
| **Comment anti-patterns** | `pos_search_project(content_type="standards", query="comment anti-patterns")` |

---

## 🔗 Related Standards

**Query workflow for complete documentation:**

1. **Start with comments** → `pos_search_project(content_type="standards", query="code comments")` (this document)
2. **API docs** → `pos_search_project(content_type="standards", query="API documentation")` → `standards/documentation/api-documentation.md`
3. **README** → `pos_search_project(content_type="standards", query="README templates")` → `standards/documentation/readme-templates.md`

**By Category:**

**Documentation:**
- `standards/documentation/api-documentation.md` - Documenting APIs → `pos_search_project(content_type="standards", query="API documentation")`
- `standards/documentation/readme-templates.md` - Project README structure → `pos_search_project(content_type="standards", query="README templates")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Documentation requirements for production → `pos_search_project(content_type="standards", query="production code checklist")`

**Architecture:**
- `standards/architecture/solid-principles.md` - Single Responsibility (helps code clarity) → `pos_search_project(content_type="standards", query="SOLID principles")`

---

**Good comments are like good jokes—if you have to explain it, it's probably not that good. Write code that explains itself, and use comments to provide context, rationale, and warnings that code alone cannot convey.**
