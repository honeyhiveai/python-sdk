# Database Patterns - Universal Database Practice

**Timeless patterns for working with databases effectively.**

---

## 🎯 TL;DR - Database Patterns Quick Reference

**Keywords for search**: database patterns, database optimization, N+1 query problem, database indexes, database transactions, query optimization, schema design, database migrations, connection pooling, database testing, database performance

**Critical Database Principles:**
1. **Avoid N+1 Queries** - Use JOINs or eager loading (1-2 queries instead of 100+)
2. **Index Strategically** - Index WHERE/JOIN columns, avoid over-indexing
3. **Handle Transactions** - ACID guarantees for multi-step operations
4. **Batch Operations** - Process multiple rows in single query
5. **Connection Pool** - Reuse connections, don't create per-query
6. **Test with Real DB** - In-memory DBs hide performance issues

**Common Anti-Patterns:**
- SELECT * (retrieve all columns unnecessarily)
- Missing indexes on foreign keys
- Long-running transactions
- Not handling deadlocks/retries
- Testing only with mocks (not real database)

**Performance Targets:**
- Index queries: <10ms for simple lookups
- Complex queries: <100ms
- Transactions: <1 second
- Connection pool: 10-50 connections for most apps

---

## ❓ Questions This Answers

1. "How do I avoid N+1 query problems?"
2. "When should I add database indexes?"
3. "How do I handle database transactions properly?"
4. "What's the best way to optimize slow database queries?"
5. "How do I design database schemas effectively?"
6. "How do I handle database migrations safely?"
7. "What's connection pooling and how do I use it?"
8. "What database anti-patterns should I avoid?"
9. "How do I test code that uses a database?"
10. "How do I improve database performance?"
11. "What's the difference between optimistic and pessimistic locking?"
12. "How do I batch database operations?"

---

## Core Principle

**"Database operations are expensive. Minimize them."**

**Key principles:**
- Batch operations when possible
- Use indexes strategically
- Avoid N+1 queries
- Handle transactions properly

---

## How to Avoid the N+1 Query Problem (Most Critical Pattern)

The N+1 query problem is the most common and most expensive database anti-pattern. Understanding and preventing it is essential for performant database code.

**Problem:** Making N additional queries inside a loop.

```
// ❌ BAD: N+1 queries (1 + N where N = number of users)
users = database.query("SELECT * FROM users")
for user in users:
    orders = database.query(
        "SELECT * FROM orders WHERE user_id = ?",
        user.id
    )
    user.orders = orders

// With 100 users: 101 database queries!
```

**Solution 1: JOIN**
```
// ✅ GOOD: 1 query with JOIN
results = database.query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
""")

// Group results by user
users = group_by_user(results)
```

**Solution 2: Eager Loading**
```
// ✅ GOOD: 2 queries (much better than N+1)
users = database.query("SELECT * FROM users")
user_ids = [user.id for user in users]

orders = database.query(
    "SELECT * FROM orders WHERE user_id IN (?)",
    user_ids
)

// Associate orders with users in memory
orders_by_user = group_by(orders, "user_id")
for user in users:
    user.orders = orders_by_user.get(user.id, [])
```

**Performance Impact:**
- N+1 queries: 101 database calls
- JOIN or eager loading: 1-2 database calls
- **Speedup: 50x-100x**

---

## How to Use Database Indexes Effectively

Indexes dramatically improve query performance but cost storage and slow down writes. Strategic indexing is a critical skill for database-driven applications.

### Pattern 1: Index Frequently Queried Columns

```sql
-- ❌ BAD: No index
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT,
    created_at TIMESTAMP
);

-- Query: SELECT * FROM users WHERE email = ?
-- Result: Full table scan (slow)

-- ✅ GOOD: Index on email
CREATE INDEX idx_users_email ON users(email);

-- Query: SELECT * FROM users WHERE email = ?
-- Result: Index lookup (fast)
```

**When to add indexes:**
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Columns used frequently in queries

---

### Pattern 2: Composite Indexes

```sql
-- Query pattern: WHERE user_id = ? AND created_at > ?

-- ❌ BAD: Two separate indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ✅ GOOD: Composite index
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
```

**Rule:** Order matters! Put equality checks before range checks.

---

### Pattern 3: Avoid Over-Indexing

```sql
-- ❌ BAD: Too many indexes
CREATE INDEX idx1 ON users(email);
CREATE INDEX idx2 ON users(name);
CREATE INDEX idx3 ON users(created_at);
CREATE INDEX idx4 ON users(updated_at);
CREATE INDEX idx5 ON users(status);

-- Indexes slow down writes (INSERT, UPDATE, DELETE)
```

**Rule:** Only index what you query. Each index has a cost.

---

## How to Handle Database Transactions Properly

Transactions ensure that multi-step database operations either complete fully or roll back completely, maintaining data consistency and integrity.

### Pattern 1: Atomic Operations

**Concept:** All operations succeed or all fail.

```
// ❌ BAD: No transaction
database.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
// App crashes here!
database.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
// Money disappeared!

// ✅ GOOD: Transaction
transaction = database.begin_transaction()
try:
    database.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    database.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    transaction.commit()
except Exception:
    transaction.rollback()
    raise
```

---

### Pattern 2: Isolation Levels

**Four standard isolation levels:**

1. **Read Uncommitted:** Can see uncommitted changes (dirty reads)
2. **Read Committed:** Only sees committed changes
3. **Repeatable Read:** Same read returns same result
4. **Serializable:** Full isolation (slowest)

```
// Example: Prevent race conditions
transaction = database.begin_transaction(isolation="SERIALIZABLE")
try:
    user = database.query("SELECT * FROM users WHERE id = ? FOR UPDATE", user_id)
    if user.balance >= amount:
        database.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            amount, user_id
        )
        transaction.commit()
    else:
        transaction.rollback()
except Exception:
    transaction.rollback()
    raise
```

**Trade-off:** Higher isolation = more correctness but less concurrency.

---

### Pattern 3: Short Transactions

```
// ❌ BAD: Long transaction
transaction = database.begin_transaction()
data = fetch_from_external_api()  // Slow! Holds lock
database.execute("INSERT INTO data VALUES (?)", data)
transaction.commit()

// ✅ GOOD: Short transaction
data = fetch_from_external_api()  // Outside transaction
transaction = database.begin_transaction()
database.execute("INSERT INTO data VALUES (?)", data)
transaction.commit()
```

**Rule:** Keep transactions as short as possible. Don't hold locks during I/O.

---

## How to Optimize Database Queries

Query optimization transforms slow queries into fast ones. Small changes to query structure can produce 10x-100x performance improvements.

### Pattern 1: SELECT Only Needed Columns

```
// ❌ BAD: SELECT *
results = database.query("SELECT * FROM users")
for user in results:
    print(user.email)  // Only using email!

// ✅ GOOD: SELECT specific columns
results = database.query("SELECT email FROM users")
for user in results:
    print(user.email)
```

**Benefit:** Less data transferred, less memory used.

---

### Pattern 2: LIMIT Results

```
// ❌ BAD: No LIMIT
users = database.query("SELECT * FROM users")  // Returns 1 million rows!

// ✅ GOOD: LIMIT results
users = database.query("SELECT * FROM users LIMIT 100")
```

---

### Pattern 3: Use EXPLAIN

```
// Analyze query performance
EXPLAIN SELECT * FROM users WHERE email = ?

// Look for:
// - Table scans (bad)
// - Index usage (good)
// - Estimated rows
```

---

## How to Design Database Schemas Effectively

Good schema design prevents data anomalies, improves query performance, and makes your database maintainable. These patterns apply across all relational databases.

### Pattern 1: Normalization

**Concept:** Eliminate data redundancy.

```
// ❌ BAD: Denormalized (redundant data)
CREATE TABLE orders (
    id INTEGER,
    user_name TEXT,
    user_email TEXT,
    user_address TEXT,
    product_name TEXT,
    product_price DECIMAL
);
// If user changes address, must update ALL their orders!

// ✅ GOOD: Normalized
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    address TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price DECIMAL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id)
);
```

---

### Pattern 2: Denormalization (When Appropriate)

**Concept:** Sometimes redundancy improves performance.

```
// For read-heavy workloads
CREATE TABLE orders (
    id INTEGER,
    user_id INTEGER,
    user_name TEXT,  // Denormalized for faster reads
    product_id INTEGER,
    product_name TEXT  // Denormalized for faster reads
);

// Trade-off: Faster reads, slower writes, data can become stale
```

**When to denormalize:**
- Read:write ratio > 100:1
- JOIN performance is bottleneck
- Data doesn't change often

---

### Pattern 3: Use Appropriate Data Types

```sql
-- ❌ BAD: Wrong data types
CREATE TABLE users (
    id TEXT,              -- Should be INTEGER
    created_at TEXT,      -- Should be TIMESTAMP
    is_active TEXT        -- Should be BOOLEAN
);

-- ✅ GOOD: Correct data types
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

---

## How to Handle Database Migrations Safely

Database migrations modify schema or data in production. Safe migrations prevent downtime, data loss, and difficult-to-reverse changes.

### Pattern 1: Reversible Migrations

```
// ✅ GOOD: Both upgrade and downgrade
migration_001_add_email_index:
    upgrade():
        database.execute("CREATE INDEX idx_users_email ON users(email)")
    
    downgrade():
        database.execute("DROP INDEX idx_users_email")
```

---

### Pattern 2: Safe Schema Changes

```
// ❌ BAD: Unsafe (drops data)
ALTER TABLE users DROP COLUMN old_field;

// ✅ GOOD: Safe (phased approach)
Step 1: Add new column
ALTER TABLE users ADD COLUMN new_field TEXT;

Step 2: Migrate data
UPDATE users SET new_field = transform(old_field);

Step 3: Update code to use new_field

Step 4: (Later) Remove old column
ALTER TABLE users DROP COLUMN old_field;
```

---

### Pattern 3: Online Schema Changes

```
// For zero-downtime deployments
Step 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN new_field TEXT NULL;

Step 2: Deploy code that writes to both columns

Step 3: Backfill data
UPDATE users SET new_field = old_field WHERE new_field IS NULL;

Step 4: Make column NOT NULL
ALTER TABLE users ALTER COLUMN new_field SET NOT NULL;

Step 5: Deploy code that only uses new_field

Step 6: Drop old column
ALTER TABLE users DROP COLUMN old_field;
```

---

## How to Manage Database Connections

Database connections are expensive to create. Connection pooling reuses existing connections, dramatically improving performance and resource utilization.

### Pattern 1: Connection Pooling

```
// ❌ BAD: New connection per query
function query_database():
    connection = create_connection()  // Expensive!
    result = connection.query(...)
    connection.close()
    return result

// ✅ GOOD: Connection pool
pool = ConnectionPool(
    size=10,
    max_overflow=5,
    timeout=30
)

function query_database():
    with pool.get_connection() as connection:
        return connection.query(...)
```

**Benefits:**
- Reuses connections
- Faster (no connection overhead)
- Limits total connections

---

### Pattern 2: Graceful Degradation

```
// ✅ GOOD: Handle connection failures
function query_with_retry():
    for attempt in range(3):
        try:
            return database.query(...)
        except ConnectionError:
            if attempt < 2:
                sleep(exponential_backoff(attempt))
            else:
                # Graceful degradation
                return cached_result() or default_value()
```

---

## What Database Anti-Patterns Should I Avoid?

These common mistakes cause severe performance degradation and maintenance issues. Recognizing them early prevents costly refactoring.

### Anti-Pattern 1: SELECT * with Large BLOB

```
// ❌ BAD: Loading huge BLOBs unnecessarily
users = database.query("SELECT * FROM users")
for user in users:
    print(user.name)  // Loaded profile_image (1MB each) for nothing!

// ✅ GOOD: Don't SELECT BLOBs unless needed
users = database.query("SELECT id, name, email FROM users")
```

---

### Anti-Pattern 2: Looping for Aggregations

```
// ❌ BAD: Aggregating in application code
users = database.query("SELECT * FROM users")
total_age = 0
for user in users:
    total_age += user.age
average_age = total_age / len(users)

// ✅ GOOD: Let database do aggregation
result = database.query("SELECT AVG(age) FROM users")
average_age = result[0]
```

**Rule:** Use database for what it's good at (aggregations, filtering, sorting).

---

### Anti-Pattern 3: No Connection Timeout

```
// ❌ BAD: Can hang forever
connection = create_connection(host, port)

// ✅ GOOD: Always set timeouts
connection = create_connection(
    host,
    port,
    connect_timeout=5,
    read_timeout=30
)
```

---

## How to Test Database Code

Testing database code requires real database instances. In-memory databases and mocks hide performance issues and subtle bugs that only appear with real database engines.

### Test 1: Use Test Database

```
// ✅ GOOD: Separate test database
test_setup():
    test_db = create_test_database()
    run_migrations(test_db)
    return test_db

test_teardown():
    drop_test_database()
```

---

### Test 2: Transactions for Isolation

```
// ✅ GOOD: Rollback after each test
test_create_user():
    transaction = database.begin_transaction()
    try:
        user = create_user("test@example.com")
        assert user.email == "test@example.com"
    finally:
        transaction.rollback()  // Clean up
```

---

### Test 3: Test Constraints

```
test_unique_constraint():
    create_user("alice@example.com")
    
    # Should fail (duplicate email)
    with assert_raises(UniqueViolation):
        create_user("alice@example.com")
```

---

## Database Performance Checklist

- [ ] **Indexes:** On frequently queried columns
- [ ] **N+1 queries:** Fixed with JOINs or eager loading
- [ ] **SELECT \*:** Only fetch needed columns
- [ ] **Connection pooling:** Configured and sized appropriately
- [ ] **Transactions:** Short and properly handled
- [ ] **Query analysis:** EXPLAIN used to identify slow queries
- [ ] **Timeouts:** Connection and query timeouts set
- [ ] **Migrations:** Reversible and tested

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Slow queries** | `pos_search_project(content_type="standards", query="how to optimize slow database queries")` |
| **Designing schema** | `pos_search_project(content_type="standards", query="database schema design patterns")` |
| **Writing loops** | `pos_search_project(content_type="standards", query="N+1 query problem")` |
| **Adding indexes** | `pos_search_project(content_type="standards", query="when to add database indexes")` |
| **Multi-step operations** | `pos_search_project(content_type="standards", query="database transactions")` |
| **Database tests** | `pos_search_project(content_type="standards", query="how to test database code")` |
| **Migrations** | `pos_search_project(content_type="standards", query="database migrations")` |
| **Performance issues** | `pos_search_project(content_type="standards", query="database performance")` |

---

## 🔗 Related Standards

**Query workflow for database implementation:**

1. **Start here** → `pos_search_project(content_type="standards", query="database patterns")`
2. **Then design** → `pos_search_project(content_type="standards", query="database schema design")`
3. **Then test** → `pos_search_project(content_type="standards", query="integration testing database")` → `standards/testing/integration-testing.md`
4. **Then optimize** → `pos_search_project(content_type="standards", query="database performance")` (this document)

**By Category:**

**Testing:**
- `standards/testing/integration-testing.md` - How to test database integration → `pos_search_project(content_type="standards", query="integration testing database")`
- `standards/testing/test-pyramid.md` - Test ratios (integration tests 20-30%) → `pos_search_project(content_type="standards", query="test pyramid")`

**Architecture:**
- `standards/architecture/api-design-principles.md` - API design for database-backed services → `pos_search_project(content_type="standards", query="API design patterns")`
- `standards/architecture/dependency-injection.md` - Injecting database connections → `pos_search_project(content_type="standards", query="dependency injection")`

**Failure Modes:**
- `standards/failure-modes/retry-strategies.md` - Retrying failed database operations → `pos_search_project(content_type="standards", query="retry strategies")`
- `standards/failure-modes/timeout-patterns.md` - Database query timeouts → `pos_search_project(content_type="standards", query="timeout patterns")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Production code checklist (includes database validation) → `pos_search_project(content_type="standards", query="production code checklist")`

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-database.md`
- See `.praxis-os/standards/development/go-database.md`
- See `.praxis-os/standards/development/rust-database.md`
- Etc.

---

**Database operations are expensive. Minimize queries, use indexes strategically, handle transactions properly, and always use connection pooling. The N+1 query problem is the most common performance issue - fix it with JOINs or eager loading.**
