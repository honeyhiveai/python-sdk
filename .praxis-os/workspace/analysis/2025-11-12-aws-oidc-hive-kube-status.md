# AWS OIDC Status - Hive-Kube Analysis

**Date:** 2025-11-12  
**Status:** ❌ OIDC NOT implemented in hive-kube yet

---

## 🔍 Analysis of Hive-Kube GitHub Actions

### Current State: Still Using Long-Lived Credentials

**Checked 22 workflows across all environments:**
- ✅ `production-*`
- ✅ `staging-*`
- ✅ `testing-*`
- ✅ `nationwide-*`

**All workflows use the OLD pattern:**

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.HONEYHIVE_PRODUCTION_DEPLOYMENT_AWS_USER_KEY_ID }}
    aws-secret-access-key: ${{ secrets.HONEYHIVE_PRODUCTION_DEPLOYMENT_AWS_USER_KEY_SECRET }}
    aws-region: ${{ env.AWS_REGION }}
```

### What's Missing

1. **No `permissions` block with `id-token: write`**
   - Only `contents: write` found in package release workflows
   - OIDC requires `id-token: write` permission

2. **No `role-to-assume` parameter**
   - Still using `aws-access-key-id` and `aws-secret-access-key`
   - No IAM role ARN configuration

3. **No OIDC provider setup**
   - Would require AWS IAM Identity Provider configuration
   - Trust relationship with GitHub

---

## 🎯 This Means: Python-SDK Can Be First!

### Benefits of Implementing OIDC for Python-SDK

1. **🔒 Security**
   - No long-lived credentials stored in GitHub Secrets
   - Temporary credentials that expire after job completion
   - Reduced risk if GitHub is compromised

2. **♻️ Zero Credential Rotation**
   - No need to rotate access keys every 90 days
   - No secret expiration management

3. **📊 Better Audit Trail**
   - CloudTrail shows which GitHub repo/workflow made the call
   - Direct mapping of GitHub Actions → AWS API calls

4. **🎯 Granular Permissions**
   - IAM role can be scoped per repository
   - Different trust policies for main vs. PR workflows

---

## 📝 OIDC Implementation Plan for Python-SDK

### Step 1: AWS IAM Setup

**Create OIDC Identity Provider in AWS:**

```bash
# In AWS Console or via Terraform
Provider URL: https://token.actions.githubusercontent.com
Audience: sts.amazonaws.com
```

**Create IAM Role with Trust Policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:honeyhiveai/python-sdk:*"
        }
      }
    }
  ]
}
```

**Attach Lambda Permissions Policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:DeleteFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:InvokeFunction",
        "lambda:GetFunction",
        "lambda:PublishLayerVersion",
        "lambda:DeleteLayerVersion"
      ],
      "Resource": "arn:aws:lambda:us-east-1:*:function:honeyhive-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy"
      ],
      "Resource": "arn:aws:iam::*:role/honeyhive-lambda-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*"
      ],
      "Resource": "arn:aws:cloudformation:us-east-1:*:stack/honeyhive-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": "arn:aws:s3:::aws-sam-cli-managed-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### Step 2: Update `.github/workflows/lambda-tests.yml`

**Change from:**

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

**To:**

```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required for checkout
  actions: read     # Required for workflow

jobs:
  lambda-real-aws-tests:
    name: "☁️ Real AWS Environment"
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.event_name == 'schedule'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCOUNT_ID:role/honeyhive-python-sdk-lambda-ci
          role-session-name: github-actions-lambda-test
          aws-region: us-east-1
```

---

### Step 3: Environment-Specific Roles (Optional)

**For more security, use different roles per branch:**

```yaml
- name: Configure AWS credentials via OIDC
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ github.ref == 'refs/heads/main' && 
      'arn:aws:iam::ACCOUNT_ID:role/honeyhive-python-sdk-lambda-prod' || 
      'arn:aws:iam::ACCOUNT_ID:role/honeyhive-python-sdk-lambda-test' }}
    role-session-name: github-actions-lambda-${{ github.run_id }}
    aws-region: us-east-1
```

---

### Step 4: Update Trust Policy for Stricter Security

**Restrict to specific branches/events:**

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": [
        "repo:honeyhiveai/python-sdk:ref:refs/heads/main",
        "repo:honeyhiveai/python-sdk:environment:production"
      ]
    }
  }
}
```

---

## 📋 Implementation Checklist

### AWS Infrastructure
- [ ] Create GitHub OIDC Identity Provider in AWS IAM
- [ ] Create IAM role: `honeyhive-python-sdk-lambda-ci`
- [ ] Configure trust policy for python-sdk repo
- [ ] Attach Lambda/CloudFormation/S3 permissions policy
- [ ] Test OIDC authentication from local AWS CLI (optional)
- [ ] Document IAM role ARN

### GitHub Actions
- [ ] Update `.github/workflows/lambda-tests.yml` with `permissions` block
- [ ] Replace `aws-access-key-id`/`aws-secret-access-key` with `role-to-assume`
- [ ] Add role session naming for audit trail
- [ ] Remove old AWS secret references (after testing)
- [ ] Update documentation

### Testing
- [ ] Trigger workflow manually to test OIDC authentication
- [ ] Verify CloudTrail logs show correct GitHub metadata
- [ ] Confirm Lambda deployment works
- [ ] Validate cleanup works
- [ ] Document any issues

### Documentation
- [ ] Update `docs/development/testing/lambda-testing.rst` with OIDC setup
- [ ] Add troubleshooting guide for OIDC issues
- [ ] Document IAM role configuration
- [ ] Add to CI/CD integration docs

---

## 🎓 Educational Value

**This makes python-sdk the reference implementation for:**
1. Modern GitHub Actions security best practices
2. AWS OIDC integration patterns
3. Zero-trust CI/CD workflows

**When hive-kube eventually migrates to OIDC, we'll have:**
- Working examples
- Lessons learned
- Reusable IAM role configurations
- Troubleshooting knowledge

---

## 🚀 Next Steps

1. **Decide**: Do we implement OIDC now or stick with secrets for initial rollout?
2. **If OIDC**: Start with AWS IAM setup
3. **If secrets first**: Document OIDC as a future enhancement

**Recommendation:** 
- **Short-term (v1.0.0):** Use secrets (faster to implement, battle-tested)
- **Post-v1.0.0:** Migrate to OIDC (better security, becomes reference for hive-kube)

This gives us stable Lambda testing now, with a clear migration path to modern auth later.

---

## 📚 Resources

- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC Identity Providers](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [configure-aws-credentials Action](https://github.com/aws-actions/configure-aws-credentials)

