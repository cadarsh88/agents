import re
from typing import Dict
from uuid import uuid4

from ..llm import LLMClient
from ..models import Lead
from ..repository import LeadRepository


class LeadCaptureAgent:
    def __init__(self, llm: LLMClient, repo: LeadRepository) -> None:
        self._llm = llm
        self._repo = repo

    def _normalize_email(self, email: str) -> str:
        email = (email or "").strip().lower()
        return email

    def _is_valid_email(self, email: str) -> bool:
        if not email:
            return False
        # basic check
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D", "", phone or "")
        return digits

    def capture(self, input_text: str) -> Lead:
        extracted: Dict[str, str] = self._llm.extract_lead_fields(input_text)

        full_name = (extracted.get("full_name") or "").strip()
        email_raw = extracted.get("email") or ""
        phone_raw = extracted.get("phone") or ""
        source = (extracted.get("source") or "manual").strip() or "manual"

        email = self._normalize_email(email_raw)
        phone = self._normalize_phone(phone_raw)

        # Basic validations; keep minimal for now
        if email and not self._is_valid_email(email):
            email = ""

        lead = Lead(
            id=uuid4(),
            full_name=full_name,
            email=email,
            phone=phone,
            source=source,
        )

        self._repo.add(lead)

        print(f"EVENT: lead.created {lead.id}")

        return lead


