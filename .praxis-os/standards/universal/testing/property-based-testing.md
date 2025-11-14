# Property-Based Testing - Universal Testing Strategy

**Timeless approach to finding edge cases through generative testing.**

**Keywords for search**: property-based testing, PBT, QuickCheck, Hypothesis, generative testing, property testing, test properties, invariants, round-trip property, idempotence, shrinking, fuzzing

---

## 🚨 Quick Reference (TL;DR)

**Definition:** Specify properties that should hold for all inputs → framework generates hundreds/thousands of random test cases automatically.

**Invented by:** QuickCheck (Haskell, 1999) by Koen Claessen and John Hughes

**Core Principle:** Test universal properties, not specific examples.

**Five Types of Properties:**
1. **Invariants** - Things always true (e.g., sort preserves length)
2. **Idempotence** - Doing twice = doing once (e.g., sort(sort(x)) == sort(x))
3. **Round-Trip** - Encode then decode = original (e.g., parse(serialize(x)) == x)
4. **Commutativity** - Order doesn't matter (e.g., a + b == b + a)
5. **Oracle** - Compare with known-good implementation

**Key Benefits:**
- ✅ Finds edge cases automatically
- ✅ Generates hundreds of tests from one property
- ✅ Shrinks failing inputs to minimal case
- ✅ Catches bugs example-based tests miss

**When to Use:**
- Complex algorithms (sorting, parsing, compression)
- APIs with invariants (data structures, serialization)
- Mathematical properties (commutativity, associativity)

**Frameworks by Language:**
- Python: Hypothesis
- JavaScript: fast-check
- Java: jqwik
- Rust: proptest
- Go: gopter

---

## Questions This Answers

- "What is property-based testing?"
- "How does property-based testing differ from example-based testing?"
- "When should I use property-based testing?"
- "What are properties in property-based testing?"
- "How to write properties for my code?"
- "What is shrinking in property testing?"
- "What frameworks exist for property-based testing?"
- "How to test sorting algorithms with properties?"
- "What is QuickCheck?"
- "How to generate test data automatically?"
- "What properties should I test for my API?"
- "How to find edge cases automatically?"

---

## What is Property-Based Testing?

Property-based testing (PBT) is a testing approach where you specify properties that should hold true for all inputs, and a testing framework generates hundreds/thousands of random test cases.

**Invented by:** QuickCheck (Haskell, 1999) by Koen Claessen and John Hughes

**Key principle:** Instead of testing specific examples, test universal properties.

---

## Example-Based vs Property-Based

### Example-Based Testing (Traditional)

```
def test_reverse():
    assert reverse([1, 2, 3]) == [3, 2, 1]
    assert reverse([]) == []
    assert reverse([1]) == [1]
    assert reverse([1, 1, 1]) == [1, 1, 1]
```

**Problems:**
- Manual selection of test cases
- May miss edge cases
- Only tests specific examples

---

### Property-Based Testing

```
@property_test
def test_reverse(data: List[int]):
    """
    Property: Reversing twice should return original
    """
    original = data
    reversed_once = reverse(data)
    reversed_twice = reverse(reversed_once)
    assert reversed_twice == original

// Framework generates 100 random test cases:
// test_reverse([])
// test_reverse([1])
// test_reverse([1, 2])
// test_reverse([-5, 0, 100, -200])
// test_reverse([1] * 1000)
// ...
```

**Benefits:**
- Generates many test cases automatically
- Finds edge cases you didn't think of
- Tests universal properties, not just examples

---

## What Types of Properties Exist?

### Property 1: Invariants

**Definition:** Things that should always be true.

```
@property_test
def test_sort_preserves_length(data: List[int]):
    """Property: Sorting doesn't change length"""
    assert len(sort(data)) == len(data)

@property_test
def test_absolute_value_non_negative(x: int):
    """Property: Absolute value is always >= 0"""
    assert abs(x) >= 0

@property_test
def test_set_no_duplicates(items: List[int]):
    """Property: Set contains no duplicates"""
    s = set(items)
    assert len(s) == len(list(s))  // No duplicates
```

---

### Property 2: Idempotence

**Definition:** Applying operation multiple times has same effect as once.

```
@property_test
def test_sort_idempotent(data: List[int]):
    """Property: Sorting twice = sorting once"""
    sorted_once = sort(data)
    sorted_twice = sort(sorted_once)
    assert sorted_once == sorted_twice

@property_test
def test_absolute_idempotent(x: int):
    """Property: abs(abs(x)) = abs(x)"""
    assert abs(abs(x)) == abs(x)

@property_test
def test_set_idempotent(items: List[int]):
    """Property: set(set(items)) = set(items)"""
    assert set(set(items)) == set(items)
```

---

### Property 3: Inverse Functions

**Definition:** One function undoes another.

```
@property_test
def test_encode_decode_inverse(data: bytes):
    """Property: decode(encode(x)) = x"""
    encoded = base64_encode(data)
    decoded = base64_decode(encoded)
    assert decoded == data

@property_test
def test_encrypt_decrypt_inverse(plaintext: str, key: str):
    """Property: decrypt(encrypt(x, key), key) = x"""
    ciphertext = encrypt(plaintext, key)
    decrypted = decrypt(ciphertext, key)
    assert decrypted == plaintext

@property_test
def test_serialize_deserialize_inverse(obj: User):
    """Property: deserialize(serialize(x)) = x"""
    json_str = serialize(obj)
    deserialized = deserialize(json_str)
    assert deserialized == obj
```

---

### Property 4: Commutativity

**Definition:** Order of operations doesn't matter.

```
@property_test
def test_addition_commutative(a: int, b: int):
    """Property: a + b = b + a"""
    assert a + b == b + a

@property_test
def test_set_union_commutative(set_a: Set[int], set_b: Set[int]):
    """Property: A ∪ B = B ∪ A"""
    assert set_a.union(set_b) == set_b.union(set_a)

@property_test
def test_min_commutative(a: int, b: int):
    """Property: min(a, b) = min(b, a)"""
    assert min(a, b) == min(b, a)
```

---

### Property 5: Associativity

**Definition:** Grouping of operations doesn't matter.

```
@property_test
def test_addition_associative(a: int, b: int, c: int):
    """Property: (a + b) + c = a + (b + c)"""
    assert (a + b) + c == a + (b + c)

@property_test
def test_string_concat_associative(a: str, b: str, c: str):
    """Property: (a + b) + c = a + (b + c)"""
    assert (a + b) + c == a + (b + c)

@property_test
def test_list_concat_associative(a: List, b: List, c: List):
    """Property: (a + b) + c = a + (b + c)"""
    assert (a + b) + c == a + (b + c)
```

---

### Property 6: Identity Elements

**Definition:** Operation with identity returns original.

```
@property_test
def test_addition_identity(x: int):
    """Property: x + 0 = x"""
    assert x + 0 == x

@property_test
def test_multiplication_identity(x: int):
    """Property: x * 1 = x"""
    assert x * 1 == x

@property_test
def test_set_union_identity(s: Set[int]):
    """Property: s ∪ ∅ = s"""
    assert s.union(set()) == s
```

---

### Property 7: Postconditions

**Definition:** Expected state after operation.

```
@property_test
def test_sort_ascending(data: List[int]):
    """Property: Sorted list is in ascending order"""
    sorted_data = sort(data)
    for i in range(len(sorted_data) - 1):
        assert sorted_data[i] <= sorted_data[i + 1]

@property_test
def test_filter_removes_items(data: List[int], predicate: Callable):
    """Property: Filtered list contains only items matching predicate"""
    filtered = [x for x in data if predicate(x)]
    for item in filtered:
        assert predicate(item)

@property_test
def test_dedup_no_consecutive_dupes(data: List[int]):
    """Property: Deduplicated list has no consecutive duplicates"""
    deduped = deduplicate(data)
    for i in range(len(deduped) - 1):
        assert deduped[i] != deduped[i + 1]
```

---

## How to Generate Test Data? (Generators)

### Built-in Generators

```
// Integers
@property_test
def test_with_integers(x: int):
    // Framework generates: -1000, 0, 1, 100, -5, etc.
    pass

// Positive integers
@property_test
def test_with_positive_integers(x: int):
    assume(x > 0)  // Filter generated data
    assert x > 0

// Lists
@property_test
def test_with_lists(data: List[int]):
    // Generates: [], [1], [1,2,3], [-5, 0, 100], etc.
    pass

// Strings
@property_test
def test_with_strings(s: str):
    // Generates: "", "a", "hello", "123", etc.
    pass
```

---

### Custom Generators

```
// Generate even numbers
@property_test
def test_with_even_numbers(x: int):
    assume(x % 2 == 0)
    assert x % 2 == 0

// Generate valid emails
@custom_generator
def email_generator():
    name = text(min_size=1, max_size=20, alphabet=string.ascii_lowercase)
    domain = sampled_from(["gmail.com", "yahoo.com", "example.com"])
    return f"{name}@{domain}"

@property_test
def test_with_emails(email: email_generator):
    assert "@" in email

// Generate users
@custom_generator
def user_generator():
    return User(
        name=text(min_size=1, max_size=50),
        age=integers(min_value=0, max_value=120),
        email=email_generator()
    )

@property_test
def test_with_users(user: user_generator):
    assert 0 <= user.age <= 120
```

---

## How Does Shrinking Work? (Finding Minimal Failing Case)

**Concept:** When test fails, framework reduces input to smallest failing example.

### Example

```
@property_test
def test_list_operation(data: List[int]):
    """This test has a bug when list contains 0"""
    result = [1 / x for x in data]  // Division by zero!
    assert len(result) == len(data)

// Initial failure (generated input)
test_list_operation([1, 5, -3, 0, 10, 22, -100])  // FAILS

// Shrinking process:
test_list_operation([1, 5, -3, 0, 10, 22])  // Still fails
test_list_operation([1, 5, -3, 0])          // Still fails
test_list_operation([0, 1])                 // Still fails
test_list_operation([0])                    // Still fails!

// Minimal failing case found: [0]
```

**Benefit:** You see the simplest case that triggers the bug, making debugging easier.

---

## What Common Property Patterns Exist?

### Pattern 1: Round-Trip Testing

**Concept:** Serialize → Deserialize should give original.

```
@property_test
def test_json_round_trip(data: Dict):
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    assert parsed == data

@property_test
def test_protobuf_round_trip(message: MyProtoMessage):
    serialized = message.SerializeToString()
    deserialized = MyProtoMessage()
    deserialized.ParseFromString(serialized)
    assert deserialized == message
```

---

### Pattern 2: Test Against Oracle

**Concept:** Compare your implementation against known-correct reference.

```
@property_test
def test_custom_sort_matches_builtin(data: List[int]):
    """Custom sort should match Python's built-in sort"""
    custom_sorted = custom_sort(data)
    builtin_sorted = sorted(data)
    assert custom_sorted == builtin_sorted

@property_test
def test_fast_fibonacci_matches_naive(n: int):
    assume(0 <= n <= 30)
    assert fast_fibonacci(n) == naive_fibonacci(n)
```

---

### Pattern 3: Metamorphic Testing

**Concept:** Test relationships between different inputs.

```
@property_test
def test_search_substring(haystack: str, needle: str):
    """If needle found in haystack, haystack + haystack should find it too"""
    if needle in haystack:
        assert needle in (haystack + haystack)

@property_test
def test_sort_with_duplicates(data: List[int], x: int):
    """Adding duplicate shouldn't change sorted order"""
    sorted_original = sorted(data)
    sorted_with_dup = sorted(data + [x])
    
    // Remove one instance of x from result
    if x in sorted_with_dup:
        sorted_with_dup.remove(x)
    
    assert sorted_original == sorted_with_dup or x not in data
```

---

### Pattern 4: Invariant Testing

**Concept:** Properties that hold before and after operation.

```
@property_test
def test_balance_preserved_after_transfer(account_a: Account, account_b: Account, amount: Money):
    assume(amount > 0)
    assume(account_a.balance >= amount)
    
    initial_total = account_a.balance + account_b.balance
    
    transfer(account_a, account_b, amount)
    
    final_total = account_a.balance + account_b.balance
    
    assert initial_total == final_total  // Total unchanged
```

---

## When to Use Property-Based Testing

### ✅ Good Use Cases

**1. Parsing and Serialization**
```
@property_test
def test_url_parsing(url: str):
    assume(is_valid_url(url))
    parsed = parse_url(url)
    reconstructed = construct_url(parsed)
    assert normalize_url(reconstructed) == normalize_url(url)
```

**2. Data Structure Invariants**
```
@property_test
def test_bst_invariant(operations: List[Operation]):
    tree = BinarySearchTree()
    for op in operations:
        tree.apply(op)
    assert tree.is_valid_bst()  // Left < node < right
```

**3. Mathematical Functions**
```
@property_test
def test_distance_metric(a: Point, b: Point, c: Point):
    """Triangle inequality: d(a,c) <= d(a,b) + d(b,c)"""
    assert distance(a, c) <= distance(a, b) + distance(b, c)
```

**4. Compression/Encryption**
```
@property_test
def test_compression_lossless(data: bytes):
    compressed = compress(data)
    decompressed = decompress(compressed)
    assert decompressed == data
```

---

### ❌ Poor Use Cases

**1. Highly Specific Business Logic**
```
// BAD: Too specific for property testing
def test_vip_discount():
    """VIP customers get 15% off on Tuesdays after 5pm"""
    // Better suited for example-based test
```

**2. UI Behavior**
```
// BAD: UI interactions don't have universal properties
def test_button_click():
    """Button should change color when clicked"""
    // Better suited for UI test
```

**3. External Integrations**
```
// BAD: Can't generate random API calls
def test_stripe_api():
    """Charge customer via Stripe"""
    // Better suited for integration test
```

---

## What Tools and Frameworks Are Available?

### Python
- **Hypothesis:** Most popular, powerful
- **pytest-quickcheck:** QuickCheck port

### JavaScript/TypeScript
- **fast-check:** Feature-rich
- **jsverify:** QuickCheck port

### Java
- **jqwik:** Modern, JUnit 5
- **QuickTheories:** Fluent API

### Scala
- **ScalaCheck:** Native QuickCheck port

### Haskell
- **QuickCheck:** Original

### Go
- **gopter:** Property-based testing
- **rapid:** Hypothesis-inspired

### Rust
- **proptest:** Popular
- **quickcheck:** QuickCheck port

---

## What Are Property-Based Testing Best Practices?

### 1. Start Simple

```
// Start with obvious properties
@property_test
def test_reverse_length(data: List):
    assert len(reverse(data)) == len(data)

// Then add more sophisticated properties
@property_test
def test_reverse_reverse_identity(data: List):
    assert reverse(reverse(data)) == data
```

### 2. Use Assumptions to Filter

```
@property_test
def test_division(a: int, b: int):
    assume(b != 0)  // Filter out division by zero
    result = a / b
    assert result * b == a  // Check inverse
```

### 3. Combine with Example Tests

```
// Property test for general cases
@property_test
def test_sort_general(data: List[int]):
    sorted_data = sort(data)
    assert is_sorted(sorted_data)

// Example test for specific edge cases
def test_sort_empty():
    assert sort([]) == []

def test_sort_single():
    assert sort([1]) == [1]
```

### 4. Test Properties, Not Implementation

```
// GOOD: Tests property (behavior)
@property_test
def test_cache_returns_same_value(key: str, value: Any):
    cache.set(key, value)
    assert cache.get(key) == value

// BAD: Tests implementation details
@property_test
def test_cache_uses_dict(key: str, value: Any):
    assert isinstance(cache._storage, dict)  // Implementation detail!
```

---

## How to Debug Failed Properties?

### 1. Examine Minimal Case

```
test_list_operation([0])  // Framework shrunk to this

// Now debug with simplest failing input
def test_list_operation(data):
    result = [1 / x for x in data]  // Ah! Division by zero
```

### 2. Add Logging

```
@property_test
def test_complex_property(x: int, y: int):
    print(f"Testing with x={x}, y={y}")
    result = complex_operation(x, y)
    print(f"Result: {result}")
    assert result > 0
```

### 3. Reproduce with Example Test

```
// Failed property test
@property_test
def test_sort(data: List[int]):
    assert is_sorted(sort(data))

// Failed with: data = [5, 3, 5, 1]

// Create example test to debug
def test_sort_specific_case():
    data = [5, 3, 5, 1]
    result = sort(data)
    assert result == [1, 3, 5, 5]  // Can step through in debugger
```

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-testing.md` (Python: Hypothesis)
- See `.praxis-os/standards/development/js-testing.md` (JavaScript: fast-check)
- See `.praxis-os/standards/development/java-testing.md` (Java: jqwik)
- Etc.

---

## When to Query This Standard

This standard is most valuable when:

1. **Testing Complex Algorithms**
   - Situation: Writing tests for sorting, parsing, compression
   - Query: `pos_search_project(content_type="standards", query="property-based testing algorithms")`

2. **Finding Edge Cases**
   - Situation: Want to find bugs example-based tests miss
   - Query: `pos_search_project(content_type="standards", query="property-based testing edge cases")`

3. **Testing API Invariants**
   - Situation: API has properties that should always hold
   - Query: `pos_search_project(content_type="standards", query="what properties to test")`

4. **Learning Property-Based Testing**
   - Situation: Never used PBT before, want to understand
   - Query: `pos_search_project(content_type="standards", query="what is property-based testing")`

5. **Debugging Shrinking Issues**
   - Situation: Property test failing, need to understand shrinking
   - Query: `pos_search_project(content_type="standards", query="shrinking property testing")`

6. **Choosing Test Framework**
   - Situation: Want to add PBT to project
   - Query: `pos_search_project(content_type="standards", query="property-based testing frameworks")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Learn PBT | `pos_search_project(content_type="standards", query="what is property-based testing")` |
| Write properties | `pos_search_project(content_type="standards", query="types of properties PBT")` |
| Generate test data | `pos_search_project(content_type="standards", query="generators property testing")` |
| Debug failures | `pos_search_project(content_type="standards", query="shrinking property testing")` |
| Common patterns | `pos_search_project(content_type="standards", query="round-trip property testing")` |
| Choose framework | `pos_search_project(content_type="standards", query="Hypothesis vs QuickCheck")` |

---

## Cross-References and Related Standards

**Testing Standards:**
- `standards/testing/test-pyramid.md` - Where PBT fits in test strategy
  → `pos_search_project(content_type="standards", query="test pyramid structure")`
- `standards/testing/test-doubles.md` - May need mocks for property tests
  → `pos_search_project(content_type="standards", query="how to use test doubles")`
- `standards/testing/integration-testing.md` - PBT complements integration tests
  → `pos_search_project(content_type="standards", query="integration testing patterns")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Test coverage requirements
  → `pos_search_project(content_type="standards", query="production code checklist")`

**Query workflow for adding property-based testing:**
1. **Learn Concept**: `pos_search_project(content_type="standards", query="what is property-based testing")` → Understand approach
2. **Identify Properties**: `pos_search_project(content_type="standards", query="types of properties")` → Find invariants, round-trips
3. **Choose Framework**: `pos_search_project(content_type="standards", query="property testing frameworks")` → Select Hypothesis/fast-check/jqwik
4. **Write Tests**: `pos_search_project(content_type="standards", query="generators property testing")` → Generate test data
5. **Debug**: `pos_search_project(content_type="standards", query="shrinking property testing")` → Understand minimal failures
6. **Refine**: `pos_search_project(content_type="standards", query="property testing best practices")` → Improve properties

---

**Property-based testing is a powerful complement to example-based testing. It finds edge cases you didn't think of and ensures your code works for all inputs, not just the examples you manually selected. Start with simple properties and build up.**
