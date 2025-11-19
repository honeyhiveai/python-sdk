# SOLID Principles - Universal Object-Oriented Design

**Timeless design principles for maintainable, flexible object-oriented code.**

---

## 🚨 SOLID Quick Reference (TL;DR)

**Keywords for search**: SOLID principles, class design, maintainable code, object-oriented design, single responsibility, open closed principle, liskov substitution, interface segregation, dependency inversion, dependency injection, testable code, how to design classes

**Critical information:**

1. **Single Responsibility (SRP)** - One class, one reason to change. Each class does one thing well.
2. **Open/Closed (OCP)** - Open for extension, closed for modification. Add features without changing existing code.
3. **Liskov Substitution (LSP)** - Subtypes must be substitutable for their base types. Child classes work anywhere parent does.
4. **Interface Segregation (ISP)** - Many small interfaces > one large interface. Don't force clients to depend on unused methods.
5. **Dependency Inversion (DIP)** - Depend on abstractions, not concretions. High-level modules shouldn't depend on low-level details.

**When to query this standard:**
- Designing new classes → `pos_search_project(content_type="standards", query="how to design maintainable classes")`
- Code review feedback about coupling → `pos_search_project(content_type="standards", query="reducing code coupling")`
- Making code testable → `pos_search_project(content_type="standards", query="dependency injection pattern")`
- Class doing too many things → `pos_search_project(content_type="standards", query="single responsibility principle")`
- Adding features breaks existing code → `pos_search_project(content_type="standards", query="open closed principle")`
- Inheritance causing bugs → `pos_search_project(content_type="standards", query="liskov substitution")`
- Interface has unused methods → `pos_search_project(content_type="standards", query="interface segregation")`

**For complete guide with examples, continue reading below.**

---

## Questions This Answers

- "How do I design maintainable classes?"
- "What are the SOLID principles?"
- "How do I make my code more testable?"
- "When should I split a class into multiple classes?"
- "What is dependency injection and why use it?"
- "How do I reduce coupling in my codebase?"
- "What does open/closed principle mean?"
- "How do I use inheritance correctly?"
- "What are good class design best practices?"
- "Why is my class hard to test?"

---

## What are SOLID Principles?

SOLID is an acronym for five design principles that help create understandable, flexible, and maintainable object-oriented software.

**Created by:** Robert C. Martin (Uncle Bob) in the early 2000s  
**Applies to:** All object-oriented programming languages  
**Purpose:** Guide class design to minimize coupling, maximize cohesion, and support change

---

## S - How to Apply Single Responsibility Principle

**Definition:** A class should have one, and only one, reason to change.

**Translation:** Each class should do one thing and do it well.

### Why Single Responsibility Matters

- **Easier to understand** (focused responsibility)
- **Easier to test** (fewer dependencies)
- **Easier to maintain** (changes isolated)
- **Reduced coupling** (fewer connections between classes)

### How to Recognize SRP Violations

Ask yourself:
- Does this class do more than one thing?
- If I change the database, do I need to change this class?
- If I change the UI, do I need to change this class?
- If I change business logic, do I need to change this class?

If multiple answers are "yes", you're violating SRP.

### Example: Single Responsibility Violation

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        # Database logic here
        pass
    
    def send_email(self, message):
        # Email logic here
        pass
    
    def generate_report(self):
        # Reporting logic here
        pass
```

**Problems:**
- User class has 4 responsibilities: data model, persistence, communication, reporting
- Changes to database affect User class
- Changes to email system affect User class
- Changes to reporting affect User class
- Hard to test in isolation (need to mock database, email, reporting)

### Example: Correct Single Responsibility

```python
class User:
    """Data model only - single responsibility"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    """Persistence only - single responsibility"""
    def save(self, user):
        # Database logic here
        pass

class EmailService:
    """Communication only - single responsibility"""
    def send(self, recipient, message):
        # Email logic here
        pass

class ReportGenerator:
    """Reporting only - single responsibility"""
    def generate_user_report(self, user):
        # Reporting logic here
        pass
```

**Benefits:**
- Each class has one clear responsibility
- Changes to database only affect UserRepository
- Changes to email only affect EmailService
- Changes to reporting only affect ReportGenerator
- Easy to test each class in isolation
- Easy to replace implementations (swap MySQL for PostgreSQL)

---

## O - How to Apply Open/Closed Principle

**Definition:** Software entities should be open for extension, but closed for modification.

**Translation:** You should be able to add new functionality without changing existing code.

### Why Open/Closed Matters

- **Reduces risk** of breaking existing functionality
- **Encourages reusability** through inheritance and composition
- **Supports polymorphism** and plugin architectures
- **Protects stable code** from modification

### How to Recognize OCP Violations

Ask yourself:
- Do I need to modify existing classes when adding new features?
- Does adding a new type require changing conditional logic?
- Am I using long if/elif/else chains based on types?

If yes, you're likely violating OCP.

### Example: Open/Closed Violation

```python
class Shape:
    def __init__(self, type, width, height):
        self.type = type
        self.width = width
        self.height = height

class AreaCalculator:
    def calculate_area(self, shape):
        if shape.type == "rectangle":
            return shape.width * shape.height
        elif shape.type == "circle":
            return 3.14 * shape.width ** 2
        elif shape.type == "triangle":
            return 0.5 * shape.width * shape.height
        # Adding a new shape requires modifying this method!
```

**Problems:**
- Adding new shapes (hexagon, pentagon) requires modifying AreaCalculator
- Risk of breaking existing calculations when adding new shapes
- AreaCalculator knows too much about shape internals
- Violates open/closed principle (not open for extension, requires modification)

### Example: Correct Open/Closed Design

```python
class Shape:
    """Abstract base - defines contract"""
    def area(self):
        raise NotImplementedError("Subclasses must implement area()")

class Rectangle(Shape):
    """Concrete implementation - extends base"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    """Concrete implementation - extends base"""
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Triangle(Shape):
    """Concrete implementation - extends base"""
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    """Uses polymorphism - never needs modification"""
    def calculate_area(self, shape):
        return shape.area()  # Polymorphism!
```

**Benefits:**
- Adding new shapes (Hexagon, Pentagon) doesn't require changing AreaCalculator
- Each shape encapsulates its own area calculation logic
- Open for extension (add new shapes by creating new classes)
- Closed for modification (AreaCalculator remains unchanged)
- Easy to test (mock shapes for testing)

---

## L - How to Apply Liskov Substitution Principle

**Definition:** Subtypes must be substitutable for their base types without altering program correctness.

**Translation:** If class B inherits from class A, you should be able to use B anywhere you use A without breaking things.

### Why Liskov Substitution Matters

- **Ensures inheritance is used correctly** (not just for code reuse)
- **Prevents unexpected behavior** from subclasses
- **Maintains polymorphism contracts** (child honors parent's promises)
- **Supports reliable abstraction** (trust the interface)

### How to Recognize LSP Violations

Ask yourself:
- Does the subclass change method behavior in unexpected ways?
- Does the subclass throw exceptions the parent doesn't?
- Does the subclass refuse to implement parent methods?
- Can I swap subclass for parent without breaking code?

If any answers are "no" to the last question, you're violating LSP.

### Example: Liskov Substitution Violation

```python
class Bird:
    def fly(self):
        return "Flying high!"

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying!"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Breaks LSP!

# Code that uses birds
def make_bird_fly(bird: Bird):
    return bird.fly()  # Expects all birds to fly

# Works fine
make_bird_fly(Sparrow())  # "Sparrow flying!"

# Breaks!
make_bird_fly(Penguin())  # Exception! Violates LSP
```

**Problems:**
- Penguin inherits from Bird but can't fly
- Code expecting a Bird will break with Penguin
- Violates the contract that all Birds can fly()
- Subclass is NOT substitutable for base class

### Example: Correct Liskov Substitution

```python
class Bird:
    """Base class with general contract"""
    def move(self):
        raise NotImplementedError()

class FlyingBird(Bird):
    """Contract: can fly"""
    def move(self):
        return self.fly()
    
    def fly(self):
        raise NotImplementedError()

class Sparrow(FlyingBird):
    """Honors flying contract"""
    def fly(self):
        return "Sparrow flying!"

class Penguin(Bird):
    """Different contract: can swim"""
    def move(self):
        return self.swim()
    
    def swim(self):
        return "Penguin swimming!"

# Code uses general Bird contract
def make_bird_move(bird: Bird):
    return bird.move()  # All birds can move

# Both work correctly!
make_bird_move(Sparrow())  # "Sparrow flying!" (via fly)
make_bird_move(Penguin())  # "Penguin swimming!" (via swim)
```

**Benefits:**
- Penguin doesn't inherit `fly()` it can't implement
- All Birds can `move()`, but in different ways
- Subtypes are properly substitutable for base type
- No surprises - contracts are honored
- Code works correctly with any Bird subtype

---

## I - How to Apply Interface Segregation Principle

**Definition:** Clients should not be forced to depend on interfaces they don't use.

**Translation:** Don't create fat interfaces. Create small, focused interfaces.

### Why Interface Segregation Matters

- **Reduces coupling** (clients depend only on what they need)
- **Makes systems more flexible** (easier to swap implementations)
- **Easier to implement** (smaller contracts to fulfill)
- **Easier to test** (mock only relevant methods)

### How to Recognize ISP Violations

Ask yourself:
- Does the interface have methods not all implementers need?
- Do implementers have empty or stub methods?
- Does the interface combine multiple unrelated responsibilities?

If yes, you're violating ISP.

### Example: Interface Segregation Violation

```python
interface Worker:
    def work()
    def eat()
    def sleep()

class HumanWorker implements Worker:
    def work(self):
        # Work logic
        pass
    
    def eat(self):
        # Eating logic
        pass
    
    def sleep(self):
        # Sleeping logic
        pass

class RobotWorker implements Worker:
    def work(self):
        # Work logic
        pass
    
    def eat(self):
        pass  # Robots don't eat! Forced to implement anyway
    
    def sleep(self):
        pass  # Robots don't sleep! Forced to implement anyway
```

**Problems:**
- RobotWorker forced to implement methods it doesn't need (eat, sleep)
- Interface is too broad (combines unrelated responsibilities)
- Violates ISP (client forced to depend on unused methods)
- Confusing for maintainers (why do robots eat?)

### Example: Correct Interface Segregation

```python
interface Workable:
    """Small, focused interface"""
    def work()

interface Eatable:
    """Small, focused interface"""
    def eat()

interface Sleepable:
    """Small, focused interface"""
    def sleep()

class HumanWorker implements Workable, Eatable, Sleepable:
    """Implements all interfaces it needs"""
    def work(self):
        # Work logic
        pass
    
    def eat(self):
        # Eating logic
        pass
    
    def sleep(self):
        # Sleeping logic
        pass

class RobotWorker implements Workable:
    """Implements only what it needs"""
    def work(self):
        # Work logic
        pass
    # Only implements Workable! No eat/sleep
```

**Benefits:**
- RobotWorker only implements Workable (not forced to implement eat/sleep)
- Interfaces are small and focused (single responsibility)
- Easy to add new worker types (AutonomousRobot might only work, no maintenance)
- Clear contracts (if you implement Eatable, you can eat)

---

## D - How to Apply Dependency Inversion Principle

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Translation:** Depend on interfaces, not concrete implementations.

### Why Dependency Inversion Matters

- **Reduces coupling** (high-level logic independent of low-level details)
- **Makes code testable** (can mock dependencies easily)
- **Easier to swap implementations** (database, email service, etc.)
- **Supports plugin architectures** (inject different behaviors)

### How to Recognize DIP Violations

Ask yourself:
- Does my class instantiate its dependencies directly?
- Does my class depend on concrete classes instead of interfaces?
- Can I easily test this class in isolation?

If the answers are "yes", "yes", "no", you're violating DIP.

### Example: Dependency Inversion Violation

```python
class MySQLDatabase:
    def save(self, data):
        # MySQL-specific code
        pass

class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  # Depends on concrete class!
    
    def save_user(self, user):
        self.database.save(user)
```

**Problems:**
- UserService tightly coupled to MySQLDatabase
- Can't switch to PostgreSQL without changing UserService
- Hard to test (can't mock MySQLDatabase easily)
- High-level module (UserService) depends on low-level module (MySQLDatabase)

### Example: Correct Dependency Inversion

```python
interface Database:
    """Abstraction - defines contract"""
    def save(data)

class MySQLDatabase implements Database:
    """Low-level module - depends on abstraction"""
    def save(self, data):
        # MySQL-specific code
        pass

class PostgreSQLDatabase implements Database:
    """Low-level module - depends on abstraction"""
    def save(self, data):
        # PostgreSQL-specific code
        pass

class MockDatabase implements Database:
    """Test double - depends on abstraction"""
    def save(self, data):
        # In-memory storage for testing
        pass

class UserService:
    """High-level module - depends on abstraction"""
    def __init__(self, database: Database):  # Depends on interface!
        self.database = database
    
    def save_user(self, user):
        self.database.save(user)

# Usage - Production
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# Usage - Easy to swap!
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)

# Usage - Testing
mock_db = MockDatabase()
test_service = UserService(mock_db)
```

**Benefits:**
- UserService depends on Database interface, not concrete implementation
- Easy to swap database implementations (MySQL → PostgreSQL)
- Easy to test (inject mock database)
- High-level module (UserService) and low-level modules (MySQLDatabase, PostgreSQLDatabase) both depend on abstraction (Database)
- Dependency is "inverted" - both depend on interface, not on each other

---

## SOLID Together: Real-World Example

**Scenario:** Building a notification system that sends emails, SMS, and push notifications.

### Without SOLID (Bad)

```python
class NotificationService:
    def send_notification(self, user, message, type):
        if type == "email":
            # Email sending logic here
            smtp_connect()
            smtp_send(user.email, message)
        elif type == "sms":
            # SMS sending logic here
            twilio_connect()
            twilio_send(user.phone, message)
        elif type == "push":
            # Push notification logic here
            firebase_connect()
            firebase_send(user.device_token, message)
        
        # Save to database
        db_connect()
        db_save(user.id, message, type)
        
        # Log the notification
        log_to_file(f"Sent {type} to {user.id}")
```

**Problems:**
- ❌ Violates SRP (multiple responsibilities: sending, logging, persistence)
- ❌ Violates OCP (adding notification types requires modification)
- ❌ Violates DIP (depends on concrete implementations: smtp, twilio, firebase)
- ❌ Hard to test (tightly coupled to external services)
- ❌ Hard to maintain (changes to email affect entire class)

### With SOLID (Good)

```python
# Single Responsibility + Dependency Inversion
interface NotificationChannel:
    """Abstraction for sending notifications"""
    def send(recipient, message)

class EmailChannel implements NotificationChannel:
    """Single responsibility: email sending"""
    def send(self, recipient, message):
        # Email logic
        pass

class SMSChannel implements NotificationChannel:
    """Single responsibility: SMS sending"""
    def send(self, recipient, message):
        # SMS logic
        pass

class PushChannel implements NotificationChannel:
    """Single responsibility: push notifications"""
    def send(self, recipient, message):
        # Push logic
        pass

# Interface Segregation
interface NotificationLogger:
    """Focused interface: logging only"""
    def log(user_id, message, channel)

interface NotificationRepository:
    """Focused interface: persistence only"""
    def save(user_id, message, channel)

# Open/Closed + Liskov Substitution
class NotificationService:
    """High-level orchestration - depends on abstractions"""
    def __init__(
        self,
        channel: NotificationChannel,
        logger: NotificationLogger,
        repository: NotificationRepository
    ):
        self.channel = channel
        self.logger = logger
        self.repository = repository
    
    def send_notification(self, user, message):
        # Send via channel (polymorphism - works with any NotificationChannel)
        self.channel.send(user.contact_info, message)
        
        # Log the notification
        self.logger.log(user.id, message, self.channel.__class__.__name__)
        
        # Save to repository
        self.repository.save(user.id, message, self.channel.__class__.__name__)

# Usage - Production
email_service = NotificationService(
    EmailChannel(),
    FileLogger(),
    DatabaseRepository()
)

sms_service = NotificationService(
    SMSChannel(),
    FileLogger(),
    DatabaseRepository()
)

# Usage - Testing
test_service = NotificationService(
    MockChannel(),
    MockLogger(),
    MockRepository()
)
```

**Benefits:**
- ✅ **SRP**: Each class has single responsibility
- ✅ **OCP**: Easy to add new notification channels (just create new NotificationChannel implementation)
- ✅ **LSP**: Can substitute any NotificationChannel implementation
- ✅ **ISP**: Focused interfaces (NotificationLogger, NotificationRepository)
- ✅ **DIP**: Depends on abstractions (NotificationChannel, NotificationLogger, NotificationRepository)
- ✅ **Testable**: Easy to inject mocks for testing
- ✅ **Maintainable**: Changes isolated to specific classes

---

## When to Apply SOLID (Practical Guidance)

### ✅ Apply SOLID when:

- **Building systems that will evolve** over time
- **Code will be maintained by multiple people** (team size > 1)
- **Requirements are likely to change** (most production systems)
- **System needs to be testable** (unit tests, integration tests)
- **You're refactoring existing code** (improve maintainability)
- **Building libraries or frameworks** (used by multiple consumers)

### ⚠️ Consider pragmatism when:

- **Building prototypes or proof-of-concepts** (exploration phase)
- **System is very simple** (single responsibility, unlikely to change)
- **Over-engineering would add unnecessary complexity** (3-line class doesn't need abstraction)
- **Time constraints are critical** (but plan to refactor later)

**Balance:** Apply SOLID principles to reduce future maintenance costs, but don't over-engineer. Start simple, refactor to SOLID as complexity grows.

**Refactoring tip:** Add SOLID when you notice:
- Class doing multiple things → Apply SRP
- Adding features requires modifications → Apply OCP
- Inheritance causing bugs → Apply LSP
- Interface has unused methods → Apply ISP
- Hard to test due to dependencies → Apply DIP

---

## When to Query This Standard

### During Design Phase

```python
# Designing new features
pos_search_project(content_type="standards", query="how to design maintainable classes")
pos_search_project(content_type="standards", query="class design best practices")
pos_search_project(content_type="standards", query="dependency injection pattern")
```

### During Code Review

```python
# Reviewing code quality
pos_search_project(content_type="standards", query="reducing code coupling")
pos_search_project(content_type="standards", query="single responsibility principle")
pos_search_project(content_type="standards", query="interface segregation")
```

### During Refactoring

```python
# Improving existing code
pos_search_project(content_type="standards", query="open closed principle")
pos_search_project(content_type="standards", query="liskov substitution")
pos_search_project(content_type="standards", query="making code testable")
```

### During Testing

```python
# Making code testable
pos_search_project(content_type="standards", query="dependency inversion")
pos_search_project(content_type="standards", query="how to mock dependencies")
```

---

## Cross-References

### Related Architecture Standards

Query when designing systems:

```python
# For layered architecture
pos_search_project(content_type="standards", query="clean architecture hexagonal")

# For API design
pos_search_project(content_type="standards", query="API design best practices")

# For dependency management
pos_search_project(content_type="standards", query="dependency injection containers")

# For testing strategy
pos_search_project(content_type="standards", query="test pyramid testing levels")
```

**Related Standards:**
- [Clean Architecture](clean-architecture.md) - How to structure applications using SOLID
- [Design Patterns](design-patterns.md) - Common patterns that implement SOLID
- [Test-Driven Development](../testing/test-driven-development.md) - SOLID makes TDD easier
- [Production Code Checklist](../ai-safety/production-code-checklist.md) - Includes SOLID validation

### Language-Specific Implementations

This document covers universal concepts. For language-specific implementations:

```python
# Python-specific SOLID
pos_search_project(content_type="standards", query="python dependency injection decorators")
pos_search_project(content_type="standards", query="python abstract base classes protocols")

# Go-specific SOLID
pos_search_project(content_type="standards", query="go interfaces composition")

# Rust-specific SOLID  
pos_search_project(content_type="standards", query="rust traits generics")
```

**Language-Specific Standards:**
- Python: ABC, protocols, type hints, dependency injection
- Go: Interfaces, composition over inheritance, struct embedding
- Rust: Traits, generics, zero-cost abstractions
- TypeScript: Interfaces, decorators, dependency injection

---

## Common Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: God Class

```python
# ❌ BAD: Class does everything
class ApplicationManager:
    def handle_request(self): pass
    def save_to_database(self): pass
    def send_email(self): pass
    def log_event(self): pass
    def validate_input(self): pass
    def render_response(self): pass
```

**Fix:** Apply SRP - split into focused classes

### Anti-Pattern 2: Conditional Chains

```python
# ❌ BAD: Type checking with if/elif
if type == "email":
    send_email()
elif type == "sms":
    send_sms()
elif type == "push":
    send_push()
```

**Fix:** Apply OCP - use polymorphism

### Anti-Pattern 3: Concrete Dependencies

```python
# ❌ BAD: Depends on concrete class
class Service:
    def __init__(self):
        self.db = MySQLDatabase()  # Tight coupling!
```

**Fix:** Apply DIP - depend on interface

### Anti-Pattern 4: Fat Interfaces

```python
# ❌ BAD: Interface with many unrelated methods
interface Everything:
    def work()
    def eat()
    def sleep()
    def fly()
    def swim()
```

**Fix:** Apply ISP - create focused interfaces

---

**SOLID principles are timeless. They create flexible, maintainable code that evolves gracefully. Start with SRP (Single Responsibility), then apply others as needed. When in doubt, query this standard for guidance on specific scenarios.**
