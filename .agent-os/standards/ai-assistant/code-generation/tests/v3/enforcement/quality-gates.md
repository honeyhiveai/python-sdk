# Quality Gates - Automated Framework Checkpoints

## 🚨 **CRITICAL: AUTOMATED QUALITY ENFORCEMENT**

🛑 VALIDATE-GATE: Quality Gates Entry Requirements
- [ ] Quality regression understanding confirmed ✅/❌
- [ ] V2 failure analysis reviewed (22% pass rate) ✅/❌
- [ ] Automated enforcement necessity acknowledged ✅/❌

🚨 FRAMEWORK-VIOLATION: If attempting to bypass quality gates

**Purpose**: Automated quality gates to prevent framework completion without achieving quality targets  
**Archive Success**: Manual quality checks maintained standards  
**V2 Failure**: No automated gates allowed 22% pass rate completion  
**V3 Enhancement**: Automated gates with script validation prevent quality failures  

---

## 🛑 **QUALITY GATE ARCHITECTURE EXECUTION**

⚠️ MUST-READ: All quality gates are mandatory checkpoints - no bypassing allowed

### **GATE 1: PHASE COMPLETION GATES**

**Purpose**: Ensure each phase is completely finished before proceeding
```python
def validate_phase_completion(phase_num, evidence):
    """Validate phase completion with evidence."""
    
    required_evidence = {
        1: ["function_count", "attribute_list", "signature_analysis"],
        2: ["logging_calls", "mock_strategy", "conditional_patterns"],
        3: ["dependency_count", "mock_plan", "path_strategy"],
        4: ["usage_patterns", "parameter_combinations", "error_scenarios"],
        5: ["coverage_target", "branch_analysis", "edge_cases"],
        6: ["import_validation", "signature_verification", "readiness_check"],
        7: ["metrics_collected", "quality_assessment", "path_validation"],
        8: ["automated_validation", "exit_code_0", "quality_targets_met"]
    }
    
    if phase_num not in required_evidence:
        return False, f"Unknown phase: {phase_num}"
    
    required = required_evidence[phase_num]
    missing = [item for item in required if item not in evidence]
    
    if missing:
        return False, f"Missing evidence: {missing}"
    
    return True, "Phase completion validated"
```

### **GATE 2: ANALYSIS DEPTH GATES**

**Purpose**: Ensure deep analysis is performed, not surface-level shortcuts
```python
def validate_analysis_depth(phase_num, commands_executed, analysis_results):
    """Validate analysis depth meets framework requirements."""
    
    depth_requirements = {
        1: {
            "min_commands": 4,
            "required_results": ["ast_parsing", "attribute_detection", "signature_extraction"],
            "quality_indicators": ["function_signatures_with_params", "attribute_access_patterns"]
        },
        2: {
            "min_commands": 4,
            "required_results": ["logging_analysis", "conditional_patterns", "mock_strategy"],
            "quality_indicators": ["safe_log_count", "conditional_branches"]
        },
        3: {
            "min_commands": 4,
            "required_results": ["dependency_mapping", "mock_strategy", "path_planning"],
            "quality_indicators": ["external_deps", "internal_deps", "config_deps"]
        }
    }
    
    if phase_num not in depth_requirements:
        return True, "No depth requirements for this phase"
    
    requirements = depth_requirements[phase_num]
    
    # Check command count
    if commands_executed < requirements["min_commands"]:
        return False, f"Insufficient commands: {commands_executed}/{requirements['min_commands']}"
    
    # Check required results
    missing_results = [r for r in requirements["required_results"] if r not in analysis_results]
    if missing_results:
        return False, f"Missing analysis results: {missing_results}"
    
    return True, "Analysis depth validated"
```

### **GATE 3: PATH CONSISTENCY GATES**

**Purpose**: Ensure consistent unit or integration path throughout framework
```python
def validate_path_consistency(chosen_path, test_content, analysis_data):
    """Validate path consistency throughout framework execution."""
    
    if chosen_path == "unit":
        # Unit path validation
        violations = []
        
        # Check for real API calls (should be none)
        real_api_patterns = ["requests.", "HoneyHive(api_key=", "os.getenv"]
        for pattern in real_api_patterns:
            if pattern in test_content:
                violations.append(f"Real API call found: {pattern}")
        
        # Check for sufficient mocking
        mock_count = test_content.count("@patch(")
        if mock_count < 3:
            violations.append(f"Insufficient mocking: {mock_count} patches")
        
        # Check for mock completeness
        if "MockHoneyHiveTracer" not in test_content:
            violations.append("Missing comprehensive mock tracer")
        
        if violations:
            return False, f"Unit path violations: {violations}"
    
    elif chosen_path == "integration":
        # Integration path validation
        violations = []
        
        # Check for real API usage (should be present)
        real_api_found = any(pattern in test_content for pattern in 
                           ["HoneyHive(api_key=", "os.getenv(\"HH_TEST_API_KEY\")"])
        if not real_api_found:
            violations.append("Missing real API usage")
        
        # Check for excessive mocking (should be minimal)
        mock_count = test_content.count("@patch(")
        if mock_count > 5:  # Some mocking allowed for test-specific needs
            violations.append(f"Excessive mocking for integration: {mock_count} patches")
        
        # Check for cleanup patterns
        cleanup_patterns = ["tearDown", "cleanup", "tempfile"]
        cleanup_found = any(pattern in test_content for pattern in cleanup_patterns)
        if not cleanup_found:
            violations.append("Missing cleanup patterns")
        
        if violations:
            return False, f"Integration path violations: {violations}"
    
    else:
        return False, f"Invalid path: {chosen_path}"
    
    return True, f"{chosen_path.title()} path consistency validated"
```

### **GATE 4: AUTOMATED QUALITY GATES**

**Purpose**: Automated validation of final test quality
```python
def validate_automated_quality(test_file_path):
    """Execute automated quality validation script."""
    
    import subprocess
    import json
    
    try:
        # Execute validation script
        result = subprocess.run([
            "python", ".agent-os/scripts/validate-test-quality.py",
            "--test-file", test_file_path
        ], capture_output=True, text=True)
        
        # Check exit code
        if result.returncode != 0:
            return False, f"Quality validation failed with exit code {result.returncode}"
        
        # Parse JSON output for detailed results
        try:
            # Extract JSON from output
            output_lines = result.stdout.split('\n')
            json_line = None
            for line in output_lines:
                if line.strip().startswith('{'):
                    json_line = line.strip()
                    break
            
            if json_line:
                quality_data = json.loads(json_line)
                
                # Validate all quality targets met
                if not quality_data.get("overall_passed", False):
                    failing_targets = []
                    for target, data in quality_data.get("quality_targets", {}).items():
                        if not data.get("passed", False):
                            failing_targets.append(f"{target}: {data.get('details', 'Failed')}")
                    
                    return False, f"Quality targets not met: {failing_targets}"
                
                return True, "All automated quality targets achieved"
            
        except json.JSONDecodeError:
            pass  # Fall back to exit code validation
        
        return True, "Automated quality validation passed (exit code 0)"
        
    except FileNotFoundError:
        return False, "Quality validation script not found"
    except Exception as e:
        return False, f"Quality validation error: {str(e)}"
```

---

## 🚨 **QUALITY GATE ENFORCEMENT**

### **ENFORCEMENT LEVEL 1: SOFT GATES (Warnings)**

**Trigger**: Minor quality issues or missing evidence
```python
def soft_gate_enforcement(issue_description, corrective_action):
    """Issue warning for minor quality gate failures."""
    
    return f"""
⚠️  QUALITY GATE WARNING: {issue_description}

Impact: May affect test quality and success rate
Recommended Action: {corrective_action}
Consequence: Proceed with caution - quality may be compromised

This is a warning. You may continue but quality is not guaranteed.
"""
```

### **ENFORCEMENT LEVEL 2: HARD GATES (Blocking)**

**Trigger**: Critical quality issues or framework violations
```python
def hard_gate_enforcement(issue_description, required_action):
    """Block framework execution for critical quality failures."""
    
    return f"""
🛑 QUALITY GATE BLOCKED: {issue_description}

Impact: Will cause test failures and low pass rates
Required Action: {required_action}
Consequence: Framework execution blocked until resolved

You CANNOT proceed until this issue is resolved.
This gate prevents the 22% pass rate failures that V2 experienced.
"""
```

### **ENFORCEMENT LEVEL 3: FRAMEWORK RESET (Critical)**

**Trigger**: Multiple gate failures or systematic quality issues
```python
def framework_reset_enforcement(violations_list):
    """Reset framework execution for systematic quality failures."""
    
    violations_text = '\n'.join(f"- {violation}" for violation in violations_list)
    
    return f"""
🚨 FRAMEWORK RESET REQUIRED: Multiple quality gate failures

Violations Detected:
{violations_text}

Impact: Framework integrity compromised - 22% pass rate likely
Required Action: Restart framework execution from Phase 1
Consequence: Current progress discarded - systematic execution required

The quality gate system exists to prevent V2's catastrophic failures.
Multiple violations indicate systematic issues requiring fresh start.
"""
```

---

## 📊 **QUALITY GATE METRICS**

### **GATE SUCCESS METRICS**

**Track Quality Gate Effectiveness:**
```python
def track_gate_metrics(gate_results):
    """Track quality gate effectiveness metrics."""
    
    metrics = {
        "gates_passed": sum(1 for result in gate_results if result["passed"]),
        "gates_failed": sum(1 for result in gate_results if not result["passed"]),
        "enforcement_actions": sum(1 for result in gate_results if result.get("enforcement_triggered")),
        "framework_resets": sum(1 for result in gate_results if result.get("reset_required")),
        "quality_improvements": sum(1 for result in gate_results if result.get("quality_improved"))
    }
    
    metrics["gate_success_rate"] = (
        metrics["gates_passed"] / len(gate_results) * 100 
        if gate_results else 0
    )
    
    return metrics
```

### **QUALITY CORRELATION TRACKING**

**Correlate Gate Success with Final Quality:**
```python
def correlate_gates_with_quality(gate_metrics, final_test_quality):
    """Correlate gate success with final test quality."""
    
    correlation_data = {
        "gate_success_rate": gate_metrics["gate_success_rate"],
        "final_pass_rate": final_test_quality.get("pass_rate", 0),
        "final_pylint_score": final_test_quality.get("pylint_score", 0),
        "final_mypy_errors": final_test_quality.get("mypy_errors", 0),
        "quality_correlation": None
    }
    
    # Calculate correlation (simplified)
    if correlation_data["gate_success_rate"] > 90:
        expected_pass_rate = 80  # High gate success should yield 80%+ pass rate
    elif correlation_data["gate_success_rate"] > 70:
        expected_pass_rate = 60  # Medium gate success
    else:
        expected_pass_rate = 30  # Low gate success (like V2's 22%)
    
    correlation_data["expected_pass_rate"] = expected_pass_rate
    correlation_data["quality_correlation"] = (
        "Strong" if abs(correlation_data["final_pass_rate"] - expected_pass_rate) < 10
        else "Weak"
    )
    
    return correlation_data
```

---

## 🎯 **QUALITY GATE SUCCESS CRITERIA**

**Quality gates are successful when:**
1. ✅ All phase completion gates pass with evidence
2. ✅ Analysis depth gates ensure comprehensive analysis
3. ✅ Path consistency gates maintain unit/integration separation
4. ✅ Automated quality gates achieve exit code 0
5. ✅ Enforcement actions prevent quality degradation
6. ✅ Gate success correlates with 80%+ final pass rates

**Quality gate system protects framework integrity and ensures V3 achieves 80%+ success rates instead of V2's 22% failures.**
