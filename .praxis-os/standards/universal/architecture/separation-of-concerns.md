# Separation of Concerns - Universal Architecture Principle

**Timeless principle for organizing code into distinct responsibilities.**

**Keywords for search**: separation of concerns, SoC, single responsibility, layered architecture, MVC, repository pattern, service layer, hexagonal architecture, modularity, code organization, maintainability

---

## 🚨 Quick Reference (TL;DR)

**Core Principle:** Each module/class/function should address a single concern, and concerns should not overlap.

**Coined by:** Edsger W. Dijkstra (1974)

**Common Concerns:**
- **Horizontal** (Cross-cutting): Logging, error handling, auth, caching, validation
- **Vertical** (Feature-specific): User management, order processing, payments

**Four Key Patterns:**
1. **MVC** (Model-View-Controller) - Separates data, presentation, and control
2. **Repository Pattern** - Separates business logic from data access
3. **Service Layer** - Separates workflow orchestration from business rules
4. **Hexagonal Architecture** - Separates core logic from external dependencies

**Benefits:**
- ✅ Easy to test (isolated concerns)
- ✅ Easy to maintain (change one concern, others unaffected)
- ✅ Easy to reuse (concerns are independent)
- ✅ Follows Single Responsibility Principle

**Quick Example:**
```python
# Without SoC (Bad) - Everything in one function
def handle_request(data):
    # Validation + business logic + database + API + response...
    # 50 lines mixing 5 concerns

# With SoC (Good) - Separate classes
validator.validate(data)
user = user_service.create_user(data)
return presenter.to_json(user)
```

---

## Questions This Answers

- "What is separation of concerns and why is it important?"
- "How to organize code into distinct responsibilities?"
- "What concerns should be separated in my application?"
- "How to implement MVC pattern?"
- "What is the repository pattern and when to use it?"
- "How to separate business logic from data access?"
- "What is hexagonal architecture (ports and adapters)?"
- "How to identify violation of separation of concerns?"
- "What is a God Object and how to fix it?"
- "How to apply layered architecture?"
- "How to make code easier to test and maintain?"
- "What's the difference between horizontal and vertical concerns?"

---

## What is Separation of Concerns?

Separation of Concerns (SoC) is the design principle of dividing a program into distinct sections, each addressing a separate concern.

**Coined by:** Edsger W. Dijkstra (1974)

**Key principle:** Each module/class/function should address a single concern, and concerns should not overlap.

---

## The Problem: Tangled Concerns

### Without SoC (Bad)

```
def handle_user_request(request_data):
    // Concern 1: Input validation
    if not request_data.get("email"):
        return {"error": "Email required"}, 400
    if "@" not in request_data["email"]:
        return {"error": "Invalid email"}, 400
    
    // Concern 2: Business logic
    user = User(
        email=request_data["email"],
        name=request_data.get("name", "")
    )
    if existing_user(user.email):
        return {"error": "Email exists"}, 409
    
    // Concern 3: Data persistence
    connection = database.connect("postgresql://...")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (email, name) VALUES (%s, %s)",
        (user.email, user.name)
    )
    connection.commit()
    connection.close()
    
    // Concern 4: External integration
    requests.post(
        "https://email-service.com/send",
        json={"to": user.email, "template": "welcome"}
    )
    
    // Concern 5: Response formatting
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }, 201
```

**Problems:**
- 5 concerns tangled in one function
- Hard to test (must mock database, API, etc.)
- Hard to reuse (validation logic locked in this function)
- Hard to maintain (change to database affects entire function)
- Violates Single Responsibility Principle

---

## The Solution: Separated Concerns

### With SoC (Good)

```
// Concern 1: Input validation (separate layer)
class UserValidator:
    def validate(self, data):
        if not data.get("email"):
            raise ValidationError("Email required")
        if "@" not in data["email"]:
            raise ValidationError("Invalid email format")
        return True

// Concern 2: Business logic (separate layer)
class UserService:
    def __init__(self, repository, email_service):
        self.repository = repository
        self.email_service = email_service
    
    def create_user(self, email, name):
        if self.repository.exists(email):
            raise DuplicateEmailError()
        
        user = User(email=email, name=name)
        self.repository.save(user)
        self.email_service.send_welcome(user.email)
        return user

// Concern 3: Data persistence (separate layer)
class UserRepository:
    def __init__(self, database):
        self.database = database
    
    def save(self, user):
        self.database.execute(
            "INSERT INTO users (email, name) VALUES (?, ?)",
            (user.email, user.name)
        )
    
    def exists(self, email):
        return self.database.exists("users", {"email": email})

// Concern 4: External integration (separate service)
class EmailService:
    def send_welcome(self, email):
        requests.post(
            "https://email-service.com/send",
            json={"to": email, "template": "welcome"}
        )

// Concern 5: Response formatting (separate layer)
class UserPresenter:
    def to_json(self, user):
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }

// Controller glues everything together
def handle_user_request(request_data):
    validator = UserValidator()
    validator.validate(request_data)
    
    user_service = UserService(user_repository, email_service)
    user = user_service.create_user(
        email=request_data["email"],
        name=request_data.get("name", "")
    )
    
    presenter = UserPresenter()
    return presenter.to_json(user), 201
```

**Benefits:**
- Each class has one concern
- Easy to test (mock dependencies)
- Easy to reuse (validation works anywhere)
- Easy to maintain (change database only affects repository)
- Follows Single Responsibility Principle

---

## What Types of Concerns Exist in Software?

### What Are Horizontal Concerns? (Cross-cutting)

```
Application
    ├── Logging
    ├── Error Handling
    ├── Authentication
    ├── Authorization
    ├── Caching
    ├── Rate Limiting
    ├── Monitoring
    └── Validation
```

**Characteristic:** Apply across entire application.

---

### What Are Vertical Concerns? (Feature-specific)

```
User Management Feature
    ├── User Creation
    ├── User Authentication
    ├── Profile Management
    └── Password Reset

Order Management Feature
    ├── Order Creation
    ├── Payment Processing
    ├── Inventory Management
    └── Shipping
```

**Characteristic:** Specific to business features.

---

## How to Apply Layered Architecture?

### What is Classic N-Tier Separation?

```
┌─────────────────────────────────┐
│   Presentation Layer            │  (UI, API endpoints, formatting)
├─────────────────────────────────┤
│   Business Logic Layer          │  (Domain rules, workflows)
├─────────────────────────────────┤
│   Data Access Layer             │  (Database, external APIs)
├─────────────────────────────────┤
│   Infrastructure Layer          │  (Logging, caching, config)
└─────────────────────────────────┘
```

### Rules:
- **Each layer only depends on layer below**
- **No skipping layers** (Presentation can't call Data Access directly)
- **Each layer has one concern**

---

## What Separation Patterns Should I Use?

### Pattern 1: How to Use MVC (Model-View-Controller)

**Concerns:**
- **Model:** Data and business logic
- **View:** Presentation and UI
- **Controller:** Request handling and coordination

```
// Model (business logic + data)
class User:
    def __init__(self, email, name):
        self.email = email
        self.name = name
    
    def change_email(self, new_email):
        if "@" not in new_email:
            raise ValueError("Invalid email")
        self.email = new_email

// View (presentation)
class UserView:
    def render(self, user):
        return f"""
        <div class="user">
            <h2>{user.name}</h2>
            <p>{user.email}</p>
        </div>
        """

// Controller (coordination)
class UserController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def show_user(self, user_id):
        user = self.model.find(user_id)
        return self.view.render(user)
```

---

### Pattern 2: How to Use Repository Pattern (Data Access Separation)

**Concern:** Separate business logic from data persistence.

```
// Business logic (doesn't know about database)
class OrderService:
    def __init__(self, order_repository):
        self.repository = order_repository
    
    def place_order(self, user, items):
        order = Order(user=user, items=items)
        order.calculate_total()
        self.repository.save(order)
        return order

// Data access (knows about database)
class OrderRepository:
    def __init__(self, database):
        self.database = database
    
    def save(self, order):
        self.database.execute(
            "INSERT INTO orders (...) VALUES (...)",
            order.to_dict()
        )
    
    def find(self, order_id):
        data = self.database.query("SELECT * FROM orders WHERE id = ?", order_id)
        return Order.from_dict(data)
```

**Benefits:**
- Change database (PostgreSQL → MongoDB) without changing business logic
- Test business logic without database (mock repository)

---

### Pattern 3: How to Use Service Layer Pattern

**Concern:** Separate workflow orchestration from business logic.

```
// Domain model (business rules)
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
    
    def can_purchase(self, quantity):
        return self.stock >= quantity
    
    def reduce_stock(self, quantity):
        if not self.can_purchase(quantity):
            raise InsufficientStockError()
        self.stock -= quantity

// Service layer (workflow orchestration)
class PurchaseService:
    def __init__(self, product_repo, payment_service, email_service):
        self.product_repo = product_repo
        self.payment_service = payment_service
        self.email_service = email_service
    
    def purchase_product(self, user, product_id, quantity):
        // Orchestrates workflow across multiple concerns
        product = self.product_repo.find(product_id)
        
        if not product.can_purchase(quantity):
            raise InsufficientStockError()
        
        total = product.price * quantity
        self.payment_service.charge(user, total)
        
        product.reduce_stock(quantity)
        self.product_repo.save(product)
        
        self.email_service.send_receipt(user, product, quantity, total)
```

---

### Pattern 4: How to Use Hexagonal Architecture (Ports & Adapters)

**Concern:** Separate core business logic from external dependencies.

```
       ┌─────────────────────────┐
       │   External Systems      │
       │  (Database, APIs, UI)   │
       └───────────┬─────────────┘
                   │ Adapters
       ┌───────────▼─────────────┐
       │   Ports (Interfaces)    │
       └───────────┬─────────────┘
                   │
       ┌───────────▼─────────────┐
       │   Core Business Logic   │
       │   (Domain Model)        │
       └─────────────────────────┘
```

**Example:**

```
// Port (interface in core)
interface UserRepository:
    def save(user)
    def find(user_id)

// Core business logic (knows about port, not adapter)
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def register_user(self, email, name):
        user = User(email=email, name=name)
        self.repository.save(user)
        return user

// Adapter (implements port, knows about database)
class PostgreSQLUserRepository implements UserRepository:
    def save(self, user):
        psql_connection.execute(...)
    
    def find(self, user_id):
        data = psql_connection.query(...)
        return User.from_dict(data)

// Can easily swap to different database
class MongoDBUserRepository implements UserRepository:
    def save(self, user):
        mongo_collection.insert_one(...)
    
    def find(self, user_id):
        data = mongo_collection.find_one(...)
        return User.from_dict(data)
```

**Benefits:**
- Business logic independent of infrastructure
- Easy to test (mock ports)
- Easy to swap implementations (different adapters)

---

## How to Identify Separation of Concerns Violations?

### Violation 1: God Object (Everything in One Class)

**Problem:** One class that does everything.

```
class UserManager:
    // Validation
    def validate_email(self, email): ...
    def validate_password(self, password): ...
    
    // Business logic
    def register_user(self, data): ...
    def authenticate(self, email, password): ...
    
    // Data access
    def save_to_database(self, user): ...
    def query_database(self, sql): ...
    
    // Email
    def send_welcome_email(self, user): ...
    def send_password_reset(self, user): ...
    
    // Logging
    def log(self, message): ...
```

**Fix:** Split into separate classes by concern.

---

### Violation 2: Feature Envy (Accessing Another Class's Data Excessively)

**Problem:** Class accessing another class's data excessively.

```
class OrderPrinter:
    def print_order(self, order):
        // Accessing order internals excessively
        total = sum(item.price * item.quantity for item in order.items)
        tax = total * 0.1
        shipping = 5.0 if total < 50 else 0.0
        grand_total = total + tax + shipping
        
        print(f"Total: {grand_total}")
```

**Fix:** Move calculation to Order class.

```
class Order:
    def calculate_total(self):
        subtotal = sum(item.price * item.quantity for item in self.items)
        tax = subtotal * 0.1
        shipping = 5.0 if subtotal < 50 else 0.0
        return subtotal + tax + shipping

class OrderPrinter:
    def print_order(self, order):
        print(f"Total: {order.calculate_total()}")
```

---

### Violation 3: Inappropriate Intimacy (Classes Too Tightly Coupled)

**Problem:** Two classes too tightly coupled.

```
class User:
    def __init__(self):
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)
        order.user = self  // Tight coupling!
        order.update_status("pending")  // Knows too much about Order!
```

**Fix:** Use proper interfaces.

```
class User:
    def __init__(self):
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)

class Order:
    def assign_to_user(self, user):
        self.user = user
        self.update_status("pending")
```

---

## How Does Separation of Concerns Improve Testing?

### Without Separation (Hard to Test)

```
def process_payment(card_number, amount):
    // Mixed concerns make testing hard
    if len(card_number) != 16:
        return False
    
    connection = database.connect()  // Need real database
    user = connection.query("SELECT * FROM users WHERE card = ?", card_number)
    
    response = requests.post("https://payment-api.com/charge", ...)  // Need real API
    
    if response.ok:
        connection.execute("INSERT INTO transactions ...")
        return True
    return False
```

---

### With Separation (Easy to Test)

```
class CardValidator:
    def is_valid(self, card_number):
        return len(card_number) == 16

class PaymentGateway:
    def charge(self, card_number, amount):
        response = requests.post(...)
        return response.ok

class PaymentService:
    def __init__(self, validator, gateway, transaction_repo):
        self.validator = validator
        self.gateway = gateway
        self.transaction_repo = transaction_repo
    
    def process_payment(self, card_number, amount):
        if not self.validator.is_valid(card_number):
            return False
        
        if self.gateway.charge(card_number, amount):
            self.transaction_repo.record(card_number, amount)
            return True
        return False

// Test
def test_payment_success():
    mock_validator = MockValidator(returns=True)
    mock_gateway = MockGateway(returns=True)
    mock_repo = MockRepository()
    
    service = PaymentService(mock_validator, mock_gateway, mock_repo)
    result = service.process_payment("1234567890123456", 100.0)
    
    assert result == True
    assert mock_repo.recorded == True
```

---

## What Are Separation of Concerns Best Practices?

### 1. One Concern Per Module/Class/Function

```
// GOOD: One concern
class EmailValidator:
    def is_valid(self, email): ...

// BAD: Multiple concerns
class EmailHandler:
    def validate(self, email): ...
    def send(self, to, subject, body): ...
    def parse_address(self, email): ...
```

### 2. Hide Implementation Details

```
// GOOD: Public interface, private implementation
class UserRepository:
    def save(self, user):
        self._execute_sql(...)  // Private
    
    def _execute_sql(self, query):  // Private
        ...

// BAD: Exposes implementation
class UserRepository:
    def save(self, user):
        self.execute_sql(...)  // Public!
```

### 3. Depend on Abstractions

```
// GOOD: Depends on interface
class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

// BAD: Depends on concrete class
class OrderService:
    def __init__(self, stripe_api: StripeAPI):
        self.stripe_api = stripe_api
```

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-architecture.md` (Python: modules, packages, `__init__.py`)
- See `.praxis-os/standards/development/java-architecture.md` (Java: packages, access modifiers)
- See `.praxis-os/standards/development/go-architecture.md` (Go: packages, internal visibility)
- Etc.

---

## When to Query This Standard

This standard is most valuable when:

1. **Designing New Features**
   - Situation: Planning how to organize code for new functionality
   - Query: `pos_search_project(content_type="standards", query="how to organize code by concern")`

2. **Refactoring Tangled Code**
   - Situation: Code has multiple responsibilities mixed together
   - Query: `pos_search_project(content_type="standards", query="separation of concerns pattern")`

3. **Choosing Architecture Pattern**
   - Situation: Deciding on MVC vs Repository vs Service Layer vs Hexagonal
   - Query: `pos_search_project(content_type="standards", query="what separation pattern to use")`

4. **Improving Testability**
   - Situation: Hard to test because concerns are mixed
   - Query: `pos_search_project(content_type="standards", query="how to make code testable")`

5. **Code Review Feedback**
   - Situation: Reviewer says "this violates separation of concerns"
   - Query: `pos_search_project(content_type="standards", query="separation of concerns violations")`

6. **Identifying God Objects**
   - Situation: Class doing too many things
   - Query: `pos_search_project(content_type="standards", query="God Object anti-pattern")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Organize code | `pos_search_project(content_type="standards", query="how to organize code by concern")` |
| Refactor tangled code | `pos_search_project(content_type="standards", query="separation of concerns refactoring")` |
| Choose pattern | `pos_search_project(content_type="standards", query="MVC vs repository pattern")` |
| Improve testability | `pos_search_project(content_type="standards", query="make code testable")` |
| Fix God Object | `pos_search_project(content_type="standards", query="God Object anti-pattern")` |

---

## Cross-References and Related Standards

**Architecture Standards:**
- `standards/architecture/solid-principles.md` - SRP (Single Responsibility) is core to SoC
  → `pos_search_project(content_type="standards", query="single responsibility principle")`
- `standards/architecture/dependency-injection.md` - DI enables separation
  → `pos_search_project(content_type="standards", query="dependency injection pattern")`

**Testing Standards:**
- `standards/testing/test-doubles.md` - Separated concerns are easier to mock
  → `pos_search_project(content_type="standards", query="how to use test doubles")`
- `standards/testing/integration-testing.md` - Testing separated layers
  → `pos_search_project(content_type="standards", query="integration testing patterns")`

**Production Code:**
- `standards/ai-safety/production-code-checklist.md` - Validates separation
  → `pos_search_project(content_type="standards", query="production code checklist")`

**Query workflow for applying SoC:**
1. **Learn Principle**: `pos_search_project(content_type="standards", query="separation of concerns")` → Read this standard
2. **Learn SOLID**: `pos_search_project(content_type="standards", query="single responsibility principle")` → Understand SRP
3. **Choose Pattern**: `pos_search_project(content_type="standards", query="MVC vs repository pattern")` → Select approach
4. **Implement**: Apply chosen pattern to your code
5. **Test**: `pos_search_project(content_type="standards", query="how to test with mocks")` → Write tests for each concern
6. **Review**: `pos_search_project(content_type="standards", query="separation of concerns violations")` → Validate approach

---

**Separation of Concerns is fundamental to maintainable code. Each module should address one concern. Concerns should not overlap. This makes code easier to understand, test, and modify.**
