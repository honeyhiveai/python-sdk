# Table Enforcement - Mandatory Progress Tracking

## 🚨 **CRITICAL: MANDATORY PROGRESS TABLE ENFORCEMENT**

🛑 VALIDATE-GATE: Table Enforcement Entry Requirements
- [ ] Progress tracking importance understood ✅/❌
- [ ] V2 bypass consequences reviewed ✅/❌
- [ ] Mandatory table update commitment confirmed ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without table update commitment

**Purpose**: Enforce mandatory progress table updates to prevent framework shortcuts and ensure systematic execution  
**Archive Success**: Mandatory table updates prevented shortcuts and maintained systematic execution  
**V2 Failure**: No table enforcement allowed framework bypasses leading to incomplete analysis  
**V3 Enhancement**: Automated table validation with specific formatting and evidence requirements  

---

## 🛑 **MANDATORY PROGRESS TABLE FORMAT EXECUTION**

⚠️ MUST-READ: Progress table updates are non-negotiable framework requirements

### **STANDARD PROGRESS TABLE STRUCTURE**

**Required Table Format:**
```markdown
| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Pre-Generation Setup | ❌ | None | 0/5 | Manual | ❌ |
| 0B: Pre-Generation Metrics | ❌ | None | 0/1 | JSON Required | ❌ |
| 0C: Target Validation | ❌ | None | 0/5 | Manual | ❌ |
| 1: Method Verification | ❌ | None | 0/4 | Manual | ❌ |
| 2: Logging Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 4: Usage Patterns | ❌ | None | 0/4 | Manual | ❌ |
| 5: Coverage Analysis | ❌ | None | 0/4 | Manual | ❌ |
| 6: Pre-Generation Validation | ❌ | None | 0/8 | Manual | ❌ |
| 7: Post-Generation Metrics | ❌ | None | 0/4 | JSON Required | ❌ |
| 8: **AUTOMATED QUALITY ENFORCEMENT** | ❌ | None | 0/5 | **SCRIPT EXIT CODE 0** | ❌ |
```

### **TABLE FORMATTING STANDARDS**

**MANDATORY FORMATTING REQUIREMENTS:**
1. **Markdown Table Format**: Must use proper markdown table syntax
2. **Column Alignment**: Pipes (|) must align properly
3. **Status Indicators**: Use ✅ for complete, ❌ for incomplete, 🔄 for in-progress
4. **Evidence Specificity**: Must include specific counts and details, not generic descriptions
5. **Command Tracking**: Must show completed/total commands (e.g., "3/4")
6. **Validation Types**: Must specify Manual, JSON Required, or SCRIPT EXIT CODE 0
7. **Gate Status**: Must show ✅ only when phase fully complete with evidence

---

## 🛑 **TABLE ENFORCEMENT PATTERNS**

### **ENFORCEMENT PATTERN 1: Missing Table Detection**

**Violation Detection:**
```python
def detect_missing_progress_table(response_text):
    """Detect if progress table is missing from phase completion response."""
    
    # Phase completion indicators
    completion_phrases = [
        "phase complete", "phase finished", "moving to phase",
        "proceeding to", "analysis complete", "phase done"
    ]
    
    # Table structure indicators
    table_indicators = [
        "| Phase |", "|-------|", "| Status |", "Evidence", "Commands", "Gate"
    ]
    
    has_completion = any(phrase in response_text.lower() for phrase in completion_phrases)
    has_table = any(indicator in response_text for indicator in table_indicators)
    
    if has_completion and not has_table:
        return True, "Phase completion claimed without progress table update"
    
    return False, None

def enforce_missing_table(phase_num):
    """Enforce table requirement for missing table violation."""
    
    return f"""
🛑 TABLE ENFORCEMENT VIOLATION: Missing progress table

VIOLATION: You completed Phase {phase_num} but didn't update the progress table.

REQUIRED ACTION: Show me the updated progress table in the chat window with:
- Phase {phase_num} marked as ✅
- Specific evidence documented (counts, findings, results)
- Command completion status (X/Y commands executed)
- Validation type confirmed
- Gate status updated to ✅

ENFORCEMENT: You CANNOT proceed to the next phase without showing the updated table.

This enforcement prevents the shortcuts that caused V2's 22% pass rate failure.
"""
```

### **ENFORCEMENT PATTERN 2: Malformed Table Detection**

**Violation Detection:**
```python
def detect_malformed_table(table_text):
    """Detect malformed progress table structure."""
    
    violations = []
    
    # Check for proper markdown table structure
    if not table_text.startswith("|"):
        violations.append("Table must start with pipe character (|)")
    
    # Check for header row
    if "| Phase |" not in table_text:
        violations.append("Missing required header row with '| Phase |'")
    
    # Check for separator row
    if "|-------|" not in table_text:
        violations.append("Missing table separator row with |-------|")
    
    # Check for required columns
    required_columns = ["Phase", "Status", "Evidence", "Commands", "Validation", "Gate"]
    for column in required_columns:
        if column not in table_text:
            violations.append(f"Missing required column: {column}")
    
    # Check for proper status indicators
    lines = table_text.split('\n')
    for line in lines:
        if '|' in line and ('Phase' not in line and '---' not in line):
            # This is a data row
            if not any(indicator in line for indicator in ['✅', '❌', '🔄']):
                violations.append(f"Missing status indicator in row: {line.strip()}")
    
    return violations

def enforce_malformed_table(violations):
    """Enforce table formatting requirements."""
    
    violations_text = '\n'.join(f"- {violation}" for violation in violations)
    
    return f"""
🛑 TABLE ENFORCEMENT VIOLATION: Malformed progress table

FORMATTING VIOLATIONS:
{violations_text}

REQUIRED FORMAT:
```markdown
| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 1: Method Verification | ✅ | Found X functions, Y attributes, Z signatures | 4/4 | Manual | ✅ |
```

ENFORCEMENT: Fix table formatting before proceeding.
Proper table formatting ensures systematic progress tracking.
"""
```

### **ENFORCEMENT PATTERN 3: Insufficient Evidence Detection**

**Violation Detection:**
```python
def detect_insufficient_evidence(phase_num, evidence_text):
    """Detect insufficient evidence in progress table."""
    
    evidence_requirements = {
        1: ["function count", "attribute list", "signature analysis"],
        2: ["logging calls", "conditional patterns", "mock strategy"],
        3: ["dependency count", "mock plan", "path strategy"],
        4: ["usage patterns", "parameter combinations", "error scenarios"],
        5: ["coverage target", "branch analysis", "edge cases"],
        6: ["import validation", "signature verification", "readiness check"],
        7: ["metrics collected", "quality assessment", "path validation"],
        8: ["automated validation", "exit code 0", "quality targets"]
    }
    
    if phase_num not in evidence_requirements:
        return False, None
    
    required = evidence_requirements[phase_num]
    evidence_lower = evidence_text.lower()
    
    missing_evidence = []
    for requirement in required:
        if requirement not in evidence_lower:
            missing_evidence.append(requirement)
    
    if missing_evidence:
        return True, missing_evidence
    
    # Check for generic evidence (violations)
    generic_phrases = ["analysis complete", "done", "finished", "none", "n/a"]
    if any(phrase in evidence_lower for phrase in generic_phrases):
        return True, ["Generic evidence - specific counts and details required"]
    
    return False, None

def enforce_insufficient_evidence(phase_num, missing_evidence):
    """Enforce specific evidence requirements."""
    
    missing_text = '\n'.join(f"- {item}" for item in missing_evidence)
    
    return f"""
🛑 TABLE ENFORCEMENT VIOLATION: Insufficient evidence

PHASE {phase_num} MISSING EVIDENCE:
{missing_text}

REQUIRED: Specific evidence with counts and details, not generic descriptions.

EXAMPLES OF PROPER EVIDENCE:
- "Found 15 functions (12 public, 3 private), 8 attributes detected, 20 signatures analyzed"
- "Analyzed 25 safe_log calls (10 debug, 8 info, 7 error), 5 conditional branches"
- "Mapped 12 external deps, 8 internal imports, unit path strategy confirmed"

ENFORCEMENT: Update table with specific evidence before proceeding.
"""
```

---

## 📋 **TABLE VALIDATION AUTOMATION**

### **AUTOMATED TABLE VALIDATION**

**Complete Table Validation Function:**
```python
def validate_progress_table(table_text, phase_num):
    """Comprehensive progress table validation."""
    
    validation_results = {
        "valid": True,
        "violations": [],
        "enforcement_required": False,
        "enforcement_message": ""
    }
    
    # Check 1: Table structure
    structure_violations = detect_malformed_table(table_text)
    if structure_violations:
        validation_results["violations"].extend(structure_violations)
        validation_results["valid"] = False
    
    # Check 2: Evidence sufficiency
    evidence_insufficient, missing_evidence = detect_insufficient_evidence(phase_num, table_text)
    if evidence_insufficient:
        validation_results["violations"].extend([f"Insufficient evidence: {missing_evidence}"])
        validation_results["valid"] = False
    
    # Check 3: Phase completion status
    if f"Phase {phase_num}" in table_text:
        phase_line = [line for line in table_text.split('\n') if f"Phase {phase_num}" in line]
        if phase_line and "✅" not in phase_line[0]:
            validation_results["violations"].append(f"Phase {phase_num} not marked as complete (✅)")
            validation_results["valid"] = False
    
    # Generate enforcement message if needed
    if not validation_results["valid"]:
        validation_results["enforcement_required"] = True
        validation_results["enforcement_message"] = generate_table_enforcement_message(
            phase_num, validation_results["violations"]
        )
    
    return validation_results

def generate_table_enforcement_message(phase_num, violations):
    """Generate comprehensive table enforcement message."""
    
    violations_text = '\n'.join(f"- {violation}" for violation in violations)
    
    return f"""
🛑 COMPREHENSIVE TABLE ENFORCEMENT VIOLATION

PHASE: {phase_num}
VIOLATIONS:
{violations_text}

REQUIRED ACTIONS:
1. Fix table formatting (proper markdown structure)
2. Add specific evidence with counts and details
3. Mark phase as complete (✅) with proper status
4. Include command completion status (X/Y)
5. Confirm validation type and gate status

ENFORCEMENT: Framework execution blocked until table compliance achieved.

This systematic progress tracking prevents the shortcuts that caused V2's 22% failure rate.
V3 requires complete documentation for 80%+ success rates.
"""
```

---

## 🎯 **TABLE ENFORCEMENT SUCCESS CRITERIA**

### **ENFORCEMENT SUCCESS METRICS**

**Track Table Enforcement Effectiveness:**
```python
def track_table_enforcement_metrics(enforcement_actions):
    """Track table enforcement effectiveness."""
    
    metrics = {
        "total_enforcements": len(enforcement_actions),
        "missing_table_violations": sum(1 for action in enforcement_actions 
                                      if "missing table" in action["type"]),
        "malformed_table_violations": sum(1 for action in enforcement_actions 
                                        if "malformed table" in action["type"]),
        "insufficient_evidence_violations": sum(1 for action in enforcement_actions 
                                               if "insufficient evidence" in action["type"]),
        "compliance_achieved": sum(1 for action in enforcement_actions 
                                 if action.get("resolved", False))
    }
    
    metrics["compliance_rate"] = (
        metrics["compliance_achieved"] / metrics["total_enforcements"] * 100
        if metrics["total_enforcements"] > 0 else 100
    )
    
    return metrics
```

### **QUALITY CORRELATION**

**Correlate Table Compliance with Final Quality:**
```python
def correlate_table_compliance_with_quality(table_metrics, final_quality):
    """Correlate table compliance with final test quality."""
    
    correlation = {
        "table_compliance_rate": table_metrics["compliance_rate"],
        "final_pass_rate": final_quality.get("pass_rate", 0),
        "systematic_execution": table_metrics["compliance_rate"] > 90,
        "quality_prediction": None
    }
    
    # Predict quality based on table compliance
    if correlation["table_compliance_rate"] > 90:
        correlation["quality_prediction"] = "80%+ pass rate expected"
    elif correlation["table_compliance_rate"] > 70:
        correlation["quality_prediction"] = "60-80% pass rate expected"
    else:
        correlation["quality_prediction"] = "22% pass rate risk (like V2)"
    
    return correlation
```

---

## ✅ **TABLE ENFORCEMENT SUCCESS VALIDATION**

**Table enforcement is successful when:**
1. ✅ All progress tables follow mandatory formatting standards
2. ✅ Every phase completion includes specific evidence documentation
3. ✅ Table violations are detected and enforced immediately
4. ✅ Framework shortcuts are prevented through table requirements
5. ✅ Systematic execution is maintained through progress tracking
6. ✅ Table compliance correlates with 80%+ final pass rates

**Table enforcement system ensures systematic framework execution and prevents the shortcuts that caused V2's 22% pass rate failure.**
