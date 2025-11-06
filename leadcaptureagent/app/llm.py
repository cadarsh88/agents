import json
import os
import re
from typing import Dict


class LLMClient:
    """OpenAI-compatible client placeholder. Not used by default.

    Configure via env: OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def extract_lead_fields(self, input_text: str) -> Dict[str, str]:
        try:
            from openai import OpenAI, DefaultHttpxClient
        except Exception as e:  # pragma: no cover
            raise RuntimeError("openai package not installed. Please install from requirements.txt") from e

        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        # Construct a default http client without passing unsupported kwargs (e.g., proxies)
        http_client = DefaultHttpxClient()
        client = OpenAI(api_key=self.api_key, base_url=self.base_url, http_client=http_client)

        system = (
            "You are an information extraction assistant. Extract lead fields as strict JSON with keys: "
            "full_name, email, phone, source. Use 'manual' as default for source if not provided. "
            "Return only valid JSON without code fences."
        )
        user = (
            f"Input text:\n{input_text}\n\n"
            "Respond with a JSON object like: {\"full_name\": \"...\", \"email\": \"...\", \"phone\": \"...\", \"source\": \"manual\"}"
        )

        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            data = json.loads(content)
        except Exception:
            # Fallback: empty fields structure if the provider doesn't support response_format
            try:
                # Retry without response_format
                resp = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                )
                content = resp.choices[0].message.content or "{}"
                # Try to parse JSON from free-form content
                # Extract first JSON object
                match = re.search(r"\{[\s\S]*\}", content)
                data = json.loads(match.group(0)) if match else {}
            except Exception as e:
                raise RuntimeError(f"LLM extraction failed: {e}") from e

        return {
            "full_name": (data.get("full_name") or "").strip(),
            "email": (data.get("email") or "").strip(),
            "phone": (data.get("phone") or "").strip(),
            "source": (data.get("source") or "manual").strip() or "manual",
        }


class MockLLMClient:
    """Deterministic extractor for local testing without network/API keys.

    Uses simple regex heuristics to extract fields from free-form text.
    """

    EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+")
    PHONE_RE = re.compile(r"(?:\+?\d[\s\-()]?){7,15}")

    def _extract_name(self, text: str) -> str:
        text = text or ""
        # Common patterns: my name is X, I am X, I'm X, this is X
        patterns = [
            r"\bmy name is\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3})",
            r"\b(?:I am|I'm)\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3})",
            r"\bthis is\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3})",
        ]
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                # Keep original casing for the captured group
                return m.group(1).strip()

        # Fallback: first name-like phrase (two consecutive capitalized words)
        m = re.search(r"\b([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)\b", text)
        if m:
            return m.group(1).strip()

        # Fallback: single capitalized word early in the text
        m = re.search(r"\b([A-Z][a-zA-Z]+)\b", text)
        if m:
            return m.group(1).strip()

        return ""

    def extract_lead_fields(self, input_text: str) -> Dict[str, str]:
        email_match = self.EMAIL_RE.search(input_text or "")
        phone_match = self.PHONE_RE.search(input_text or "")

        name = self._extract_name(input_text)

        return {
            "full_name": name or "",
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "source": "manual",
        }


