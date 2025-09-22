# Phase 7: Performance Analysis

**🎯 Measure Test Performance and Resource Usage**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Performance Analysis Prerequisites
- [ ] Quality assessment completed with evidence ✅/❌
- [ ] Test execution successful ✅/❌
- [ ] Phase 7.3 progress table updated ✅/❌

## 🛑 **PERFORMANCE ANALYSIS EXECUTION**

🛑 EXECUTE-NOW: All performance analysis commands in sequence

### **Execution Time Analysis**
```bash
# MANDATORY: Execute all commands below - no skipping allowed
echo "=== PERFORMANCE ANALYSIS ===

# Detailed test timing
echo "--- Test Execution Times ---"
pytest tests/unit/test_tracer_instrumentation_initialization.py --durations=0 -v

# Multiple runs for consistency
echo "--- Performance Consistency ---"
for i in {1..3}; do
    echo "Run $i:"
    time pytest tests/unit/test_tracer_instrumentation_initialization.py --tb=no -q
done
```

### **Resource Usage Analysis**
```python
# Monitor memory and CPU during test execution
import psutil
import subprocess

def analyze_test_performance():
    process = subprocess.Popen(['pytest', 'tests/unit/test_tracer_instrumentation_initialization.py', '-v'])
    
    max_memory = 0
    cpu_samples = []
    
    while process.poll() is None:
        try:
            proc = psutil.Process(process.pid)
            memory = proc.memory_info().rss / 1024 / 1024  # MB
            cpu = proc.cpu_percent()
            max_memory = max(max_memory, memory)
            cpu_samples.append(cpu)
        except psutil.NoSuchProcess:
            break
    
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    print(f"Max memory: {max_memory:.1f} MB, Avg CPU: {avg_cpu:.1f}%")
    return max_memory, avg_cpu, process.returncode

max_mem, avg_cpu, exit_code = analyze_test_performance()
```

### **Test Efficiency Analysis**
```python
# Calculate test efficiency metrics
import subprocess
import re

def calculate_test_efficiency():
    # Get test count
    result = subprocess.run(['pytest', 'tests/unit/test_tracer_instrumentation_initialization.py', '--collect-only', '-q'], 
                          capture_output=True, text=True)
    test_count_match = re.search(r'(\d+) tests? collected', result.stdout)
    test_count = int(test_count_match.group(1)) if test_count_match else 0
    
    # Get execution time  
    timed_result = subprocess.run(['time', 'pytest', 'tests/unit/test_tracer_instrumentation_initialization.py', '--tb=no', '-q'], 
                                capture_output=True, text=True)
    time_match = re.search(r'(\d+\.\d+)s', timed_result.stderr)
    execution_time = float(time_match.group(1)) if time_match else 0.0
    
    tests_per_second = test_count / execution_time if execution_time > 0 else 0
    print(f"Tests: {test_count}, Time: {execution_time:.2f}s, Rate: {tests_per_second:.1f}/s")
    return test_count, execution_time, tests_per_second

test_count, exec_time, efficiency = calculate_test_efficiency()
```

## 📊 **EVIDENCE REQUIRED**
- **Max execution time**: [SECONDS]
- **Average execution time**: [SECONDS]
- **Memory usage**: [MB]
- **CPU usage**: [PERCENTAGE]
- **Tests per second**: [NUMBER]
- **Command output**: Paste actual performance results

## 🚨 **VALIDATION GATE**
- [ ] Execution times measured
- [ ] Resource usage analyzed
- [ ] Performance consistency checked
- [ ] Efficiency metrics calculated

**Next**: Task 7.5 Evidence Collection Framework
