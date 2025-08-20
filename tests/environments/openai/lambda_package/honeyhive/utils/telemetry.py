import os
import uuid
from pathlib import Path
import logging
import sys
import platform
import requests
from posthog import Posthog
import pkg_resources

POSTHOG_API_KEY = "phc_yeqaIP07fjwZ5n3w47wPtSz7G58igfczuQ9X3zKhuxa"

class Telemetry:
    ANON_ID_PATH = str(Path.home() / ".cache" / "honeyhive" / "telemetry_anon_id")
    UNKNOWN_ANON_ID = "UNKNOWN"
    _posthog: Posthog = None

    def __new__(cls) -> "Telemetry":
        if not hasattr(cls, "instance"):
            obj = cls.instance = super(Telemetry, cls).__new__(cls)
            obj._telemetry_enabled = (
                os.getenv("HONEYHIVE_TELEMETRY") or "true"
            ).lower() == "true" and "pytest" not in sys.modules
            if obj._telemetry_enabled:
                try:
                    obj._posthog = Posthog(
                        project_api_key=POSTHOG_API_KEY,
                        host="https://app.posthog.com",
                    )
                    obj._curr_anon_id = None
                    posthog_logger = logging.getLogger("posthog")
                    posthog_logger.disabled = True
                except Exception:
                    # disable telemetry if it fails
                    obj._telemetry_enabled = False
        return cls.instance

    def _anon_id(self) -> str:
        if self._curr_anon_id:
            return self._curr_anon_id
        try:
            if not os.path.exists(self.ANON_ID_PATH):
                os.makedirs(os.path.dirname(self.ANON_ID_PATH), exist_ok=True)
                with open(self.ANON_ID_PATH, "w") as f:
                    new_anon_id = str(uuid.uuid4())
                    f.write(new_anon_id)
                self._curr_anon_id = new_anon_id
            else:
                with open(self.ANON_ID_PATH, "r") as f:
                    self._curr_anon_id = f.read()
        except Exception:
            self._curr_anon_id = self.UNKNOWN_ANON_ID
        return self._curr_anon_id

    def _get_package_version(self, package_name: str) -> str:
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            return "Not installed"

    def _context(self) -> dict:
        context = {
            "sdk": "honeyhive",
            "sdk_version": self._get_package_version("honeyhive"),
        }
        
        # Language settings
        context["language"] = {
            "name": "python",
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        }
        
        # Runtime settings
        context["runtime"] = self._get_runtime_info()
        
        # OS version
        context["os"] = {
            "name": os.name,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        }
        
        # Chip version
        context["chip"] = {
            "architecture": platform.machine(),
            "processor": platform.processor(),
        }

        # Service Provider Info
        context["service_provider_info"] = self._get_service_provider_info()

        # Notebook Environment Info
        context["notebook_info"] = self._get_notebook_info()

        # Execution Info
        context["execution_info"] = self._get_execution_info()
        
        # Package versions
        context["package_versions"] = {
            # orchestration frameworks
            "langchain": self._get_package_version("langchain"),
            "llamaindex": self._get_package_version("llama-index"),
            "haystack": self._get_package_version("haystack"),
            "boto3": self._get_package_version("boto3"),

            # llms
            "openai": self._get_package_version("openai"),
            "anthropic": self._get_package_version("anthropic"),
            "ollama": self._get_package_version("ollama"),
            "mistralai": self._get_package_version("mistralai"),
            "google-generativeai": self._get_package_version("google-generativeai"),
            "watsonx": self._get_package_version("ibm-watson-machine-learning"),
            "vertexai": self._get_package_version("google-cloud-aiplatform"),
            "transformers": self._get_package_version("transformers"),
            "together": self._get_package_version("together"),
            "replicate": self._get_package_version("replicate"),
            "groq": self._get_package_version("groq"),

            # vector dbs
            "qdrant": self._get_package_version("qdrant-client"),
            "weaviate": self._get_package_version("weaviate-client"),
            "milvus": self._get_package_version("pymilvus"),
            "pinecone": self._get_package_version("pinecone-client"),
        }
        
        return context

    def _get_runtime_info(self) -> dict:
        runtime_info = {}
        
        # Detect if running in a cloud environment
        if 'LAMBDA_TASK_ROOT' in os.environ:
            runtime_info['environment'] = 'AWS Lambda'
        elif 'RoleRoot' in os.environ:
            runtime_info['environment'] = 'Azure Functions'
        elif 'GOOGLE_CLOUD_PROJECT' in os.environ:
            runtime_info['environment'] = 'Google Cloud Functions'
        else:
            runtime_info['environment'] = 'Unknown'

        # Detect server-side framework
        try:
            import django
            runtime_info['framework'] = f"Django {django.get_version()}"
        except ImportError:
            try:
                import flask
                runtime_info['framework'] = f"Flask {flask.__version__}"
            except ImportError:
                try:
                    import fastapi
                    runtime_info['framework'] = f"FastAPI {fastapi.__version__}"
                except ImportError:
                    runtime_info['framework'] = "Unknown"

        return runtime_info

    def _get_service_provider_info(self) -> dict:
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Failed to fetch data: HTTP {response.status_code}'}
        except Exception as e:
            return {'error': f'Failed to fetch data: {str(e)}'}

    def _get_notebook_info(self) -> dict:
        notebook_info = {}

        # Check if we're in a notebook environment
        notebook_info['in_notebook'] = 'ipykernel' in sys.modules

        # Get more detailed IPython information
        if notebook_info['in_notebook']:
            notebook_info['environment'] = 'notebook'
            try:
                import IPython
                ip_version = IPython.version_info
                notebook_info['ipython_version'] = '.'.join(map(str, ip_version))

                # Get client information
                ip = sys.modules['ipykernel']
                notebook_info['ipython_client'] = ip.write_connection_file.__module__.split('.')[0]

                # Get system info
                sys_info = IPython.utils.sysinfo.get_sys_info()
                notebook_info['sys_info'] = {
                    'ipython_version': sys_info['ipython_version'],
                    'ipython_path': sys_info['ipython_path']
                }
            except Exception as e:
                notebook_info['error'] = f"Failed to get detailed IPython info: {str(e)}"
        elif 'IPython' in sys.modules:
            notebook_info['environment'] = 'terminal'
        else:
            notebook_info['environment'] = 'standard_python'

        return notebook_info

    def _get_execution_info(self) -> dict:
        execution_info = {}
        
        # Get the Python executable path
        execution_info['executable'] = sys.executable
        
        # Get the command-line arguments
        execution_info['argv'] = sys.argv
        
        # Determine how the script was likely executed
        if sys.argv[0].endswith('pyinstaller-script.py'):
            execution_info['execution_method'] = 'pyinstaller'
        elif 'python' in sys.executable.lower():
            if len(sys.argv) > 0 and sys.argv[0].endswith('.py'):
                execution_info['execution_method'] = 'python_script'
            else:
                execution_info['execution_method'] = 'python_module'
        elif 'ipython' in sys.executable.lower():
            execution_info['execution_method'] = 'ipython'
        elif 'jupyter' in sys.executable.lower():
            execution_info['execution_method'] = 'jupyter'
        else:
            execution_info['execution_method'] = 'unknown'
        
        return execution_info

    def capture(self, event: str, event_properties: dict = {}) -> None:
        try:  # don't fail if telemetry fails
            if self._telemetry_enabled:
                self._posthog.capture(
                    self._anon_id(), event, {**self._context(), **event_properties}
                )
        except Exception:
            pass

    def log_exception(self, exception: Exception):
        try:  # don't fail if telemetry fails
            return self._posthog.capture(
                self._anon_id(),
                "exception",
                {
                    **self._context(),
                    "exception": str(exception),
                },
            )
        except Exception:
            pass
