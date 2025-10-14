# Security Patterns - Universal Security Practice

**Timeless patterns for writing secure code.**

## Core Principle

**"Security is not a feature - it's a requirement."**

Security must be built in from the start, not added later.

**Key principle:** Assume all input is malicious until proven otherwise.

---

## The OWASP Top 10 (Universal Threats)

### 1. Injection

**Problem:** Untrusted data sent to interpreter as part of command or query.

```
// ❌ BAD: SQL Injection
query = "SELECT * FROM users WHERE id = " + user_input
database.execute(query)

// If user_input = "1 OR 1=1", returns ALL users!

// ✅ GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = ?"
database.execute(query, [user_input])
```

**Prevention:**
- Use parameterized queries (prepared statements)
- Use ORMs that handle escaping
- Validate and sanitize all input
- Never construct queries with string concatenation

---

### 2. Broken Authentication

**Problem:** Weak authentication or session management.

```
// ❌ BAD: Storing passwords in plain text
database.save(user.email, user.password)

// ✅ GOOD: Hash passwords with salt
hashed = secure_hash(user.password, salt=random_salt())
database.save(user.email, hashed)
```

**Prevention:**
- Hash passwords (bcrypt, Argon2, scrypt)
- Use strong session management
- Implement multi-factor authentication
- Rate-limit login attempts
- Secure password reset flows

---

### 3. Sensitive Data Exposure

**Problem:** Sensitive data not properly protected.

```
// ❌ BAD: Logging sensitive data
log(f"User {email} logged in with password {password}")

// ✅ GOOD: Never log sensitive data
log(f"User {email} logged in")
```

**Prevention:**
- Encrypt sensitive data at rest
- Use TLS for data in transit
- Never log passwords, tokens, API keys
- Minimize data retention
- Use environment variables for secrets

**See:** `universal/standards/ai-safety/credential-file-protection.md`

---

### 4. XML External Entities (XXE)

**Problem:** Parsing untrusted XML with external entities enabled.

```
// ❌ BAD: XXE vulnerable
parser = XMLParser(resolve_entities=True)
data = parser.parse(user_provided_xml)

// ✅ GOOD: Disable external entities
parser = XMLParser(resolve_entities=False)
data = parser.parse(user_provided_xml)
```

**Prevention:**
- Disable external entity processing in XML parsers
- Use simpler data formats (JSON) when possible
- Validate XML against schema

---

### 5. Broken Access Control

**Problem:** Users can access resources they shouldn't.

```
// ❌ BAD: No authorization check
function get_user(user_id):
    return database.query("SELECT * FROM users WHERE id = ?", user_id)

// Any user can access any other user's data!

// ✅ GOOD: Authorization check
function get_user(user_id, current_user):
    if current_user.id != user_id and not current_user.is_admin:
        raise PermissionDenied("Cannot access other user's data")
    return database.query("SELECT * FROM users WHERE id = ?", user_id)
```

**Prevention:**
- Implement proper authorization checks
- Use role-based access control (RBAC)
- Deny by default, allow explicitly
- Test authorization in automated tests

---

### 6. Security Misconfiguration

**Problem:** Insecure default configurations, verbose errors.

```
// ❌ BAD: Exposing stack traces to users
try:
    dangerous_operation()
except Exception as e:
    return f"Error: {e}\n{stack_trace}"  // Reveals internal structure

// ✅ GOOD: Generic error to user, detailed log internally
try:
    dangerous_operation()
except Exception as e:
    log_error(f"Operation failed: {e}\n{stack_trace}")
    return "An error occurred. Please try again."
```

**Prevention:**
- Use secure defaults
- Disable debug mode in production
- Remove default accounts
- Keep software updated
- Minimize attack surface (disable unused features)

---

### 7. Cross-Site Scripting (XSS)

**Problem:** Untrusted data included in web page without proper escaping.

```
// ❌ BAD: XSS vulnerable
html = f"<div>Welcome, {user_name}</div>"

// If user_name = "<script>alert('XSS')</script>", executes!

// ✅ GOOD: Escape HTML
html = f"<div>Welcome, {escape_html(user_name)}</div>"
```

**Prevention:**
- Escape all user-provided data in HTML
- Use Content Security Policy (CSP)
- Use templating engines with auto-escaping
- Sanitize HTML if user input must contain HTML

---

### 8. Insecure Deserialization

**Problem:** Deserializing untrusted data can lead to code execution.

```
// ❌ BAD: Deserializing untrusted data
data = deserialize(user_provided_data)  // Can execute arbitrary code!

// ✅ GOOD: Use safe formats
data = json_parse(user_provided_data)  // JSON is safe
```

**Prevention:**
- Avoid deserializing untrusted data
- Use safe formats (JSON, not pickle/marshal)
- Validate deserialized objects
- Implement integrity checks (HMAC)

---

### 9. Using Components with Known Vulnerabilities

**Problem:** Using outdated libraries with security flaws.

**Prevention:**
- Keep dependencies updated
- Monitor security advisories
- Use automated vulnerability scanning
- Pin versions with known security
- Audit dependencies regularly

---

### 10. Insufficient Logging & Monitoring

**Problem:** Attacks not detected or investigated.

```
// ✅ GOOD: Log security events
log_security_event(
    event="failed_login",
    user=email,
    ip=request.ip,
    timestamp=now()
)

// ✅ GOOD: Alert on suspicious patterns
if failed_login_count > 5:
    alert_security_team(f"Multiple failed logins for {email}")
```

**Prevention:**
- Log all authentication events
- Log authorization failures
- Monitor for suspicious patterns
- Set up alerts for anomalies
- Retain logs securely

---

## Input Validation Patterns

### Pattern 1: Allowlist Validation

**Concept:** Only accept known-good input.

```
// ❌ BAD: Blocklist (trying to block bad input)
if "<script>" not in user_input and "DROP TABLE" not in user_input:
    process(user_input)  // Endless cat and mouse

// ✅ GOOD: Allowlist (only allow known-good input)
if matches_pattern(user_input, "^[a-zA-Z0-9_]+$"):
    process(user_input)
else:
    raise ValidationError("Invalid input format")
```

---

### Pattern 2: Length Validation

```
// ❌ BAD: No length check
function create_user(username):
    database.save(username)  // What if username is 1MB?

// ✅ GOOD: Length validation
function create_user(username):
    if len(username) < 3 or len(username) > 50:
        raise ValidationError("Username must be 3-50 characters")
    database.save(username)
```

---

### Pattern 3: Type Validation

```
// ❌ BAD: Assuming type
function get_user(user_id):
    return database.query("SELECT * FROM users WHERE id = ?", user_id)

// What if user_id = "1 OR 1=1"?

// ✅ GOOD: Enforce type
function get_user(user_id: Integer):
    if not isinstance(user_id, Integer):
        raise TypeError("user_id must be an integer")
    return database.query("SELECT * FROM users WHERE id = ?", user_id)
```

---

## Authentication Patterns

### Pattern 1: Secure Password Storage

```
// ❌ BAD: Plain text or weak hashing
password_hash = md5(password)  // Weak!

// ✅ GOOD: Strong hashing with salt
password_hash = argon2_hash(
    password,
    salt=random_salt(),
    iterations=4,
    memory=64MB
)
```

**Best hashing algorithms (2025):**
1. Argon2 (winner of Password Hashing Competition)
2. bcrypt
3. scrypt

**Never use:** MD5, SHA-1, plain SHA-256 (too fast, vulnerable to brute force)

---

### Pattern 2: Rate Limiting

```
// ✅ GOOD: Rate limit login attempts
function login(email, password):
    attempt_count = get_recent_attempts(email)
    if attempt_count >= 5:
        raise TooManyAttempts("Too many failed logins. Try again in 15 minutes.")
    
    if verify_password(email, password):
        reset_attempts(email)
        return generate_session_token()
    else:
        increment_attempts(email)
        raise InvalidCredentials("Invalid email or password")
```

---

### Pattern 3: Session Management

```
// ✅ GOOD: Secure session tokens
session_token = cryptographically_random_bytes(32)
session_expiry = now() + 1_hour

store_session(
    token=session_token,
    user_id=user.id,
    expiry=session_expiry,
    secure=True,  // Only sent over HTTPS
    httponly=True,  // Not accessible to JavaScript
    samesite="Strict"  // CSRF protection
)
```

---

## Authorization Patterns

### Pattern 1: Role-Based Access Control (RBAC)

```
// ✅ GOOD: Check permissions
function delete_user(user_id, current_user):
    if not current_user.has_permission("delete_user"):
        raise PermissionDenied("You don't have permission to delete users")
    
    if not current_user.has_role("admin"):
        raise PermissionDenied("Only admins can delete users")
    
    database.delete("users", user_id)
```

---

### Pattern 2: Object-Level Authorization

```
// ❌ BAD: Only checking if user is authenticated
function update_order(order_id, new_status, current_user):
    if not current_user:
        raise NotAuthenticated()
    
    database.update("orders", order_id, {"status": new_status})
    // Any authenticated user can update any order!

// ✅ GOOD: Check if user owns the resource
function update_order(order_id, new_status, current_user):
    order = database.get("orders", order_id)
    
    if order.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("You can only update your own orders")
    
    database.update("orders", order_id, {"status": new_status})
```

---

## Cryptography Patterns

### Pattern 1: Use Standard Libraries

```
// ❌ BAD: Rolling your own crypto
function encrypt(data, key):
    // Custom encryption algorithm
    return custom_cipher(data, key)  // Probably broken!

// ✅ GOOD: Use standard library
function encrypt(data, key):
    cipher = AES_256_GCM(key)
    return cipher.encrypt(data)
```

**Rule:** Never implement your own cryptography. Use vetted libraries.

---

### Pattern 2: Secure Random Numbers

```
// ❌ BAD: Predictable random
token = random(0, 999999)  // Predictable!

// ✅ GOOD: Cryptographically secure random
token = cryptographically_secure_random_bytes(32)
```

---

### Pattern 3: Key Management

```
// ❌ BAD: Hardcoded keys
encryption_key = "my_secret_key_12345"

// ✅ GOOD: Keys from environment
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ConfigurationError("ENCRYPTION_KEY not set")
```

---

## Common Security Anti-Patterns

### Anti-Pattern 1: Security by Obscurity

❌ Relying on secrecy of implementation.

```
// ❌ BAD: Hidden admin endpoint
@app.route("/secret_admin_panel_xyz123")
def admin_panel():
    # No authentication check!
    return render_admin_page()

// ✅ GOOD: Proper authentication
@app.route("/admin")
@require_authentication
@require_role("admin")
def admin_panel():
    return render_admin_page()
```

---

### Anti-Pattern 2: Client-Side Security

❌ Trusting client-side validation.

```
// ❌ BAD: Only client-side validation
// JavaScript: if (is_admin) { show_admin_button() }

// ✅ GOOD: Server-side authorization
@app.route("/admin/delete_user")
@require_role("admin")
def delete_user(user_id):
    # Server enforces authorization
```

**Rule:** Always validate and authorize on the server.

---

### Anti-Pattern 3: Insufficient Entropy

❌ Using weak random values for security.

```
// ❌ BAD: Weak session token
session_id = timestamp + user_id  // Predictable!

// ✅ GOOD: High-entropy token
session_id = cryptographically_secure_random_bytes(32)
```

---

## Security Testing

### Test 1: Authentication Bypass

```
test_authentication_required():
    response = client.get("/admin/users")
    assert response.status_code == 401  // Must require authentication
```

---

### Test 2: Authorization Bypass

```
test_authorization_required():
    regular_user_token = login("regular@example.com")
    response = client.delete(
        "/admin/users/123",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 403  // Must check authorization
```

---

### Test 3: SQL Injection

```
test_sql_injection_protection():
    malicious_input = "1 OR 1=1"
    response = client.get(f"/users/{malicious_input}")
    # Should not return all users
    assert response.json().length == 0 or response.status_code == 400
```

---

## Security Checklist

**Before deploying:**

- [ ] **Authentication:** Strong password hashing (Argon2/bcrypt)
- [ ] **Authorization:** Proper access control checks
- [ ] **Input validation:** Allowlist validation, length checks
- [ ] **SQL injection:** Parameterized queries
- [ ] **XSS:** HTML escaping, CSP
- [ ] **CSRF:** CSRF tokens, SameSite cookies
- [ ] **Secrets:** No hardcoded credentials
- [ ] **HTTPS:** All traffic encrypted
- [ ] **Dependencies:** Up-to-date, no known vulnerabilities
- [ ] **Logging:** Security events logged
- [ ] **Rate limiting:** Login, API endpoints
- [ ] **Error messages:** Generic to users, detailed in logs

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-security.md`
- See `.agent-os/standards/development/go-security.md`
- See `.agent-os/standards/development/rust-security.md`
- Etc.

---

**Security is not optional. Assume all input is malicious. Validate everything. Use standard cryptography. Keep dependencies updated. Security must be built in from the start.**
