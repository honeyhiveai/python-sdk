.PHONY: test cleanup

# The names of the required environment variables
REQUIRED_ENV_VARS := HH_API_KEY HH_DATASET HH_PROJECT OPENAI_API_KEY SERP_API_KEY COHERE_API_KEY

# Function to check whether an environment variable is set
env_var_check = $(if $(value $(1)),,$(error $(1) is not set. Please set $(1)))

# The test target
test: start_services
	@$(foreach var,$(REQUIRED_ENV_VARS),$(call env_var_check,$(var)))
	@docker build -f tests/Dockerfile . -t my-test
	@docker run \
		-e HH_API_KEY=$$HH_API_KEY \
		-e HH_PROJECT="$$HH_PROJECT" \
		-e HH_DATASET="$$HH_DATASET" \
		-e SERP_API_KEY=$$SERP_API_KEY \
		-e OPENAI_API_KEY=$$OPENAI_API_KEY \
		-e COHERE_API_KEY=$$COHERE_API_KEY \
		my-test
	@$(MAKE) cleanup

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
