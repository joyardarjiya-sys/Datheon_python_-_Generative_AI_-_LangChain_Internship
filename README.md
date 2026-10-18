# structuralAI
LLM-powered structured data extraction with Gemini, reusable prompt templates, and Pydantic validation
# structuralAI

A production-minded structured LLM prompt pipeline and JSON extractor for invoice and resume analysis. Paste unstructured text, choose OpenAI or Google Gemini, and receive a result only after strict JSON parsing and Pydantic validation succeed.

## What is included

The Python FastAPI backend validates the request before any provider call, rejects empty or oversized input and instruction-like content, builds a parameterized prompt from the selected document type and schema, calls the selected real provider, parses a single JSON object, and rejects unexpected fields with strict Pydantic models. Provider credentials stay in server environment variables and are never sent to the browser or written to logs.

The frontend is a same-origin static workspace served by FastAPI. It shows explicit `Verified` and `Not verified` states, a readable field inspector, the validated JSON, sanitized errors, and the provider/model used for a verified run.

## Dependencies

Install Python 3.11 or newer. The only runtime dependencies are pinned in `requirements.txt`:

- `fastapi` and `uvicorn[standard]` for the API and local server.
- `pydantic` for strict request and output validation.
- `python-dotenv` for local `.env` loading.
- `httpx` for provider SDK HTTP support.
- `openai` for OpenAI Chat Completions with JSON mode.
- `google-genai` for Google Gemini JSON responses.

## Run in VS Code

Open the repository folder in VS Code and open a new terminal. Create and activate a virtual environment:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

Install the pinned dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create the local environment file and add at least one provider key:

```bash
cp .env.example .env
```

For OpenAI, set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` (default `gpt-4o-mini`). For Google Gemini, set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` (default `gemini-2.5-flash`). Never put either key in `static/`, never commit `.env`, and never paste a key into a browser field. You can configure both providers and switch between them in the UI.

Start the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

Open <http://127.0.0.1:3000>. A health check is available at <http://127.0.0.1:3000/api/health>; it reports only whether a provider is configured, not the key.

## Extraction contract

Invoice mode requires a typed object with invoice number, vendor, dates, currency, totals, line items, and payment terms. Resume mode requires a typed object with name, contact fields, summary, skills, experience, and education. Nullable fields must still be present in the model output; unknown extra fields cause validation to fail. A valid HTTP response includes `verified: true` only after the provider response passed JSON parsing and the selected strict Pydantic model.

The backend returns safe error codes: `INPUT_REJECTED`, `PROVIDER_NOT_CONFIGURED`, `PROVIDER_FAILED`, `OUTPUT_NOT_VERIFIED`, or `INTERNAL_ERROR`. Provider payloads, prompt content, document text, and secrets are not logged.

## VS Code tips

Select the `.venv` interpreter with **Python: Select Interpreter**. The project does not require Node or a separate frontend build. If you want automatic formatting, install the official Python extension and optionally use Ruff; Ruff is not required to run the project. The app serves the frontend directly, so there is no second dev server or CORS setup.
