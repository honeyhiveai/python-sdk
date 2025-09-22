# Complex Function Templates

**🎯 Copy-paste ready templates for complex function generation with error handling**

## 🏗️ **Complex Function with Error Handling**

```python
def complex_function(
    data: Dict[str, Any],
    tracer: HoneyHiveTracer,
    *,
    timeout: Optional[float] = None,
    retry_count: int = 3
) -> Tuple[bool, Optional[str]]:
    """Process data with comprehensive error handling.
    
    :param data: Input data dictionary
    :type data: Dict[str, Any]
    :param tracer: HoneyHive tracer instance
    :type tracer: HoneyHiveTracer
    :param timeout: Optional timeout in seconds
    :type timeout: Optional[float]
    :param retry_count: Number of retry attempts
    :type retry_count: int
    :return: Tuple of (success, error_message)
    :rtype: Tuple[bool, Optional[str]]
    :raises TypeError: When data is not a dictionary
    
    **Example:**
    
    .. code-block:: python
    
        success, error = complex_function(
            {"key": "value"}, 
            tracer,
            timeout=30.0,
            retry_count=5
        )
        if success:
            print("Processing completed")
        else:
            print(f"Error: {error}")
    """
    # Type annotations for local variables
    processed_data: Dict[str, Any] = {}
    attempt: int = 0
    
    try:
        # Input validation
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
        
        # Main processing logic with retries
        for attempt in range(retry_count):
            try:
                processed_data = process_with_tracer(data, tracer, timeout=timeout)
                return True, None
                
            except TemporaryError as e:
                safe_log(tracer, "warning", f"Attempt {attempt + 1} failed: {e}")
                if attempt == retry_count - 1:
                    return False, f"All {retry_count} attempts failed"
                continue
                
    except TypeError as e:
        safe_log(tracer, "error", f"Type error in complex_function: {e}")
        return False, str(e)
        
    except Exception as e:
        safe_log(tracer, "debug", f"Unexpected error in complex_function: {e}")
        return False, "Internal processing error"
```

## 🔄 **Async Function Template**

```python
async def async_function(
    data: List[Dict[str, Any]],
    tracer: HoneyHiveTracer,
    *,
    batch_size: int = 100,
    concurrent_limit: int = 10
) -> AsyncGenerator[Dict[str, Any], None]:
    """Process data asynchronously with batching.
    
    :param data: List of data items to process
    :type data: List[Dict[str, Any]]
    :param tracer: HoneyHive tracer instance
    :type tracer: HoneyHiveTracer
    :param batch_size: Maximum items per batch
    :type batch_size: int
    :param concurrent_limit: Maximum concurrent operations
    :type concurrent_limit: int
    :return: Async generator yielding processed items
    :rtype: AsyncGenerator[Dict[str, Any], None]
    :raises ValueError: When data list is empty
    
    **Example:**
    
    .. code-block:: python
    
        async for result in async_function(data_list, tracer, batch_size=50):
            print(f"Processed: {result}")
    """
    if not data:
        raise ValueError("Data list cannot be empty")
    
    # Type annotations for local variables
    semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrent_limit)
    
    async def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            try:
                # Process individual item
                return await async_process_with_tracer(item, tracer)
            except Exception as e:
                safe_log(tracer, "warning", f"Failed to process item: {e}")
                return {"error": str(e)}
    
    # Process in batches
    for i in range(0, len(data), batch_size):
        batch: List[Dict[str, Any]] = data[i:i + batch_size]
        tasks = [process_item(item) for item in batch]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if not isinstance(result, Exception):
                    yield result
        except Exception as e:
            safe_log(tracer, "error", f"Batch processing failed: {e}")
```

## 📋 **Complex Function Checklist**

**When generating complex functions:**

- [ ] **Error handling**: Multiple exception types handled appropriately
- [ ] **Logging**: Uses safe_log utility for all logging
- [ ] **Type safety**: Complete type annotations for all variables
- [ ] **Graceful degradation**: Returns sensible defaults on errors
- [ ] **Resource management**: Proper cleanup and resource handling
- [ ] **Retry logic**: Appropriate retry strategies for transient failures
- [ ] **Performance**: Considers timeout and concurrency limits

---

**📝 Next**: [class-templates.md](class-templates.md) - Templates for class generation
