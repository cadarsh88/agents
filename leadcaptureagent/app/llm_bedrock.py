import json
import os
import re
from typing import Dict

try:
    from strands import Agent
    from strands.models import BedrockModel
except ImportError:
    raise ImportError(
        "strands-agents package not installed. Install with: pip install strands-agents"
    )


class BedrockLLMClient:
    """AWS Bedrock client using Strands agents with Claude Sonnet."""

    def __init__(self) -> None:
        # AWS region for Bedrock (default: us-east-1)
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        # Claude Sonnet model ID for Bedrock
        # Available models (check with: aws bedrock list-foundation-models --region us-east-1):
        # - anthropic.claude-3-sonnet-20240229-v1:0 (Claude 3 Sonnet - base)
        # - anthropic.claude-3-sonnet-20240229-v1:0:28k (Claude 3 Sonnet - 28k context)
        # - anthropic.claude-3-sonnet-20240229-v1:0:200k (Claude 3 Sonnet - 200k context)
        # - anthropic.claude-sonnet-4-20250514-v1:0 (Claude Sonnet 4)
        # - anthropic.claude-sonnet-4-5-20250929-v1:0 (Claude Sonnet 4.5)
        # Using Claude 3 Sonnet base model as default (most widely available)
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID", 
            "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        
        # Temperature for generation
        self.temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.3"))
        
        # Set AWS region via environment if not already set
        # BedrockModel uses boto3 which reads from AWS_REGION env var or AWS config
        if not os.getenv("AWS_REGION"):
            os.environ["AWS_REGION"] = self.region
        
        # Initialize Bedrock model
        # Note: region is configured via AWS_REGION env var, not passed as parameter
        self.model = BedrockModel(
            model_id=self.model_id,
            temperature=self.temperature,
        )
        
        # Create the agent with system prompt for structured extraction
        self.agent = Agent(
            model=self.model,
            system_prompt=(
                "You are a lead capture assistant specialized in extracting structured information from free-form text. "
                "Your task is to analyze user input and extract the following fields:\n\n"
                "- full_name: The person's full name (e.g., 'John Doe', 'Praveen Kumar')\n"
                "- email: Email address (e.g., 'user@example.com')\n"
                "- phone: Phone number as digits only, no formatting (e.g., '9876543210')\n"
                "- source: Lead source (default to 'manual' if not specified in the input)\n\n"
                "IMPORTANT: You must respond with ONLY a valid JSON object containing these four fields. "
                "Do not include any explanatory text, markdown formatting, or code blocks. "
                "Example output format:\n"
                '{"full_name": "John Doe", "email": "john@example.com", "phone": "9876543210", "source": "manual"}'
            ),
        )

    def extract_lead_fields(self, input_text: str) -> Dict[str, str]:
        """Extract lead fields using Strands agent with Claude Sonnet via Bedrock."""
        try:
            # Construct the user prompt for extraction
            user_prompt = (
                f"Extract lead information from the following text:\n\n{input_text}\n\n"
                "Return a JSON object with the fields: full_name, email, phone, source."
            )
            
            # Invoke the agent with the prompt
            response = self.agent(user_prompt)
            
            # Convert response to string
            content = str(response).strip()
            
            # Extract JSON from the response (handle various formats)
            json_match = None
            
            # Try to extract from markdown code blocks
            if "```json" in content:
                match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                if match:
                    json_match = match.group(1)
            elif "```" in content:
                # Generic code block
                match = re.search(r"```\s*(\{.*?\})\s*```", content, re.DOTALL)
                if match:
                    json_match = match.group(1)
            
            # If no code block, try to find JSON object directly
            if not json_match:
                match = re.search(r"\{[\s\S]*\}", content)
                if match:
                    json_match = match.group(0)
            
            # Parse JSON
            if json_match:
                data = json.loads(json_match)
            else:
                # Last resort: try parsing the entire content as JSON
                data = json.loads(content)
            
            # Ensure all required fields are present with defaults
            return {
                "full_name": (data.get("full_name") or "").strip(),
                "email": (data.get("email") or "").strip(),
                "phone": (data.get("phone") or "").strip(),
                "source": (data.get("source") or "manual").strip() or "manual",
            }
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, log and return empty structure
            print(f"WARNING: Failed to parse JSON from agent response: {e}")
            print(f"Response content: {content[:200]}...")  # Log first 200 chars
            return {
                "full_name": "",
                "email": "",
                "phone": "",
                "source": "manual",
            }
        except Exception as e:
            raise RuntimeError(f"Bedrock LLM extraction failed: {e}") from e

