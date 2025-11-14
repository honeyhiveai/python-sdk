# API Documentation - Universal Documentation Practice

**Timeless principles for documenting APIs effectively.**

---

## 🎯 TL;DR - API Documentation Quick Reference

**Keywords for search**: API documentation, REST API documentation, API reference, getting started guide, API examples, OpenAPI, Swagger, API versioning, authentication documentation, error codes, rate limiting documentation

**Core Principle:** Great documentation answers "How do I...?" before developers ask.

**Three Types of API Documentation:**
1. **Reference** - Complete specification (every endpoint/function)
2. **Getting Started** - Quick integration guide (0 to working in 10 minutes)
3. **Tutorials** - Step-by-step guides for common use cases

**For Every Endpoint/Function:**
- **Purpose** - What does it do?
- **Parameters** - What inputs? (type, required/optional, validation rules)
- **Response** - What outputs? (success cases, error cases with codes)
- **Example** - Working code snippet (copy-paste ready)
- **Rate Limits** - How many requests allowed?
- **Authentication** - What credentials needed?

**Documentation Formats:**
- **OpenAPI/Swagger** - REST API standard (generates interactive docs)
- **Markdown** - Simple, version-controllable
- **Code comments** - JSDoc, docstrings (auto-generate docs)
- **Interactive** - Try API in browser (Swagger UI, Postman)

**Best Practices:**
- **Show examples first** - Code before prose
- **Keep it current** - Update docs with code
- **Test code samples** - Every example must work
- **Document errors** - Every error code explained
- **Version docs** - Match docs to API version
- **Make it searchable** - Good structure, clear headers

**Anti-Patterns:**
- No examples
- Outdated documentation
- Missing error codes
- No authentication guide
- Breaking changes without notice

---

## ❓ Questions This Answers

1. "How do I document an API?"
2. "What should API documentation include?"
3. "What's the difference between reference docs and tutorials?"
4. "How do I write a getting started guide?"
5. "What format should I use for API documentation?"
6. "How do I document authentication?"
7. "How do I document error codes?"
8. "How do I version API documentation?"
9. "What are API documentation best practices?"
10. "How do I make documentation interactive?"
11. "What's OpenAPI/Swagger?"
12. "How do I test API documentation?"

---

## What is API Documentation?

API documentation explains how to use an interface (library, REST API, GraphQL, SDK, etc.) so developers can integrate with it successfully.

**Key principle:** Great documentation answers "How do I...?" before developers ask.

---

## What Types of API Documentation Exist?

Different documentation types serve different purposes. Effective API documentation includes all three types.

### Type 1: Reference Documentation

**What:** Complete, detailed specification of every endpoint/function.

**Purpose:** Look up exact syntax, parameters, return values.

**Example:**
```
GET /api/users/{id}

Retrieves a single user by ID.

Parameters:
  id (integer, required): User ID

Response:
  200 OK
    {
      "id": 123,
      "email": "alice@example.com",
      "name": "Alice Smith",
      "created_at": "2025-01-15T10:30:00Z"
    }
  
  404 Not Found
    {
      "error": "User not found"
    }

Rate Limit: 100 requests/minute
```

---

### Type 2: Getting Started Guide

**What:** Quick path from zero to first successful API call.

**Purpose:** Get developers productive in 5 minutes.

**Example:**
```markdown
# Quick Start

## 1. Get API Key
Sign up at https://example.com/signup and copy your API key.

## 2. Install SDK
```bash
pip install example-sdk
```

## 3. Make Your First Request
```python
from example_sdk import Client

client = Client(api_key="your_api_key")
user = client.users.get(123)
print(user.email)  # alice@example.com
```

That's it! See [Full Documentation](link) for more.
```

---

### Type 3: Tutorials

**What:** Step-by-step guides for common tasks.

**Purpose:** Teach how to accomplish specific goals.

**Example:**
```markdown
# Tutorial: Implementing OAuth Authentication

Learn how to add OAuth login to your app.

## Prerequisites
- API key (sign up at...)
- Python 3.8+
- Understanding of HTTP

## Step 1: Register Your App
Navigate to https://example.com/apps and...

## Step 2: Implement Authorization Flow
Create an endpoint to handle OAuth redirects:

```python
@app.route("/auth/callback")
def oauth_callback():
    code = request.args.get("code")
    token = client.exchange_code(code)
    return redirect("/dashboard")
```

## Step 3: ...
```

---

### Type 4: Conceptual Guides (How It Works)

**What:** Explanation of architecture, design decisions, concepts.

**Purpose:** Help developers understand the "why" and "how."

**Example:**
```markdown
# How Authentication Works

Our API uses JWT tokens for authentication.

## Token Lifecycle

1. User logs in with credentials
2. Server generates JWT with user claims
3. JWT signed with secret key
4. Client stores JWT (secure cookie/localStorage)
5. Client includes JWT in Authorization header
6. Server validates signature and expiration

## Token Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  // Header
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6...  // Payload
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV...    // Signature
```

Tokens expire after 1 hour. Refresh tokens last 30 days.
```

---

## What Should I Document for Every Endpoint?

Complete, accurate documentation for every API endpoint prevents integration issues and support requests.

### For Every Endpoint/Function

#### 1. Purpose (What it does)

```
GET /api/users/{id}

**Purpose:** Retrieves detailed information about a single user.
```

---

#### 2. Authentication/Authorization

```
**Authentication:** Bearer token required
**Authorization:** Must be admin or the user being accessed
```

---

#### 3. Parameters (Inputs)

```
**Path Parameters:**
- id (integer, required): Unique user identifier

**Query Parameters:**
- include (string[], optional): Additional fields to include
  - Allowed values: "orders", "addresses", "preferences"
  - Example: ?include=orders,addresses

**Headers:**
- Authorization (string, required): Bearer {token}
- Content-Type (string, required): application/json
```

**Template:**
```
parameter_name (type, required/optional): Description
  - Constraints: min, max, pattern, allowed values
  - Default: default value
  - Example: example value
```

---

#### 4. Request Body (For POST/PUT/PATCH)

```
POST /api/users

**Request Body:**
```json
{
  "email": "alice@example.com",      // Required: User email (unique)
  "name": "Alice Smith",             // Required: Full name
  "age": 30,                         // Optional: Age (18-120)
  "preferences": {
    "newsletter": true,              // Optional: Email preferences
    "notifications": false
  }
}
```

**Validation:**
- email: Must be valid email format, unique
- name: 1-100 characters
- age: Integer between 18-120
```

---

#### 5. Response (Outputs)

```
**Success Response (200 OK):**
```json
{
  "id": 123,
  "email": "alice@example.com",
  "name": "Alice Smith",
  "age": 30,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Field Descriptions:**
- id: Unique user identifier (immutable)
- email: User email address
- name: User full name
- age: User age (null if not provided)
- created_at: ISO 8601 timestamp of user creation
- updated_at: ISO 8601 timestamp of last update
```

---

#### 6. Error Responses

```
**Error Responses:**

400 Bad Request:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": {
    "email": ["Must be valid email format"],
    "age": ["Must be between 18 and 120"]
  }
}
```

404 Not Found:
```json
{
  "error": "USER_NOT_FOUND",
  "message": "User with ID 123 not found"
}
```

429 Too Many Requests:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```
```

---

#### 7. Examples (Multiple Use Cases)

```
**Example 1: Basic Usage**

Request:
```bash
curl -X GET https://api.example.com/users/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": 123,
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

**Example 2: With Additional Fields**

Request:
```bash
curl -X GET "https://api.example.com/users/123?include=orders" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": 123,
  "email": "alice@example.com",
  "name": "Alice Smith",
  "orders": [
    {"id": 456, "total": 99.99},
    {"id": 789, "total": 149.99}
  ]
}
```
```

---

#### 8. Rate Limits

```
**Rate Limits:**
- 100 requests per minute per API key
- 10,000 requests per day per API key

**Headers:**
- X-RateLimit-Limit: 100
- X-RateLimit-Remaining: 95
- X-RateLimit-Reset: 1672531200 (Unix timestamp)

**When limit exceeded:**
- 429 Too Many Requests response
- Retry-After header with seconds to wait
```

---

#### 9. Pagination (For List Endpoints)

```
GET /api/users

**Pagination:**
- Default page size: 20
- Max page size: 100
- Page parameter: ?page=2
- Page size parameter: ?page_size=50

**Response Structure:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "page_size": 20,
    "total_items": 500,
    "total_pages": 25,
    "next": "https://api.example.com/users?page=3",
    "prev": "https://api.example.com/users?page=1"
  }
}
```
```

---

#### 10. Webhooks (If Applicable)

```
**Webhook: user.created**

Triggered when a new user is created.

**Payload:**
```json
{
  "event": "user.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "id": 123,
    "email": "alice@example.com",
    "name": "Alice Smith"
  }
}
```

**Headers:**
- X-Webhook-Signature: HMAC-SHA256 signature for verification

**Retry Policy:**
- 3 retries with exponential backoff (1s, 5s, 30s)
- Fails after 3 attempts
```

---

## What Documentation Formats Should I Use?

Different formats suit different needs. Choose based on your API type and audience.

### Format 1: OpenAPI/Swagger (REST APIs)

**Standard:** OpenAPI 3.0

```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
  description: User management API

paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        email:
          type: string
        name:
          type: string
```

**Tools:** Swagger UI, ReDoc, Stoplight

---

### Format 2: GraphQL Schema

```graphql
"""
User type representing a registered user
"""
type User {
  """Unique user identifier"""
  id: ID!
  
  """User email address (unique)"""
  email: String!
  
  """User full name"""
  name: String!
  
  """User's orders"""
  orders(
    """Filter by status"""
    status: OrderStatus
    
    """Limit number of results"""
    limit: Int = 20
  ): [Order!]!
}

"""
Query type for fetching data
"""
type Query {
  """
  Get user by ID
  
  Example:
    query {
      user(id: "123") {
        email
        name
      }
    }
  """
  user(id: ID!): User
}
```

**Tools:** GraphQL Playground, Apollo Studio

---

### Format 3: Language-Specific Docstrings

**Python (Sphinx/Google style):**
```python
def get_user(user_id: int, include_orders: bool = False) -> User:
    """
    Retrieve a user by ID.
    
    Args:
        user_id: Unique user identifier
        include_orders: Whether to include user's orders
    
    Returns:
        User object with requested data
    
    Raises:
        UserNotFoundError: If user doesn't exist
        AuthenticationError: If not authenticated
    
    Example:
        >>> user = get_user(123)
        >>> print(user.email)
        'alice@example.com'
        
        >>> user_with_orders = get_user(123, include_orders=True)
        >>> print(len(user_with_orders.orders))
        5
    """
    pass
```

**JavaScript (JSDoc):**
```javascript
/**
 * Retrieve a user by ID.
 * 
 * @param {number} userId - Unique user identifier
 * @param {boolean} [includeOrders=false] - Whether to include orders
 * @returns {Promise<User>} User object with requested data
 * @throws {UserNotFoundError} If user doesn't exist
 * 
 * @example
 * const user = await getUser(123);
 * console.log(user.email); // 'alice@example.com'
 * 
 * @example
 * const userWithOrders = await getUser(123, true);
 * console.log(userWithOrders.orders.length); // 5
 */
async function getUser(userId, includeOrders = false) {
  // Implementation
}
```

---

## How to Create Interactive Documentation

Interactive documentation lets developers explore and test your API directly in the browser, dramatically improving the developer experience.

### 1. Try It Out (API Explorer)

```
GET /api/users/{id}

[Try it out]

Path Parameters:
  id: [123]

Headers:
  Authorization: Bearer [your_token]

[Execute]

Response:
Status: 200 OK
Body:
{
  "id": 123,
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

**Tools:** Swagger UI, Postman Collections, Insomnia

---

### 2. Code Examples in Multiple Languages

```
# Get User

<tabs>
  <tab title="Python">
    ```python
    from example_sdk import Client
    
    client = Client(api_key="YOUR_API_KEY")
    user = client.users.get(123)
    print(user.email)
    ```
  </tab>
  
  <tab title="JavaScript">
    ```javascript
    const client = new ExampleClient('YOUR_API_KEY');
    const user = await client.users.get(123);
    console.log(user.email);
    ```
  </tab>
  
  <tab title="cURL">
    ```bash
    curl -X GET https://api.example.com/users/123 \
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
  </tab>
</tabs>
```

---

### 3. Sandbox Environment

```
**Try our API in sandbox mode (no authentication required):**

Base URL: https://sandbox.example.com/api
Test User ID: 123
Test Token: sandbox_test_token_xyz

Example:
```bash
curl https://sandbox.example.com/api/users/123 \
  -H "Authorization: Bearer sandbox_test_token_xyz"
```
```

---

## What API Documentation Anti-Patterns Should I Avoid?

These common documentation mistakes frustrate developers and increase support burden.

### Anti-Pattern 1: Stale Documentation

❌ Documentation doesn't match actual API behavior.

```
// Documentation says:
GET /api/users returns {id, email}

// API actually returns:
{id, email, name, created_at, updated_at}

// Users confused by extra fields!
```

**Fix:** Auto-generate docs from code, validate in CI/CD.

---

### Anti-Pattern 2: No Examples

❌ Only showing abstract schemas without concrete examples.

```
// BAD
User object has properties: id, email, name

// GOOD
User object:
{
  "id": 123,
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

---

### Anti-Pattern 3: Missing Error Documentation

❌ Only documenting success cases.

```
// BAD
Returns 200 OK with user object

// GOOD
Returns:
- 200 OK: User found
- 404 Not Found: User doesn't exist
- 401 Unauthorized: Invalid or missing token
- 429 Too Many Requests: Rate limit exceeded
```

---

### Anti-Pattern 4: Assuming Knowledge

❌ Using jargon without explanation.

```
// BAD
"Returns idempotency key for request deduplication"

// GOOD
"Returns idempotency key - a unique identifier that prevents 
duplicate requests. If you retry a request with the same key,
the API returns the original response instead of processing twice."
```

---

## What Are API Documentation Best Practices?

Follow these practices to create documentation developers love and that reduces support requests.

### 1. Start with Quick Start

Get users to first success in 5 minutes.

```
Quick Start → Tutorials → Full Reference → Advanced Guides
```

---

### 2. Show Don't Tell

```
// BAD (Tell)
The filter parameter accepts an array of strings

// GOOD (Show)
?filter=active,verified
// Returns users who are both active AND verified
```

---

### 3. Document Edge Cases

```
**Edge Cases:**

- What happens if user doesn't exist? → 404 Not Found
- What if user is deleted? → 410 Gone
- What if ID is invalid (not integer)? → 400 Bad Request
- What if ID is negative? → 400 Bad Request
- What if ID is extremely large (overflow)? → 400 Bad Request
```

---

### 4. Provide SDKs and Examples

```
Official SDKs:
- Python: pip install example-sdk
- JavaScript: npm install example-sdk
- Ruby: gem install example-sdk
- Go: go get github.com/example/sdk

Community SDKs:
- PHP: composer require community/example-sdk
- Java: Available at Maven Central
```

---

### 5. Versioning Documentation

```
API Versions:
- v1 (deprecated, EOL 2025-12-31)
- v2 (current, stable)
- v3 (beta, breaking changes)

[View v1 docs] [View v2 docs] [View v3 docs]
```

---

### 6. Changelog

```
# Changelog

## v2.1.0 (2025-01-15)

### Added
- New endpoint: GET /api/users/{id}/orders
- Filter parameter for GET /api/users

### Changed
- Increased rate limit from 60 to 100 req/min

### Deprecated
- POST /api/user (use /api/users instead)

### Fixed
- 500 error when email contains special characters
```

---

### 7. Search

```
Documentation should be searchable:
- Full-text search across all docs
- Search by endpoint, parameter, error code
- Autocomplete suggestions
```

---

## How to Test API Documentation

Testing documentation ensures examples work and information is accurate, preventing developer frustration.

### 1. Ensure Examples Work

```
// Run examples in CI/CD
def test_documentation_examples():
    // Parse code examples from docs
    examples = extract_examples("docs/api.md")
    
    for example in examples:
        result = execute_example(example)
        assert result.success, f"Example failed: {example}"
```

---

### 2. Validate Against OpenAPI Schema

```
// Ensure docs match actual API
def test_docs_match_api():
    schema = load_openapi_schema()
    actual_endpoints = discover_api_endpoints()
    
    for endpoint in actual_endpoints:
        assert endpoint in schema.paths, \
            f"Endpoint {endpoint} not documented"
```

---

### 3. Check for Broken Links

```
// Find dead links in documentation
def test_documentation_links():
    docs = load_documentation()
    links = extract_links(docs)
    
    for link in links:
        response = requests.head(link)
        assert response.status_code != 404, \
            f"Broken link: {link}"
```

---

## What Documentation Tools Should I Use?

These tools automate documentation generation, validation, and hosting.

### REST APIs
- **Swagger/OpenAPI:** Industry standard
- **ReDoc:** Beautiful OpenAPI renderer
- **Postman:** API explorer with collections
- **Stoplight:** API design and documentation

### GraphQL
- **GraphQL Playground:** Interactive explorer
- **Apollo Studio:** Schema management
- **GraphiQL:** In-browser IDE

### Static Site Generators
- **Docusaurus:** React-based (Meta)
- **MkDocs:** Python-based, simple
- **VitePress:** Vue-based, fast
- **GitBook:** Polished, commercial

### API Documentation Platforms
- **ReadMe:** Hosted docs with metrics
- **Redocly:** OpenAPI-first platform
- **Stripe-like docs:** Reference implementation

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Building an API** | `pos_search_project(content_type="standards", query="API documentation")` |
| **Writing API reference** | `pos_search_project(content_type="standards", query="API reference documentation")` |
| **Getting started guide** | `pos_search_project(content_type="standards", query="getting started guide")` |
| **Documenting authentication** | `pos_search_project(content_type="standards", query="authentication documentation")` |
| **Error code documentation** | `pos_search_project(content_type="standards", query="error codes documentation")` |
| **API examples** | `pos_search_project(content_type="standards", query="API examples")` |
| **Interactive documentation** | `pos_search_project(content_type="standards", query="interactive API docs")` |
| **API versioning** | `pos_search_project(content_type="standards", query="API versioning")` |
| **OpenAPI/Swagger** | `pos_search_project(content_type="standards", query="OpenAPI Swagger")` |

---

## 🔗 Related Standards

**Query workflow for complete API documentation:**

1. **Start here** → `pos_search_project(content_type="standards", query="API documentation")` (this document)
2. **Code comments** → `pos_search_project(content_type="standards", query="code comments")` → `standards/documentation/code-comments.md`
3. **README** → `pos_search_project(content_type="standards", query="README templates")` → `standards/documentation/readme-templates.md`
4. **Security** → `pos_search_project(content_type="standards", query="security patterns")` → `standards/security/security-patterns.md`

**By Category:**

**Documentation:**
- `standards/documentation/code-comments.md` - Inline code documentation → `pos_search_project(content_type="standards", query="code comments")`
- `standards/documentation/readme-templates.md` - Project README structure → `pos_search_project(content_type="standards", query="README templates")`

**Architecture:**
- `standards/architecture/api-design-principles.md` - API design best practices → `pos_search_project(content_type="standards", query="API design")`

**Security:**
- `standards/security/security-patterns.md` - Securing APIs → `pos_search_project(content_type="standards", query="security patterns")`

**Testing:**
- `standards/testing/integration-testing.md` - Testing API endpoints → `pos_search_project(content_type="standards", query="integration testing")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Documentation requirements for production → `pos_search_project(content_type="standards", query="production code checklist")`

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-documentation.md` (Python: Sphinx, docstrings)
- See `.praxis-os/standards/development/js-documentation.md` (JavaScript: JSDoc, TypeDoc)
- See `.praxis-os/standards/development/java-documentation.md` (Java: Javadoc)
- Etc.

---

**Great API documentation is the difference between adoption and abandonment. Make it easy to get started, provide clear examples, document errors, and keep it up-to-date. Test your docs like you test your code.**
