import uuid
from traceback import print_exc
import os
import sys
import threading
import io
from contextlib import redirect_stdout
import subprocess
from typing import Dict, Any, Optional

# from honeyhive.utils.telemetry import Telemetry
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import operations, components, errors
from honeyhive.sdk import HoneyHive

from traceloop.sdk import Traceloop
from traceloop.sdk.tracing.tracing import TracerWrapper

from opentelemetry import context, baggage
from opentelemetry.context import Context
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

DEFAULT_API_URL = "https://api.honeyhive.ai"

class HoneyHiveTracer:
    """HoneyHive distributed tracing client.
    
    This class provides distributed tracing capabilities for applications using
    the HoneyHive platform. It integrates with OpenTelemetry to capture and
    export trace data, session information, and contextual metadata.
    
    The tracer automatically instruments applications and provides methods for
    session management, context linking, and span enrichment.
    
    Attributes:
        verbose (bool): Enable verbose logging output
        api_key (str): HoneyHive API key for authentication
        is_evaluation (bool): Whether this tracer is used for evaluation workloads
        server_url (str): HoneyHive server URL endpoint
        session_id (str): Current session identifier
        project (str): Project name
        source (str): Source environment identifier
        baggage (BaggageDict): Context propagation data
        tags (dict): User-defined tags for the session
    """
    
    # Class-level configuration
    verbose = False
    api_key = None
    server_url = None
    
    # Class-level state management
    _is_traceloop_initialized = False
    is_evaluation = False
    _flush_lock = threading.RLock()
    propagator = None  # Will be set when Traceloop is initialized

    def __init__(
        self,
        api_key=None,
        project=None,
        session_name=None,
        source=None,
        server_url=None,
        session_id=None,
        disable_http_tracing=False,
        disable_batch=False,
        verbose=False,
        inputs=None,
        is_evaluation=False,
        run_id=None,
        dataset_id=None,
        datapoint_id=None,
        link_carrier=None,
        tags=None
    ):
        """Initialize the HoneyHive tracer.
        
        Args:
            api_key (str, optional): HoneyHive API key. If not provided, will use HH_API_KEY env var
            project (str, optional): Project name. If not provided, will use HH_PROJECT env var
            session_name (str, optional): Session name. Defaults to script filename
            source (str, optional): Source environment. If not provided, will use HH_SOURCE env var (default: 'dev')
            server_url (str, optional): HoneyHive server URL. If not provided, will use HH_API_URL env var
            session_id (str, optional): Existing session ID to use. If not provided, creates new session
            disable_http_tracing (bool, optional): Disable HTTP request tracing. Defaults to False
            disable_batch (bool, optional): Disable batch span export. Defaults to False
            verbose (bool, optional): Enable verbose logging. Defaults to False
            inputs (dict, optional): Initial inputs for the session
            is_evaluation (bool, optional): Whether this is an evaluation session. Defaults to False
            run_id (str, optional): Evaluation run ID (only used with is_evaluation=True)
            dataset_id (str, optional): Dataset ID (only used with is_evaluation=True)
            datapoint_id (str, optional): Datapoint ID (only used with is_evaluation=True)
            link_carrier (dict, optional): Context carrier to link with parent trace
            tags (dict, optional): User-defined tags to associate with the session
            
        Raises:
            Exception: If required parameters are missing or invalid
            errors.SDKError: If session_id is not a valid UUID
        """
        
        # if HoneyHiveTracer is already initialized, get association properties from the context
        ctx: Context = context.get_current()
        association_properties = ctx.get('association_properties') if ctx is not None else None
        if association_properties is not None and isinstance(association_properties, dict):
            # Unpack association properties by name - only use if they're valid values
            ctx_session_id = association_properties.get('session_id')
            ctx_project = association_properties.get('project')
            ctx_source = association_properties.get('source')
            ctx_disable_http_tracing = association_properties.get('disable_http_tracing')
            ctx_run_id = association_properties.get('run_id')
            ctx_dataset_id = association_properties.get('dataset_id')
            ctx_datapoint_id = association_properties.get('datapoint_id')
            
            # Only override parameters if context values are valid strings (not mocks)
            if ctx_session_id is not None and isinstance(ctx_session_id, str):
                session_id = ctx_session_id
            if ctx_project is not None and isinstance(ctx_project, str):
                project = ctx_project
            if ctx_source is not None and isinstance(ctx_source, str):
                source = ctx_source
            if ctx_disable_http_tracing is not None:
                disable_http_tracing = ctx_disable_http_tracing or False
            if ctx_run_id is not None:
                run_id = ctx_run_id
            if ctx_dataset_id is not None:
                dataset_id = ctx_dataset_id
            if ctx_datapoint_id is not None:
                datapoint_id = ctx_datapoint_id

        try:
            # Configure core settings
            api_key = self._configure_api_key(api_key)
            server_url = self._configure_server_url(server_url)
            project = self._configure_project(project)
            
            # Configure additional settings
            session_name = self._configure_session_name(session_name)
            source = self._configure_source(source)
            
            # verbose
            HoneyHiveTracer.verbose = verbose

            # tags
            self.tags = tags or {}
            self._tags_initialized = False
            
            # Initialize session
            self._initialize_session(session_id, session_name, project, source, inputs)

            # Setup baggage and context
            self._setup_baggage(project, source, disable_http_tracing, is_evaluation, run_id, dataset_id, datapoint_id)

            # Initialize Traceloop
            self._initialize_traceloop(disable_batch, is_evaluation)

            # Setup context linking
            self._setup_context_linking(link_carrier)
            
            # ------------------------------------------------------------
            # TODO: log-based session initialization
            # ------------------------------------------------------------
            # save the init metadata
            # self._init_metadata = {
            #     "project": project,
            #     "session_name": session_name,
            #     "source": source,
            #     "server_url": server_url,
            #     "verbose": verbose,
            #     "disable_batch": disable_batch,
            #     "link_carrier_provided": link_carrier is not None,
            #     "instrumentation_id": HoneyHiveTracer.instrumentation_id,
            # }
            
            # # log the session initialization
            # @trace
            # def __session_init():
            #     enrich_span(metadata={
            #         '_init_metadata': self._init_metadata
            #     })
            # __session_init()
            # ------------------------------------------------------------
        except errors.SDKError as e:
            # Re-raise SDK exceptions for proper error handling
            # Ensure tags are still initialized even on error
            if not hasattr(self, 'tags'):
                self.tags = tags or {}
            self._tags_initialized = False
            raise e
        except Exception as e:
            # Handle configuration errors by printing but not raising
            if not hasattr(self, 'tags'):
                self.tags = tags or {}
            self._tags_initialized = False
            
            error_msg = str(e)
            print(f"\033[91mHoneyHive SDK Error: {error_msg}\033[0m")
            
            # Log additional details if verbose
            if HoneyHiveTracer.verbose:
                print_exc()


    # TODO: remove this, legacy DX
    @staticmethod
    def init(*args, **kwargs) -> 'HoneyHiveTracer':
        """Legacy initialization method.
        
        This is a convenience method that creates a new HoneyHiveTracer instance.
        Prefer using HoneyHiveTracer() constructor directly.
        
        Args:
            *args: Positional arguments passed to HoneyHiveTracer constructor
            **kwargs: Keyword arguments passed to HoneyHiveTracer constructor
            
        Returns:
            HoneyHiveTracer: New tracer instance
        """
        return HoneyHiveTracer(*args, **kwargs)
    
    def _configure_api_key(self, api_key) -> str:
        """Configure and validate API key from parameter or environment."""
        if HoneyHiveTracer.api_key is None:
            if api_key is None:
                # Get API key from environment
                env_api_key = os.getenv("HH_API_KEY")
                if not self._validate_api_key(env_api_key):
                    raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
                api_key = env_api_key
            else:
                # Validate user-provided API key
                if not self._validate_api_key(api_key):
                    raise Exception("api_key must be a string.")
            
            # Set class-level API key
            HoneyHiveTracer.api_key = api_key
        
        return api_key
    
    def _configure_server_url(self, server_url) -> str:
        """Configure and validate server URL from parameter or environment."""
        if HoneyHiveTracer.server_url is None:
            if server_url is None:
                # Get server URL from environment with default
                env_server_url = os.getenv("HH_API_URL", DEFAULT_API_URL)
                if not self._validate_server_url(env_server_url):
                    raise Exception("Invalid server URL in environment variable HH_API_URL.")
                server_url = env_server_url
            else:
                # Validate user-provided server URL
                if not self._validate_server_url(server_url):
                    raise Exception("server_url must be a valid URL string.")
            
            # Set class-level server URL
            HoneyHiveTracer.server_url = server_url
        
        return server_url
    
    def _configure_project(self, project) -> str:
        """Configure and validate project from parameter or environment."""
        if project is None:
            project = os.getenv("HH_PROJECT")
            if project is None:
                raise Exception("project must be specified or set in environment variable HH_PROJECT.")
        return project
    
    def _configure_session_name(self, session_name) -> str:
        """Configure session name from parameter or derive from script name."""
        if session_name is None:
            try:
                session_name = os.path.basename(sys.argv[0])
            except Exception as e:
                if HoneyHiveTracer.verbose:
                    print(f"Error setting session_name: {e}")
                session_name = "unknown"
        return session_name
    
    def _configure_source(self, source) -> str:
        """Configure source from parameter or environment."""
        if source is None:
            source = os.getenv("HH_SOURCE", "dev")
        return source
    
    def _initialize_session(self, session_id, session_name, project, source, inputs) -> None:
        """Initialize session either by creating new one or using existing session_id."""
        if session_id is None:
            # Create new session
            git_info = HoneyHiveTracer._get_git_info()
            metadata = git_info if "error" not in git_info else None
            
            # Store necessary parameters as instance variables
            self.session_name = session_name
            self.inputs = inputs
            self.metadata = metadata
            self.project = project
            self.source = source
            
            # Start the session and get session_id
            self.session_start()
        else:
            # Use existing session_id
            try:
                uuid.UUID(session_id)
                self.session_id = session_id.lower()
                self.project = project
                self.source = source
            except (ValueError, AttributeError, TypeError):
                raise errors.SDKError("session_id must be a valid UUID string.")
    
    def _setup_baggage(self, project, source, disable_http_tracing, is_evaluation, run_id, dataset_id, datapoint_id) -> None:
        """Setup baggage dictionary with all parameters."""
        # Initialize baggage with all parameters
        self.baggage = BaggageDict().update({
            "session_id": self.session_id,
            "project": project,
            "source": source,
            "disable_http_tracing": str(disable_http_tracing).lower(),
        })

        # Add tags to baggage if provided  
        if self.tags:
            for key, value in self.tags.items():
                self.baggage[f"tag_{key}"] = str(value)
        self._tags_initialized = True

        # Add evaluation specific properties if needed
        if is_evaluation:
            self.baggage.update({
                "run_id": run_id,
                "dataset_id": dataset_id,
                "datapoint_id": datapoint_id,
            })
    
    def _initialize_traceloop(self, disable_batch, is_evaluation) -> None:
        """Initialize Traceloop with CompositePropagator."""
        # Initialize the Composite Propagator
        HoneyHiveTracer.propagator = CompositePropagator(
            propagators=[
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator()
            ]
        )

        # instrument tracer with lock
        with threading.Lock():
            # Initialize Traceloop with CompositePropagator
            if not HoneyHiveTracer._is_traceloop_initialized:
                traceloop_args = {
                    "api_endpoint": f"{HoneyHiveTracer.server_url}/opentelemetry",
                    "api_key": HoneyHiveTracer.api_key,
                    "metrics_exporter": ConsoleMetricExporter(out=open(os.devnull, "w")),
                    "disable_batch": disable_batch,
                    "propagator": HoneyHiveTracer.propagator
                }

                # Only redirect stdout if verbose is False
                if not HoneyHiveTracer.verbose:
                    with redirect_stdout(io.StringIO()):
                        Traceloop.init(**traceloop_args)
                else:
                    Traceloop.init(**traceloop_args)
                
                # Print initialization message in orange color (works in both bash and Windows)
                if not HoneyHiveTracer.is_evaluation:
                    print("\033[38;5;208mHoneyHive is initialized\033[0m")
                HoneyHiveTracer._is_traceloop_initialized = True
                HoneyHiveTracer.is_evaluation = is_evaluation
    
    def _setup_context_linking(self, link_carrier) -> None:
        """Setup context linking with carrier or attach baggage to current context."""
        if link_carrier is not None:
            self.link(link_carrier)
        else:
            # attach baggage to the current context
            ctx = context.get_current() # deep copy of the current context
            ctx = self.baggage.set_all_baggage(ctx)
            context.attach(ctx)
        
        # traceloop sets "association_properties" in the context
        # however it is not propagated since it doesn't follow the W3C spec for Baggage
        # since traceloop stamps "association_properties" from the context into every span when it starts, 
        # we must attach the baggage in traceloop format as well
        Traceloop.set_association_properties(self.baggage)
    
    @staticmethod
    def _validate_api_key(api_key) -> bool:
        return api_key is not None and isinstance(api_key, str) and len(api_key.strip()) > 0
    
    @staticmethod
    def _validate_server_url(server_url) -> bool:
        return server_url is not None and isinstance(server_url, str) and len(server_url.strip()) > 0
    
    @staticmethod
    def _validate_project(project) -> bool:
        return project is not None and isinstance(project, str) and len(project.strip()) > 0
    
    @staticmethod
    def _validate_source(source) -> bool:
        return source is not None and isinstance(source, str) and len(source.strip()) > 0
    
    # Deprecated methods - kept for backwards compatibility
    @staticmethod
    def _get_validated_api_key(api_key=None) -> str:
        if api_key is None:
            api_key = os.getenv("HH_API_KEY")
        if not HoneyHiveTracer._validate_api_key(api_key):
            raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
        return api_key
    
    @staticmethod
    def _get_validated_server_url(server_url=None) -> str:
        if server_url is None or server_url == 'https://api.honeyhive.ai':
            server_url = os.getenv("HH_API_URL", 'https://api.honeyhive.ai')
        if not HoneyHiveTracer._validate_server_url(server_url):
            raise Exception("server_url must be a valid URL string.")
        return server_url
    
    @staticmethod
    def _get_validated_project(project=None) -> str:
        if project is None:
            project = os.getenv("HH_PROJECT")
        if not HoneyHiveTracer._validate_project(project):
            raise Exception("project must be specified or set in environment variable HH_PROJECT.")
        return project
    
    @staticmethod
    def _get_validated_source(source=None) -> str:
        if source is None:
            source = os.getenv("HH_SOURCE", "dev")
        if not HoneyHiveTracer._validate_source(source):
            raise Exception("source must be a non-empty string.")
        return source
    
    
    def session_start(self) -> str:
        """Start a new session using the tracer's parameters.
        
        Creates a new session on the HoneyHive platform with the tracer's
        configured project, session name, source, inputs, and metadata.
        
        Returns:
            str: The session ID of the newly created session
            
        Raises:
            AssertionError: If session creation fails
        """
        """Start a session using the tracer's parameters"""
        self.session_id = HoneyHiveTracer.__start_session(
            HoneyHiveTracer.api_key, 
            self.project, 
            self.session_name, 
            self.source, 
            HoneyHiveTracer.server_url, 
            self.inputs, 
            self.metadata
        )
        return self.session_id
    
    @staticmethod
    def _get_git_info() -> Dict[str, Any]:
        """Collect Git repository information for telemetry.
        
        Gathers information about the current Git repository including commit hash,
        branch, repository URL, and uncommitted changes status.
        
        Returns:
            dict: Git information dictionary containing:
                - commit_hash: Current commit SHA
                - branch: Current branch name
                - repo_url: Repository URL
                - commit_link: Link to commit (for GitHub repos)
                - uncommitted_changes: Boolean indicating if there are uncommitted changes
                - relative_path: Relative path of the main module
                Or error dictionary if Git info cannot be retrieved
                
        Note:
            Returns error dictionary if telemetry is disabled via HONEYHIVE_TELEMETRY env var,
            if not in a Git repository, or if Git is not available.
        """
        try:
            # Check if telemetry is disabled
            telemetry_disabled = os.getenv("HONEYHIVE_TELEMETRY", "true").lower() in ["false", "0", "f", "no", "n"]
            if telemetry_disabled:
                if HoneyHiveTracer.verbose:
                    print("Telemetry disabled. Skipping git information collection.")
                return {"error": "Telemetry disabled"}
                
            cwd = os.getcwd()
            
            # First check if this is a git repository
            is_git_repo = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=cwd, capture_output=True, text=True, check=False
            )
            
            # If not a git repo, return early with an error
            if is_git_repo.returncode != 0:
                if HoneyHiveTracer.verbose:
                    print("Not a git repository. Skipping git information collection.")
                return {"error": "Not a git repository"}
                
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            repo_url = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip().rstrip('.git')

            commit_link = f"{repo_url}/commit/{commit_hash}" if "github.com" in repo_url else repo_url

            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            has_uncommitted_changes = bool(status)

            repo_root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Get relative path of the main module
            main_module = sys.modules.get('__main__')
            relative_path = None
            if main_module and hasattr(main_module, '__file__'):
                absolute_path = os.path.abspath(main_module.__file__)
                relative_path = os.path.relpath(absolute_path, repo_root)

            return {
                "commit_hash": commit_hash,
                "branch": branch,
                "repo_url": repo_url,
                "commit_link": commit_link,
                "uncommitted_changes": has_uncommitted_changes,
                "relative_path": relative_path
            }
        except subprocess.CalledProcessError:
            if HoneyHiveTracer.verbose:
                print("Failed to retrieve Git info. Is this a valid repo?")
            return {"error": "Failed to retrieve Git info. Is this a valid repo?"}
        except FileNotFoundError:
            if HoneyHiveTracer.verbose:
                print("Git is not installed or not in PATH.")
            return {"error": "Git is not installed or not in PATH."}
        except Exception as e:
            if HoneyHiveTracer.verbose:
                print(f"Error getting git info: {e}")
            return {"error": f"Error getting git info: {e}"}
    
    @staticmethod
    def __start_session(api_key, project, session_name, source, server_url, inputs=None, metadata=None) -> str:
        sdk = HoneyHive(bearer_auth=api_key, server_url=server_url)
        res = sdk.session.start_session(
            request=operations.StartSessionRequestBody(
                session=components.SessionStartRequest(
                    project=project,
                    session_name=session_name,
                    source=source,
                    inputs=inputs or {},
                    metadata=metadata or {}
                )
            )
        )
        assert res.status_code == 200, f"Failed to start session: {res.raw_response.text}"
        assert res.object.session_id is not None, "Failure initializing session"
        return res.object.session_id
    
    def _sanitize_carrier(carrier, getter):
        # check for baggage in the headers, potentially re-cased
        _propagation_carrier = {}
        for key in ['baggage', 'traceparent']:
            carrier_value = \
                getter.get(carrier, key.lower()) or \
                getter.get(carrier, key.capitalize()) or \
                getter.get(carrier, key.upper())
            if carrier_value is not None:
                _propagation_carrier[key] = [carrier_value]
        return _propagation_carrier
    
    def link(self, carrier={}, getter=BaggageDict.DefaultGetter):
        """Link this tracer to a parent trace context.
        
        Extracts trace context and baggage from the provided carrier and
        links the current context to the parent trace. This enables
        distributed tracing across service boundaries.
        
        Args:
            carrier (dict, optional): Context carrier containing trace headers. Defaults to {}
            getter (Callable, optional): Getter function for extracting values from carrier
            
        Returns:
            Token: Context token that can be used with unlink()
        """
        ctx = context.get_current() # deep copy of the current context
        
        # extract baggage from the carrier
        carrier = HoneyHiveTracer._sanitize_carrier(carrier, getter)
        ctx = HoneyHiveTracer.propagator.extract(carrier, ctx, getter=getter)
        
        # attach the baggage to the current context
        token = context.attach(ctx)
        
        # current context should now have baggage and span context from the carrier
        # it has been fully linked to the parent context
        
        # update the Traceloop baggage in the current context
        # this will be stamped on every span in this context
        bags = self.baggage.get_all_baggage()
        Traceloop.set_association_properties(bags)
        
        return token
    
    def unlink(self, token) -> None:
        """Unlink from a parent trace context.
        
        Detaches the current context from a parent trace context using
        the token returned by link().
        
        Args:
            token: Context token returned by link()
        """
        # included for completeness, but not necessary
        context.detach(token)
        bags = self.baggage.get_all_baggage()
        Traceloop.set_association_properties(bags)

    def add_tags(self, tags) -> None:
        """Add tags to the tracer and propagate them to the context.
        
        Tags are key-value pairs that provide additional metadata about
        the session. They are propagated to all spans created within this context.
        
        Args:
            tags (dict): Dictionary of tag key-value pairs to add
            
        Raises:
            ValueError: If tags is not a dictionary
        """
        """Add tags to the tracer and propagate them to the context"""
        if not isinstance(tags, dict):
            raise ValueError("Tags must be a dictionary")
        
        # Always update the tracer's tags even if not fully initialized
        self.tags.update(tags)
        
        # Check if tracer was initialized properly for baggage updates
        if not hasattr(self, 'baggage') or not getattr(self, '_tags_initialized', False):
            if HoneyHiveTracer.verbose:
                print("Tags updated but not propagated: HoneyHiveTracer not initialized successfully")
            return
        
        # Add tags to baggage
        for key, value in tags.items():
            self.baggage[f"tag_{key}"] = str(value)
        
        # Update the context with new baggage
        ctx = context.get_current()
        ctx = self.baggage.set_all_baggage(ctx) 
        context.attach(ctx)
        
        # Update Traceloop association properties
        bags = self.baggage.get_all_baggage()
        Traceloop.set_association_properties(bags)
    
    def inject(self, carrier={}, setter=BaggageDict.DefaultSetter) -> dict:
        """Inject current trace and baggage context into a carrier.
        
        This method is used to propagate trace context across service boundaries
        by injecting the current trace context and baggage into HTTP headers
        or other carriers.
        
        Args:
            carrier (dict, optional): Carrier object to inject context into. Defaults to {}
            setter (Callable, optional): Setter function for adding values to carrier
            
        Returns:
            dict: The carrier with injected context
        """
        # inject current trace and baggage context into the carrier
        HoneyHiveTracer.propagator.inject(carrier, None, setter)
        return carrier

    @staticmethod
    def flush() -> None:
        """Flush all pending traces to HoneyHive.
        
        This method forces all buffered spans to be exported immediately.
        It's thread-safe and can be called from both threaded and async contexts.
        For async contexts, use: await asyncio.to_thread(HoneyHiveTracer.flush)
        
        This method is particularly important for evaluation workloads and
        short-lived processes to ensure all traces are exported before exit.
        
        Note:
            This method will print an error message if the tracer is not
            properly initialized.
        """
        """
        Flush the tracer.
        Thread-safe and coroutine-safe - can be called from both threaded and async contexts.
        
        In async context, call with:
          await asyncio.to_thread(HoneyHiveTracer.flush)
        """
        if not HoneyHiveTracer._is_traceloop_initialized:
            print("\033[91mCould not flush: HoneyHiveTracer not initialized successfully\033[0m")
            return
        
        # Try to acquire the lock with a timeout to prevent silent failures
        # For evaluation workloads, we need to ensure spans are actually flushed
        try:
            acquired = HoneyHiveTracer._flush_lock.acquire(blocking=True, timeout=10.0)
            if not acquired:
                # Timeout occurred, log warning but don't silently skip
                print("\033[93mWarning: Flush timeout - spans may not be exported\033[0m")
                return
        except Exception as e:
            print(f"\033[91mError acquiring flush lock: {e}\033[0m")
            return
        
        try:
            TracerWrapper().flush()
        finally:
            # Always release the lock
            HoneyHiveTracer._flush_lock.release()

    def enrich_session(
        self,
        session_id=None,
        metadata=None, 
        feedback=None, 
        metrics=None, 
        config=None, 
        inputs=None, 
        outputs=None, 
        user_properties=None
    ) -> None:
        """Enrich a session with additional metadata.
        
        Updates the session record on HoneyHive with additional information
        such as feedback, metrics, configuration, and user properties.
        
        Args:
            session_id (str, optional): Session ID to update. Defaults to current session
            metadata (dict, optional): Additional metadata to add
            feedback (dict, optional): Feedback data to add
            metrics (dict, optional): Metrics data to add
            config (dict, optional): Configuration data to add
            inputs (dict, optional): Input data to add (not currently supported)
            outputs (dict, optional): Output data to add
            user_properties (dict, optional): User-defined properties to add
            
        Note:
            This method silently handles errors unless verbose mode is enabled.
        """
        # TODO: migrate to log-based session enrichments
        # @trace
        # def __enrich_session():
        #     _enrichments = {}
        #     if metadata is not None:
        #         _enrichments["metadata"] = metadata
        #     if feedback is not None:
        #         _enrichments["feedback"] = feedback
        #     if metrics is not None:
        #         _enrichments["metrics"] = metrics
        #     if config is not None:
        #         _enrichments["config"] = config
        #     if inputs is not None:
        #         _enrichments["inputs"] = inputs
        #     if outputs is not None:
        #         _enrichments["outputs"] = outputs
        #     if user_properties is not None:
        #         _enrichments["user_properties"] = user_properties
        #     enrich_span(metadata={
        #         '_enrichments': _enrichments,
        #         '_init_metadata': self._init_metadata
        #     })
        # __enrich_session()
        if not HoneyHiveTracer._is_traceloop_initialized:
            print("\033[91mCould not enrich session: HoneyHiveTracer not initialized successfully\033[0m")
            return
        
        session_id = session_id or self.session_id
        try:
            sdk = HoneyHive(bearer_auth=HoneyHiveTracer.api_key, server_url=HoneyHiveTracer.server_url)
            update_request = operations.UpdateEventRequestBody(event_id=session_id)
            if feedback is not None:
                update_request.feedback = feedback
            if metrics is not None:
                update_request.metrics = metrics
            if metadata is not None:
                update_request.metadata = metadata
            if config is not None:
                update_request.config = config
            if inputs is not None:
                print('inputs are not supported in enrich_session') # TODO: add support for inputs (type change)
            if outputs is not None:
                update_request.outputs = outputs
            if user_properties is not None:
                update_request.user_properties = user_properties
            response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
            if response.status_code != 200:
                raise Exception(f"Failed to enrich session: {response.raw_response.text}")
        except:
            if HoneyHiveTracer.verbose:
                print_exc()
            else:
                pass


def enrich_session(
    session_id=None,
    metadata=None,
    feedback=None,
    metrics=None,
    config=None,
    inputs=None,
    outputs=None,
    user_properties=None
):
    """Standalone function to enrich a session with additional metadata.
    
    This function can be used to enrich sessions without having a tracer instance.
    It will automatically detect the current session from the context if no
    session_id is provided.
    
    Args:
        session_id (str, optional): Session ID to update. Auto-detected if not provided
        metadata (dict, optional): Additional metadata to add
        feedback (dict, optional): Feedback data to add
        metrics (dict, optional): Metrics data to add
        config (dict, optional): Configuration data to add
        inputs (dict, optional): Input data to add (not currently supported)
        outputs (dict, optional): Output data to add
        user_properties (dict, optional): User-defined properties to add
        
    Raises:
        Exception: If HoneyHive tracer is not initialized or session_id cannot be determined
        
    Note:
        This function silently handles errors unless verbose mode is enabled.
    """
    print()
    if not HoneyHiveTracer._is_traceloop_initialized:
        print("\033[91mCould not enrich session: HoneyHiveTracer not initialized successfully\033[0m")
        return
    try:
        sdk = HoneyHive(bearer_auth=HoneyHiveTracer.api_key, server_url=HoneyHiveTracer.server_url)
        if session_id is None:
            ctx: Context = context.get_current()
            association_properties = ctx.get('association_properties') if ctx is not None else None
            if association_properties is not None:
                session_id = association_properties.get('session_id')
            if session_id is None:
                raise Exception("Please initialize HoneyHiveTracer before calling enrich_session")
            
        update_request = operations.UpdateEventRequestBody(event_id=session_id.lower())
        if feedback is not None:
            update_request.feedback = feedback
        if metrics is not None:
            update_request.metrics = metrics
        if metadata is not None:
            update_request.metadata = metadata
        if config is not None:
            update_request.config = config
        if inputs is not None:
            print('inputs are not supported in enrich_session') # TODO: add support for inputs (type change)
        if outputs is not None:
            update_request.outputs = outputs
        if user_properties is not None:
            update_request.user_properties = user_properties
        response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
        if response.status_code != 200:
            raise Exception(f"Failed to enrich session: {response.raw_response.text}")
    except:
        if HoneyHiveTracer.verbose:
            print_exc()
        else:
            pass


# Import performance monitoring utilities
try:
    from .performance import (
        performance_trace,
        perf_trace,
        performance_monitor,
        monitor,
        get_performance_summary,
        reset_performance_metrics,
        PerformanceMetrics,
        PerformanceMonitor
    )
except ImportError as e:
    if HoneyHiveTracer.verbose:
        print(f"Performance monitoring utilities not available: {e}")
    # Gracefully handle missing psutil dependency
    def performance_trace(*args, **kwargs):
        print("Performance monitoring requires 'psutil' package. Install with: pip install psutil")
        return lambda func: func
    
    perf_trace = performance_trace
    performance_monitor = None
    monitor = None
    get_performance_summary = lambda *args: {}
    reset_performance_metrics = lambda *args: None