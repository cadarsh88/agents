"""
Helper script to set AWS region for testing
Run this before testing the agent
"""

import os
import sys

def set_region():
    """Set AWS region for current session"""
    
    # Check if region is already set
    current_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    
    if current_region:
        print(f"[OK] AWS Region is already set to: {current_region}")
        print("\nTo change it, run:")
        print("  PowerShell: $env:AWS_REGION = 'us-west-2'")
        print("  CMD: set AWS_REGION=us-west-2")
        return
    
    print("[ERROR] AWS Region is not set!")
    print("\nTo set it, run one of these commands in your terminal:")
    print("\nPowerShell:")
    print('  $env:AWS_REGION = "us-west-2"')
    print("\nCMD:")
    print("  set AWS_REGION=us-west-2")
    print("\nBash/Linux:")
    print("  export AWS_REGION=us-west-2")
    print("\n[WARNING] Make sure to use a region where Bedrock is available!")
    print("Common Bedrock regions: us-west-2, us-east-1, eu-west-1")


if __name__ == "__main__":
    set_region()
    
    # Also show which credentials profile is being used
    profile = os.environ.get('AWS_PROFILE', 'default')
    print(f"\n📋 Using AWS profile: {profile}")
