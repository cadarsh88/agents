from fastapi import FastAPI

from .agents.lead_capture import LeadCaptureAgent
from .llm import LLMClient
from .models import Lead, LeadCaptureRequest
from .repository import LeadRepository


app = FastAPI(title="Lead Capture Agent")


# Simple singletons for now
_repo = LeadRepository()
_llm = LLMClient()
_agent = LeadCaptureAgent(llm=_llm, repo=_repo)


@app.post("/leads", response_model=Lead)
def create_lead(payload: LeadCaptureRequest) -> Lead:
    return _agent.capture(payload.text)


