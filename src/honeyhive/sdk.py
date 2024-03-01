"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from .configurations import Configurations
from .datapoint import Datapoint
from .datasets import Datasets
from .events import Events
from .metrics import Metrics
from .prompts import Prompts
from .sdkconfiguration import SDKConfiguration
from .session import Session
from .tasks import Tasks
from .testcases import Testcases
from .tools import Tools
from honeyhive import utils
from honeyhive._hooks import SDKHooks
from honeyhive.models import components
from typing import Callable, Dict, Union

class HoneyHive:
    configurations: Configurations
    datapoint: Datapoint
    datasets: Datasets
    events: Events
    metrics: Metrics
    prompts: Prompts
    session: Session
    tasks: Tasks
    testcases: Testcases
    tools: Tools

    sdk_configuration: SDKConfiguration

    def __init__(self,
                 bearer_auth: Union[str, Callable[[], str]],
                 server_idx: int = None,
                 server_url: str = None,
                 url_params: Dict[str, str] = None,
                 client: requests_http.Session = None,
                 retry_config: utils.RetryConfig = None
                 ) -> None:
        """Instantiates the SDK configuring it with the provided parameters.
        
        :param bearer_auth: The bearer_auth required for authentication
        :type bearer_auth: Union[str, Callable[[], str]]
        :param server_idx: The index of the server to use for all operations
        :type server_idx: int
        :param server_url: The server URL to use for all operations
        :type server_url: str
        :param url_params: Parameters to optionally template the server URL with
        :type url_params: Dict[str, str]
        :param client: The requests.Session HTTP client to use for all operations
        :type client: requests_http.Session
        :param retry_config: The utils.RetryConfig to use globally
        :type retry_config: utils.RetryConfig
        """
        if client is None:
            client = requests_http.Session()
        
        if callable(bearer_auth):
            def security():
                return components.Security(bearer_auth = bearer_auth())
        else:
            security = components.Security(bearer_auth = bearer_auth)
        
        if server_url is not None:
            if url_params is not None:
                server_url = utils.template_url(server_url, url_params)

        self.sdk_configuration = SDKConfiguration(client, security, server_url, server_idx, retry_config=retry_config)

        hooks = SDKHooks()

        current_server_url, *_ = self.sdk_configuration.get_server_details()
        server_url, self.sdk_configuration.client = hooks.sdk_init(current_server_url, self.sdk_configuration.client)
        if current_server_url != server_url:
            self.sdk_configuration.server_url = server_url

        # pylint: disable=protected-access
        self.sdk_configuration._hooks=hooks
       
        self._init_sdks()
    
    def _init_sdks(self):
        self.configurations = Configurations(self.sdk_configuration)
        self.datapoint = Datapoint(self.sdk_configuration)
        self.datasets = Datasets(self.sdk_configuration)
        self.events = Events(self.sdk_configuration)
        self.metrics = Metrics(self.sdk_configuration)
        self.prompts = Prompts(self.sdk_configuration)
        self.session = Session(self.sdk_configuration)
        self.tasks = Tasks(self.sdk_configuration)
        self.testcases = Testcases(self.sdk_configuration)
        self.tools = Tools(self.sdk_configuration)
    