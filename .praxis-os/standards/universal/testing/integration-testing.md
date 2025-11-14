# Integration Testing - Universal Testing Strategy

**Timeless approach to testing component interactions and system behavior.**

---

## 🚨 Integration Testing Quick Reference (TL;DR)

**Keywords for search**: integration testing, component integration, database testing, API testing, integration test patterns, test database strategies, external service testing, integration vs unit tests, test fixtures, test data management

**The 4 types of integration testing:**

| Type | What It Tests | Example |
|------|---------------|---------|
| **Component Integration** | Internal modules working together | Service → Repository → Database |
| **API Integration** | API endpoints with real components | HTTP requests through full stack |
| **Database Integration** | Actual database operations | Real queries, transactions, migrations |
| **External Service Integration** | Third-party service calls | Payment gateways, email services, APIs |

**Key principle:** Unit tests verify components in isolation. Integration tests verify they work together.

**Test database strategies:**
1. **In-memory** - Fast (SQLite :memory:), limited features
2. **Test instance** - Real database, slower, requires cleanup
3. **Transactions** - Rollback after each test, fast cleanup
4. **Docker containers** - Fresh database each run, exact match to production

**When to query this standard:**
- Planning integration tests → `pos_search_project(content_type="standards", query="integration testing patterns")`
- Database testing strategy → `pos_search_project(content_type="standards", query="test database strategies")`
- Testing external APIs → `pos_search_project(content_type="standards", query="external service testing")`
- Test data management → `pos_search_project(content_type="standards", query="test fixtures factories")`
- Slow integration tests → `pos_search_project(content_type="standards", query="fast integration tests")`

**For complete guide with examples, continue reading below.**

---

## Questions This Answers

- "What is integration testing and when should I use it?"
- "What's the difference between unit tests and integration tests?"
- "How do I test database interactions?"
- "Should I use an in-memory database or real database for tests?"
- "How do I test external API integrations?"
- "How do I manage test data for integration tests?"
- "Why are my integration tests so slow?"
- "What integration testing patterns should I use?"

---

## What is Integration Testing?

Integration testing verifies that different components/modules work together correctly when integrated.

**Key principle:** Unit tests verify components in isolation. Integration tests verify they work together.

---

## Test Pyramid Context

```
          ╱╲
         ╱  ╲
        ╱ E2E ╲         (Few, slow, expensive)
       ╱────────╲
      ╱          ╲
     ╱ Integration╲     (Medium, moderate speed)
    ╱──────────────╲
   ╱                ╲
  ╱   Unit Tests     ╲  (Many, fast, cheap)
 ╱────────────────────╲
```

**Integration tests sit in the middle:** More realistic than unit tests, faster than E2E tests.

---

## What Types of Integration Testing Exist?

There are 4 main types, each testing different integration boundaries.

### How to Test Component Integration (Type 1)

**What:** Test integration between internal components.

```
// Unit test (isolated)
def test_user_service_alone():
    mock_repo = MockRepository()
    service = UserService(mock_repo)
    user = service.create_user("alice@example.com")
    assert user.email == "alice@example.com"

// Integration test (real dependencies)
def test_user_service_with_repository():
    real_repo = UserRepository(test_database)
    service = UserService(real_repo)
    
    user = service.create_user("alice@example.com")
    
    // Verify integration: service → repository → database
    stored_user = real_repo.find(user.id)
    assert stored_user.email == "alice@example.com"
```

---

### How to Test API Integration (Type 2)

**What:** Test API endpoints with real components.

```
def test_create_user_endpoint():
    // Start test server with real components
    client = TestClient(app)
    
    response = client.post("/users", json={
        "email": "alice@example.com",
        "name": "Alice"
    })
    
    assert response.status_code == 201
    assert response.json["email"] == "alice@example.com"
    
    // Verify data persisted
    user_id = response.json["id"]
    get_response = client.get(f"/users/{user_id}")
    assert get_response.json["email"] == "alice@example.com"
```

---

### How to Test External Service Integration (Type 3)

**What:** Test integration with external services.

```
def test_payment_gateway_integration():
    // Use test/sandbox environment of real payment gateway
    gateway = PaymentGateway(
        api_key=TEST_API_KEY,
        environment="sandbox"
    )
    
    result = gateway.charge(
        card_number=TEST_CARD_NUMBER,
        amount=10.00
    )
    
    assert result.success == True
    assert result.transaction_id is not None
```

---

### How to Test Database Integration (Type 4)

**What:** Test actual database operations.

```
def test_user_repository_database_integration():
    // Use real test database
    repo = UserRepository(test_database)
    
    // Create user
    user = User(email="alice@example.com", name="Alice")
    repo.save(user)
    
    // Query database directly to verify
    result = test_database.query(
        "SELECT * FROM users WHERE email = ?",
        "alice@example.com"
    )
    assert len(result) == 1
    assert result[0]["name"] == "Alice"
```

---

## What Integration Test Patterns Should I Use?

Choose the pattern that matches your testing strategy and system architecture.

### How to Use Top-Down Integration Pattern

**Concept:** Test from high-level modules down to low-level.

```
Step 1: Test API → Mock Service
def test_api_layer():
    mock_service = MockUserService()
    api = UserAPI(mock_service)
    response = api.create_user(...)

Step 2: Test API → Real Service → Mock Repository
def test_api_with_service():
    mock_repo = MockRepository()
    service = UserService(mock_repo)
    api = UserAPI(service)
    response = api.create_user(...)

Step 3: Test entire stack
def test_full_integration():
    real_repo = UserRepository(test_database)
    service = UserService(real_repo)
    api = UserAPI(service)
    response = api.create_user(...)
```

---

### How to Use Bottom-Up Integration Pattern

**Concept:** Test from low-level modules up to high-level.

```
Step 1: Test Database → Repository
def test_repository():
    repo = UserRepository(test_database)
    user = repo.save(User(...))
    assert user.id is not None

Step 2: Test Repository → Service
def test_service():
    repo = UserRepository(test_database)
    service = UserService(repo)
    user = service.create_user(...)

Step 3: Test entire stack
def test_api():
    repo = UserRepository(test_database)
    service = UserService(repo)
    api = UserAPI(service)
    response = api.create_user(...)
```

---

### How to Use Big Bang Integration Pattern

**Concept:** Integrate all components at once and test.

```
def test_full_system():
    // All real components
    database = TestDatabase()
    cache = TestCache()
    email_service = TestEmailService()
    
    repo = UserRepository(database)
    service = UserService(repo, cache, email_service)
    api = UserAPI(service)
    
    // Test complete workflow
    response = api.create_user(...)
    assert response.status == 201
    assert cache.has(user_id)
    assert email_service.sent_welcome_email
```

**Pros:** Tests real system behavior  
**Cons:** Hard to debug when failures occur

---

### How to Use Sandwich Integration Pattern

**Concept:** Test high and low levels first, then middle layers.

```
Step 1: Test high level (API)
def test_api_layer():
    api = UserAPI(mock_service)
    response = api.create_user(...)

Step 2: Test low level (Repository)
def test_repository_layer():
    repo = UserRepository(test_database)
    user = repo.save(User(...))

Step 3: Test middle layer (Service)
def test_service_layer():
    repo = UserRepository(test_database)
    service = UserService(repo)
    user = service.create_user(...)

Step 4: Test all together
def test_full_integration():
    // All real components
```

---

## How to Choose a Test Database Strategy?

Pick the strategy that balances speed, realism, and isolation for your needs.

### How to Use In-Memory Database for Testing

**Concept:** Use in-memory database for fast tests.

```
def test_user_repository():
    // SQLite in-memory database
    db = sqlite3.connect(":memory:")
    db.execute(CREATE_USERS_TABLE)
    
    repo = UserRepository(db)
    user = repo.save(User(...))
    
    assert repo.find(user.id) is not None
```

**Pros:**
- ✅ Very fast
- ✅ No cleanup needed (destroyed after test)
- ✅ Isolated (each test gets fresh database)

**Cons:**
- ❌ May not match production database exactly
- ❌ Limited SQL features (no stored procedures, triggers)

---

### How to Use Test Database Instance

**Concept:** Use real database but separate instance for testing.

```
def test_user_repository():
    // Connect to test database
    db = connect("postgresql://localhost:5432/test_db")
    
    repo = UserRepository(db)
    user = repo.save(User(...))
    
    assert repo.find(user.id) is not None
    
    // Cleanup
    db.execute("DELETE FROM users WHERE id = ?", user.id)
```

**Pros:**
- ✅ Matches production database
- ✅ Tests real SQL features

**Cons:**
- ❌ Slower than in-memory
- ❌ Requires cleanup
- ❌ Test pollution risk

---

### How to Use Transaction Rollback for Test Isolation

**Concept:** Wrap each test in transaction, rollback after.

```
def setup_test():
    db.begin_transaction()

def teardown_test():
    db.rollback()  // Undoes all changes

def test_user_repository():
    repo = UserRepository(db)
    user = repo.save(User(...))
    assert repo.find(user.id) is not None
    // Rollback happens automatically in teardown
```

**Pros:**
- ✅ Fast cleanup (rollback instant)
- ✅ Tests isolated
- ✅ Real database

**Cons:**
- ❌ Can't test transaction behavior
- ❌ Some operations can't be rolled back (DDL)

---

### How to Use Docker Containers for Test Databases

**Concept:** Spin up fresh database container for each test run.

```
def setup_tests():
    // Start PostgreSQL container
    container = docker.run("postgres:14", ports={"5432": "5432"})
    wait_for_database_ready()
    
    db = connect("postgresql://localhost:5432/postgres")
    db.execute(SCHEMA_SQL)
    return db

def teardown_tests():
    docker.stop(container)
    docker.remove(container)

def test_user_repository():
    repo = UserRepository(db)
    user = repo.save(User(...))
```

**Pros:**
- ✅ Isolated (fresh database each run)
- ✅ Exact production database
- ✅ No manual cleanup

**Cons:**
- ❌ Slower (container startup)
- ❌ Requires Docker

---

## How to Test External Services?

Choose the approach that balances realism with test speed and reliability.

### How to Use Test/Sandbox Environment

**Concept:** Use service provider's test environment.

```
def test_stripe_payment():
    // Stripe provides test API keys
    stripe = StripeClient(api_key=TEST_API_KEY)
    
    result = stripe.charge(
        card_number="4242424242424242",  // Test card
        amount=10.00
    )
    
    assert result.success == True
```

**Pros:**
- ✅ Tests real integration
- ✅ Safe (no real charges)

**Cons:**
- ❌ Requires network
- ❌ Test environment may differ from production

---

### How to Use Mock Servers for External Services

**Concept:** Run mock server that mimics external service.

```
def test_payment_service():
    // Start mock payment server
    mock_server = start_mock_server(port=8080)
    mock_server.expect_request("/charge", returns={"success": True})
    
    client = PaymentClient(base_url="http://localhost:8080")
    result = client.charge(card_number="...", amount=10.00)
    
    assert result.success == True
    mock_server.verify_all_requests_received()
```

**Pros:**
- ✅ Fast (no network)
- ✅ Deterministic
- ✅ Can simulate errors

**Cons:**
- ❌ Not real service
- ❌ Mock may drift from real API

---

### How to Use Contract Testing

**Concept:** Test that your client matches service's contract.

```
// Record real API interactions (once)
@record_interactions
def record_api_calls():
    client = PaymentClient()
    client.charge(...)  // Records request/response

// Replay in tests (offline)
@replay_interactions
def test_payment_client():
    client = PaymentClient()
    result = client.charge(...)  // Uses recorded response
    assert result.success == True
```

**Tools:** Pact, VCR, WireMock

---

## How to Manage Test Data?

Choose the test data strategy that fits your test maintenance and flexibility needs.

### How to Use Fixtures for Test Data

**Concept:** Predefined test data loaded before tests.

```
// fixtures.sql
INSERT INTO users (id, email, name) VALUES
    (1, 'alice@example.com', 'Alice'),
    (2, 'bob@example.com', 'Bob'),
    (3, 'charlie@example.com', 'Charlie');

// test_users.py
def setup():
    db.execute_file("fixtures.sql")

def test_get_user():
    user = user_repo.find(1)
    assert user.email == "alice@example.com"
```

**Pros:**
- ✅ Consistent test data
- ✅ Easy to understand

**Cons:**
- ❌ Brittle (tests depend on specific IDs)
- ❌ Maintenance burden

---

### How to Use Factories for Test Data

**Concept:** Generate test data programmatically.

```
class UserFactory:
    @staticmethod
    def create(email=None, name=None):
        return User(
            email=email or f"user{random_id()}@example.com",
            name=name or f"User {random_id()}"
        )

def test_user_creation():
    user = UserFactory.create()
    repo.save(user)
    
    found = repo.find(user.id)
    assert found.email == user.email
```

**Pros:**
- ✅ Flexible (customize as needed)
- ✅ No hardcoded IDs
- ✅ Easy to create variations

**Cons:**
- ❌ Non-deterministic (random data)

---

### How to Use Builders for Test Data

**Concept:** Fluent API for building test objects.

```
class UserBuilder:
    def __init__(self):
        self.email = "default@example.com"
        self.name = "Default User"
        self.role = "user"
    
    def with_email(self, email):
        self.email = email
        return self
    
    def with_admin_role(self):
        self.role = "admin"
        return self
    
    def build(self):
        return User(email=self.email, name=self.name, role=self.role)

def test_admin_permissions():
    admin = UserBuilder().with_admin_role().build()
    assert admin.can_delete_users() == True
```

**Pros:**
- ✅ Readable
- ✅ Flexible
- ✅ Clear intent

---

## What are Integration Testing Best Practices?

### 1. How to Test One Integration at a Time

```
// GOOD: Tests repository → database integration
def test_repository_database():
    repo = UserRepository(test_database)
    user = repo.save(User(...))
    assert repo.find(user.id) is not None

// BAD: Tests too many integrations
def test_entire_system():
    api = setup_api()
    service = setup_service()
    repo = setup_repo()
    cache = setup_cache()
    email = setup_email()
    // Too much to debug if this fails!
```

### 2. When to Use Real Dependencies vs Mocks

```
// GOOD: Use real database
def test_user_service():
    repo = UserRepository(test_database)  // Real
    service = UserService(repo)

// OK: Mock slow external service
def test_user_service():
    repo = UserRepository(test_database)  // Real
    email_service = MockEmailService()    // Mock (slow)
    service = UserService(repo, email_service)
```

### 3. How to Isolate Tests Properly

```
// GOOD: Each test independent
def test_create_user():
    clear_database()
    user = create_user(...)

def test_update_user():
    clear_database()
    user = create_user(...)
    update_user(...)

// BAD: Tests depend on each other
def test_1_create_user():
    global user_id
    user_id = create_user(...)

def test_2_update_user():
    update_user(user_id, ...)  // Depends on test_1!
```

### 4. How Fast Should Integration Tests Be?

```
// Target: Integration tests should run in < 5 minutes
// If too slow:
// - Use in-memory database instead of real database
// - Parallelize tests
// - Reduce test data size
// - Mock slower external services
```

---

## What Common Pitfalls Should I Avoid?

### Pitfall 1: Testing Too Much (Treat as E2E Test)

❌ Testing implementation details instead of integration.

```
// BAD
def test_user_service_calls_repository():
    mock_repo = MockRepository()
    service = UserService(mock_repo)
    service.create_user(...)
    assert mock_repo.save.called == True  // Testing implementation!
```

### Pitfall 2: Tests That Are Too Slow

❌ Tests take too long, developers stop running them.

**Fix:** Use faster test doubles, in-memory databases, parallel execution.

### Pitfall 3: Flaky Tests (Non-Deterministic Failures)

❌ Tests pass/fail randomly.

**Common causes:**
- Timing issues (async operations)
- Shared state (tests not isolated)
- External service instability
- Non-deterministic data

---

## Cross-References and Related Standards

### Related Testing Standards

Query for comprehensive testing strategy:

```python
# For test strategy overview
pos_search_project(content_type="standards", query="test pyramid unit integration e2e")

# For test doubles and mocking
pos_search_project(content_type="standards", query="test doubles mocks stubs spies")

# For database patterns
pos_search_project(content_type="standards", query="database patterns repository")

# For API design and testing
pos_search_project(content_type="standards", query="API design principles testing")
```

**Related Standards:**
- [Test Pyramid](test-pyramid.md) - Overall testing strategy, 70-15-5 rule
- [Test Doubles](test-doubles.md) - Mocks, stubs, fakes for testing
- [Production Code Checklist](../ai-safety/production-code-checklist.md) - Testing requirements
- [Database Patterns](../architecture/database-patterns.md) - Repository pattern, transactions

### When to Query This Standard

```python
# When planning integration tests
pos_search_project(content_type="standards", query="integration testing patterns")

# When tests are too slow
pos_search_project(content_type="standards", query="fast integration tests database")

# When managing test data
pos_search_project(content_type="standards", query="test fixtures factories builders")

# When testing external services
pos_search_project(content_type="standards", query="external service testing mocking")
```

### Language-Specific Implementation

This document covers universal concepts. For language-specific tools and patterns:

```python
# Python integration testing
pos_search_project(content_type="standards", query="pytest fixtures test client python")

# Java integration testing  
pos_search_project(content_type="standards", query="spring boot test testcontainers")

# JavaScript integration testing
pos_search_project(content_type="standards", query="supertest jest integration tests")
```

**Language-Specific Guides:**
- Python: pytest fixtures, TestClient, pytest-mock, SQLAlchemy test patterns
- Java: @SpringBootTest, TestContainers, Mockito, JUnit integration
- JavaScript: supertest, jest, test databases, Prisma test patterns
- Go: httptest, testify, database/sql testing patterns

---

**Integration tests verify that components work together correctly. They sit between unit tests (fast, isolated) and E2E tests (slow, full system). Test real integrations when practical, mock only when necessary. Keep tests fast enough to run frequently (<5 minutes).**
