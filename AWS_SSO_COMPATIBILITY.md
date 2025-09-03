# AWS SSO Compatibility with HoneyHive + Strands Integration

## ✅ **AWS SSO FULLY SUPPORTED**

The HoneyHive + AWS Strands integration script **works seamlessly with AWS SSO credentials** and all other AWS credential methods.

## 🔑 **Supported AWS Credential Methods**

### 1. **AWS SSO (Recommended)**
```bash
# One-time setup
aws configure sso

# Before each session
aws sso login

# Verify credentials
aws sts get-caller-identity
```

**✅ Benefits:**
- Secure, temporary credentials
- Automatic credential rotation
- Centralized access management
- Works with MFA/conditional access

### 2. **Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
```

### 3. **AWS Credentials File**
```bash
# ~/.aws/credentials
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
region = us-east-1
```

### 4. **IAM Roles (EC2/Lambda/ECS)**
- Automatic credential detection
- No manual configuration needed
- Works on AWS services

### 5. **AWS CLI Profiles**
```bash
# Use specific profile
export AWS_PROFILE=my-profile

# Or pass to script
AWS_PROFILE=my-profile python test_strands_integration.py
```

## 🧪 **Test Script AWS Integration**

Our test script automatically:

### **✅ Detects AWS Credentials**
```
✅ AWS credentials configured
   Account: 123456789012
   User/Role: josh-hhai
   Region: us-west-2
```

### **⚠️ Handles Missing Credentials**
```
⚠️  No AWS credentials found
   AWS Strands will use mock mode only
   For real testing, configure AWS credentials:
     - AWS SSO: aws configure sso && aws sso login
     - Environment: export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...
     - AWS CLI: aws configure
```

### **🔧 Sets Default Region**
```
⚠️  No AWS region configured, setting default to us-east-1
```

## 🎯 **AWS SSO Usage Examples**

### **Standard AWS SSO Flow**
```bash
# Configure SSO (one-time)
aws configure sso
# SSO session name: my-company
# SSO start URL: https://my-company.awsapps.com/start
# SSO region: us-east-1
# Account: 123456789012
# Role: PowerUserAccess
# CLI default region: us-east-1

# Login for each session
aws sso login

# Run HoneyHive + Strands tests
export HONEYHIVE_API_KEY="your-key"
python test_strands_integration.py
```

### **Multi-Account SSO**
```bash
# Configure multiple profiles
aws configure sso --profile dev
aws configure sso --profile prod

# Use specific profile
AWS_PROFILE=dev python test_strands_integration.py
```

### **Session Management**
```bash
# Check current session
aws sts get-caller-identity

# Renew expired session
aws sso login

# Use different session
aws sso login --profile another-profile
```

## 🔍 **Credential Troubleshooting**

### **Common Issues & Solutions**

#### **"Session expired"**
```bash
# Solution: Re-login
aws sso login
```

#### **"No credentials found"**
```bash
# Check configuration
aws configure list

# Verify SSO config
cat ~/.aws/config

# Test manually
aws sts get-caller-identity
```

#### **"Permission denied"**
```bash
# Check IAM permissions for Bedrock
aws bedrock list-foundation-models --region us-east-1
```

#### **"Wrong region"**
```bash
# Set region explicitly
export AWS_REGION=us-east-1

# Or use profile with correct region
AWS_PROFILE=us-east-1-profile python test_strands_integration.py
```

## 🛡️ **Security Best Practices**

### **✅ Recommended: AWS SSO**
- Temporary credentials (2-12 hours)
- Centralized access control
- Audit logging
- MFA enforcement
- Automatic credential rotation

### **⚠️ Avoid: Long-term Access Keys**
- Hard to rotate
- Risk of exposure
- No centralized control
- Difficult to audit

### **🔒 For CI/CD: IAM Roles**
- Use IAM roles for service accounts
- Avoid storing credentials in code
- Use OIDC for GitHub Actions
- Leverage AWS service roles

## 📋 **Test Verification**

The integration script verifies:

1. **✅ Credential Detection**: Automatically finds AWS credentials
2. **✅ Permission Testing**: Calls `aws sts get-caller-identity`
3. **✅ Account Information**: Shows account/user for verification
4. **✅ Region Configuration**: Sets default region if missing
5. **✅ Graceful Fallback**: Uses mock mode if credentials unavailable

## 🎯 **Summary**

**AWS SSO is fully supported and recommended** for the HoneyHive + AWS Strands integration. The test script automatically detects and validates AWS credentials from any source, including SSO, making it easy to test the integration in any AWS environment.

```bash
# Complete SSO workflow
aws configure sso
aws sso login
export HONEYHIVE_API_KEY="your-key"
python test_strands_integration.py
# ✅ Everything works!
```
