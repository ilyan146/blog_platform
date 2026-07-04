"""Export the FastAPI OpenAPI schema to a JSON file for frontend client codegen
(hey-api / openapi-ts).

Uses the same safe env-var defaults as tests/conftest.py so this runs without
a live Postgres or Azure OpenAI connection - it only needs to import the app
and read its route definitions, never actually serves a request.

Usage (from repo root):
    uv run --package blog-platform-backend python backend/scripts/export_openapi.py
"""

import json
import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "export-only-secret")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.test")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

from app.main import app  # noqa: E402

OUT_PATH = Path(__file__).resolve().parent.parent.parent / "frontend" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUT_PATH.write_text(json.dumps(schema, indent=2))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
