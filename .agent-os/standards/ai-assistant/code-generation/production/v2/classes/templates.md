# Class Templates

**🎯 Copy-paste ready templates for class generation**

## 🏛️ **Pydantic v2 Model Template**

```python
from pydantic import BaseModel, Field

class ProcessingResult(BaseModel):
    """Result of data processing operation.
    
    **Example:**
    
    .. code-block:: python
    
        result = ProcessingResult(
            success_count=10,
            error_count=2,
            results=[{"id": 1}, {"id": 2}]
        )
        print(f"Success rate: {result.get_success_rate()}")
    """
    success_count: int = Field(..., description="Number of successfully processed items")
    error_count: int = Field(..., description="Number of items that failed processing")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Processed results")
    
    def get_success_rate(self) -> float:
        """Calculate success rate as percentage.
        
        :return: Success rate between 0.0 and 1.0
        :rtype: float
        """
        total_count: int = self.success_count + self.error_count
        if total_count == 0:
            return 0.0
        return self.success_count / total_count
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary.
        
        :return: Summary dictionary with counts and rate
        :rtype: Dict[str, Any]
        """
        return {
            "success_count": self.success_count,
            "error_count": self.error_count,
            "total_count": self.success_count + self.error_count,
            "success_rate": self.get_success_rate(),
            "result_count": len(self.results)
        }
```

## 🔧 **Service Class Template**

```python
class DataProcessor:
    """Process data with HoneyHive tracing integration.
    
    **Example:**
    
    .. code-block:: python
    
        processor = DataProcessor(tracer, config={"batch_size": 100})
        result = processor.process_batch([{"id": 1}, {"id": 2}])
        print(f"Processed {result.success_count} items")
    """
    
    def __init__(
        self, 
        tracer: HoneyHiveTracer, 
        *, 
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the data processor.
        
        :param tracer: HoneyHive tracer instance
        :type tracer: HoneyHiveTracer
        :param config: Optional configuration dictionary
        :type config: Optional[Dict[str, Any]]
        """
        self.tracer: HoneyHiveTracer = tracer
        self.config: Dict[str, Any] = config or {}
        self._batch_size: int = self.config.get("batch_size", 100)
    
    def process_batch(
        self,
        items: List[Dict[str, Any]],
        *,
        parallel: bool = False
    ) -> ProcessingResult:
        """Process a batch of items with tracing.
        
        :param items: List of items to process
        :type items: List[Dict[str, Any]]
        :param parallel: Whether to process in parallel
        :type parallel: bool
        :return: Processing results with statistics
        :rtype: ProcessingResult
        :raises ValueError: When items list is empty
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        
        # Type annotations for local variables
        results: List[Dict[str, Any]] = []
        success_count: int = 0
        error_count: int = 0
        
        try:
            with self.tracer.trace("batch_processing") as span:
                span.set_attribute("batch_size", len(items))
                span.set_attribute("parallel", parallel)
                
                for item in items:
                    try:
                        processed_item = self._process_single_item(item)
                        results.append(processed_item)
                        success_count += 1
                    except Exception as e:
                        safe_log(self.tracer, "warning", f"Failed to process item: {e}")
                        error_count += 1
                
                return ProcessingResult(
                    success_count=success_count,
                    error_count=error_count,
                    results=results
                )
                
        except Exception as e:
            safe_log(self.tracer, "error", f"Batch processing failed: {e}")
            return ProcessingResult(
                success_count=0,
                error_count=len(items),
                results=[]
            )
    
    def _process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item.
        
        :param item: Item to process
        :type item: Dict[str, Any]
        :return: Processed item
        :rtype: Dict[str, Any]
        """
        # Implementation here
        return {"processed": item}
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.
        
        :return: Configuration dictionary
        :rtype: Dict[str, Any]
        """
        return self.config.copy()
```

## 📋 **Class Generation Checklist**

**When generating classes:**

- [ ] **Clear purpose**: Class has single, well-defined responsibility
- [ ] **Complete docstring**: Class-level documentation with examples
- [ ] **Type annotations**: All attributes and methods fully typed
- [ ] **Initialization**: Proper `__init__` method with validation
- [ ] **Method documentation**: All public methods have complete docstrings
- [ ] **Error handling**: Appropriate exception handling in methods
- [ ] **Configuration**: Flexible configuration through constructor parameters

---

**📝 Next**: [docstring-templates.md](docstring-templates.md) - Templates for documentation
