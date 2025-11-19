Authentication Reference
========================

.. note::
   **Complete reference for HoneyHive authentication methods and security**
   
   This document provides detailed specifications for authenticating with HoneyHive APIs and configuring security settings.

HoneyHive uses API keys for authentication across all SDK and API interactions. This reference covers all authentication methods, security best practices, and troubleshooting.

API Key Authentication
----------------------

Basic Authentication
~~~~~~~~~~~~~~~~~~~~

**API Key Format**:

All HoneyHive API keys follow this format:
- **Prefix**: ``hh_``
- **Length**: 32+ characters after prefix
- **Characters**: Alphanumeric (a-z, A-Z, 0-9)
- **Example**: ``hh_1234567890abcdef1234567890abcdef``

**Obtaining API Keys**:

1. **HoneyHive Dashboard**:
   - Navigate to Settings → API Keys
   - Click "Generate New API Key"
   - Copy and securely store the key
   - API keys are only shown once

2. **Team Management**:
   - Team admins can generate keys for team members
   - Different permission levels available
   - Keys can be scoped to specific projects

**API Key Permissions**:

.. list-table:: API Key Permission Levels
   :header-rows: 1
   :widths: 20 30 50

   * - Level
     - Capabilities
     - Use Cases
   * - **Read Only**
     - View projects, sessions, events
     - Monitoring, reporting, analysis
   * - **Read/Write**
     - All read operations + create/update data
     - Application integration, data ingestion
   * - **Admin**
     - All operations + manage projects/settings
     - Full control, configuration management

Authentication Methods
----------------------

Environment Variable
~~~~~~~~~~~~~~~~~~~~

**Primary Method** (Recommended):

.. code-block:: bash

   # Set environment variable
   export HH_API_KEY="hh_your_api_key_here"

**Benefits**:
- Secure (not in code)
- Environment-specific
- Easy rotation
- CI/CD friendly

**Python Usage**:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   # Automatically uses HH_API_KEY environment variable
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
       # api_key not needed - loaded from HH_API_KEY environment variable
   )

Direct Parameter
~~~~~~~~~~~~~~~~

**For Testing/Development**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Direct API key parameter
   tracer = HoneyHiveTracer.init(
       api_key="hh_your_api_key_here",  # Or set HH_API_KEY environment variable
       project="your-project"           # Or set HH_PROJECT environment variable
   )

**Use Cases**:
- Unit testing with mock keys
- Development environments
- Quick prototyping

**Security Warning**: Never commit API keys directly in code

Configuration File
~~~~~~~~~~~~~~~~~~

**YAML Configuration**:

.. code-block:: yaml

   # honeyhive.yaml
   api_key: "hh_your_api_key_here"
   project: "my-project"

**JSON Configuration**:

.. code-block:: json

   {
     "api_key": "hh_your_api_key_here", 
     "project": "my-project"
   }

**Loading Configuration**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Load from config file
   tracer = HoneyHiveTracer.init(config_file="honeyhive.yaml")

CLI Authentication
~~~~~~~~~~~~~~~~~~

**Login Command**:

.. code-block:: bash

   # Interactive login
   honeyhive auth login --api-key hh_your_api_key_here
   
   # Save credentials
   honeyhive auth login --api-key hh_your_key --save

**Check Authentication**:

.. code-block:: bash

   # Verify current authentication
   honeyhive auth whoami
   
   # Output:
   # Authenticated as: user@example.com
   # Organization: My Company
   # Permissions: Read/Write

**Logout**:

.. code-block:: bash

   # Logout current user
   honeyhive auth logout
   
   # Remove all stored credentials
   honeyhive auth logout --all

Authentication Precedence
-------------------------

The SDK resolves authentication in this order (highest to lowest precedence):

1. **Direct Parameter**: ``api_key`` parameter in function calls
2. **Environment Variable**: ``HH_API_KEY`` environment variable
3. **Configuration File**: ``api_key`` in config file
4. **CLI Stored Credentials**: Credentials saved via ``honeyhive auth login``

**Example**:

.. code-block:: python

   # This takes precedence over all other methods
   tracer = HoneyHiveTracer.init(
       api_key="hh_direct_key",  # Highest precedence (or set HH_API_KEY environment variable)
       project="your-project"    # Or set HH_PROJECT environment variable
   )

.. code-block:: bash

   # This takes precedence over config file and CLI
   export HH_API_KEY="hh_env_key"

Security Best Practices
-----------------------

API Key Management
~~~~~~~~~~~~~~~~~~

**Do's**:

✅ **Use Environment Variables**:

.. code-block:: bash

   # Production deployment
   export HH_API_KEY="hh_prod_key_here"

✅ **Rotate Keys Regularly**:

.. code-block:: bash

   # Generate new key, update environment, revoke old key
   honeyhive auth login --api-key hh_new_key_here

✅ **Use Different Keys per Environment**:

.. code-block:: bash

   # Development
   export HH_API_KEY="hh_dev_key_here"
   
   # Staging  
   export HH_API_KEY="hh_staging_key_here"
   
   # Production
   export HH_API_KEY="hh_prod_key_here"

✅ **Scope Keys Appropriately**:

.. code-block:: python

   # Use read-only keys for monitoring
   monitoring_tracer = HoneyHiveTracer.init(
       api_key="hh_readonly_key_here",  # Or set HH_API_KEY environment variable
       project="your-project"           # Or set HH_PROJECT environment variable
   )

**Don'ts**:

❌ **Never Commit Keys to Code**:

.. code-block:: python

   # DON'T DO THIS
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef...",  # Never hardcode! Use HH_API_KEY environment variable
       project="your-project"             # Or set HH_PROJECT environment variable
   )

❌ **Don't Share Keys**:
- Each developer should have their own key
- Use service accounts for automated systems
- Revoke keys when team members leave

❌ **Don't Log Keys**:

.. code-block:: python

   import logging
   
   # DON'T DO THIS
   logging.info(f"Using API key: {api_key}")  # Never log keys!
   
   # DO THIS INSTEAD
   logging.info(f"Using API key: {api_key[:8]}***")  # Masked logging

Storage Security
~~~~~~~~~~~~~~~~

**Secure Storage Options**:

1. **Environment Variables**:
   
   .. code-block:: bash
   
      # In .bashrc or .zshrc (for development)
      export HH_API_KEY="hh_your_key_here"
   
   .. code-block:: yaml
   
      # In Kubernetes secrets
      apiVersion: v1
      kind: Secret
      metadata:
        name: honeyhive-secret
      data:
        api-key: aGhfeW91cl9rZXlfaGVyZQ==  # base64 encoded

2. **Cloud Secret Managers**:
   
   .. code-block:: python
   
      # AWS Secrets Manager
      import boto3
      
      def get_honeyhive_key():
          client = boto3.client('secretsmanager')
          response = client.get_secret_value(SecretId='honeyhive-api-key')
          return response['SecretString']
   
   .. code-block:: python
   
      # Azure Key Vault
      from azure.keyvault.secrets import SecretClient
      
      def get_honeyhive_key():
          client = SecretClient(vault_url="https://vault.vault.azure.net/", 
                               credential=credential)
          secret = client.get_secret("honeyhive-api-key")
          return secret.value

3. **Configuration Management**:
   
   .. code-block:: python
   
      # Using python-decouple
      from decouple import config
      
      api_key = config('HH_API_KEY')
      tracer = HoneyHiveTracer.init(
          api_key=api_key,         # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      )

Access Control
~~~~~~~~~~~~~~

**Network Security**:

.. code-block:: yaml

   # Restrict API access by IP (if available)
   allowed_ips:
     - "192.168.1.0/24"    # Internal network
     - "10.0.0.0/8"        # VPN range
     - "203.0.113.10"      # Specific server

**Rate Limiting**:

.. code-block:: python

   # SDK handles rate limiting automatically
   tracer = HoneyHiveTracer.init(
       api_key="hh_your_key",       # Or set HH_API_KEY environment variable
       project="your-project",      # Or set HH_PROJECT environment variable
       # Rate limiting is automatic
   )

Environment-Specific Authentication
-----------------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.development
   HH_API_KEY=hh_dev_1234567890abcdef
   HH_BASE_URL=https://api-dev.honeyhive.ai
   HH_TEST_MODE=false
   HH_DEBUG=true

.. code-block:: python

   # Load development environment
   from dotenv import load_dotenv
   load_dotenv('.env.development')
   
   from honeyhive import HoneyHiveTracer
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from .env.development

Testing Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.test
   HH_API_KEY=hh_test_1234567890abcdef
   HH_BASE_URL=https://api-test.honeyhive.ai
   HH_TEST_MODE=true
   HH_DEBUG=false

.. code-block:: python

   # Testing with mock authentication
   import pytest
   from unittest.mock import patch
   
   @patch.dict('os.environ', {'HH_API_KEY': 'hh_mock_key'})
   def test_honeyhive_integration():
       from honeyhive import HoneyHiveTracer
       tracer = HoneyHiveTracer.init(
           project="your-project",  # Or set HH_PROJECT environment variable
           test_mode=True            # No real API calls (or set HH_TEST_MODE=true)
       )
       # Test your code here

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # production.yaml (deployed securely)
   api_key: "${HH_API_KEY}"  # Environment variable substitution
   base_url: "https://api.honeyhive.ai"
   project: "my-app-prod"
   test_mode: false
   debug: false
   
   # Security settings
   verify_ssl: true
   timeout: 30.0

.. code-block:: bash

   # Production deployment
   export HH_API_KEY="hh_prod_secure_key_here"
   
   # Start application
   python app.py

CI/CD Authentication
--------------------

GitHub Actions
~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test HoneyHive Integration
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v4
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install dependencies
         run: |
           pip install honeyhive pytest
       
       - name: Run tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
           HH_TEST_MODE: "true"
         run: |
           pytest tests/

**Setting GitHub Secrets**:
1. Repository Settings → Secrets and variables → Actions
2. New repository secret: ``HH_TEST_API_KEY``
3. Value: Your test API key

GitLab CI
~~~~~~~~~

.. code-block:: yaml

   # .gitlab-ci.yml
   test:
     image: python:3.11
     variables:
       HH_TEST_MODE: "true"
     script:
       - pip install honeyhive pytest
       - pytest tests/
     only:
       - merge_requests
       - main

**Setting GitLab Variables**:
1. Project Settings → CI/CD → Variables
2. Add variable: ``HH_TEST_API_KEY``
3. Make it protected and masked

Jenkins
~~~~~~~

.. code-block:: text

   // Jenkinsfile
   pipeline {
       agent any
       
       environment {
           HH_API_KEY = credentials('honeyhive-test-api-key')
           HH_TEST_MODE = 'true'
       }
       
       stages {
           stage('Test') {
               steps {
                   sh '''
                       pip install honeyhive pytest
                       pytest tests/
                   '''
               }
           }
       }
   }

**Setting Jenkins Credentials**:
1. Manage Jenkins → Manage Credentials
2. Add Secret Text credential
3. ID: ``honeyhive-test-api-key``

Docker Authentication
---------------------

**Dockerfile with Build Args**:

.. code-block:: dockerfile

   FROM python:3.11
   
   # Use build arg for API key (not recommended for production)
   ARG HH_API_KEY
   ENV HH_API_KEY=${HH_API_KEY}
   
   # Install application
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   CMD ["python", "app.py"]

**Build and Run**:

.. code-block:: bash

   # Build (not recommended - API key in build context)
   docker build --build-arg HH_API_KEY=hh_your_key -t myapp .
   
   # Better: Pass at runtime
   docker run -e HH_API_KEY=hh_your_key myapp

**Docker Compose**:

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   
   services:
     app:
       build: .
       environment:
         - HH_API_KEY=${HH_API_KEY}
       env_file:
         - .env.production

**Docker Secrets** (Docker Swarm):

.. code-block:: yaml

   # docker-compose.yml (with secrets)
   version: '3.8'
   
   services:
     app:
       image: myapp
       secrets:
         - honeyhive_api_key
       environment:
         - HH_API_KEY_FILE=/run/secrets/honeyhive_api_key
   
   secrets:
     honeyhive_api_key:
       external: true

Kubernetes Authentication
-------------------------

**Using Secrets**:

.. code-block:: yaml

   # honeyhive-secret.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: honeyhive-secret
   type: Opaque
   data:
     api-key: aGhfeW91cl9rZXlfaGVyZQ==  # base64 encoded

.. code-block:: yaml

   # deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: myapp
   spec:
     template:
       spec:
         containers:
         - name: app
           image: myapp:latest
           env:
           - name: HH_API_KEY
             valueFrom:
               secretKeyRef:
                 name: honeyhive-secret
                 key: api-key

**Create Secret**:

.. code-block:: bash

   # Create secret from command line
   kubectl create secret generic honeyhive-secret \
     --from-literal=api-key=hh_your_api_key_here

**Using External Secrets Operator**:

.. code-block:: yaml

   # external-secret.yaml
   apiVersion: external-secrets.io/v1beta1
   kind: ExternalSecret
   metadata:
     name: honeyhive-secret
   spec:
     refreshInterval: 15s
     secretStoreRef:
       name: aws-secrets-manager
       kind: SecretStore
     target:
       name: honeyhive-secret
     data:
     - secretKey: api-key
       remoteRef:
         key: honeyhive-api-key

Troubleshooting Authentication
------------------------------

Common Issues
~~~~~~~~~~~~~

**Invalid API Key**:

.. code-block:: python

   # Error: 401 Unauthorized
   # Causes:
   # 1. Wrong API key
   # 2. Expired API key
   # 3. API key not set
   
   # Debug:
   import os
   print(f"API Key set: {'HH_API_KEY' in os.environ}")
   print(f"API Key preview: {os.environ.get('HH_API_KEY', 'NOT_SET')[:8]}***")

**Permission Denied**:

.. code-block:: python

   # Error: 403 Forbidden
   # Causes:
   # 1. Insufficient permissions
   # 2. Project access denied
   # 3. Feature not enabled
   
   # Check permissions:
   honeyhive auth whoami

**Network Issues**:

.. code-block:: python

   # Error: Connection timeout
   # Causes:
   # 1. Network connectivity
   # 2. Firewall blocking
   # 3. SSL/TLS issues
   
   # Debug:
   import requests
   response = requests.get("https://api.honeyhive.ai/api/v1/health")
   print(f"API accessible: {response.status_code == 200}")

**Configuration Issues**:

.. code-block:: python

   # Debug configuration loading
   from honeyhive.utils.config import get_config
   
   config = get_config()
   print(f"Configuration: {config}")
   print(f"API Key source: {config.get('api_key_source', 'unknown')}")

Debugging Tools
~~~~~~~~~~~~~~~

**CLI Debugging**:

.. code-block:: bash

   # Check authentication
   honeyhive auth whoami --verbose
   
   # Test API connectivity
   honeyhive project list --debug
   
   # Validate configuration
   honeyhive config list

**Python Debugging**:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   from honeyhive import HoneyHiveTracer
   
   # Enable debug mode
   tracer = HoneyHiveTracer.init(
       api_key="hh_your_key",       # Or set HH_API_KEY environment variable
       project="your-project",      # Or set HH_PROJECT environment variable
       debug=True                   # Enables debug logging (or set HH_DEBUG_MODE=true)
   )

**Authentication Test Script**:

.. code-block:: python

   #!/usr/bin/env python3
   """Test HoneyHive authentication"""
   
   import os
   import sys
   from honeyhive import HoneyHive
   
   def test_auth():
       """Test authentication and basic API access"""
       api_key = os.getenv('HH_API_KEY')
       
       if not api_key:
           print("❌ HH_API_KEY environment variable not set")
           return False
       
       if not api_key.startswith('hh_'):
           print("❌ API key format invalid (must start with 'hh_')")
           return False
       
       print(f"✅ API key format valid: {api_key[:8]}***")
       
       try:
           client = HoneyHive(api_key=api_key)
           projects = client.projects.list()
           print(f"✅ Authentication successful")
           print(f"✅ Access to {len(projects)} projects")
           return True
       except Exception as e:
           print(f"❌ Authentication failed: {e}")
           return False
   
   if __name__ == "__main__":
       success = test_auth()
       sys.exit(0 if success else 1)

Security Monitoring
-------------------

**API Key Usage Monitoring**:

.. code-block:: python

   # Monitor API key usage
   import logging
   from honeyhive import HoneyHive
   
   # Set up security logging
   security_logger = logging.getLogger('honeyhive.security')
   security_logger.setLevel(logging.INFO)
   
   # Log authentication attempts
   client = HoneyHive(api_key="hh_your_key")
   security_logger.info(f"HoneyHive client initialized with key: {client.api_key[:8]}***")

**Anomaly Detection**:

Monitor for unusual patterns:
- API calls from unexpected IP addresses
- High volume of requests
- Failed authentication attempts
- Access to unauthorized resources

**Key Rotation Monitoring**:

.. code-block:: python

   # Track key age and rotation
   import datetime
   from honeyhive.utils.auth import get_key_info
   
   key_info = get_key_info()
   key_age = datetime.datetime.now() - key_info['created_at']
   
   if key_age.days > 90:
       print("⚠️ API key is older than 90 days - consider rotation")

See Also
--------

- :doc:`environment-vars` - Environment variable configuration
- :doc:`config-options` - Complete configuration reference
- :doc:`../cli/commands` - CLI authentication commands
- :doc:`../../development/testing/ci-cd-integration` - CI/CD authentication patterns
