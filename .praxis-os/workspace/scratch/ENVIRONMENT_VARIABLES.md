# HoneyHive SDK Environment Variables

This document lists all environment variables supported by the HoneyHive Python SDK, including both HoneyHive-specific and standard environment variables for maximum compatibility.

> **⚠️ OTLP Tracing Requirement**: The `HH_PROJECT` environment variable is **required** when using OTLP tracing due to backend compatibility requirements. The OTLP ingestion service validates project information in both HTTP headers and span attributes.

## API Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| `HH_API_KEY` | HoneyHive API key | None | **Yes** |
| `HH_API_URL` | API base URL | `https://api.honeyhive.ai` | No |
| `HH_PROJECT` | Project name | `default` | **Yes** (for OTLP) |
| `HH_SOURCE` | Source environment | `production` | No |

## Tracing Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| `HH_DISABLE_TRACING` | Disable tracing | `false` | No |
| `HH_DISABLE_HTTP_TRACING` | Disable HTTP instrumentation | `false` | No |
| `HH_TEST_MODE` | Enable test mode | `false` | No |
| `HH_VERBOSE` | Enable verbose logging | `false` | No |

## OTLP Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| `HH_OTLP_ENABLED` | Enable OTLP export | `true` | No |
| `HH_OTLP_ENDPOINT` | Custom OTLP endpoint | Auto-detected | No |
| `HH_OTLP_HEADERS` | OTLP headers (JSON format) | None | No |
| `HH_BATCH_SIZE` | OTLP batch size for performance optimization | `100` | No |
| `HH_FLUSH_INTERVAL` | OTLP flush interval in seconds | `5.0` | No |

## HTTP Client Configuration

### Connection Pool Settings

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_MAX_CONNECTIONS` | `HTTP_MAX_CONNECTIONS` | Maximum connections in pool | `10` | Integer |
| `HH_MAX_KEEPALIVE_CONNECTIONS` | `HTTP_MAX_KEEPALIVE_CONNECTIONS` | Maximum keepalive connections | `20` | Integer |
| `HH_KEEPALIVE_EXPIRY` | `HTTP_KEEPALIVE_EXPIRY` | Keepalive expiry time (seconds) | `30.0` | Float |
| `HH_POOL_TIMEOUT` | `HTTP_POOL_TIMEOUT` | Pool timeout (seconds) | `10.0` | Float |

### Rate Limiting

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_RATE_LIMIT_CALLS` | `HTTP_RATE_LIMIT_CALLS` | Maximum calls per time window | `100` | Integer |
| `HH_RATE_LIMIT_WINDOW` | `HTTP_RATE_LIMIT_WINDOW` | Rate limit time window (seconds) | `60.0` | Float |

### Proxy Settings

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_HTTP_PROXY` | `HTTP_PROXY`, `http_proxy` | HTTP proxy URL | None | String |
| `HH_HTTPS_PROXY` | `HTTPS_PROXY`, `https_proxy` | HTTPS proxy URL | None | String |
| `HH_NO_PROXY` | `NO_PROXY`, `no_proxy` | Comma-separated list of hosts to bypass proxy | None | String |

### SSL and Redirects

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_VERIFY_SSL` | `VERIFY_SSL` | Verify SSL certificates | `true` | Boolean |
| `HH_FOLLOW_REDIRECTS` | `FOLLOW_REDIRECTS` | Follow HTTP redirects | `true` | Boolean |

## Experiment Harness Configuration

### Experiment Identification

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_EXPERIMENT_ID` | `EXPERIMENT_ID`, `MLFLOW_EXPERIMENT_ID`, `WANDB_RUN_ID`, `COMET_EXPERIMENT_KEY` | Unique experiment identifier | None | String |
| `HH_EXPERIMENT_NAME` | `EXPERIMENT_NAME`, `MLFLOW_EXPERIMENT_NAME`, `WANDB_PROJECT`, `COMET_PROJECT_NAME` | Experiment name | None | String |

### Experiment Variants and Groups

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_EXPERIMENT_VARIANT` | `EXPERIMENT_VARIANT`, `VARIANT`, `AB_TEST_VARIANT`, `TREATMENT` | Experiment variant/treatment | None | String |
| `HH_EXPERIMENT_GROUP` | `EXPERIMENT_GROUP`, `GROUP`, `AB_TEST_GROUP`, `COHORT` | Experiment group/cohort | None | String |

### Experiment Metadata

| Environment Variable | Standard Alternative | Description | Default | Type |
|---------------------|---------------------|-------------|---------|------|
| `HH_EXPERIMENT_METADATA` | `EXPERIMENT_METADATA`, `MLFLOW_TAGS`, `WANDB_TAGS`, `COMET_TAGS` | Experiment metadata/tags | None | String/JSON |

## SDK Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| `HH_TIMEOUT` | Request timeout in seconds | `30.0` | No |
| `HH_MAX_RETRIES` | Maximum retry attempts | `3` | No |

## Usage Examples

### Basic Configuration

```bash
export HH_API_KEY="your-api-key-here"
export HH_PROJECT="my-project"
export HH_SOURCE="development"
```

### HTTP Client Tuning

```bash
export HH_MAX_CONNECTIONS="50"
export HH_RATE_LIMIT_CALLS="200"
export HH_RATE_LIMIT_WINDOW="30"
export HH_HTTP_PROXY="http://proxy.company.com:8080"
export HH_VERIFY_SSL="false"
```

### OTLP Performance Tuning

```bash
# Performance optimized (larger batches, faster flush)
export HH_BATCH_SIZE="200"
export HH_FLUSH_INTERVAL="1.0"

# Memory optimized (smaller batches, slower flush)
export HH_BATCH_SIZE="50"
export HH_FLUSH_INTERVAL="10.0"

# Real-time optimized (very fast flush)
export HH_BATCH_SIZE="10"
export HH_FLUSH_INTERVAL="0.5"
```

### Experiment Harness Integration

```bash
export HH_EXPERIMENT_ID="exp_12345"
export HH_EXPERIMENT_NAME="model-comparison"
export HH_EXPERIMENT_VARIANT="baseline"
export HH_EXPERIMENT_GROUP="control"
export HH_EXPERIMENT_METADATA='{"model_type": "gpt-4", "temperature": 0.7}'
```

### Standard Environment Variable Compatibility

```bash
# These will also work
export HTTP_MAX_CONNECTIONS="50"
export HTTP_PROXY="http://proxy.company.com:8080"
export EXPERIMENT_ID="exp_12345"
export MLFLOW_EXPERIMENT_NAME="model-comparison"
```

## Backwards Compatibility

All existing `HH_` prefixed environment variables continue to work exactly as before. The SDK now also supports standard environment variable names for better integration with existing infrastructure and tools.

## Configuration Precedence

1. **Constructor parameters** (highest priority)
2. **HoneyHive-specific environment variables** (`HH_*`)
3. **Standard environment variables** (e.g., `HTTP_*`, `EXPERIMENT_*`)
4. **Default values** (lowest priority)

## Notes

- Boolean environment variables accept: `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off`
- Numeric environment variables are automatically converted to appropriate types
- JSON environment variables (like `HH_EXPERIMENT_METADATA`) support multiple formats
- The SDK gracefully handles invalid environment variable values by falling back to defaults
- All environment variables can be reloaded at runtime using `config.reload()`
