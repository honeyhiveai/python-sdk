# Default target
.DEFAULT_GOAL := help

# Declare phony targets
.PHONY: help clean test dev lambda

# Help target
help:
	@echo "Usage: make test FILE=<test-file> ENV=<environment>"
	@echo "Example: make test FILE=integration/sanity.py ENV=openai"
	@echo ""
	@echo "Available environments:"
	@ls -d environments/*/ | sed 's/environments\///g' | sed 's/\///g'

# Function to build and run tests
define build_and_run
	@echo "Setting up test environment..."
	@if [ ! -f honeyhive.tar.gz ]; then \
		echo "Building package..." && \
		cd .. && poetry build && \
		LATEST_TARBALL=$$(ls -t dist/honeyhive-*.tar.gz | head -1) && \
		cp $$LATEST_TARBALL tests/honeyhive.tar.gz && \
		cd tests; \
	fi
	@echo "Copying files to $(2)..."
	@cp honeyhive.tar.gz environments/$(2)/
	@cp $(1) environments/$(2)/__init__.py
	@cp Dockerfile environments/$(2)/
	@echo "Building and running Docker container..."
	@cd environments/$(2) && docker build -t python-sdk-$(2) . && docker run --rm --env-file ../../../.env.docker python-sdk-$(2)
	@echo "Cleaning up Docker image..."
	@docker rmi python-sdk-$(2)
	@echo "Cleaning up environment..."
	@rm -f \
		environments/$(2)/honeyhive.tar.gz \
		environments/$(2)/__init__.py \
		environments/$(2)/Dockerfile
endef

# Function to build Lambda package
define build_lambda_package
	@echo "Setting up Lambda environment..."
	@if [ ! -f honeyhive.tar.gz ]; then \
		echo "Building package..." && \
		cd .. && poetry build && \
		LATEST_TARBALL=$$(ls -t dist/honeyhive-*.tar.gz | head -1) && \
		cp $$LATEST_TARBALL tests/honeyhive.tar.gz && \
		cd tests; \
	fi
	@echo "Creating Lambda package in $(2)..."
	@mkdir -p environments/$(2)/lambda_package
	@cp $(1) environments/$(2)/lambda_package/lambda_function.py
	@cp honeyhive.tar.gz environments/$(2)/lambda_package/
	@cp environments/$(2)/requirements.txt environments/$(2)/lambda_package/
	@cp ../.env.docker environments/$(2)/lambda_package/.env
	@echo "Building Lambda package in Docker container..."
	@cd environments/$(2) && \
		docker run --rm -v $$(pwd)/lambda_package:/var/task --platform=linux/amd64 python:3.11-slim bash -c " \
			cd /var/task && \
			pip install \
			  --platform manylinux2014_x86_64 \
			  --target . \
			  --implementation cp \
			  --python-version 3.11 \
			  --only-binary=:all: \
			  --upgrade -r requirements.txt && \
			pip install \
			  --platform manylinux2014_x86_64 \
			  --target . \
			  --implementation cp \
			  --python-version 3.11 \
			  --only-binary=:all: \
			  honeyhive.tar.gz && \
			rm -f honeyhive.tar.gz \
		" && \
		cd lambda_package && zip -r ../lambda.zip . && \
		cd ../..
	@echo "Lambda package created at environments/$(2)/lambda.zip"
endef

# Test target
test:
	@if [ -z "$(FILE)" ] || [ -z "$(ENV)" ]; then \
		echo "Error: Both FILE and ENV must be specified."; \
		echo "Usage: make test FILE=<test-file> ENV=<environment>"; \
		exit 1; \
	fi
	$(call build_and_run,$(FILE),$(ENV))

dev:
	@if [ -z "$(FILE)" ] || [ -z "$(ENV)" ]; then \
		echo "Error: Both FILE and ENV must be specified."; \
		echo "Usage: make dev FILE=<test-file> ENV=<environment>"; \
		exit 1; \
	fi
	@echo "Building package in root directory..."
	@cd .. && poetry build && \
	LATEST_TARBALL=$$(ls -t dist/honeyhive-*.tar.gz | head -1) && \
	cp $$LATEST_TARBALL tests/honeyhive.tar.gz && \
	cd tests
	$(call build_and_run,$(FILE),$(ENV))

# Lambda target
lambda:
	@if [ -z "$(FILE)" ] || [ -z "$(ENV)" ]; then \
		echo "Error: Both FILE and ENV must be specified."; \
		echo "Usage: make lambda FILE=<test-file> ENV=<environment>"; \
		exit 1; \
	fi
	$(call build_lambda_package,$(FILE),$(ENV))

# Clean target
clean:
	@echo "Cleaning up..."
	@rm -f honeyhive.tar.gz
	@for dir in environments/*/; do \
		rm -f $$dir/honeyhive.tar.gz; \
		rm -f $$dir/__init__.py; \
		rm -f $$dir/Dockerfile; \
		rm -f $$dir/lambda.zip;
	done 