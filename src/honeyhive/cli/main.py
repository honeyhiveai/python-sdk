"""Enhanced CLI for HoneyHive."""

import json
import sys
import time
from typing import Optional

import click

from ..api.client import HoneyHive
from ..tracer import HoneyHiveTracer
from ..utils.cache import close_global_cache, get_global_cache
from ..utils.config import Config
from ..utils.connection_pool import close_global_pool, get_global_pool


@click.group()
@click.version_option()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def cli(config: Optional[str], verbose: bool, debug: bool) -> None:
    """HoneyHive CLI - LLM Observability and Evaluation Platform."""
    if verbose:
        click.echo("Verbose mode enabled")

    if debug:
        click.echo("Debug mode enabled")

    if config:
        click.echo(f"Using config file: {config}")


@cli.group()
def config() -> None:
    """Configuration management commands.

    Manage HoneyHive configuration including viewing, setting, and updating
    configuration values for API keys, project settings, and other options.
    """


@config.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "env"]),
    default="json",
    help="Output format",
)
def show(output_format: str) -> None:
    """Show current configuration.

    Display the current HoneyHive configuration in various formats.

    Args:
        output_format: Output format for configuration display
            - json: JSON format (default)
            - yaml: YAML format
            - env: Environment variable format
    """
    from ..utils.config import config

    if output_format == "json":
        # Convert config to a serializable dictionary
        config_dict = {
            "api_key": config.api_key,
            "api_url": config.api_url,
            "project": config.project,
            "source": config.source,
            "debug_mode": config.debug_mode,
            "test_mode": config.test_mode,
            "experiment_id": config.experiment_id,
            "experiment_name": config.experiment_name,
            "experiment_variant": config.experiment_variant,
            "experiment_group": config.experiment_group,
            "experiment_metadata": config.experiment_metadata,
        }
        click.echo(json.dumps(config_dict, indent=2))
    elif output_format == "yaml":
        import yaml

        # Convert config to a serializable dictionary
        config_dict = {
            "api_key": config.api_key,
            "api_url": config.api_url,
            "project": config.project,
            "source": config.source,
            "debug_mode": config.debug_mode,
            "test_mode": config.test_mode,
            "experiment_id": config.experiment_id,
            "experiment_name": config.experiment_name,
            "experiment_variant": config.experiment_variant,
            "experiment_group": config.experiment_group,
            "experiment_metadata": config.experiment_metadata,
        }
        click.echo(yaml.dump(config_dict, default_flow_style=False))
    elif output_format == "env":
        # Convert config to environment variables
        config_dict = {
            "api_key": config.api_key,
            "api_url": config.api_url,
            "project": config.project,
            "source": config.source,
            "debug_mode": config.debug_mode,
            "test_mode": config.test_mode,
            "experiment_id": config.experiment_id,
            "experiment_name": config.experiment_name,
            "experiment_variant": config.experiment_variant,
            "experiment_group": config.experiment_group,
            "experiment_metadata": config.experiment_metadata,
        }
        for key, value in config_dict.items():
            if value is not None:
                click.echo(f"HH_{key.upper()}={value}")


@config.command()
@click.option("--key", required=True, help="Configuration key")
@click.option("--value", required=True, help="Configuration value")
def set(key: str, value: str) -> None:
    """Set configuration value.

    Update a specific configuration key with a new value.

    Args:
        key: Configuration key to update
        value: New value for the configuration key
    """
    from ..utils.config import config

    if hasattr(config, key):
        setattr(config, key, value)
        click.echo(f"Set {key} = {value}")
    else:
        click.echo(f"Unknown configuration key: {key}", err=True)
        sys.exit(1)


@cli.group()
def trace() -> None:
    """Tracing commands.

    Manage OpenTelemetry tracing including starting spans, enriching sessions,
    and monitoring trace performance.
    """


@trace.command()
@click.option("--name", required=True, help="Span name")
@click.option("--session-id", help="Session ID")
@click.option("--attributes", help="Span attributes (JSON)")
def start(name: str, session_id: Optional[str], attributes: Optional[str]) -> None:
    """Start a trace span.

    Create and start a new trace span with the specified name and attributes.
    The span will remain active until manually ended or the process exits.

    Args:
        name: Name of the span to create
        session_id: Optional session ID to associate with the span
        attributes: JSON string containing span attributes
    """
    try:
        tracer = HoneyHiveTracer()

        # Parse attributes
        span_attributes = {}
        if attributes:
            try:
                span_attributes = json.loads(attributes)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for attributes", err=True)
                sys.exit(1)

        # Start span
        with tracer.start_span(
            name=name, session_id=session_id, attributes=span_attributes
        ):
            click.echo(f"Started span: {name}")
            click.echo("Press Enter to end span...")
            input()

        click.echo(f"Ended span: {name}")

    except Exception as e:
        click.echo(f"Failed to start trace: {e}", err=True)
        sys.exit(1)


@trace.command()
@click.option("--session-id", help="Session ID to enrich")
@click.option("--metadata", help="Metadata (JSON)")
@click.option("--feedback", help="User feedback (JSON)")
@click.option("--metrics", help="Metrics (JSON)")
def enrich(
    session_id: Optional[str],
    metadata: Optional[str],
    feedback: Optional[str],
    metrics: Optional[str],
) -> None:
    """Enrich a session with additional data.

    Add metadata, feedback, and metrics to an existing session to provide
    additional context and evaluation data.

    Args:
        session_id: ID of the session to enrich
        metadata: JSON string containing session metadata
        feedback: JSON string containing user feedback
        metrics: JSON string containing computed metrics
    """
    try:
        if not session_id:
            click.echo("Session ID is required", err=True)
            sys.exit(1)

        # Parse JSON data
        enrich_data = {}

        if metadata:
            try:
                enrich_data["metadata"] = json.loads(metadata)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for metadata", err=True)
                sys.exit(1)

        if feedback:
            try:
                enrich_data["feedback"] = json.loads(feedback)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for feedback", err=True)
                sys.exit(1)

        if metrics:
            try:
                enrich_data["metrics"] = json.loads(metrics)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for metrics", err=True)
                sys.exit(1)

        # For now, just show what would be enriched
        click.echo(f"Would enrich session {session_id} with: {enrich_data}")
        click.echo("Note: Session enrichment is not yet implemented in this version")

    except Exception as e:
        click.echo(f"Failed to enrich session: {e}", err=True)
        sys.exit(1)


@cli.group()
def api() -> None:
    """API client commands.

    Interact with the HoneyHive API directly, including making requests,
    managing resources, and testing API endpoints.
    """


@api.command()
@click.option("--method", default="GET", help="HTTP method")
@click.option("--url", required=True, help="Request URL")
@click.option("--headers", help="Request headers (JSON)")
@click.option("--data", help="Request data (JSON)")
@click.option("--timeout", type=float, default=30.0, help="Request timeout")
def request(
    method: str, url: str, headers: Optional[str], data: Optional[str], timeout: float
) -> None:
    """Make an API request.

    Send an HTTP request to the HoneyHive API using the configured client.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: API endpoint URL
        headers: JSON string containing request headers
        data: JSON string containing request body data
        timeout: Request timeout in seconds
    """
    try:
        client = HoneyHive()

        # Parse headers and data
        request_headers = {}
        if headers:
            try:
                request_headers = json.loads(headers)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for headers", err=True)
                sys.exit(1)

        request_data = None
        if data:
            try:
                request_data = json.loads(data)
            except json.JSONDecodeError:
                click.echo("Invalid JSON for data", err=True)
                sys.exit(1)

        # Make request
        start_time = time.time()
        response = client.sync_client.request(
            method=method,
            url=url,
            headers=request_headers,
            json=request_data,
            timeout=timeout,
        )
        duration = time.time() - start_time

        # Display response
        click.echo(f"Status: {response.status_code}")
        click.echo(f"Duration: {duration:.3f}s")
        click.echo(f"Headers: {dict(response.headers)}")

        try:
            response_data = response.json()
            click.echo(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            click.echo(f"Response: {response.text}")

    except Exception as e:
        click.echo(f"API request failed: {e}", err=True)
        sys.exit(1)


@cli.group()
def monitor() -> None:
    """Monitoring and performance commands.

    Monitor system health, performance metrics, and operational status
    of the HoneyHive SDK and its components.
    """


@monitor.command()
def status() -> None:
    """Show system status.

    Display comprehensive status information including configuration,
    tracer status, cache performance, and system health metrics.
    """
    try:
        # Configuration status
        config = Config()
        click.echo("=== Configuration Status ===")
        click.echo(f"API Key: {'✓' if config.api_key else '✗'}")
        click.echo(f"Project: {config.project or 'Not set'}")
        click.echo(f"Source: {config.source}")
        click.echo(f"Debug Mode: {config.debug_mode}")
        click.echo(f"Tracing Enabled: {not config.disable_tracing}")

        # Tracer status
        click.echo("\n=== Tracer Status ===")
        try:
            # Note: In the new multi-instance approach, we can't easily check for existing tracers
            # Users should manage their own tracer instances
            click.echo("ℹ️  Tracer status: Multi-instance mode enabled")
            click.echo(
                "   Create tracers with: HoneyHiveTracer(api_key='...', project='...')"
            )
            click.echo("   Multiple tracers can coexist in the same runtime")
        except Exception as e:
            click.echo(f"✗ Tracer error: {e}")

        # Cache status
        click.echo("\n=== Cache Status ===")
        try:
            cache = get_global_cache()
            stats = cache.get_stats()
            click.echo(f"✓ Cache active")
            click.echo(f"  Size: {stats['size']}/{stats['max_size']}")
            click.echo(f"  Hit Rate: {stats['hit_rate']:.2%}")
        except Exception as e:
            click.echo(f"✗ Cache error: {e}")

        # Connection pool status
        click.echo("\n=== Connection Pool Status ===")
        try:
            pool = get_global_pool()
            stats = pool.get_stats()
            click.echo(f"✓ Connection pool active")
            click.echo(f"  Total Requests: {stats['total_requests']}")
            click.echo(f"  Pool Hits: {stats['pool_hits']}")
            click.echo(f"  Pool Misses: {stats['pool_misses']}")
        except Exception as e:
            click.echo(f"✗ Connection pool error: {e}")

    except Exception as e:
        click.echo(f"Failed to get status: {e}", err=True)
        sys.exit(1)


@monitor.command()
@click.option("--duration", type=int, default=60, help="Monitor duration in seconds")
@click.option("--interval", type=float, default=5.0, help="Update interval in seconds")
def watch(duration: int, interval: float) -> None:
    """Monitor system in real-time.

    Continuously monitor HoneyHive system performance metrics
    including cache statistics and connection pool performance.

    Args:
        duration: Total monitoring duration in seconds
        interval: Update interval between status checks in seconds
    """
    try:
        click.echo(f"Monitoring for {duration} seconds (updates every {interval}s)")
        click.echo("Press Ctrl+C to stop early")
        click.echo()

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            try:
                # Get current stats
                cache_stats = get_global_cache().get_stats()
                pool_stats = get_global_pool().get_stats()

                # Clear screen and show stats
                click.clear()
                click.echo(f"=== HoneyHive Monitor ({time.strftime('%H:%M:%S')}) ===")
                click.echo(f"Elapsed: {time.time() - start_time:.1f}s / {duration}s")
                click.echo()

                click.echo("Cache:")
                click.echo(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
                click.echo(f"  Hit Rate: {cache_stats['hit_rate']:.2%}")
                click.echo(
                    f"  Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}"
                )
                click.echo()

                click.echo("Connection Pool:")
                click.echo(f"  Total Requests: {pool_stats['total_requests']}")
                click.echo(f"  Pool Hits: {pool_stats['pool_hits']}")
                click.echo(f"  Pool Misses: {pool_stats['pool_misses']}")
                click.echo(f"  Active Connections: {pool_stats['active_connections']}")

                time.sleep(interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                click.echo(f"Error getting stats: {e}")
                time.sleep(interval)

        click.echo("\nMonitoring completed")

    except Exception as e:
        click.echo(f"Failed to start monitoring: {e}", err=True)
        sys.exit(1)


@cli.group()
def performance() -> None:
    """Performance analysis commands.

    Commands for analyzing and benchmarking HoneyHive SDK
    performance including cache operations and system metrics.
    """


@performance.command()
@click.option("--iterations", type=int, default=1000, help="Number of iterations")
@click.option("--warmup", type=int, default=100, help="Warmup iterations")
def benchmark(iterations: int, warmup: int) -> None:
    """Run performance benchmarks.

    Execute comprehensive performance benchmarks for cache operations
    and other system components to measure performance characteristics.

    Args:
        iterations: Number of benchmark iterations to run
        warmup: Number of warmup iterations before benchmarking
    """
    try:
        click.echo("Running performance benchmarks...")
        click.echo(f"Iterations: {iterations}")
        click.echo(f"Warmup: {warmup}")
        click.echo()

        # Warmup
        if warmup > 0:
            click.echo("Warming up...")
            for i in range(warmup):
                # Simple operation for warmup
                _ = i * i
            click.echo("Warmup completed")
            click.echo()

        # Benchmark cache operations
        click.echo("=== Cache Performance ===")
        cache = get_global_cache()

        if iterations > 0:
            # Set operations
            start_time = time.time()
            for i in range(iterations):
                cache.set(f"key_{i}", f"value_{i}")
            set_duration = time.time() - start_time

            # Get operations
            start_time = time.time()
            for i in range(iterations):
                _ = cache.get(f"key_{i}")
            get_duration = time.time() - start_time

            click.echo(f"Set operations: {iterations / set_duration:.0f} ops/s")
            click.echo(f"Get operations: {iterations / get_duration:.0f} ops/s")
        else:
            click.echo("Skipping cache benchmarks (0 iterations)")
            set_duration = 0
            get_duration = 0

        click.echo()

        # Benchmark tracer operations
        click.echo("=== Tracer Performance ===")
        try:
            if iterations > 0:
                # Note: In the new multi-instance approach, we can't easily access existing tracers
                # Users should create their own tracer instances for benchmarking
                click.echo("ℹ️  Tracer benchmarks: Multi-instance mode enabled")
                click.echo("   Create a tracer for benchmarking:")
                click.echo("   tracer = HoneyHiveTracer(api_key='...', project='...')")
                click.echo("   Then run: with tracer.start_span('name'): pass")
            elif iterations == 0:
                click.echo("Skipping tracer benchmarks (0 iterations)")
            else:
                click.echo("Tracer not available")
        except Exception as e:
            click.echo(f"Tracer benchmark failed: {e}")

        click.echo()
        click.echo("Benchmarks completed")

    except Exception as e:
        click.echo(f"Benchmark failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def cleanup() -> None:
    """Clean up resources.

    Safely shut down and clean up all HoneyHive SDK resources
    including cache, connection pools, and other system components.
    """
    try:
        click.echo("Cleaning up resources...")

        # Close cache
        try:
            close_global_cache()
            click.echo("✓ Cache closed")
        except Exception as e:
            click.echo(f"✗ Cache cleanup failed: {e}")

        # Close connection pool
        try:
            close_global_pool()
            click.echo("✓ Connection pool closed")
        except Exception as e:
            click.echo(f"✗ Connection pool cleanup failed: {e}")

        click.echo("Cleanup completed")

    except Exception as e:
        click.echo(f"Cleanup failed: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
