"""Dynamic HTTP instrumentation for HoneyHive tracing.

This module provides flexible HTTP instrumentation using dynamic library
detection, configuration-driven enablement, and extensible tracing patterns.
All instrumentation logic is designed to be non-intrusive and gracefully
degrade when libraries are not available.
"""

# pylint: disable=duplicate-code
# Standard exception logging patterns are intentionally consistent for error handling

import os
from typing import TYPE_CHECKING, Any, Dict, List

# Import shared logging utility
from ...utils.logger import safe_log

if TYPE_CHECKING:
    import httpx
    import requests


class HTTPInstrumentation:
    """Dynamic HTTP instrumentation for automatic request tracing."""

    def __init__(self, tracer_instance: Any = None) -> None:
        """Initialize HTTP instrumentation with dynamic library detection.

        Args:
            tracer_instance: Optional tracer instance for logging context
        """
        self.tracer_instance = tracer_instance
        self._library_availability = self._detect_libraries_dynamically()
        self._original_methods: Dict[str, Any] = {}
        self._is_instrumented = False
        self._instrumentation_config = self._build_instrumentation_config_dynamically()

    def _detect_libraries_dynamically(self) -> Dict[str, bool]:
        """Dynamically detect available HTTP libraries.

        Returns:
            Dictionary mapping library names to availability status
        """
        libraries = {}

        # Dynamic library detection patterns
        library_detection_map = {
            "httpx": "httpx",
            "requests": "requests",
            "aiohttp": "aiohttp",
            "urllib3": "urllib3",
        }

        for lib_name, import_name in library_detection_map.items():
            try:
                __import__(import_name)
                libraries[lib_name] = True
                safe_log(
                    self.tracer_instance,
                    "debug",
                    f"HTTP library detected: {lib_name}",
                    honeyhive_data={"library": lib_name},
                )
            except ImportError:
                libraries[lib_name] = False

        return libraries

    def _build_instrumentation_config_dynamically(self) -> Dict[str, Any]:
        """Dynamically build instrumentation configuration.

        Returns:
            Configuration dictionary for instrumentation
        """
        return {
            "enabled": not self._is_http_tracing_disabled_dynamically(),
            "libraries": {
                "httpx": {
                    "enabled": self._library_availability.get("httpx", False),
                    "methods": ["request"],
                    "classes": ["Client", "AsyncClient"],
                },
                "requests": {
                    "enabled": self._library_availability.get("requests", False),
                    "methods": ["request"],
                    "classes": ["Session"],
                },
            },
            "span_attributes": {
                "http.method": True,
                "http.url": True,
                "http.status_code": True,
                "http.user_agent": False,  # Privacy consideration
            },
            "error_handling": {
                "graceful_degradation": True,
                "log_failures": True,
                "fallback_to_original": True,
            },
        }

    def _is_http_tracing_disabled_dynamically(self) -> bool:
        """Dynamically check if HTTP tracing is disabled.

        Returns:
            True if HTTP tracing is disabled
        """
        # Dynamic environment variable patterns
        disable_patterns = [
            "HH_DISABLE_HTTP_TRACING",
            "HONEYHIVE_DISABLE_HTTP_TRACING",
            "DISABLE_HTTP_TRACING",
        ]

        for pattern in disable_patterns:
            value = os.getenv(pattern, "false").lower()
            if value in {"true", "1", "yes", "on"}:
                return True

        return False

    def instrument(self) -> None:
        """Dynamically instrument HTTP libraries for automatic tracing."""
        if self._is_instrumented:
            safe_log(
                self.tracer_instance, "debug", "HTTP instrumentation already active"
            )
            return

        if not self._instrumentation_config["enabled"]:
            safe_log(
                self.tracer_instance, "info", "HTTP tracing disabled by configuration"
            )
            return

        # Dynamic instrumentation execution
        instrumentation_results = self._execute_instrumentation_dynamically()

        self._is_instrumented = any(instrumentation_results.values())

        safe_log(
            self.tracer_instance,
            "info",
            "HTTP instrumentation completed",
            honeyhive_data={
                "instrumented_libraries": [
                    lib for lib, success in instrumentation_results.items() if success
                ],
                "total_instrumented": sum(instrumentation_results.values()),
            },
        )

    def _execute_instrumentation_dynamically(self) -> Dict[str, bool]:
        """Dynamically execute instrumentation for available libraries.

        Returns:
            Dictionary mapping library names to instrumentation success status
        """
        results = {}

        # Dynamic instrumentation strategies
        instrumentation_strategies = {
            "httpx": self._instrument_httpx_dynamically,
            "requests": self._instrument_requests_dynamically,
        }

        for library_name, strategy in instrumentation_strategies.items():
            if self._should_instrument_library_dynamically(library_name):
                try:
                    success = strategy()
                    results[library_name] = success

                    if success:
                        safe_log(
                            self.tracer_instance,
                            "debug",
                            f"Successfully instrumented {library_name}",
                            honeyhive_data={"library": library_name},
                        )
                    else:
                        safe_log(
                            self.tracer_instance,
                            "warning",
                            f"Failed to instrument {library_name}",
                            honeyhive_data={"library": library_name},
                        )

                except Exception as e:
                    results[library_name] = False
                    safe_log(
                        self.tracer_instance,
                        "error",
                        f"Error instrumenting {library_name}",
                        honeyhive_data={
                            "library": library_name,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )
            else:
                results[library_name] = False

        return results

    def _should_instrument_library_dynamically(self, library_name: str) -> bool:
        """Dynamically determine if library should be instrumented.

        Args:
            library_name: Name of the library to check

        Returns:
            True if library should be instrumented
        """
        library_config = self._instrumentation_config["libraries"].get(library_name, {})

        return library_config.get("enabled", False) and self._library_availability.get(
            library_name, False
        )

    def _instrument_httpx_dynamically(self) -> bool:
        """Dynamically instrument httpx library.

        Returns:
            True if instrumentation successful
        """
        try:
            import httpx  # pylint: disable=import-outside-toplevel

            # Store original methods dynamically
            original_methods = self._store_original_methods_dynamically(
                httpx, ["Client", "AsyncClient"], ["request"]
            )

            if not original_methods:
                return False

            self._original_methods["httpx"] = original_methods

            # Create instrumented methods dynamically
            instrumented_methods = self._create_instrumented_methods_dynamically(
                "httpx", original_methods
            )

            # Apply instrumentation dynamically
            return self._apply_instrumentation_dynamically(
                httpx, instrumented_methods, ["Client", "AsyncClient"]
            )

        except ImportError:
            safe_log(
                self.tracer_instance, "debug", "httpx not available for instrumentation"
            )
            return False
        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to instrument httpx",
                honeyhive_data={"error": str(e)},
            )
            return False

    def _instrument_httpx(self) -> None:
        """Instrument httpx for automatic tracing (compatibility method)."""
        # This is a compatibility method for tests that expect the original naming
        self._instrument_httpx_dynamically()

    def _instrument_requests(self) -> None:
        """Instrument requests for automatic tracing (compatibility method)."""
        # This is a compatibility method for tests that expect the original naming
        self._instrument_requests_dynamically()

    def _instrument_requests_dynamically(self) -> bool:
        """Dynamically instrument requests library.

        Returns:
            True if instrumentation successful
        """
        try:
            import requests  # pylint: disable=import-outside-toplevel

            # Store original methods dynamically
            original_methods = self._store_original_methods_dynamically(
                requests, ["Session"], ["request"]
            )

            if not original_methods:
                return False

            self._original_methods["requests"] = original_methods

            # Create instrumented methods dynamically
            instrumented_methods = self._create_instrumented_methods_dynamically(
                "requests", original_methods
            )

            # Apply instrumentation dynamically
            return self._apply_instrumentation_dynamically(
                requests, instrumented_methods, ["Session"]
            )

        except ImportError:
            safe_log(
                self.tracer_instance,
                "debug",
                "requests not available for instrumentation",
            )
            return False
        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to instrument requests",
                honeyhive_data={"error": str(e)},
            )
            return False

    def _store_original_methods_dynamically(
        self, module: Any, class_names: List[str], method_names: List[str]
    ) -> Dict[str, Any]:
        """Dynamically store original methods before instrumentation.

        Args:
            module: Module containing classes to instrument
            class_names: Names of classes to instrument
            method_names: Names of methods to instrument

        Returns:
            Dictionary of original methods
        """
        original_methods = {}

        for class_name in class_names:
            if not hasattr(module, class_name):
                continue

            class_obj = getattr(module, class_name)

            for method_name in method_names:
                if hasattr(class_obj, method_name):
                    method_key = f"{class_name}.{method_name}"
                    original_methods[method_key] = getattr(class_obj, method_name)

        return original_methods

    def _create_instrumented_methods_dynamically(
        self, library_name: str, original_methods: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dynamically create instrumented methods.

        Args:
            library_name: Name of the library being instrumented
            original_methods: Dictionary of original methods

        Returns:
            Dictionary of instrumented methods
        """
        instrumented_methods = {}

        for method_key, original_method in original_methods.items():
            # Create instrumented wrapper dynamically
            instrumented_method = self._create_method_wrapper_dynamically(
                library_name, method_key, original_method
            )
            instrumented_methods[method_key] = instrumented_method

        return instrumented_methods

    def _create_method_wrapper_dynamically(
        self, library_name: str, method_key: str, original_method: Any
    ) -> Any:
        """Dynamically create method wrapper with tracing.

        Args:
            library_name: Name of the library
            method_key: Key identifying the method
            original_method: Original method to wrap

        Returns:
            Wrapped method with tracing
        """

        def instrumented_wrapper(self_obj: Any, *args: Any, **kwargs: Any) -> Any:
            """Dynamically instrumented method wrapper."""
            try:
                # Dynamic span creation and tracing
                return self._execute_with_tracing_dynamically(
                    library_name,
                    method_key,
                    original_method=original_method,
                    self_obj=self_obj,
                    args=args,
                    kwargs=kwargs,
                )
            except Exception as e:
                # Graceful degradation on instrumentation failure
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Instrumentation wrapper failed, falling back to original",
                    honeyhive_data={
                        "library": library_name,
                        "method": method_key,
                        "error": str(e),
                    },
                )
                return original_method(self_obj, *args, **kwargs)

        return instrumented_wrapper

    # pylint: disable=too-many-arguments
    # Justification: HTTP tracing execution requires multiple parameters for
    # library identification, method handling, and argument processing.
    def _execute_with_tracing_dynamically(
        self,
        library_name: str,
        _method_key: str,
        *,
        original_method: Any,
        self_obj: Any,
        args: tuple,
        kwargs: dict,
    ) -> Any:
        """Dynamically execute method with tracing.

        Args:
            library_name: Name of the library
            method_key: Method identifier
            original_method: Original method to call
            self_obj: Instance object
            args: Method arguments
            kwargs: Method keyword arguments

        Returns:
            Result of original method call
        """
        # For now, just call the original method
        # Future enhancement: Add actual tracing logic here

        # Dynamic attribute extraction for tracing
        trace_attributes = self._extract_trace_attributes_dynamically(
            library_name, args, kwargs
        )

        safe_log(
            self.tracer_instance,
            "debug",
            "HTTP request traced",
            honeyhive_data={
                "library": library_name,
                "method": _method_key,
                "attributes": trace_attributes,
            },
        )

        return original_method(self_obj, *args, **kwargs)

    def _extract_trace_attributes_dynamically(
        self, library_name: str, args: tuple, _kwargs: dict
    ) -> Dict[str, Any]:
        """Dynamically extract trace attributes from method arguments.

        Args:
            library_name: Name of the library
            args: Method arguments
            kwargs: Method keyword arguments

        Returns:
            Dictionary of trace attributes
        """
        attributes = {}

        # Dynamic attribute extraction patterns
        if library_name in {"httpx", "requests"}:
            # Extract HTTP method and URL
            if len(args) >= 1:
                attributes["http.method"] = str(args[0]).upper()
            if len(args) >= 2:
                attributes["http.url"] = str(args[1])

        return attributes

    def _apply_instrumentation_dynamically(
        self, module: Any, instrumented_methods: Dict[str, Any], class_names: List[str]
    ) -> bool:
        """Dynamically apply instrumentation to module classes.

        Args:
            module: Module to instrument
            instrumented_methods: Dictionary of instrumented methods
            class_names: Names of classes to instrument

        Returns:
            True if instrumentation applied successfully
        """
        try:
            for method_key, instrumented_method in instrumented_methods.items():
                class_name, method_name = method_key.split(".", 1)

                if class_name in class_names and hasattr(module, class_name):
                    class_obj = getattr(module, class_name)
                    setattr(class_obj, method_name, instrumented_method)

            return True

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to apply instrumentation",
                honeyhive_data={
                    "module": module.__name__,
                    "error": str(e),
                },
            )
            return False

    def uninstrument(self) -> None:
        """Dynamically remove HTTP instrumentation."""
        if not self._is_instrumented:
            safe_log(self.tracer_instance, "debug", "HTTP instrumentation not active")
            return

        # Dynamic uninstrumentation
        uninstrumentation_results = self._execute_uninstrumentation_dynamically()

        self._is_instrumented = False

        safe_log(
            self.tracer_instance,
            "info",
            "HTTP uninstrumentation completed",
            honeyhive_data={
                "uninstrumented_libraries": [
                    lib for lib, success in uninstrumentation_results.items() if success
                ],
                "total_uninstrumented": sum(uninstrumentation_results.values()),
            },
        )

    def _execute_uninstrumentation_dynamically(self) -> Dict[str, bool]:
        """Dynamically execute uninstrumentation for all libraries.

        Returns:
            Dictionary mapping library names to uninstrumentation success status
        """
        results = {}

        for library_name, original_methods in self._original_methods.items():
            try:
                success = self._restore_original_methods_dynamically(
                    library_name, original_methods
                )
                results[library_name] = success
            except Exception as e:
                results[library_name] = False
                safe_log(
                    self.tracer_instance,
                    "error",
                    f"Error uninstrumenting {library_name}",
                    honeyhive_data={
                        "library": library_name,
                        "error": str(e),
                    },
                )

        return results

    def _restore_original_methods_dynamically(
        self, library_name: str, original_methods: Dict[str, Any]
    ) -> bool:
        """Dynamically restore original methods.

        Args:
            library_name: Name of the library
            original_methods: Dictionary of original methods

        Returns:
            True if restoration successful
        """
        try:
            # Dynamic module import
            module = __import__(library_name)

            # Restore methods dynamically
            for method_key, original_method in original_methods.items():
                class_name, method_name = method_key.split(".", 1)

                if hasattr(module, class_name):
                    class_obj = getattr(module, class_name)
                    setattr(class_obj, method_name, original_method)

            return True

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                f"Failed to restore original methods for {library_name}",
                honeyhive_data={"error": str(e)},
            )
            return False

    def get_instrumentation_status(self) -> Dict[str, Any]:
        """Get dynamic instrumentation status.

        Returns:
            Dictionary with instrumentation status information
        """
        return {
            "is_instrumented": self._is_instrumented,
            "enabled": self._instrumentation_config["enabled"],
            "library_availability": self._library_availability,
            "instrumented_libraries": list(self._original_methods.keys()),
            "configuration": self._instrumentation_config,
        }


class DummyInstrumentation:
    """Dummy HTTP instrumentation that does nothing when HTTP tracing is disabled."""

    def __init__(self, tracer_instance: Any = None) -> None:
        """Initialize dummy instrumentation.

        Args:
            tracer_instance: Optional tracer instance for logging context
        """
        self.tracer_instance = tracer_instance

    def instrument(self) -> None:
        """No-op instrument method."""
        safe_log(
            self.tracer_instance,
            "debug",
            "HTTP instrumentation disabled - using dummy implementation",
        )

    def uninstrument(self) -> None:
        """No-op uninstrument method."""

    def get_instrumentation_status(self) -> Dict[str, Any]:
        """Get dummy instrumentation status."""
        return {
            "is_instrumented": False,
            "enabled": False,
            "library_availability": {},
            "instrumented_libraries": [],
            "configuration": {"enabled": False},
        }


# Global instrumentation instance with dynamic selection
def _create_instrumentation_instance_dynamically() -> Any:
    """Dynamically create appropriate instrumentation instance.

    Returns:
        HTTPInstrumentation or DummyInstrumentation based on configuration
    """
    # Check if HTTP tracing is disabled at import time
    disable_patterns = [
        "HH_DISABLE_HTTP_TRACING",
        "HONEYHIVE_DISABLE_HTTP_TRACING",
        "DISABLE_HTTP_TRACING",
    ]

    for pattern in disable_patterns:
        if os.getenv(pattern, "false").lower() in {"true", "1", "yes", "on"}:
            return DummyInstrumentation()

    return HTTPInstrumentation()


# Global instrumentation instance
_instrumentation = _create_instrumentation_instance_dynamically()


def instrument_http() -> None:
    """Dynamically instrument HTTP libraries for automatic tracing."""
    _instrumentation.instrument()


def uninstrument_http() -> None:
    """Dynamically remove HTTP instrumentation."""
    _instrumentation.uninstrument()


def get_http_instrumentation_status() -> Dict[str, Any]:
    """Get current HTTP instrumentation status.

    Returns:
        Dictionary with instrumentation status information
    """
    result = _instrumentation.get_instrumentation_status()
    return dict(result) if result else {}
