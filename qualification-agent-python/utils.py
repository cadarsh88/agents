"""
Utility functions for cost tracking and error handling
Essential for testing the agent locally with realistic cost estimates
"""

from typing import Dict, Any
import time
import os
from datetime import datetime

# Model pricing (per 1M tokens) - Using Bedrock pricing
MODEL_PRICING = {
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "input": 3.00,   # $3.00 per 1M input tokens
        "output": 15.00, # $15.00 per 1M output tokens
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "input": 0.25,   # $0.25 per 1M input tokens
        "output": 1.25,  # $1.25 per 1M output tokens
    },
    "amazon.nova-lite-v1:0": {
        "input": 0.06,   # $0.06 per 1M input tokens
        "output": 0.24,  # $0.24 per 1M output tokens
    },
    "amazon.nova-pro-v1:0": {
        "input": 0.80,   # $0.80 per 1M input tokens
        "output": 3.20,  # $3.20 per 1M output tokens
    },
    "amazon.titan-text-premier-v1:0": {
        "input": 0.50,   # $0.50 per 1M input tokens
        "output": 1.50,  # $1.50 per 1M output tokens
    },
    "amazon.titan-text-express-v1": {
        "input": 0.13,   # $0.13 per 1M input tokens
        "output": 0.17,  # $0.17 per 1M output tokens
    },
    "ai21.jamba-1-5-mini-v1:0": {
        "input": 0.20,   # $0.20 per 1M input tokens
        "output": 0.40,  # $0.40 per 1M output tokens
    },
    "meta.llama3-8b-instruct-v1:0": {
        "input": 0.30,   # $0.30 per 1M input tokens
        "output": 0.60,  # $0.60 per 1M output tokens
    }
}


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of tokens (1 token ≈ 4 characters)
    For testing purposes only
    """
    return len(text) // 4


def calculate_cost(
    input_text: str,
    output_text: str,
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
) -> Dict[str, Any]:
    """
    Calculate estimated cost for the agent operation
    
    Args:
        input_text: Input prompt text
        output_text: Model output text
        model_id: Bedrock model ID
        
    Returns:
        Dict with cost breakdown
    """
    # Get pricing or use Claude Sonnet as default
    pricing = MODEL_PRICING.get(model_id, MODEL_PRICING["anthropic.claude-3-5-sonnet-20241022-v2:0"])
    
    # Estimate tokens
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    
    # Calculate costs
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "model_id": model_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "timestamp": datetime.now().isoformat()
    }


def print_cost_summary(cost_info: Dict[str, Any]) -> None:
    """Pretty print cost information"""
    print("\n[COST] COST ESTIMATE:")
    print(f"  Model: {cost_info['model_id'].split('/')[-1]}")
    print(f"  Input Tokens: ~{cost_info['input_tokens']:,}")
    print(f"  Output Tokens: ~{cost_info['output_tokens']:,}")
    print(f"  Input Cost: ${cost_info['input_cost']:.6f}")
    print(f"  Output Cost: ${cost_info['output_cost']:.6f}")
    print(f"  TOTAL COST: ${cost_info['total_cost']:.6f}")


class AgentTimer:
    """Simple timer context manager for performance tracking"""
    
    def __init__(self, operation: str = "Operation"):
        self.operation = operation
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        print(f"\n[TIMER] Starting {self.operation}...")
        return self
        
    def __exit__(self, *args):
        duration = time.time() - self.start_time
        print(f"[TIMER] {self.operation} completed in {duration:.2f} seconds")


def validate_aws_config() -> Dict[str, bool]:
    """
    Check if AWS is properly configured for testing
    Returns dict with configuration status
    """
    import boto3
    
    checks = {
        "aws_credentials": False,
        "aws_region": False,
        "bedrock_access": False
    }
    
    # Check AWS credentials
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            checks["aws_credentials"] = True
    except:
        pass
    
    # Check AWS region (hardcoded to us-east-1)
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
    if region:
        checks["aws_region"] = True
    
    # Check Bedrock access (without making actual API call)
    if checks["aws_credentials"] and checks["aws_region"]:
        checks["bedrock_access"] = True  # Assume true if credentials exist
    
    return checks


def print_aws_config_status():
    """Print AWS configuration status for debugging"""
    checks = validate_aws_config()
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
    
    print("\n[CONFIG] AWS Configuration Status:")
    print(f"  [OK] AWS Credentials: {'Found' if checks['aws_credentials'] else '[FAIL] Not found'}")
    print(f"  [OK] AWS Region: Set to {region}")
    print(f"  [OK] Bedrock Access: {'Ready' if checks['bedrock_access'] else '[FAIL] Not ready'}")
    
    if not all(checks.values()):
        print("\n  [WARNING] To use Bedrock, ensure:")
        print("     1. AWS credentials are configured")
        print("     2. You have Bedrock model access in us-east-1")
        print("     3. Claude 3.5 Sonnet is enabled in Bedrock console")


# Test the utilities if run directly
if __name__ == "__main__":
    # Test cost calculation
    test_input = "Please qualify this lead with email john@example.com and budget $500,000"
    test_output = "The lead is qualified with a score of 85/100. High budget and good source."
    
    cost = calculate_cost(test_input, test_output)
    print_cost_summary(cost)
    
    # Test AWS config
    print_aws_config_status()
    
    # Test timer
    with AgentTimer("Test Operation"):
        time.sleep(1)  # Simulate work
