# AWS Strands + HoneyHive Integration Test

This test script verifies HoneyHive's automatic instrumentation with AWS Strands in multiple scenarios.

## 🎯 Test Objectives

1. **Verify initialization order independence** - HoneyHive should work regardless of whether it's initialized before or after Strands
2. **Confirm span processor integration** - HoneyHive should enrich all Strands spans with session/project context
3. **Test multi-agent workflows** - Multiple Strands agents should all be traced by HoneyHive
4. **Validate span enrichment** - Verify HoneyHive attributes are added to OpenTelemetry spans

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install test requirements
pip install -r test_strands_requirements.txt

# Alternative: Install manually
pip install honeyhive opentelemetry-api opentelemetry-sdk

# For AWS Strands (verified working):
pip install strands-agents
```

### 2. Set Environment Variables

```bash
# Required: HoneyHive API key
export HONEYHIVE_API_KEY="your-honeyhive-api-key"

# Required: AWS Region
export AWS_REGION="us-east-1"  # or your preferred region
```

### 3. AWS Credentials Setup

AWS Strands supports **all standard AWS credential methods**:

#### Option A: AWS SSO (Recommended)
```bash
# Configure AWS SSO
aws configure sso
aws sso login

# Verify credentials
aws sts get-caller-identity
```

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
```

#### Option C: AWS Credentials File
```bash
# Configure via AWS CLI
aws configure

# Or manually edit ~/.aws/credentials
[default]
aws_access_key_id = your-key
aws_secret_access_key = your-secret
region = us-east-1
```

#### Option D: IAM Roles (EC2/Lambda)
No additional setup needed when running on AWS services.

### 4. Check Bedrock Access (Important!)

Before running tests with real models, check your Bedrock access:

```bash
# Check which Bedrock models you can access
python check_bedrock_access.py
```

This will show you:
- Which AWS regions have Bedrock access
- Which Claude models are available
- Recommended model IDs for your setup

### 5. Run the Tests

#### Option A: Simple Test (Recommended First)
```bash
# Test integration without model calls
python test_strands_simple.py
```

#### Option B: Full Test (Requires Bedrock Access)
```bash
# Test with real model execution
python test_strands_integration.py
```

#### Option C: Automated Test Runner
```bash
# Complete test suite with setup validation
./run_strands_tests.sh
```

## 📊 Test Scenarios

### Scenario 1: HoneyHive First
```python
# Initialize HoneyHive tracer first
tracer = HoneyHiveTracer.init(...)

# Create Strands agent (uses HoneyHive's TracerProvider)
agent = Agent(...)
response = agent("query")
```

**Expected Result**: HoneyHive becomes the global TracerProvider, Strands automatically uses it.

### Scenario 2: Strands First
```python
# Create Strands agent first (sets up its own TracerProvider)
agent = Agent(...)

# Initialize HoneyHive tracer (adds span processor to existing provider)
tracer = HoneyHiveTracer.init(...)
response = agent("query")
```

**Expected Result**: HoneyHive adds its span processor to Strands' TracerProvider, enriching all spans.

### Scenario 3: Multiple Agents
```python
# Single HoneyHive tracer with multiple Strands agents
tracer = HoneyHiveTracer.init(...)
research_agent = Agent(...)
writing_agent = Agent(...)

# Both agents traced by HoneyHive
research_result = research_agent("research query")
writing_result = writing_agent("writing query")
```

**Expected Result**: All agents are traced in a unified HoneyHive session.

### Scenario 4: Span Enrichment Verification
```python
# Set up console exporter to see span details
# Verify HoneyHive attributes are added to all spans
```

**Expected Result**: All spans contain `honeyhive.*` attributes.

## 🔍 What the Test Verifies

### ✅ Initialization Order Independence
- ✅ HoneyHive works when initialized first
- ✅ HoneyHive works when initialized after Strands
- ✅ No conflicts between TracerProviders

### ✅ Automatic Span Capture
- ✅ All Strands agent calls are traced
- ✅ Sub-operations (model calls, tool usage) are captured
- ✅ Span hierarchy is maintained

### ✅ HoneyHive Enrichment
- ✅ `honeyhive.session_id` attribute added
- ✅ `honeyhive.project` attribute added
- ✅ `honeyhive.source` attribute added
- ✅ Custom span metadata preserved

### ✅ Multi-Instance Support
- ✅ HoneyHive doesn't override existing providers unnecessarily
- ✅ Span processors are added correctly
- ✅ Context propagation works across agent calls

## 📈 Expected Output

```
🧪 AWS Strands + HoneyHive Integration Test
============================================================
✅ Environment variables configured
✅ Mock Strands Agent created

==================================================
SCENARIO 1: HoneyHive First
==================================================
Step 1: Initializing HoneyHive tracer...
🔧 Creating new TracerProvider as main provider
✓ Set as global TracerProvider
   HoneyHive is main provider: True
   Current provider: TracerProvider
Step 2: Creating Strands agent...
Step 3: Executing agent query...
   Agent response: Mock response to: What is the capital of France?...

==================================================
SCENARIO 2: Strands First
==================================================
Step 1: Creating Strands agent first...
   Provider after Strands: TracerProvider
Step 2: Initializing HoneyHive tracer...
🔧 Using existing TracerProvider: TracerProvider
   HoneyHive will add span processors to the existing provider
✓ Added to existing TracerProvider (not overriding global)
   HoneyHive is main provider: False
   Current provider: TracerProvider
Step 3: Executing agent query...
   Agent response: Mock response to: What is the largest planet in our solar system?...

============================================================
TEST SUMMARY
============================================================
Total Tests: 4
Passed: 4
Failed: 0
Success Rate: 100.0%
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. **Bedrock Access Denied**
```
Error: AccessDeniedException: You don't have access to the model
```

**Solution:**
```bash
# Check Bedrock access
python check_bedrock_access.py

# Request model access in AWS Console
# Go to Bedrock > Model access > Request access
```

#### 2. **Invalid HoneyHive API Key**
```
Error: Invalid authorization token format
```

**Solution:**
```bash
# Set a valid HoneyHive API key
export HONEYHIVE_API_KEY="hh-your-actual-api-key"

# Or use test mode
python test_strands_simple.py  # Uses test mode automatically
```

#### 3. **Import Error for strands-agents**
```bash
pip install strands-agents
```

#### 4. **ProxyTracerProvider Warning**
```
⚠️ Existing provider doesn't support span processors
```

**This is normal** - HoneyHive detects existing OpenTelemetry setup and adds itself appropriately.

#### 5. **AWS Region Issues**
```bash
# Set explicit region
export AWS_REGION="us-east-1"

# Check which regions have Bedrock
python check_bedrock_access.py
```

#### 6. **OpenTelemetry Version Conflicts**
```bash
pip install --upgrade opentelemetry-api opentelemetry-sdk
```

### Mock Mode

If AWS Strands isn't available, the test automatically creates mock agents that simulate the OpenTelemetry integration pattern. This allows testing the core instrumentation logic without requiring the actual Strands package.

## 🎯 Key Verification Points

1. **Order Independence**: Both initialization orders should pass
2. **Provider Handling**: 
   - Scenario 1: `is_main_provider: True`
   - Scenario 2: `is_main_provider: False`
3. **Span Enrichment**: All spans should have HoneyHive attributes
4. **No Failures**: All test scenarios should pass

## 📝 Adding to Examples Directory

After successful testing, this integration pattern should be documented in:
- `examples/strands_integration.py` - Basic integration example
- `docs/how-to/integrations/aws-strands.rst` - Comprehensive documentation
- `tests/compatibility_matrix/test_strands.py` - Automated testing
