from __future__ import annotations

import json
import re
from typing import Type

from pydantic import BaseModel, ValidationError

from .schemas import InvoiceData, ResumeData

MAX_TEXT_LENGTH = 12_000
MAX_GUIDANCE_LENGTH = 1_000

# These markers are a safety boundary, not a claim that every matching document is malicious.
INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous",
    "system prompt",
    "developer message",
    "reveal your instructions",
    "jailbreak",
    "<|system|>",
    "<|assistant|>",
)


class InputRejected(ValueError):
    pass


def preflight_text(text: str, guidance: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise InputRejected("Add document text before running extraction.")
    if len(text) > MAX_TEXT_LENGTH:
        raise InputRejected(f"Document text is too long. Keep it under {MAX_TEXT_LENGTH:,} characters.")
    if len(guidance) > MAX_GUIDANCE_LENGTH:
        raise InputRejected(f"Guidance is too long. Keep it under {MAX_GUIDANCE_LENGTH:,} characters.")

    control_count = sum(1 for char in text if ord(char) < 32 and char not in "\n\r\t")
    if control_count > 3:
        raise InputRejected("The document contains unsupported control characters.")

    lowered = f"{text}\n{guidance}".lower()
    if any(marker in lowered for marker in INJECTION_MARKERS):
        raise InputRejected("The input contains instruction-like content. Remove it and submit the document text only.")


def parse_json_object(raw: str) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("The provider returned an empty response.")

    candidate = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        candidate = fenced.group(1).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError("The provider response was not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("The provider response must be a JSON object.")
    return parsed


def validate_extraction(raw: str, document_type: str) -> BaseModel:
    payload = parse_json_object(raw)
    model: Type[BaseModel] = InvoiceData if document_type == "invoice" else ResumeData
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("The JSON did not match the required extraction schema.") from exc
