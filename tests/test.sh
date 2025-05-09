#!/bin/bash

# Check if all arguments are provided
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: ./test.sh <target> <file> [<env>]"
    echo "\nAvailable targets:"
    echo "  dev"
    echo "  test"
    echo "  lambda"
    echo "\nAvailable environments:"
    echo "$(ls -1 environments | grep -v "\.py$")"
    echo "\nExample: ./test.sh dev integration/sanity.py openai"
    echo "\nIf env is not specified, openai will be used by default."
    exit 1
fi

TARGET=$1
FILE=$2
ENV=${3:-openai}  # Default to openai if not specified

# Validate target
if [ "$TARGET" != "dev" ] && [ "$TARGET" != "test" ] && [ "$TARGET" != "lambda" ]; then
    echo "Error: Target must be either 'dev', 'test', or 'lambda'"
    exit 1
fi

# Validate environment
if [ ! -d "environments/$ENV" ]; then
    echo "Error: Environment '$ENV' not found"
    exit 1
fi

make $TARGET FILE=$FILE ENV=$ENV