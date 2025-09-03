#!/usr/bin/env python3
"""
Check Bedrock model access and provide recommendations.

This script helps verify which Bedrock models you have access to
and provides guidance for the Strands integration tests.
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_bedrock_access():
    """Check Bedrock model access and provide recommendations."""
    
    print("🔍 Checking AWS Bedrock Model Access")
    print("=" * 40)
    
    try:
        # Try to create a Bedrock client
        session = boto3.Session()
        
        # Check credentials first
        try:
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Identity: {identity.get('Arn', 'unknown').split('/')[-1]}")
            print(f"   Account: {identity.get('Account', 'unknown')}")
            print(f"   Region: {session.region_name or 'us-east-1'}")
        except Exception as e:
            print(f"❌ AWS credential error: {e}")
            return
        
        # Try different regions for Bedrock
        regions_to_try = [
            session.region_name or 'us-east-1',
            'us-east-1',
            'us-west-2', 
            'eu-west-1'
        ]
        
        available_models = {}
        
        for region in set(regions_to_try):  # Remove duplicates
            print(f"\n🌍 Checking region: {region}")
            try:
                bedrock = session.client('bedrock', region_name=region)
                
                # List available foundation models
                response = bedrock.list_foundation_models()
                models = response.get('modelSummaries', [])
                
                if models:
                    print(f"   ✅ Found {len(models)} models in {region}")
                    
                    # Filter for Claude models (most commonly used with Strands)
                    claude_models = [
                        model for model in models 
                        if 'claude' in model.get('modelId', '').lower()
                        and model.get('modelLifecycle', {}).get('status') == 'ACTIVE'
                    ]
                    
                    if claude_models:
                        available_models[region] = claude_models
                        print(f"   🤖 Claude models available: {len(claude_models)}")
                        for model in claude_models[:3]:  # Show first 3
                            print(f"      • {model.get('modelId')}")
                        if len(claude_models) > 3:
                            print(f"      • ... and {len(claude_models) - 3} more")
                    else:
                        print(f"   ⚠️  No Claude models found in {region}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDeniedException':
                    print(f"   ❌ Access denied to Bedrock in {region}")
                elif error_code == 'UnauthorizedOperation':
                    print(f"   ❌ Not authorized for Bedrock in {region}")
                else:
                    print(f"   ❌ Error in {region}: {error_code}")
            except Exception as e:
                print(f"   ❌ Unexpected error in {region}: {e}")
        
        # Provide recommendations
        print(f"\n📋 Recommendations")
        print("=" * 20)
        
        if available_models:
            print("✅ You have Bedrock access! Recommended models for Strands:")
            
            # Find the best region and models
            best_region = None
            best_models = []
            
            for region, models in available_models.items():
                for model in models:
                    model_id = model.get('modelId', '')
                    if 'claude-3-haiku' in model_id:
                        best_region = region
                        best_models.append(model_id)
                        break
            
            if best_models:
                print(f"\n🎯 Best setup for Strands testing:")
                print(f"   Region: {best_region}")
                print(f"   Model: {best_models[0]}")
                print(f"\n📝 Update your scripts to use:")
                print(f'   export AWS_REGION="{best_region}"')
                print(f'   model="{best_models[0]}"')
            
        else:
            print("❌ No Bedrock access found. You need to:")
            print("   1. Request Bedrock access in AWS Console")
            print("   2. Enable Claude models in Bedrock settings")
            print("   3. Ensure your IAM user/role has bedrock:* permissions")
            print("   4. Check if Bedrock is available in your region")
            
            print(f"\n🔗 Links:")
            print("   • Request access: https://console.aws.amazon.com/bedrock/")
            print("   • Model access: Go to Bedrock > Model access > Request access")
            print("   • IAM policy: bedrock:ListFoundationModels, bedrock:InvokeModel")
        
        print(f"\n🧪 For testing without Bedrock:")
        print("   • Use test_mode=True in HoneyHive")
        print("   • Tests will use mock Strands agents")
        print("   • Integration logic still validates correctly")
            
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("   Configure AWS credentials first:")
        print("   • aws configure sso")
        print("   • aws configure")
        print("   • export AWS_ACCESS_KEY_ID=...")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_bedrock_access()
