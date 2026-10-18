from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ProviderUnavailable(RuntimeError):
    pass


class ProviderCallFailed(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderResult:
    raw_text: str
    model: str
    provider: str = "gemini"


def configured_providers() -> dict[str, bool]:
    configured = bool(os.getenv("GEMINI_API_KEY"))

    return {
        "gemini": configured,
        "gemini_fallback": configured,
    }


def call_provider(provider: str, prompt: str) -> ProviderResult:
    if provider not in ("gemini", "gemini_fallback", "auto"):
        raise ProviderUnavailable(
            "Only Google Gemini models are supported."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ProviderUnavailable(
            "Google Gemini is not configured. Set GEMINI_API_KEY."
        )

    primary_model = os.getenv(
        "GEMINI_MODEL", "gemini-3.5-flash-lite"
    )

    fallback_model = os.getenv(
        "GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite"
    )

    if provider == "gemini_fallback":
        models = [fallback_model]
    else:
        models = [primary_model]

        if fallback_model != primary_model:
            models.append(fallback_model)

    errors = []

    for model in models:
        try:
            return _call_gemini(prompt, model, api_key)

        except ProviderCallFailed as exc:
            errors.append(f"{model}: {exc}")
            print(f"Gemini model failed: {model} — {exc}")

    raise ProviderCallFailed(
        "All configured Gemini models failed. "
        + " | ".join(errors)
    )


def _call_gemini(
    prompt: str,
    model: str,
    api_key: str,
) -> ProviderResult:
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=45_000),
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        content = response.text or ""

        if not content.strip():
            raise ProviderCallFailed(
                f"{model} returned an empty response."
            )

        return ProviderResult(
            raw_text=content,
            model=model,
            provider="gemini",
        )

    except ProviderCallFailed:
        raise

    except Exception as exc:
        raise ProviderCallFailed(
            f"{model} failed: {type(exc).__name__}: {exc}"
        ) from exc