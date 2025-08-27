.PHONY: test cleanup tox

# The names of the required environment variables
REQUIRED_ENV_VARS := HH_API_KEY HH_DATASET HH_PROJECT OPENAI_API_KEY SERP_API_KEY COHERE_API_KEY HH_PROJECT_ID

# Function to check whether an environment variable is set
env_var_check = $(if $(value $(1)),,$(error $(1) is not set. Please set $(1)))

# The test target
test:
	@$(foreach var,$(REQUIRED_ENV_VARS),$(call env_var_check,$(var)))
	@docker build -f tests/Dockerfile . -t my-test
	@docker run \
		-e HH_API_KEY=$$HH_API_KEY \
		-e HH_API_URL=$$HH_API_URL \
		-e HH_PROJECT="$$HH_PROJECT" \
		-e HH_PROJECT_ID="$$HH_PROJECT_ID" \
		-e HH_DATASET="$$HH_DATASET" \
		-e SERP_API_KEY=$$SERP_API_KEY \
		-e OPENAI_API_KEY=$$OPENAI_API_KEY \
		-e COHERE_API_KEY=$$COHERE_API_KEY \
		my-test

# Start the services needed before running the tests
start_services:
	@bash ./tests/standalone_embed.sh start

# Cleanup after tests
cleanup: stop_services delete_services

# Stop the services
stop_services:
	@bash ./tests/standalone_embed.sh stop

# Delete the services
delete_services:
	@bash ./tests/standalone_embed.sh delete

# Run tests with tox across multiple Python versions
tox:
	@echo "Running tests with tox across Python 3.10-3.12..."
	@python scripts/run_tox.py test

# Run specific Python version tests

tox-py310:
	@echo "Running tests with Python 3.10..."
	@python scripts/run_tox.py test -e py310

tox-py311:
	@echo "Running tests with Python 3.11..."
	@python scripts/run_tox.py test -e py311

tox-py312:
	@echo "Running tests with Python 3.12..."
	@python scripts/run_tox.py test -e py312

# Run linting checks
tox-lint:
	@echo "Running linting checks..."
	@python scripts/run_tox.py lint

# Run code formatting checks
tox-format:
	@echo "Running code formatting checks..."
	@python scripts/run_tox.py format

# Install tox
tox-install:
	@echo "Installing tox..."
	@python scripts/run_tox.py install
