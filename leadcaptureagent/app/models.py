from uuid import UUID
from pydantic import BaseModel, Field


class Lead(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: str
    source: str = Field(default="manual")


class LeadCaptureRequest(BaseModel):
    text: str


