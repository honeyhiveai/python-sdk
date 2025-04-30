import json
import os
import uuid
import time
import urllib.request
import urllib.error
import random
import socket
from typing import Dict, Any, Callable, TypeVar

T = TypeVar('T')

def _retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 5.0,
    timeout: float = 5.0,
    verbose: bool = False
) -> T:
    """
    Retry a function with exponential backoff and jitter.
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        timeout: Socket timeout in seconds
        verbose: Whether to print debug information
        
    Returns:
        The result of the function call
        
    Raises:
        Exception: If all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            # Set socket timeout
            socket.setdefaulttimeout(timeout)
            
            # Try the function
            return func()
            
        except (urllib.error.URLError, socket.timeout) as e:
            last_exception = e
            
            if attempt == max_retries:
                if verbose:
                    print(f"Final attempt failed: {str(e)}")
                raise
            
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # Add up to 10% jitter
            total_delay = delay + jitter
            
            if verbose:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {total_delay:.2f} seconds...")
            
            time.sleep(total_delay)
            
        except Exception as e:
            # For non-retryable errors, raise immediately
            raise

def start(
    api_key: str = None,
    project: str = None,
    session_name: str = "unknown",
    env: str = "dev",
    config: Dict[str, Any] = None,
    inputs: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    user_properties: Dict[str, Any] = None,
    session_id: str = None,
    server_url: str = 'https://api.honeyhive.ai',
    verbose: bool = False
) -> str:
    """
    Start a new session with HoneyHive using only built-in Python packages.

    Use update() to update the session with new data.
    
    Refer to https://docs.honeyhive.ai/schema-overview for more information on the schema.

    Args:
        api_key (str, optional): Your HoneyHive API key. Must be provided or set via HH_API_KEY env var.
        project (str, optional): The project name. Must be provided or set via HH_PROJECT env var.
        session_name (str, optional): Optional tag to filter sessions on "v1", "au1i249c" (commit hash), etc. Defaults to "unknown".
        environment (str, optional): Environment where the code is running. Defaults to "dev" or HH_SOURCE env var.
        config (dict, optional): Configuration details for the session like experiment versions, model names, etc.
        inputs (dict, optional): Input parameters for the session.
        metadata (dict, optional): Additional metadata for the session.
        user_properties (dict, optional): User-defined properties for the session.
        session_id (str, optional): A valid UUIDv4 for the session to correlate with your logs. If not provided, one will be generated.
        server_url (str, optional): HoneyHive API server URL. Defaults to "https://api.honeyhive.ai" or HH_API_URL env var.
        verbose (bool, optional): Print detailed error messages for debugging. Defaults to False.
        
    Returns:
        str: The session ID (UUIDv4)
    """
    try:
        # Get required parameters from environment if not provided
        api_key = api_key or os.getenv("HH_API_KEY")
        project = project or os.getenv("HH_PROJECT")
        source = env or os.getenv("HH_SOURCE", "dev")
        server_url = server_url or os.getenv("HH_API_URL", "https://api.honeyhive.ai")

        session_name = project

        if not api_key:
            raise Exception(
                "API key is required but not provided. Please either:\n"
                "1. Pass it as an argument: start(api_key='your-api-key')\n"
                "2. Set it as an environment variable: export HH_API_KEY='your-api-key'\n"
                "You can find your API key in Settings > Project > API Keys"
            )
        if not project:
            raise Exception(
                "Project name is required but not provided. Please either:\n"
                "1. Pass it as an argument: start(project='your-project')\n"
                "2. Set it as an environment variable: export HH_PROJECT='your-project'\n"
                "You can find your project name in All Projects"
            )

        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Prepare request data
        data = {
            "session": {
                "project": project,
                "session_name": session_name,
                "source": source,
                "session_id": session_id,
                "config": config or {},
                "inputs": inputs or {},
                "metadata": metadata or {},
                "user_properties": user_properties or {},
                "start_time": int(time.time() * 1000)  # Current time in milliseconds
            }
        }

        if verbose:
            print("POST /session/start request made with data", data)
            
        def make_request():
            # Create request
            req = urllib.request.Request(
                f"{server_url}/session/start",
                method="POST",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "HoneyHive-Python-SDK"
                }
            )

            # Send request
            with urllib.request.urlopen(req, data=json.dumps(data).encode()) as response:
                if response.status != 200:
                    error_msg = response.read().decode()
                    raise Exception(
                        f"Failed to start session (HTTP {response.status}): {error_msg}\n"
                        "Please check:\n"
                        "1. Your API key is valid and has the correct permissions\n"
                        "2. The project name exists and you have access to it\n"
                        "3. The server URL is correct and accessible\n"
                        "4. The SSL certificate is whitelisted in your VPN"
                    )
                
                response_data = json.loads(response.read().decode())
                if not response_data.get("session_id"):
                    raise Exception(
                        "Invalid response from server: session_id not found\n"
                        "Please contact HoneyHive support if this issue persists"
                    )
                
                print("\033[38;5;208mHoneyHive is initialized\033[0m") 
                return response_data["session_id"]

        return _retry_with_backoff(make_request, verbose=verbose)

    except Exception as e:
        print("HoneyHive: Failed to start session. Please enable verbose mode to debug.")
        if verbose:
            print(f"Error starting session: {str(e)}")
            raise

def log(
    api_key: str = None,
    project: str = None,
    env: str = "dev",
    event_name: str = None,
    event_type: str = "model",
    config: Dict[str, Any] = None,
    inputs: Dict[str, Any] = None,
    outputs: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    session_id: str = None,
    duration_ms: int = 10,
    server_url: str = 'https://api.honeyhive.ai',
    verbose: bool = False
) -> str:
    """
    Log an event to HoneyHive using only built-in Python packages.

    Use update() to update the event with new data.

    Refer to https://docs.honeyhive.ai/schema-overview for more information on the schema.
    
    Args:
        api_key (str, optional): Your HoneyHive API key. Must be provided or set via HH_API_KEY env var.
        project (str, optional): The project name. Must be provided or set via HH_PROJECT env var.
        env (str, optional): Environment where the code is running. Defaults to "dev" or HH_SOURCE env var.
        event_name (str): Name of the event being logged. Required.
        event_type (str, optional): Type of event - "model", "tool", or "chain". Defaults to "model".
        config (dict, optional): Configuration details for the event like model name, vector index name, etc.
        inputs (dict, optional): Input parameters for the event.
        outputs (dict, optional): Output data from the event.
        metadata (dict, optional): Additional metadata for the event.
        session_id (str): The ID of the session to log the event under. If not provided, a session is automatically created.
        duration_ms (int, optional): Duration of the event in milliseconds. If not provided, will be set to 10.
        server_url (str, optional): HoneyHive API server URL. Defaults to "https://api.honeyhive.ai" or HH_API_URL env var.
        verbose (bool, optional): Print detailed error messages for debugging. Defaults to False.
        
    Returns:
        str: The event ID (UUIDv4)
        
    Raises:
        Exception: If required parameters are missing or invalid
    """
    try:
        # Get required parameters from environment if not provided
        api_key = api_key or os.getenv("HH_API_KEY")
        project = project or os.getenv("HH_PROJECT")
        server_url = server_url or os.getenv("HH_API_URL", "https://api.honeyhive.ai")

        if not api_key:
            raise Exception(
                "API key is required but not provided. Please either:\n"
                "1. Pass it as an argument: log(api_key='your-api-key')\n"
                "2. Set it as an environment variable: export HH_API_KEY='your-api-key'\n"
                "You can find your API key in Settings > Project > API Keys"
            )
        if not project:
            raise Exception(
                "Project name is required but not provided. Please either:\n"
                "1. Pass it as an argument: log(project='your-project')\n"
                "2. Set it as an environment variable: export HH_PROJECT='your-project'\n"
                "You can find your project name in All Projects"
            )
        if not event_name:
            raise Exception(
                "Event name is required but not provided. Please provide a name for your event:\n"
                "log(event_name='your-event-name')"
            )
            
        # Case-insensitive validation of event_type
        valid_types = ["model", "tool", "chain"]
        if event_type.lower() not in valid_types:
            raise Exception(
                f"Invalid event type: '{event_type}'\n"
                f"Valid event types are: {', '.join(valid_types)}\n"
                "Please use one of these types when logging events"
            )
            
        if not session_id:
            session_id = str(uuid.uuid4())
        if not duration_ms:
            duration_ms = 10

        # Generate event_id
        start_time = int(time.time() * 1000)

        # Prepare request data
        data = {
            "event": {
                "session_id": session_id,
                "project": project,
                "source": env,
                "event_name": event_name,
                "event_type": event_type.lower(),  # Normalize to lowercase
                "config": config or {},
                "inputs": inputs or {},
                "outputs": outputs or {},
                "metadata": metadata or {},
                "start_time": start_time,
                "duration": duration_ms
            }
        }

        if verbose:
            print("POST /events request made with data", data)
            
        def make_request():
            # Create request
            req = urllib.request.Request(
                f"{server_url}/events",
                method="POST",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "HoneyHive-Python-SDK"
                }
            )

            # Send request
            with urllib.request.urlopen(req, data=json.dumps(data).encode()) as response:
                if response.status != 200:
                    error_msg = response.read().decode()
                    raise Exception(
                        f"Failed to log event (HTTP {response.status}): {error_msg}\n"
                        "Please check:\n"
                        "1. Your API key is valid and has the correct permissions\n"
                        "2. The project name exists and you have access to it\n"
                        "3. The server URL is correct and accessible\n"
                        "4. The SSL certificate is whitelisted in your VPN"
                    )
                
                response_data = json.loads(response.read().decode())
                event_id = response_data.get("event_id")
                if not event_id:
                    raise Exception(
                        "Invalid response from server: event_id not found\n"
                        "Please contact HoneyHive support if this issue persists"
                    )
                
                return event_id

        return _retry_with_backoff(make_request, verbose=verbose)

    except Exception as e:
        print("HoneyHive: Failed to log event. Please enable verbose mode to debug.")
        if verbose:
            print(f"Error logging event: {str(e)}")
            raise

def update(
    api_key: str = None,
    event_id: str = None,
    metadata: Dict[str, Any] = None,
    feedback: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    config: Dict[str, Any] = None,
    outputs: Dict[str, Any] = None,
    user_properties: Dict[str, Any] = None,
    duration_ms: int = None,
    server_url: str = 'https://api.honeyhive.ai',
    verbose: bool = False
) -> None:
    """
    Update an event or session with additional data using only built-in Python packages.

    Refer to https://docs.honeyhive.ai/schema-overview for more information on the schema.
    
    Args:
        api_key (str, optional): Your HoneyHive API key. Must be provided or set via HH_API_KEY env var.
        event_id (str): The ID to update. This can be either:
                       - A session_id returned from start()
                       - An event_id returned from log()
        metadata (dict, optional): Additional metadata for the event/session.
        feedback (dict, optional): User feedback for the event/session.
        metrics (dict, optional): Metrics computed for the event/session.
        config (dict, optional): Configuration used in the event/session.
        outputs (dict, optional): Output data from the event/session.
        user_properties (dict, optional): User-defined properties for the event/session.
        duration_ms (int, optional): Duration of the event in milliseconds.
        server_url (str, optional): HoneyHive API server URL. Defaults to "https://api.honeyhive.ai" or HH_API_URL env var.
        verbose (bool, optional): Print detailed error messages for debugging. Defaults to False.
        
    Raises:
        Exception: If required parameters are missing or invalid
        
    Example:
        # Update a session
        session_id = start(
            project="my-project",
            session_name="test-session"
        )
        update(
            event_id=session_id,
            metadata={"status": "completed"}
        )
        
        # Update an event
        event_id = log(
            session_id=session_id,
            event_name="test_event",
            event_type="model"
        )
        update(
            event_id=event_id,
            feedback={"rating": 5}
        )
    """
    try:
        # Get required parameters from environment if not provided
        api_key = api_key or os.getenv("HH_API_KEY")
        server_url = server_url or os.getenv("HH_API_URL", "https://api.honeyhive.ai")

        if not api_key:
            raise Exception(
                "API key is required but not provided. Please either:\n"
                "1. Pass it as an argument: update(api_key='your-api-key')\n"
                "2. Set it as an environment variable: export HH_API_KEY='your-api-key'\n"
                "You can find your API key in Settings > Project > API Keys"
            )
        if not event_id:
            raise Exception(
                "Event ID is required but not provided. Please provide either:\n"
                "1. A session_id returned from start()\n"
                "2. An event_id returned from log()"
            )

        # Check if event_id is actually a session_id
        try:
            uuid.UUID(event_id)
        except ValueError:
            raise Exception("event_id must be a valid UUID")

        # Prepare request data
        data = {
            "event_id": event_id,
            "metadata": metadata,
            "feedback": feedback,
            "metrics": metrics,
            "config": config,
            "outputs": outputs,
            "user_properties": user_properties,
            "duration": duration_ms
        }

        # Remove keys with None values
        data = {key: value for key, value in data.items() if value is not None}

        if verbose:
            print(f"\nUpdating event {event_id}")
            print("Request data:", json.dumps(data, indent=2))
            
        def make_request():
            # Create request
            req = urllib.request.Request(
                f"{server_url}/events",
                method="PUT",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "HoneyHive-Python-SDK"
                }
            )

            # Send request
            with urllib.request.urlopen(req, data=json.dumps(data).encode()) as response:
                if response.status != 200:
                    error_msg = response.read().decode()
                    if verbose:
                        print(f"Error response: {error_msg}")
                    raise Exception(
                        f"Failed to update event (HTTP {response.status}): {error_msg}\n"
                        "Please check:\n"
                        "1. Your API key is valid and has the correct permissions\n"
                        "2. The event_id or session_id is correct\n"
                        "3. The server URL is correct and accessible\n"
                        "4. The SSL certificate is whitelisted in your VPN"
                    )
                elif verbose:
                    print(f"Successfully updated event {event_id}")
                    print("Response:", response.read().decode())

        _retry_with_backoff(make_request, verbose=verbose)

    except Exception as e:
        print("HoneyHive: Failed to update event. Please enable verbose mode to debug.")
        if verbose:
            print(f"Error updating event: {str(e)}")
            raise
