# Violation Detection - Framework Enforcement Patterns

## 🚨 **CRITICAL: FRAMEWORK VIOLATION PREVENTION**

🛑 VALIDATE-GATE: Violation Detection Entry Requirements
- [ ] Framework violation consequences understood ✅/❌
- [ ] V2 bypass failure analysis reviewed (22% pass rate) ✅/❌
- [ ] Violation prevention commitment confirmed ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without violation prevention commitment

**Purpose**: Systematic detection and prevention of framework violations that cause quality failures  
**Archive Success**: Strong enforcement prevented shortcuts and maintained quality  
**V2 Failure**: No violation detection allowed framework bypasses leading to 22% pass rate  
**V3 Enhancement**: Automated violation detection with specific enforcement responses  

---

## 🛑 **FRAMEWORK VIOLATION CATEGORIES EXECUTION**

⚠️ MUST-READ: All violation patterns must be actively monitored and prevented

### **CATEGORY 1: PHASE COMPLETION VIOLATIONS**

**VIOLATION PATTERN**: Proceeding to next phase without completing current phase
```
❌ VIOLATION INDICATORS:
- "Phase X complete" without showing updated progress table
- "Moving to Phase Y" without Phase X evidence
- "Analysis finished" without specific documentation
- Skipping mandatory commands or evidence collection
```

**ENFORCEMENT RESPONSE**:
```
🛑 VIOLATION DETECTED: Phase completion bypass attempt

STOP - You completed Phase X but didn't update the progress table. 
Show me the updated table in the chat window with Phase X marked as ✅ 
and evidence documented before proceeding to Phase Y.

REQUIRED EVIDENCE:
- Progress table with Phase X marked ✅
- Specific evidence counts (functions, dependencies, patterns, etc.)
- Command completion status (X/Y commands executed)
- Validation gate confirmation
```

### **CATEGORY 2: ANALYSIS DEPTH VIOLATIONS**

**VIOLATION PATTERN**: Surface-level analysis instead of required deep analysis
```
❌ VIOLATION INDICATORS:
- Using basic grep instead of AST parsing (Phase 1)
- Generic import listing instead of dependency analysis (Phase 3)
- Simple logging search instead of conditional pattern analysis (Phase 2)
- Missing attribute detection and function signature extraction
```

**ENFORCEMENT RESPONSE**:
```
🛑 VIOLATION DETECTED: Insufficient analysis depth

The framework requires deep analysis to prevent 22% pass rate failures.
You must execute the complete analysis commands:

PHASE 1 REQUIRED:
- AST parsing for function signatures
- Attribute access pattern detection  
- Function call parameter analysis
- Mock completeness requirements

PHASE 3 REQUIRED:
- Complete dependency mapping
- Mock strategy documentation
- Configuration dependency analysis
- Path-specific mocking plans

Re-execute the phase with complete analysis before proceeding.
```

### **CATEGORY 3: PATH CONSISTENCY VIOLATIONS**

**VIOLATION PATTERN**: Mixing unit and integration test strategies
```
❌ VIOLATION INDICATORS:
- Unit tests with real API calls
- Integration tests with excessive mocking
- Mixed mock/real strategies in same test file
- Path-specific requirements not followed
```

**ENFORCEMENT RESPONSE**:
```
🛑 VIOLATION DETECTED: Path consistency violation

You must choose and consistently follow either:

UNIT PATH: Mock everything, complete isolation
- ALL external dependencies mocked
- NO real API calls allowed
- Complete mock object validation
- 90%+ coverage target

INTEGRATION PATH: Real APIs, end-to-end validation  
- Real HoneyHive API usage required
- Minimal mocking (test-specific only)
- Resource cleanup implementation
- 80%+ coverage target

Choose one path and follow it consistently throughout.
```

### **CATEGORY 4: QUALITY BYPASS VIOLATIONS**

**VIOLATION PATTERN**: Attempting to bypass quality requirements
```
❌ VIOLATION INDICATORS:
- Proceeding without Phase 8 automated validation
- Using git commit --no-verify
- Skipping quality checks
- Declaring completion without exit code 0
```

**ENFORCEMENT RESPONSE**:
```
🛑 VIOLATION DETECTED: Quality bypass attempt

Framework completion REQUIRES automated validation success:

MANDATORY REQUIREMENTS:
- Execute: python .agent-os/scripts/validate-test-quality.py --test-file [FILE]
- Achieve: Exit code 0 (all quality targets met)
- Confirm: 100% pass rate, 10.0/10 Pylint, 0 MyPy errors, Black formatting

NO BYPASSES ALLOWED:
- Cannot use --no-verify
- Cannot skip quality checks  
- Cannot proceed with exit code != 0
- Cannot declare completion without validation

Fix all quality issues and re-run validation until exit code 0.
```

---

## 🔍 **AUTOMATED VIOLATION DETECTION**

### **DETECTION PATTERN 1: Missing Progress Tables**

**Detection Logic**:
```python
def detect_missing_progress_table(response_text):
    """Detect if progress table is missing from phase completion."""
    
    completion_indicators = [
        "phase complete", "moving to phase", "analysis finished",
        "proceeding to", "next phase", "phase done"
    ]
    
    table_indicators = [
        "| Phase |", "|-------|", "✅", "❌", "Evidence"
    ]
    
    has_completion = any(indicator in response_text.lower() 
                        for indicator in completion_indicators)
    has_table = any(indicator in response_text 
                   for indicator in table_indicators)
    
    if has_completion and not has_table:
        return True, "Missing progress table for phase completion"
    
    return False, None
```

### **DETECTION PATTERN 2: Insufficient Analysis Commands**

**Detection Logic**:
```python
def detect_insufficient_analysis(phase_num, commands_executed):
    """Detect if required analysis commands were skipped."""
    
    required_commands = {
        1: 4,  # Phase 1: AST parsing, attribute detection, etc.
        2: 4,  # Phase 2: Logging analysis commands
        3: 4,  # Phase 3: Dependency analysis commands
        4: 4,  # Phase 4: Usage pattern commands
        5: 4,  # Phase 5: Coverage analysis commands
        6: 8,  # Phase 6: Pre-generation validation commands
    }
    
    if phase_num in required_commands:
        required = required_commands[phase_num]
        if commands_executed < required:
            return True, f"Phase {phase_num} requires {required} commands, only {commands_executed} executed"
    
    return False, None
```

### **DETECTION PATTERN 3: Quality Bypass Attempts**

**Detection Logic**:
```python
def detect_quality_bypass(response_text):
    """Detect attempts to bypass quality requirements."""
    
    bypass_indicators = [
        "--no-verify", "skip validation", "bypass quality",
        "framework complete" # without validation
    ]
    
    validation_indicators = [
        "validate-test-quality.py", "exit code 0", "quality targets met"
    ]
    
    has_bypass = any(indicator in response_text.lower() 
                    for indicator in bypass_indicators)
    has_validation = any(indicator in response_text.lower() 
                        for indicator in validation_indicators)
    
    completion_claimed = "framework complete" in response_text.lower()
    
    if completion_claimed and not has_validation:
        return True, "Framework completion claimed without automated validation"
    
    if has_bypass:
        return True, "Quality bypass attempt detected"
    
    return False, None
```

---

## 🚨 **ENFORCEMENT ESCALATION LEVELS**

### **LEVEL 1: WARNING (First Violation)**
```
⚠️  FRAMEWORK WARNING: Potential violation detected

Issue: [Specific violation description]
Required Action: [Specific corrective action]
Next Step: Complete the required action and continue

This is your first warning. Please follow framework requirements.
```

### **LEVEL 2: ENFORCEMENT (Repeated Violation)**
```
🛑 FRAMEWORK ENFORCEMENT: Violation confirmed

Issue: [Specific violation description]
Impact: This violation caused V2's 22% pass rate failure
Required Action: [Specific corrective action with examples]

You must complete the required action before proceeding.
Framework execution is blocked until compliance.
```

### **LEVEL 3: FRAMEWORK RESET (Persistent Violations)**
```
🚨 FRAMEWORK RESET REQUIRED: Multiple violations detected

Violations: [List of violations]
Impact: Framework integrity compromised
Required Action: Restart framework execution from Phase 1

The systematic approach is essential for 80%+ success rates.
Shortcuts and violations lead to 22% failures.
```

---

## 📋 **VIOLATION PREVENTION STRATEGIES**

### **PROACTIVE PREVENTION 1: Clear Requirements**
- Each phase has explicit completion criteria
- Progress tables are mandatory, not optional
- Evidence requirements are specific and measurable
- Quality gates are automated and non-negotiable

### **PROACTIVE PREVENTION 2: Positive Reinforcement**
```
✅ FRAMEWORK COMPLIANCE: Excellent execution

You have successfully completed Phase X with:
- Complete progress table with evidence
- All required commands executed (X/X)
- Specific evidence documented
- Quality requirements met

This systematic approach ensures 80%+ success rates.
Continue to Phase Y with the same thoroughness.
```

### **PROACTIVE PREVENTION 3: Educational Guidance**
```
📚 FRAMEWORK EDUCATION: Why this matters

V2 Framework Failure: 22% pass rate due to shortcuts
- Missing analysis → Incomplete mock objects
- Skipped validation → Wrong function signatures  
- No enforcement → Framework bypasses

V3 Framework Success: 80%+ pass rate through systematic execution
- Deep analysis → Complete mock objects
- Mandatory validation → Correct signatures
- Strong enforcement → Framework integrity

Your systematic approach prevents these failures.
```

---

## 🎯 **VIOLATION DETECTION SUCCESS CRITERIA**

**Violation detection is successful when:**
1. ✅ All framework violations are detected immediately
2. ✅ Specific enforcement responses are provided
3. ✅ Corrective actions are clearly specified
4. ✅ Framework integrity is maintained
5. ✅ Quality standards are enforced consistently
6. ✅ 80%+ success rate is protected through enforcement

**Framework protection achieved when violations are prevented before they cause quality degradation.**
