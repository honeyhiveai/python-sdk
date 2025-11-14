# Implementation Template

**Purpose:** Template and examples for implementation.md content  
**Referenced by:** Phase 4 tasks (Implementation Guidance)

---

## Document Structure

implementation.md should follow this structure:

```markdown
# Implementation Approach

**Project:** {FEATURE_NAME}
**Date:** {CURRENT_DATE}

## 1. Implementation Philosophy

Core principles guiding development

## 2. Implementation Order

Phase sequence from tasks.md

## 3. Code Patterns

Recommended patterns with examples

## 4. Testing Strategy

Unit, integration, and E2E testing

## 5. Deployment

Deployment steps and procedures

## 6. Troubleshooting

Common issues and solutions
```

---

## Code Pattern Examples

### Repository Pattern

**Good:**
```python
class UserRepository:
    """Data access layer for users."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID."""
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute(query, (user_id,))
        return User.from_row(result) if result else None
    
    def create(self, user: User) -> User:
        """Create new user."""
        query = "INSERT INTO users (id, email, name) VALUES (%s, %s, %s)"
        self.db.execute(query, (user.id, user.email, user.name))
        return user
```

**Anti-Pattern:**
```python
# DON'T: Mix business logic with data access
def get_user(user_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    if user.is_premium:  # Business logic in data layer!
        user.benefits = calculate_benefits(user)
    return user
```

### Service Layer Pattern

**Good:**
```python
class UserService:
    """Business logic for user operations."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def register_user(self, email: str, name: str) -> User:
        """Register new user with validation."""
        # Business logic here
        if self.repository.get_by_email(email):
            raise DuplicateError("Email already registered")
        
        user = User(id=uuid4(), email=email, name=name)
        return self.repository.create(user)
```

### Error Handling Pattern

**Good:**
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise CustomException("Meaningful message") from e
except AnotherError as e:
    logger.warning(f"Minor issue: {e}")
    return fallback_value
```

**Anti-Pattern:**
```python
try:
    result = operation()
except:  # Too broad
    pass  # Silent failure - BAD
```

---

## Testing Examples

### Unit Test Pattern

```python
def test_user_registration():
    """Test user registration with valid data."""
    # Arrange
    repository = MockUserRepository()
    service = UserService(repository)
    
    # Act
    user = service.register_user("test@example.com", "Test User")
    
    # Assert
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id is not None

def test_duplicate_email_rejected():
    """Test duplicate email raises error."""
    repository = MockUserRepository(existing="test@example.com")
    service = UserService(repository)
    
    with pytest.raises(DuplicateError):
        service.register_user("test@example.com", "Another User")
```

### Integration Test Pattern

```python
def test_user_registration_e2e(client, db):
    """Test user registration end-to-end."""
    # Arrange
    payload = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    # Act
    response = client.post("/users", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
    # Verify database
    user = db.query_one("SELECT * FROM users WHERE email = %s", 
                        ("test@example.com",))
    assert user is not None
    assert user["name"] == "Test User"
```

---

## Deployment Checklist Example

```markdown
### Pre-Deployment Checklist

**Code Quality:**
- [ ] All tests passing (pytest)
- [ ] Linter clean (flake8, mypy)
- [ ] Coverage > 80%
- [ ] Code reviewed and approved

**Database:**
- [ ] Migrations created
- [ ] Migrations tested on staging
- [ ] Rollback script ready
- [ ] Backup completed

**Configuration:**
- [ ] Environment variables documented
- [ ] Secrets in secret manager (not in code)
- [ ] Feature flags configured
- [ ] Monitoring alerts configured

**Documentation:**
- [ ] API documentation updated
- [ ] README updated
- [ ] Changelog updated
- [ ] Runbook created
```

---

## Troubleshooting Pattern Example

```markdown
### Issue: Database Connection Timeout

**Symptoms:**
- Application fails to start
- Error: "connection timeout after 5s"
- Health check returning 503

**Cause:**
Incorrect DATABASE_URL or database not accessible

**Solution:**
1. Verify DATABASE_URL:
   ```bash
   echo $DATABASE_URL
   ```

2. Test connectivity:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. Check firewall rules:
   ```bash
   nc -zv {db-host} {db-port}
   ```

4. Verify database is running:
   ```bash
   docker ps | grep postgres
   # or
   systemctl status postgresql
   ```

**Prevention:**
- Add connection retry logic
- Configure health checks
- Monitor connection pool metrics
```

---

## Usage Notes

**For Task Authors:**
- Reference specific sections from this template
- Adapt examples to match technology stack
- Keep task files concise by pointing here for details

**For Workflow Users:**
- Use these patterns as starting points
- Adapt to project-specific conventions
- Add project-specific patterns to implementation.md