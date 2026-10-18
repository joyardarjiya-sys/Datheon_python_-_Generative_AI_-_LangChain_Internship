from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .prompts import build_prompt
from .providers import ProviderCallFailed, ProviderUnavailable, call_provider, configured_providers
from .schemas import ExtractRequest
from .validation import InputRejected, preflight_text, validate_extraction

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(levelname)s %(message)s")
logger = logging.getLogger("structuralai")

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

app = FastAPI(title="structuralAI", version="1.0.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "structuralAI", "providers": configured_providers()}


@app.post("/api/extract")
def extract(request: Request, payload: dict) -> JSONResponse:
    request_id = uuid.uuid4().hex[:12]
    try:
        request_data = ExtractRequest.model_validate(payload)
        preflight_text(request_data.text, request_data.guidance)
    except (ValidationError, InputRejected) as exc:
        detail = str(exc) if isinstance(exc, InputRejected) else "The request shape or input limits are invalid."
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": {"code": "INPUT_REJECTED", "message": detail}, "request_id": request_id},
        )

    try:
        prompt = build_prompt(request_data.document_type, request_data.text, request_data.guidance)
        provider_result = call_provider(request_data.provider, prompt)
        validated = validate_extraction(provider_result.raw_text, request_data.document_type)
    except ProviderUnavailable as exc:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "error": {"code": "PROVIDER_NOT_CONFIGURED", "message": str(exc)}, "request_id": request_id},
        )
    except ProviderCallFailed as exc:
        logger.warning("provider_call_failed request_id=%s provider=%s", request_id, request_data.provider)
        return JSONResponse(
            status_code=502,
            content={"ok": False, "error": {"code": "PROVIDER_FAILED", "message": str(exc)}, "request_id": request_id},
        )
    except ValueError as exc:
        logger.warning("validation_failed request_id=%s type=%s", request_id, request_data.document_type)
        return JSONResponse(
            status_code=422,
            content={"ok": False, "error": {"code": "OUTPUT_NOT_VERIFIED", "message": str(exc)}, "request_id": request_id},
        )
    except Exception:
        logger.exception("unexpected_extraction_error request_id=%s", request_id)
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": {"code": "INTERNAL_ERROR", "message": "The extraction could not be completed safely."}, "request_id": request_id},
        )

    return JSONResponse(
        content={
            "ok": True,
            "verified": True,
            "request_id": request_id,
            "document_type": request_data.document_type,
            "provider": request_data.provider,
            "model": provider_result.model,
            "verification": {
                "status": "verified",
                "checks": [
                    "Provider response parsed as one JSON object",
                    "Required fields and types matched the strict schema",
                    "Unexpected fields were rejected",
                    "Only verified data is shown as final",
                ],
                "note": "The result passed structural validation. Confidence still depends on the source text.",
            },
            "data": validated.model_dump(mode="json"),
        }
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/manus-routes.json", include_in_schema=False)
def route_manifest() -> FileResponse:
    return FileResponse(ROOT / "public" / "manus-routes.json", media_type="application/json")


@app.get("/README.md", include_in_schema=False)
def setup_guide() -> FileResponse:
    return FileResponse(ROOT / "README.md", media_type="text/markdown")


@app.get("/{path:path}", include_in_schema=False)
def fallback(path: str) -> FileResponse:
    # Keep the single-page experience resilient without swallowing API errors.
    if path.startswith("api/") or path.startswith("static/"):
        return FileResponse(STATIC_DIR / "index.html", status_code=404)
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
