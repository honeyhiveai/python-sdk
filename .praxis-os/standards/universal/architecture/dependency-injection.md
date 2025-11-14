# Dependency Injection - Universal Architecture Pattern

**Timeless pattern for decoupling and testable code.**

**Keywords for search**: dependency injection, DI, constructor injection, testable code, mocking dependencies, inversion of control, IoC container, decoupling, SOLID principles, dependency management

---

## 🚨 Quick Reference (TL;DR)

**Core Principle:** Don't create what you need. Ask for it.

**Three Types of DI:**
1. **Constructor Injection** (Recommended, 90% of cases) - Dependencies passed through constructor
2. **Setter Injection** (Rare) - Dependencies set via methods after construction
3. **Interface Injection** (Almost never) - Object provides injection method

**Key Benefits:**
- ✅ Loosely coupled code
- ✅ Easy to test (inject mocks)
- ✅ Reusable components
- ✅ Follows SOLID principles

**Three Implementation Patterns:**
1. **Manual DI** - Manually wire dependencies (small projects, <20 classes)
2. **DI Container** - Framework manages dependencies (large projects, >20 classes)
3. **Factory Pattern** - Factory creates objects with dependencies (medium projects)

**Anti-Patterns to Avoid:**
- ❌ Service Locator (hidden dependencies)
- ❌ New keyword in business logic
- ❌ Overusing DI (injecting constants)

**Quick Start:**
```python
# Without DI (Bad)
class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  # Hard-coded!

# With DI (Good)
class UserService:
    def __init__(self, database):  # Dependency injected!
        self.database = database
```

---

## Questions This Answers

- "What is dependency injection and why use it?"
- "How to make code testable by injecting dependencies?"
- "What's the difference between constructor, setter, and interface injection?"
- "When should I use a DI container vs manual wiring?"
- "How to avoid hard-coded dependencies in my code?"
- "How to mock dependencies for unit testing?"
- "What are dependency injection anti-patterns?"
- "How to handle circular dependencies?"
- "When should I use constructor injection vs setter injection?"
- "How to implement dependency injection in my language?"
- "What's the difference between dependency injection and service locator?"
- "How to refactor code to use dependency injection?"

---

## What is Dependency Injection?

Dependency Injection (DI) is a design pattern where an object receives its dependencies from external sources rather than creating them itself.

**Key principle:** Don't create what you need. Ask for it.

## The Problem: Hard-Coded Dependencies

### Without DI (Bad)

```
class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  // Hard-coded!
        self.logger = FileLogger()       // Hard-coded!
        self.cache = RedisCache()        // Hard-coded!
    
    def get_user(self, user_id):
        self.logger.log(f"Fetching user {user_id}")
        cached = self.cache.get(user_id)
        if cached:
            return cached
        user = self.database.find(user_id)
        self.cache.set(user_id, user)
        return user
```

**Problems:**
1. **Tightly coupled:** Can't use PostgreSQL without changing UserService
2. **Hard to test:** Can't mock database/cache for unit tests
3. **Not reusable:** Only works with these specific implementations
4. **Violates SOLID:** Depends on concrete classes, not abstractions

---

## The Solution: Dependency Injection

### With DI (Good)

```
class UserService:
    def __init__(self, database, logger, cache):  // Dependencies injected!
        self.database = database
        self.logger = logger
        self.cache = cache
    
    def get_user(self, user_id):
        self.logger.log(f"Fetching user {user_id}")
        cached = self.cache.get(user_id)
        if cached:
            return cached
        user = self.database.find(user_id)
        self.cache.set(user_id, user)
        return user

// Production usage
mysql = MySQLDatabase()
file_logger = FileLogger()
redis = RedisCache()
user_service = UserService(mysql, file_logger, redis)

// Test usage
mock_db = MockDatabase()
mock_logger = MockLogger()
mock_cache = MockCache()
user_service = UserService(mock_db, mock_logger, mock_cache)
```

**Benefits:**
1. **Loosely coupled:** Can swap implementations
2. **Testable:** Easy to inject mocks
3. **Reusable:** Works with any implementation
4. **Follows SOLID:** Depends on abstractions

---

## How to Choose the Right Type of Dependency Injection

Understanding the three types helps you select the best approach for your specific use case.

### Type 1: How to Use Constructor Injection (Recommended)

**Concept:** Dependencies passed through constructor.

```
class OrderService:
    def __init__(self, payment_service, inventory_service, email_service):
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.email_service = email_service
    
    def place_order(self, order):
        self.payment_service.charge(order.total)
        self.inventory_service.reduce_stock(order.items)
        self.email_service.send_confirmation(order.user_email)
```

**Benefits:**
- ✅ Dependencies are explicit (visible in constructor)
- ✅ Immutable (set once, can't change)
- ✅ Easy to test
- ✅ Fails fast (can't create without dependencies)

**When to use:** Default choice (90% of cases).

---

### Type 2: How to Use Setter Injection

**Concept:** Dependencies set through methods after construction.

```
class ReportGenerator:
    def __init__(self):
        self.database = None
        self.formatter = None
    
    def set_database(self, database):
        self.database = database
    
    def set_formatter(self, formatter):
        self.formatter = formatter
    
    def generate_report(self):
        if not self.database or not self.formatter:
            raise Error("Dependencies not set!")
        data = self.database.query()
        return self.formatter.format(data)

// Usage
generator = ReportGenerator()
generator.set_database(mysql)
generator.set_formatter(pdf_formatter)
report = generator.generate_report()
```

**Benefits:**
- ✅ Optional dependencies
- ✅ Can change dependencies after construction

**Drawbacks:**
- ❌ Object may be in invalid state (missing dependencies)
- ❌ Dependencies not explicit
- ❌ Error at usage time, not construction time

**When to use:** Optional dependencies or need to swap at runtime (rare).

---

### Type 3: How to Use Interface Injection (Rarely Needed)

**Concept:** Object provides method to inject dependencies (rare).

```
interface InjectableService:
    def inject_dependencies(container)

class UserService implements InjectableService:
    def inject_dependencies(self, container):
        self.database = container.get("database")
        self.logger = container.get("logger")
```

**When to use:** Almost never (overly complex). Use constructor injection instead.

---

## How to Implement Dependency Injection (Three Patterns)

Choose the pattern that matches your project size and complexity.

### Pattern 1: How to Use Manual DI (Simple Projects)

**Concept:** Manually wire dependencies in main/setup code.

```
// main.py
def main():
    // Create dependencies
    database = MySQLDatabase(config.db_url)
    cache = RedisCache(config.redis_url)
    logger = FileLogger(config.log_path)
    
    // Wire up services
    user_service = UserService(database, logger, cache)
    order_service = OrderService(database, logger, user_service)
    api = API(user_service, order_service)
    
    // Start application
    api.start()

if __name__ == "__main__":
    main()
```

**Benefits:**
- Simple, no framework needed
- Easy to understand
- Full control

**Drawbacks:**
- Manual wiring (tedious for large apps)
- Hard to manage complex dependency graphs

**When to use:** Small to medium projects (<20 classes).

---

### Pattern 2: How to Use DI Container (Large Projects)

**Concept:** Container manages dependency creation and injection.

```
// Configure container
container = DIContainer()

// Register dependencies
container.register("database", MySQLDatabase, singleton=True)
container.register("cache", RedisCache, singleton=True)
container.register("logger", FileLogger, singleton=False)

// Register services (auto-resolve dependencies)
container.register("user_service", UserService)
container.register("order_service", OrderService)

// Resolve (container handles wiring)
user_service = container.resolve("user_service")
```

**Behind the scenes:**
```
class DIContainer:
    def resolve(self, name):
        class_type = self.registrations[name]
        
        // Inspect constructor, resolve dependencies
        dependencies = inspect_constructor(class_type)
        resolved_deps = [self.resolve(dep) for dep in dependencies]
        
        // Instantiate with resolved dependencies
        return class_type(*resolved_deps)
```

**Benefits:**
- Automatic wiring
- Handles complex graphs
- Singleton management
- Lifecycle management

**Drawbacks:**
- Adds framework dependency
- "Magic" (harder to trace)
- Learning curve

**When to use:** Large projects (>20 classes) with complex dependencies.

---

### Pattern 3: How to Use Factory Pattern for DI

**Concept:** Factory creates objects with dependencies.

```
class ServiceFactory:
    def __init__(self, config):
        self.config = config
        self.database = MySQLDatabase(config.db_url)
        self.logger = FileLogger(config.log_path)
    
    def create_user_service(self):
        return UserService(self.database, self.logger)
    
    def create_order_service(self):
        user_service = self.create_user_service()
        return OrderService(self.database, self.logger, user_service)

// Usage
factory = ServiceFactory(config)
user_service = factory.create_user_service()
order_service = factory.create_order_service()
```

**When to use:** Medium projects, need controlled creation logic.

---

## How to Handle Complex Dependency Scenarios

### How to Resolve Circular Dependencies

```
// BAD: Circular dependency
class ServiceA:
    def __init__(self, service_b):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a

// Can't create either! Both depend on each other
```

**Solution 1: Refactor (Best)**
```
// Extract shared logic to third service
class SharedService:
    def shared_logic(self):
        pass

class ServiceA:
    def __init__(self, shared_service):
        self.shared = shared_service

class ServiceB:
    def __init__(self, shared_service):
        self.shared = shared_service
```

**Solution 2: Setter Injection (If refactor not possible)**
```
class ServiceA:
    def __init__(self):
        self.service_b = None
    
    def set_service_b(self, service_b):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a

// Create separately, then wire
service_a = ServiceA()
service_b = ServiceB(service_a)
service_a.set_service_b(service_b)
```

---

### How to Handle Too Many Dependencies

```
// Code smell: Constructor with 8+ parameters
class ReportService:
    def __init__(
        self,
        database,
        cache,
        logger,
        email_service,
        pdf_generator,
        excel_generator,
        auth_service,
        audit_service
    ):
        // Too many dependencies!
```

**Solution: Facade/Aggregate**
```
class ReportDependencies:
    def __init__(
        self,
        database,
        cache,
        logger,
        formatters,
        services
    ):
        self.database = database
        self.cache = cache
        self.logger = logger
        self.formatters = formatters  // pdf_generator, excel_generator
        self.services = services       // email, auth, audit

class ReportService:
    def __init__(self, dependencies):
        self.deps = dependencies
```

---

## How to Test Code Using Dependency Injection

DI makes testing significantly easier by allowing mock injection.

### How to Write Unit Tests with Mocked Dependencies

```
def test_get_user_caches_result():
    // Arrange
    mock_db = MockDatabase()
    mock_db.set_user(123, User(id=123, name="Alice"))
    mock_cache = MockCache()
    mock_logger = MockLogger()
    
    service = UserService(mock_db, mock_logger, mock_cache)
    
    // Act
    user = service.get_user(123)
    
    // Assert
    assert user.name == "Alice"
    assert mock_cache.get(123) == user  // Cached
    assert mock_db.call_count == 1      // DB called once
```

### How to Write Integration Tests with Real Dependencies

```
def test_order_flow_integration():
    // Use real implementations, but test environment
    test_db = TestDatabase()
    test_cache = InMemoryCache()
    test_logger = TestLogger()
    
    service = OrderService(test_db, test_cache, test_logger)
    
    // Full workflow test
    order = service.create_order(...)
    assert test_db.has_order(order.id)
```

---

## What DI Containers Are Available by Language?

### Python
- **Manual:** Simple constructor injection
- **Libraries:** `dependency-injector`, `injector`, `punq`

### Java
- **Spring Framework:** `@Autowired`, `@Component`
- **Google Guice:** `@Inject`

### C#
- **Built-in:** `Microsoft.Extensions.DependencyInjection`
- **Autofac**, **Ninject**

### JavaScript/TypeScript
- **InversifyJS**, **TSyringe**, **Awilix**

### Go
- **Wire:** Compile-time DI
- **Fx:** Runtime DI

---

## What Dependency Injection Anti-Patterns Should I Avoid?

### Anti-Pattern 1: Service Locator (Hidden Dependencies)

❌ Using global registry to fetch dependencies.

```
// BAD
class UserService:
    def __init__(self):
        self.database = ServiceLocator.get("database")
        self.logger = ServiceLocator.get("logger")
```

**Problems:**
- Hidden dependencies (not visible in constructor)
- Global state (hard to test, implicit coupling)
- Runtime errors (if service not registered)

**Fix:** Use constructor injection.

---

### Anti-Pattern 2: Creating Dependencies in Business Logic

❌ Creating dependencies in methods.

```
// BAD
class OrderService:
    def place_order(self, order):
        email = EmailService()  // Creating dependency!
        email.send(order.confirmation)
```

**Fix:** Inject EmailService in constructor.

---

### Anti-Pattern 3: Overusing Dependency Injection

❌ Injecting everything, even simple values.

```
// BAD: Injecting constants
class TaxCalculator:
    def __init__(self, tax_rate):
        self.tax_rate = tax_rate  // Just use constant!
```

**When NOT to inject:**
- Constants (use config)
- Value objects (create directly)
- Standard library (don't inject `Math` or `Date`)

---

## What Are Dependency Injection Best Practices?

### 1. Prefer Constructor Injection
Makes dependencies explicit and immutable.

### 2. Depend on Abstractions, Not Implementations
```
// GOOD
def __init__(self, database: DatabaseInterface)

// BAD
def __init__(self, database: MySQLDatabase)
```

### 3. Keep Constructors Simple
Don't do heavy work in constructors. Just store dependencies.

```
// GOOD
def __init__(self, database):
    self.database = database

// BAD
def __init__(self, database):
    self.database = database
    self.connection = database.connect()  // Side effect!
```

### 4. Avoid Circular Dependencies
If you have them, refactor. They indicate design issues.

### 5. Use DI Container for Large Projects
Manual wiring doesn't scale beyond 20-30 classes.

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-architecture.md` (Python: `dependency-injector`, type hints)
- See `.praxis-os/standards/development/java-architecture.md` (Java: Spring, Guice)
- See `.praxis-os/standards/development/csharp-architecture.md` (C#: built-in DI)
- See `.praxis-os/standards/development/js-architecture.md` (JavaScript: InversifyJS)
- Etc.

---

## When to Query This Standard

This standard is most valuable when:

1. **Designing New Classes**
   - Situation: Creating classes with external dependencies
   - Query: `pos_search_project(content_type="standards", query="how to inject dependencies")`

2. **Making Code Testable**
   - Situation: Need to mock dependencies for unit tests
   - Query: `pos_search_project(content_type="standards", query="how to make code testable")`

3. **Refactoring Hard-Coded Dependencies**
   - Situation: Code has hard-coded database/API/service instantiation
   - Query: `pos_search_project(content_type="standards", query="how to remove hard-coded dependencies")`

4. **Choosing DI Implementation Pattern**
   - Situation: Deciding between manual DI, container, or factory
   - Query: `pos_search_project(content_type="standards", query="when to use DI container")`

5. **Resolving Circular Dependencies**
   - Situation: Two classes depend on each other
   - Query: `pos_search_project(content_type="standards", query="how to resolve circular dependencies")`

6. **Code Review Feedback**
   - Situation: Reviewer says "this should use dependency injection"
   - Query: `pos_search_project(content_type="standards", query="dependency injection pattern")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Make code testable | `pos_search_project(content_type="standards", query="how to make code testable")` |
| Remove hard-coding | `pos_search_project(content_type="standards", query="avoid hard-coded dependencies")` |
| Choose DI type | `pos_search_project(content_type="standards", query="constructor vs setter injection")` |
| Handle circular deps | `pos_search_project(content_type="standards", query="circular dependencies solution")` |
| DI container | `pos_search_project(content_type="standards", query="when to use DI container")` |

---

## Cross-References and Related Standards

**Architecture Standards:**
- `standards/architecture/solid-principles.md` - SOLID principles (DI supports Dependency Inversion)
  → `pos_search_project(content_type="standards", query="how to apply SOLID principles")`
- `standards/architecture/separation-of-concerns.md` - Separating concerns makes DI easier
  → `pos_search_project(content_type="standards", query="separation of concerns")`

**Testing Standards:**
- `standards/testing/test-doubles.md` - Mocks, stubs, fakes for DI testing
  → `pos_search_project(content_type="standards", query="how to use test doubles")`
- `standards/testing/test-pyramid.md` - Unit tests require DI for mocking
  → `pos_search_project(content_type="standards", query="test pyramid structure")`

**Production Code:**
- `standards/ai-safety/production-code-checklist.md` - Dependency management checklist
  → `pos_search_project(content_type="standards", query="production code checklist")`

**Query workflow for implementing DI:**
1. **Learn Pattern**: `pos_search_project(content_type="standards", query="dependency injection pattern")` → Read this standard
2. **Learn Testing**: `pos_search_project(content_type="standards", query="how to use test doubles")` → Understand mocking
3. **Choose Type**: `pos_search_project(content_type="standards", query="constructor vs setter injection")` → Select DI type
4. **Implement**: Apply constructor injection to your classes
5. **Test**: `pos_search_project(content_type="standards", query="how to unit test with mocks")` → Write tests with mocked dependencies
6. **Review**: `pos_search_project(content_type="standards", query="dependency injection anti-patterns")` → Validate approach

---

**Dependency Injection is fundamental to clean architecture. Use constructor injection by default. Don't create dependencies, ask for them. This makes code testable, flexible, and maintainable.**
