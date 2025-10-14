# Dependency Injection - Universal Architecture Pattern

**Timeless pattern for decoupling and testable code.**

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

## Three Types of Dependency Injection

### Type 1: Constructor Injection (Recommended)

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

### Type 2: Setter Injection

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

### Type 3: Interface Injection

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

## Dependency Injection Patterns

### Pattern 1: Manual DI (Simple Projects)

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

### Pattern 2: DI Container (Large Projects)

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

### Pattern 3: Factory Pattern

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

## Handling Complex Dependencies

### Problem: Circular Dependencies

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

### Problem: Too Many Dependencies

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

## Testing with Dependency Injection

### Unit Test with Mocks

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

### Integration Test with Real Dependencies

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

## DI Containers (Language Examples)

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

## Anti-Patterns

### Anti-Pattern 1: Service Locator

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

### Anti-Pattern 2: New Keyword in Business Logic

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

### Anti-Pattern 3: Overusing DI

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

## Best Practices

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
- See `.agent-os/standards/development/python-architecture.md` (Python: `dependency-injector`, type hints)
- See `.agent-os/standards/development/java-architecture.md` (Java: Spring, Guice)
- See `.agent-os/standards/development/csharp-architecture.md` (C#: built-in DI)
- See `.agent-os/standards/development/js-architecture.md` (JavaScript: InversifyJS)
- Etc.

---

**Dependency Injection is fundamental to clean architecture. Use constructor injection by default. Don't create dependencies, ask for them. This makes code testable, flexible, and maintainable.**
