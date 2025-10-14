# Integration Testing - Universal Testing Strategy

**Timeless approach to testing component interactions and system behavior.**

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

## Types of Integration Testing

### Type 1: Component Integration

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

### Type 2: API Integration

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

### Type 3: External Service Integration

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

### Type 4: Database Integration

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

## Integration Test Patterns

### Pattern 1: Top-Down Integration

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

### Pattern 2: Bottom-Up Integration

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

### Pattern 3: Big Bang Integration

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

### Pattern 4: Sandwich Integration

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

## Test Database Strategies

### Strategy 1: In-Memory Database

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

### Strategy 2: Test Database Instance

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

### Strategy 3: Database Per Test (Transactions)

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

### Strategy 4: Docker Containers

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

## Testing External Services

### Approach 1: Test/Sandbox Environment

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

### Approach 2: Mock Server

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

### Approach 3: Contract Testing

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

## Test Data Management

### Strategy 1: Fixtures

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

### Strategy 2: Factories

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

### Strategy 3: Builders

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

## Best Practices

### 1. Test One Integration at a Time

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

### 2. Use Real Dependencies When Practical

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

### 3. Isolate Tests

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

### 4. Fast Enough to Run Frequently

```
// Target: Integration tests should run in < 5 minutes
// If too slow:
// - Use in-memory database instead of real database
// - Parallelize tests
// - Reduce test data size
// - Mock slower external services
```

---

## Common Pitfalls

### Pitfall 1: Testing Too Much

❌ Testing implementation details instead of integration.

```
// BAD
def test_user_service_calls_repository():
    mock_repo = MockRepository()
    service = UserService(mock_repo)
    service.create_user(...)
    assert mock_repo.save.called == True  // Testing implementation!
```

### Pitfall 2: Slow Tests

❌ Tests take too long, developers stop running them.

**Fix:** Use faster test doubles, in-memory databases, parallel execution.

### Pitfall 3: Flaky Tests

❌ Tests pass/fail randomly.

**Common causes:**
- Timing issues (async operations)
- Shared state (tests not isolated)
- External service instability
- Non-deterministic data

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-testing.md` (Python: pytest fixtures, TestClient)
- See `.agent-os/standards/development/java-testing.md` (Java: @SpringBootTest, TestContainers)
- See `.agent-os/standards/development/js-testing.md` (JavaScript: supertest, test databases)
- Etc.

---

**Integration tests verify that components work together correctly. They sit between unit tests (fast, isolated) and E2E tests (slow, full system). Test real integrations when practical, mock only when necessary. Keep tests fast enough to run frequently.**
