#!/bin/bash
# Invalid Tracer Pattern Validation Script
# Prevents usage of deprecated tracer patterns like @tracer.trace()
#
# This script ensures that code uses the correct @trace decorator pattern
# instead of deprecated @tracer.trace() or similar patterns.

set -e

echo "🔍 Checking for invalid tracer patterns..."

# Check for invalid @*.trace( patterns in documentation, examples, and source
if grep -r "@.*\.trace(" docs/ examples/ src/ 2>/dev/null; then
    echo "❌ Invalid tracer patterns found!"
    echo ""
    echo "🚨 DEPRECATED PATTERN DETECTED"
    echo "Use '@trace' decorator instead of '@tracer.trace()' or similar patterns."
    echo ""
    echo "✅ Correct pattern:"
    echo "  from honeyhive import trace"
    echo "  @trace(event_type=EventType.model)"
    echo "  def my_function():"
    echo ""
    echo "❌ Incorrect patterns:"
    echo "  @tracer.trace()  # Don't use this"
    echo "  @my_tracer.trace()  # Don't use this"
    echo ""
    exit 1
else
    echo "✅ No invalid tracer patterns found"
    exit 0
fi
