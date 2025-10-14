# SOLID Principles - Universal Object-Oriented Design

**Timeless design principles for maintainable, flexible object-oriented code.**

## What are SOLID Principles?

SOLID is an acronym for five design principles that help create understandable, flexible, and maintainable object-oriented software.

**Created by:** Robert C. Martin (Uncle Bob) in the early 2000s  
**Applies to:** All object-oriented programming languages

---

## S - Single Responsibility Principle (SRP)

**Definition:** A class should have one, and only one, reason to change.

**Translation:** Each class should do one thing and do it well.

### Why It Matters
- Easier to understand (focused responsibility)
- Easier to test (fewer dependencies)
- Easier to maintain (changes isolated)
- Reduced coupling

### Example: Violation

```
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
- User class has 3 responsibilities: data, persistence, communication, reporting
- Changes to database affect User class
- Changes to email system affect User class
- Hard to test in isolation

### Example: Correct

```
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        # Database logic here
        pass

class EmailService:
    def send(self, recipient, message):
        # Email logic here
        pass

class ReportGenerator:
    def generate_user_report(self, user):
        # Reporting logic here
        pass
```

**Benefits:**
- Each class has one responsibility
- Changes to database only affect UserRepository
- Easy to test each class in isolation

---

## O - Open/Closed Principle (OCP)

**Definition:** Software entities should be open for extension, but closed for modification.

**Translation:** You should be able to add new functionality without changing existing code.

### Why It Matters
- Reduces risk of breaking existing functionality
- Encourages reusability
- Supports polymorphism

### Example: Violation

```
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
- Adding new shapes requires modifying AreaCalculator
- Risk of breaking existing calculations
- Violates open/closed principle

### Example: Correct

```
class Shape:
    def area(self):
        raise NotImplementedError("Subclasses must implement area()")

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate_area(self, shape):
        return shape.area()  // Polymorphism!
```

**Benefits:**
- Adding new shapes doesn't require changing AreaCalculator
- Each shape encapsulates its own area calculation
- Open for extension (add new shapes), closed for modification (AreaCalculator unchanged)

---

## L - Liskov Substitution Principle (LSP)

**Definition:** Subtypes must be substitutable for their base types without altering program correctness.

**Translation:** If class B inherits from class A, you should be able to use B anywhere you use A without breaking things.

### Why It Matters
- Ensures inheritance is used correctly
- Prevents unexpected behavior
- Maintains polymorphism contracts

### Example: Violation

```
class Bird:
    def fly(self):
        return "Flying high!"

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying!"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  // Breaks LSP!
```

**Problems:**
- Penguin inherits from Bird but can't fly
- Code expecting a Bird will break with Penguin
- Violates the contract that all Birds can fly

### Example: Correct

```
class Bird:
    def move(self):
        raise NotImplementedError()

class FlyingBird(Bird):
    def move(self):
        return self.fly()
    
    def fly(self):
        raise NotImplementedError()

class Sparrow(FlyingBird):
    def fly(self):
        return "Sparrow flying!"

class Penguin(Bird):
    def move(self):
        return self.swim()
    
    def swim(self):
        return "Penguin swimming!"
```

**Benefits:**
- Penguin doesn't inherit `fly()` it can't implement
- All Birds can `move()`, but in different ways
- Subtypes are properly substitutable

---

## I - Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use.

**Translation:** Don't create fat interfaces. Create small, focused interfaces.

### Why It Matters
- Reduces coupling
- Makes systems more flexible
- Easier to implement and test

### Example: Violation

```
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
        pass  // Robots don't eat! Forced to implement anyway
    
    def sleep(self):
        pass  // Robots don't sleep! Forced to implement anyway
```

**Problems:**
- RobotWorker forced to implement methods it doesn't need
- Interface is too broad
- Violates ISP

### Example: Correct

```
interface Workable:
    def work()

interface Eatable:
    def eat()

interface Sleepable:
    def sleep()

class HumanWorker implements Workable, Eatable, Sleepable:
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
    def work(self):
        # Work logic
        pass
    # Only implements what it needs!
```

**Benefits:**
- RobotWorker only implements Workable
- Interfaces are small and focused
- Easy to add new worker types

---

## D - Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Translation:** Depend on interfaces, not concrete implementations.

### Why It Matters
- Reduces coupling
- Makes code testable (can mock dependencies)
- Easier to swap implementations

### Example: Violation

```
class MySQLDatabase:
    def save(self, data):
        # MySQL-specific code
        pass

class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  // Depends on concrete class!
    
    def save_user(self, user):
        self.database.save(user)
```

**Problems:**
- UserService tightly coupled to MySQLDatabase
- Can't switch to PostgreSQL without changing UserService
- Hard to test (can't mock MySQLDatabase easily)

### Example: Correct

```
interface Database:
    def save(data)

class MySQLDatabase implements Database:
    def save(self, data):
        # MySQL-specific code
        pass

class PostgreSQLDatabase implements Database:
    def save(self, data):
        # PostgreSQL-specific code
        pass

class UserService:
    def __init__(self, database: Database):  // Depends on interface!
        self.database = database
    
    def save_user(self, user):
        self.database.save(user)

# Usage
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# Easy to swap!
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)
```

**Benefits:**
- UserService depends on Database interface, not concrete implementation
- Easy to swap database implementations
- Easy to test (inject mock database)

---

## SOLID Together: Real-World Example

**Scenario:** Building a notification system

### Without SOLID (Bad)

```
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
- Violates SRP (multiple responsibilities)
- Violates OCP (adding notification types requires modification)
- Violates DIP (depends on concrete implementations)

### With SOLID (Good)

```
// Single Responsibility + Dependency Inversion
interface NotificationChannel:
    def send(recipient, message)

class EmailChannel implements NotificationChannel:
    def send(self, recipient, message):
        # Email logic
        pass

class SMSChannel implements NotificationChannel:
    def send(self, recipient, message):
        # SMS logic
        pass

class PushChannel implements NotificationChannel:
    def send(self, recipient, message):
        # Push logic
        pass

// Interface Segregation
interface NotificationLogger:
    def log(user_id, message, channel)

interface NotificationRepository:
    def save(user_id, message, channel)

// Open/Closed + Liskov Substitution
class NotificationService:
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
        // Send via channel (polymorphism)
        self.channel.send(user.contact_info, message)
        
        // Log the notification
        self.logger.log(user.id, message, self.channel.__class__.__name__)
        
        // Save to repository
        self.repository.save(user.id, message, self.channel.__class__.__name__)

// Usage
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
```

**Benefits:**
- Each class has single responsibility (SRP)
- Easy to add new notification channels (OCP)
- Can substitute any NotificationChannel (LSP)
- Focused interfaces (ISP)
- Depends on abstractions (DIP)

---

## When to Apply SOLID

### ✅ Apply SOLID when:
- Building systems that will evolve
- Code will be maintained by multiple people
- Requirements are likely to change
- System needs to be testable

### ⚠️ Consider pragmatism when:
- Building prototypes or proof-of-concepts
- System is very simple (single responsibility)
- Over-engineering would add unnecessary complexity

**Balance:** Apply SOLID principles, but don't over-engineer. Start simple, refactor to SOLID as complexity grows.

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-architecture.md` (Python: ABC, protocols, type hints)
- See `.agent-os/standards/development/go-architecture.md` (Go: interfaces, composition)
- See `.agent-os/standards/development/rust-architecture.md` (Rust: traits, generics)
- Etc.

---

**SOLID principles are timeless. They create flexible, maintainable code. Start with SRP (Single Responsibility), then apply others as needed.**
