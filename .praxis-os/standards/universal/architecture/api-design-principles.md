# API Design Principles - Universal Interface Design

**Timeless principles for designing maintainable, usable APIs.**

**Keywords for search**: API design, how to design APIs, API best practices, REST API design, interface design, API principles, API usability, API consistency

---

## 🚨 API Design Quick Reference (TL;DR)

**6 Universal Principles:**
1. **Consistency** - Similar things work the same way
2. **Clarity Over Cleverness** - Obvious beats clever
3. **Fail Fast** - Detect errors early with good messages
4. **Least Surprise** - Behave as users expect
5. **Design for Common Case** - Optimize for 80% use case
6. **Versioning** - Plan for change from the start

**REST API Quick Rules:**
- **Resource-based URLs:** `/users/123` not `/getUser?id=123`
- **HTTP methods:** GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- **Status codes:** 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- **Pagination:** Always paginate collections
- **Error format:** Consistent JSON with `error`, `message`, `field` (if validation)

**Library/SDK Quick Rules:**
- **Fluent interfaces:** Chain methods naturally
- **Sensible defaults:** Make simple things simple
- **Context managers:** Use `with` for resources
- **Type hints:** Always type your interfaces

**Anti-Patterns to Avoid:**
- ❌ Boolean traps: `send_email(user, True, False, True)` → Use named parameters
- ❌ Stringly-typed APIs: `api.get("user", "123")` → Use types
- ❌ Kitchen sink APIs: One function doing 10 things → Split responsibilities

---

## Questions This Answers

- "How do I design a good API?"
- "What are API design best practices?"
- "How do I make my API easy to use?"
- "How should I design REST API endpoints?"
- "How do I handle API versioning?"
- "What HTTP status codes should I use?"
- "How do I make my API consistent?"
- "What are common API anti-patterns?"
- "How do I design GraphQL schemas?"
- "How should I document my API?"
- "How do I test APIs?"
- "How do I handle backward compatibility?"

---

## What is an API?

An API (Application Programming Interface) is a contract between software components. It defines how they communicate.

**Types:**
- **Library API:** Functions/classes developers call
- **REST API:** HTTP endpoints services call
- **GraphQL API:** Query language for APIs
- **RPC API:** Remote procedure calls

**Key principle:** Good APIs are easy to use correctly and hard to use incorrectly.

---

## What are Universal API Design Principles?

These 6 principles apply to all types of APIs (REST, GraphQL, Library, RPC).

### How to Apply Consistency in APIs (Principle 1)

**Concept:** Similar things should work the same way.

**Good (Consistent):**
```
user = api.get_user(user_id)
order = api.get_order(order_id)
product = api.get_product(product_id)

api.create_user(user_data)
api.create_order(order_data)
api.create_product(product_data)
```

**Bad (Inconsistent):**
```
user = api.get_user(user_id)
order = api.fetch_order(order_id)     // Different verb!
product = api.product(product_id)     // No verb!

api.create_user(user_data)
api.add_order(order_data)             // Different verb!
api.product_create(product_data)      // Different order!
```

**Apply consistency to:**
- **Naming:** Same verbs (get/create/update/delete)
- **Parameters:** Same order, same types
- **Return values:** Same structure
- **Error handling:** Same error format

---

### How to Prioritize Clarity Over Cleverness (Principle 2)

**Concept:** API should be obvious, not clever.

**Good (Clear):**
```
def calculate_total_price(items, tax_rate, discount):
    """Calculate total price including tax and discount."""
    subtotal = sum(item.price for item in items)
    after_discount = subtotal * (1 - discount)
    total = after_discount * (1 + tax_rate)
    return total
```

**Bad (Clever):**
```
def calc(i, t, d):  // What do these mean?
    return sum(x.p for x in i) * (1-d) * (1+t)
```

**Clarity guidelines:**
- **Descriptive names:** `get_user` not `gu`
- **Explicit parameters:** `timeout_seconds=30` not `30`
- **Clear return types:** `User` not `Dict`
- **No magic:** Avoid implicit behavior

---

### How to Fail Fast with Good Error Messages (Principle 3)

**Concept:** Detect errors early and provide actionable messages.

**Good (Fail Fast):**
```
def withdraw(account, amount):
    if amount < 0:
        raise ValueError(
            f"Amount must be positive, got {amount}. "
            f"Did you mean to call deposit()?"
        )
    if amount > account.balance:
        raise InsufficientFundsError(
            f"Insufficient funds: balance={account.balance}, "
            f"requested={amount}. "
            f"Missing {amount - account.balance}."
        )
    account.balance -= amount
```

**Bad (Fail Late):**
```
def withdraw(account, amount):
    account.balance -= amount  // Allows negative balance!
```

**Error message guidelines:**
- **What went wrong:** "Insufficient funds"
- **Why it's wrong:** "balance=100, requested=150"
- **How to fix:** "Missing 50"
- **Context:** Include relevant values

---

### How to Apply Principle of Least Surprise (Principle 4)

**Concept:** API should behave as users expect.

**Good (Expected):**
```
// delete_user() deletes user
api.delete_user(user_id)

// update_user() updates user
api.update_user(user_id, new_data)
```

**Bad (Surprising):**
```
// delete_user() archives user (surprise!)
api.delete_user(user_id)  // Actually archives, doesn't delete!

// update_user() creates if not exists (surprise!)
api.update_user(user_id, data)  // Creates user if missing!
```

**Avoid surprises:**
- **Name matches behavior:** `archive_user` not `delete_user` if archiving
- **Side effects:** Document them clearly
- **Implicit actions:** Make them explicit
- **Defaults:** Use safe, expected defaults

---

### How to Design for the Common Case (Principle 5)

**Concept:** Make common operations easy, complex ones possible.

**Good (Easy Common Case):**
```
// Common case: simple (90% of usage)
user = api.get_user(user_id)

// Complex case: still possible (10% of usage)
user = api.get_user(
    user_id,
    include_orders=True,
    include_addresses=True,
    fields=["id", "name", "email"]
)
```

**Bad (Complex Common Case):**
```
// Common case requires lots of parameters!
user = api.get_user(
    user_id,
    include_orders=False,      // Always required
    include_addresses=False,   // Always required
    fields=None,               // Always required
    format="json",             // Always required
    version="v1"               // Always required
)
```

**Design for common case:**
- **Sensible defaults:** Most common values
- **Optional parameters:** Only for advanced cases
- **Overloads:** Simple version + advanced version

---

### How to Handle Versioning and Compatibility (Principle 6)

**Concept:** Evolve APIs without breaking existing users.

### Semantic Versioning

```
Version: MAJOR.MINOR.PATCH

MAJOR: Breaking changes (incompatible)
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)

Example:
v1.0.0 → v1.1.0 (added feature, no breaking change)
v1.1.0 → v2.0.0 (breaking change!)
```

### Backward Compatibility Rules

**Safe changes (don't break compatibility):**
- ✅ Add new endpoint
- ✅ Add optional parameter (with default)
- ✅ Add field to response
- ✅ Make required parameter optional
- ✅ Relax validation (accept more)

**Breaking changes (break compatibility):**
- ❌ Remove endpoint
- ❌ Remove field from response
- ❌ Change field type
- ❌ Add required parameter
- ❌ Rename anything
- ❌ Change behavior

### Deprecation Strategy

```
// Phase 1: Deprecate old, add new (6 months)
@deprecated("Use get_user_v2() instead. Removed in v3.0")
def get_user(user_id):
    return legacy_logic()

def get_user_v2(user_id):
    return new_logic()

// Phase 2: Remove old (after 6+ months)
// Only get_user_v2() exists
```

---

## How to Design REST APIs?

### How to Design Resource-Based URLs

**Good:**
```
GET    /users          // List users
GET    /users/123      // Get user 123
POST   /users          // Create user
PUT    /users/123      // Update user 123
DELETE /users/123      // Delete user 123

GET    /users/123/orders  // List orders for user 123
```

**Bad:**
```
GET    /getUsers                    // Verb in URL
POST   /createUser                  // Verb in URL
GET    /user?action=delete&id=123   // Action in query
```

### How to Use HTTP Methods Correctly

| Method | Purpose | Safe? | Idempotent? |
|--------|---------|-------|-------------|
| GET | Retrieve resource | ✅ Yes | ✅ Yes |
| POST | Create resource | ❌ No | ❌ No |
| PUT | Replace resource | ❌ No | ✅ Yes |
| PATCH | Partial update | ❌ No | ❌ No |
| DELETE | Delete resource | ❌ No | ✅ Yes |

**Safe:** Doesn't modify server state  
**Idempotent:** Same effect if called multiple times

### How to Choose HTTP Status Codes

```
2xx Success:
    200 OK              // Successful GET, PUT, PATCH, DELETE
    201 Created         // Successful POST
    204 No Content      // Successful DELETE (no response body)

4xx Client Error:
    400 Bad Request     // Invalid data
    401 Unauthorized    // Not authenticated
    403 Forbidden       // Authenticated but not authorized
    404 Not Found       // Resource doesn't exist
    409 Conflict        // Resource conflict (duplicate email)
    422 Unprocessable   // Validation failed
    429 Too Many Requests  // Rate limit exceeded

5xx Server Error:
    500 Internal Server Error  // Unexpected server error
    503 Service Unavailable    // Temporary outage
```

### How to Implement Pagination

**Good:**
```
GET /users?page=2&limit=50

Response:
{
    "data": [...],
    "pagination": {
        "page": 2,
        "limit": 50,
        "total": 1000,
        "total_pages": 20,
        "next": "/users?page=3&limit=50",
        "prev": "/users?page=1&limit=50"
    }
}
```

### How to Implement Filtering and Sorting

**Good:**
```
GET /users?status=active&role=admin&sort=created_at:desc

Response:
{
    "data": [...],
    "filters": {
        "status": "active",
        "role": "admin"
    },
    "sort": "created_at:desc"
}
```

### How to Format Error Responses

**Good:**
```
{
    "error": {
        "code": "INSUFFICIENT_FUNDS",
        "message": "Insufficient funds for withdrawal",
        "details": {
            "balance": 100.00,
            "requested": 150.00,
            "shortfall": 50.00
        },
        "request_id": "req_abc123",
        "timestamp": "2025-10-05T12:34:56Z"
    }
}
```

---

## How to Design Library/SDK APIs?

### How to Create Fluent Interfaces

**Good (Fluent):**
```
query = QueryBuilder()
    .select("name", "email")
    .from_table("users")
    .where("status", "=", "active")
    .order_by("created_at", "desc")
    .limit(10)
    .execute()
```

**Bad (Non-Fluent):**
```
query = QueryBuilder()
query.select(["name", "email"])
query.from_table("users")
query.where("status", "=", "active")
result = query.execute()
```

### How to Provide Sensible Defaults

**Good:**
```
// Common case: simple
client = APIClient(api_key)

// Advanced case: configurable
client = APIClient(
    api_key,
    timeout=30,
    retry_count=3,
    base_url="https://api.custom.com"
)
```

### How to Use Context Managers for Resource Management

**Good:**
```
with DatabaseConnection(config) as conn:
    result = conn.query("SELECT * FROM users")
    // Connection automatically closed
```

**Bad:**
```
conn = DatabaseConnection(config)
result = conn.query("SELECT * FROM users")
conn.close()  // Easy to forget!
```

---

## How to Design GraphQL APIs?

### How to Design GraphQL Schemas

**Good:**
```
type Query {
    user(id: ID!): User
    users(filter: UserFilter, limit: Int = 20): [User!]!
}

type User {
    id: ID!
    name: String!
    email: String!
    orders: [Order!]!
}

type Order {
    id: ID!
    total: Float!
    items: [OrderItem!]!
}
```

### How to Avoid N+1 Queries in GraphQL

**Bad:**
```
// Client requests users and their orders
// Results in N+1 queries (1 for users, N for orders)
```

**Good (Use DataLoader):**
```
// Batch load orders for all users in single query
// 1 query for users, 1 query for all orders
```

---

## How to Document APIs?

### What to Document in APIs

1. **Purpose:** What does this do?
2. **Parameters:** What inputs does it accept?
3. **Return value:** What does it return?
4. **Errors:** What can go wrong?
5. **Examples:** How do I use it?
6. **Edge cases:** Special behavior

### Example: Good Documentation

```
/**
 * Transfer funds between two accounts.
 *
 * @param from_account - Account to withdraw from
 * @param to_account - Account to deposit to
 * @param amount - Amount to transfer (must be positive)
 * @return TransferResult with transaction ID
 *
 * @throws InsufficientFundsError if from_account lacks funds
 * @throws InvalidAmountError if amount <= 0
 * @throws AccountLockedError if either account is locked
 *
 * @example
 *   result = transfer(account_a, account_b, 100.00)
 *   print(result.transaction_id)  # "txn_abc123"
 *
 * @note This operation is atomic. Either both succeed or both fail.
 * @note Accounts must be in same currency.
 */
function transfer(from_account, to_account, amount)
```

---

## How to Test APIs?

### How to Unit Test Library APIs

```
def test_withdraw_insufficient_funds():
    account = BankAccount(balance=100)
    
    with assert_raises(InsufficientFundsError) as error:
        account.withdraw(150)
    
    assert "balance=100" in str(error)
    assert "requested=150" in str(error)
```

### How to Integration Test REST APIs

```
def test_create_user_endpoint():
    response = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com"
    })
    
    assert response.status_code == 201
    assert response.json["id"] is not None
    assert response.json["name"] == "Alice"
```

### How to Use Contract Tests for APIs

```
def test_api_response_schema():
    response = client.get("/users/123")
    
    // Validate response matches schema
    validate_schema(response.json, UserSchema)
```

---

## What API Anti-Patterns Should I Avoid?

### Anti-Pattern 1: Boolean Trap (Unclear Parameters)

❌ Unclear boolean parameters.

```
// BAD
user = get_user(user_id, True, False, True)
// What do these booleans mean?!
```

**Fix:** Use named parameters or enums.
```
// GOOD
user = get_user(
    user_id,
    include_orders=True,
    include_addresses=False,
    include_metadata=True
)
```

### Anti-Pattern 2: Stringly-Typed API (Everything is a String)

❌ Using strings where enums/types should be used.

```
// BAD
result = api.sort_users("name", "asc")
result = api.sort_users("naem", "ascending")  // Typo! Runtime error
```

**Fix:** Use enums.
```
// GOOD
result = api.sort_users(SortField.NAME, SortOrder.ASCENDING)
result = api.sort_users(SortField.NAEM, ...)  // Compile-time error!
```

### Anti-Pattern 3: Kitchen Sink API (Doing Too Much)

❌ One function that does everything.

```
// BAD
api.manage_user(
    action="update",  // or "create", "delete", "archive"...
    user_id=123,
    data={...},
    options={...}
)
```

**Fix:** Separate functions for each action.
```
// GOOD
api.create_user(data)
api.update_user(user_id, data)
api.delete_user(user_id)
```

---

## When to Query This Standard

This standard is most valuable when:

1. **Starting New API Design**
   - Situation: Beginning design of REST API, GraphQL API, or library API
   - Query: `pos_search_project(content_type="standards", query="how to design APIs")`

2. **During API Review**
   - Situation: Reviewing proposed API changes
   - Query: `pos_search_project(content_type="standards", query="API design best practices")`

3. **Debugging API Usability Issues**
   - Situation: Users find your API confusing or error-prone
   - Query: `pos_search_project(content_type="standards", query="API usability principles")`

4. **Choosing HTTP Status Codes**
   - Situation: Not sure which HTTP status code to return
   - Query: `pos_search_project(content_type="standards", query="HTTP status codes")`

5. **Implementing Versioning**
   - Situation: Need to evolve API without breaking clients
   - Query: `pos_search_project(content_type="standards", query="API versioning compatibility")`

6. **Handling Errors in APIs**
   - Situation: Designing error response format
   - Query: `pos_search_project(content_type="standards", query="API error handling")`

7. **Pagination/Filtering Design**
   - Situation: Need to implement pagination for collections
   - Query: `pos_search_project(content_type="standards", query="REST API pagination")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Starting API design | `pos_search_project(content_type="standards", query="how to design APIs")` |
| REST endpoint design | `pos_search_project(content_type="standards", query="REST API design")` |
| HTTP status codes | `pos_search_project(content_type="standards", query="HTTP status codes")` |
| API error messages | `pos_search_project(content_type="standards", query="API error handling")` |
| API versioning | `pos_search_project(content_type="standards", query="API versioning compatibility")` |
| Library API design | `pos_search_project(content_type="standards", query="library SDK API design")` |

---

## Cross-References and Related Standards

**Architecture & Design:**
- `standards/architecture/solid-principles.md` - Class design principles for API implementations
  → `pos_search_project(content_type="standards", query="how to design maintainable classes")`

**Testing:**
- `standards/testing/integration-testing.md` - How to test APIs effectively
  → `pos_search_project(content_type="standards", query="integration testing")`
- `standards/testing/test-pyramid.md` - Testing strategy for API layers
  → `pos_search_project(content_type="standards", query="test pyramid API testing")`

**Quality:**
- `standards/ai-safety/production-code-checklist.md` - Production code requirements
  → `pos_search_project(content_type="standards", query="production code quality checklist")`

**Documentation:**
- `standards/documentation/rag-content-authoring.md` - How to document for discoverability
  → `pos_search_project(content_type="standards", query="documentation standards")`

**Query workflow:**
1. **Before**: `pos_search_project(content_type="standards", query="API design principles")` → Learn universal principles
2. **During**: `pos_search_project(content_type="standards", query="REST API design")` → Apply to specific API type
3. **Testing**: `pos_search_project(content_type="standards", query="how to test APIs")` → Validate with tests
4. **After**: `pos_search_project(content_type="standards", query="production code checklist")` → Final quality check

---

## Best Practices Summary

1. **Be consistent:** Same patterns throughout
2. **Be clear:** Obvious > clever
3. **Fail fast:** Validate early, good errors
4. **Be unsurprising:** Match user expectations
5. **Design for common case:** Make simple things simple
6. **Version carefully:** Don't break compatibility
7. **Document well:** Purpose, params, errors, examples
8. **Test thoroughly:** Unit, integration, contract

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-architecture.md` (Python: type hints, docstrings, `__enter__/__exit__`)
- See `.praxis-os/standards/development/java-architecture.md` (Java: interfaces, builders, try-with-resources)
- See `.praxis-os/standards/development/js-architecture.md` (JavaScript: Promises, async/await, JSDoc)
- Etc.

---

**Good APIs are a joy to use. They're consistent, clear, fail fast with good errors, and make common cases easy. Invest time in API design—it's hard to change later.**
