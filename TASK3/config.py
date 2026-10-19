import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the current project directory.
PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

try:
    AGENT_MAX_ITERATIONS = int(
        os.getenv("AGENT_MAX_ITERATIONS", "8")
    )
except ValueError:
    AGENT_MAX_ITERATIONS = 8

if AGENT_MAX_ITERATIONS < 1:
    AGENT_MAX_ITERATIONS = 8

DATA_DIR = (
    PROJECT_DIR / os.getenv("ALLOWED_DATA_DIR", "data")
).resolve()

# Create the local data directory if it does not exist.
DATA_DIR.mkdir(parents=True, exist_ok=True)


def validate_config():
    """Validate required environment variables."""

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    return True