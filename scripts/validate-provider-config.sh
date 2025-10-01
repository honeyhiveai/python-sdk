#!/bin/bash
# Provider Configuration Validation - Unified Quality Gate
#
# Runs all provider validation checks in logical sequence:
# 1. YAML Schema Validation
# 2. Signature Uniqueness Check
# 3. Bundle Compilation Verification
# 4. Performance Regression Detection
#
# Agent OS Compliance: Consolidated gate for Universal LLM Discovery Engine v4.0

set -e  # Exit on first error

echo "🔍 Provider Configuration Validation"
echo "======================================"

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -f "python-sdk/bin/activate" ]]; then
        source python-sdk/bin/activate
    fi
fi

# 1. YAML Schema Validation
echo -e "\n1️⃣  YAML Schema Validation..."
python -m config.dsl.validation.yaml_schema config/dsl/providers/*/*.yaml

# 2. Signature Uniqueness Check
echo -e "\n2️⃣  Signature Uniqueness Check..."
python -m config.dsl.validation.signature_collisions config/dsl/providers/*/structure_patterns.yaml

# 3. Bundle Compilation Verification
echo -e "\n3️⃣  Bundle Compilation Verification..."
python -m config.dsl.validation.bundle_verification

# 4. Performance Regression Detection
echo -e "\n4️⃣  Performance Regression Detection..."
python -m config.dsl.validation.performance_benchmarks

echo -e "\n✅ All provider configuration checks passed"
echo "======================================"
exit 0
