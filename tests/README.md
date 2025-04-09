# HoneyHive Python SDK Testing Framework

This framework allows testing the HoneyHive Python SDK in different environments with various dependencies.

## Quick Start

To run the sanity test in the OpenAI environment:

```bash
make test FILE=integration/sanity.py ENV=openai
```

For development (builds the package first):

```bash
make dev FILE=integration/sanity.py ENV=openai
```

To create a Lambda deployment package:

```bash
make lambda FILE=integration/test_lambda.py ENV=openai
```

Or use the test.sh script:

```bash
./test.sh test integration/sanity.py openai
./test.sh lambda integration/test_lambda.py openai
```

## Overview

This testing framework solves the challenge of testing across multiple environments with different dependencies:

1. Builds the HoneyHive SDK using Poetry and creates a tarball
2. Copies the test file, environment config, and Dockerfile to the target environment directory
3. Builds and runs a Docker container with the specific environment 
4. Cleans up after the test completes

For Lambda deployments, it creates a zip package with all dependencies that can be directly uploaded to AWS Lambda.

## Directory Structure

```
.
├── .env                   # Environment variables for tests
├── Dockerfile             # Base Dockerfile for all environments
├── Makefile               # Build and test automation
├── README.md              # This file
├── environments/          # Test environments
│   ├── openai/            # OpenAI environment 
│   │   └── requirements.txt
│   ├── langchain/         # Langchain environment
│   │   └── requirements.txt
│   └── llama-index/       # LlamaIndex environment
│       └── requirements.txt
└── integration/           # Test files
    ├── sanity.py          # Basic sanity test
    └── ...                # Other test files
```

## How to Use

### Running Tests

1. List available environments:
```bash
make help
```

2. Run a test:
```bash
make test FILE=<path-to-test-file> ENV=<environment-name>
```

### Creating Lambda Deployment Packages

1. Create a Lambda function file in the `integration/` directory
2. Run the lambda target:
```bash
make lambda FILE=<path-to-lambda-file> ENV=<environment-name>
```
3. The Lambda deployment package will be created at `environments/<env>/lambda.zip`
4. Upload this zip file to AWS Lambda

### Creating New Environments

1. Create a new directory in `environments/` 
2. Add a `requirements.txt` file with necessary dependencies

### Creating New Tests

Create Python files in the `integration/` directory that can run standalone. 
Your test files will be run directly in the container.

### Environment Variables

Update the `.env` file with any required variables for your tests.

