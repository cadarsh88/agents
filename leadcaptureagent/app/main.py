import os
from fastapi import FastAPI

from .agents.lead_capture import LeadCaptureAgent
from .llm_bedrock import BedrockLLMClient
from .models import Lead, LeadCaptureRequest
from .repository import LeadRepository


app = FastAPI(title="Lead Capture Agent")


# Initialize repository
_repo = LeadRepository()

# Use Bedrock LLM client with Strands agents (agentic workflow)
# Configure via env vars:
# - AWS_REGION (default: us-east-1)
# - BEDROCK_MODEL_ID (default: anthropic.claude-3-5-sonnet-20241022-v2:0)
# - BEDROCK_TEMPERATURE (default: 0.3)
# AWS credentials should be configured via AWS CLI or environment variables
_llm = BedrockLLMClient()
_agent = LeadCaptureAgent(llm=_llm, repo=_repo)


@app.post("/leads", response_model=Lead)
def create_lead(payload: LeadCaptureRequest) -> Lead:
    return _agent.capture(payload.text)


