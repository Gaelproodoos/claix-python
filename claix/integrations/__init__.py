"""Optional agent-framework integrations for Claix."""

from __future__ import annotations

from pathlib import Path

from claix.client import ClaixClient
from claix.exceptions import ClaixValidationError
from claix.resources import FileInput


def require_extra(module: str, extra: str) -> None:
    raise ImportError(
        f"Optional extra '{extra}' is not installed (failed to import {module}). "
        f"Install it with: pip install 'claix-ai[{extra}]'"
    )


def infer_extract_kind(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".xlsx", ".xls", ".csv"}:
        return "excel"
    if suffix in {".docx", ".txt", ".md", ".rtf", ".html", ".xml"}:
        return "document"
    if suffix in {".jpeg", ".jpg", ".png", ".webp", ".heic", ".heif"}:
        return "image"
    raise ClaixValidationError(
        f"Cannot infer Claix extractor from extension {suffix or '(none)'}. "
        "Use a PDF, Excel/CSV, Word/text, or supported image file."
    )


def extract_by_path(
    client: ClaixClient,
    file: FileInput,
    schema_id: str,
    *,
    space_id: str | None = None,
    is_agent_mode: bool = False,
    kind: str | None = None,
) -> object:
    path = file if isinstance(file, str) else getattr(file, "name", "")
    detected = kind or (infer_extract_kind(str(path)) if path else "document")
    if detected == "pdf":
        return client.extract.pdf(file, schema_id, space_id=space_id, is_agent_mode=is_agent_mode)
    if detected == "excel":
        return client.extract.excel(file, schema_id, space_id=space_id, is_agent_mode=is_agent_mode)
    if detected == "image":
        return client.extract.image(file, schema_id, space_id=space_id, is_agent_mode=is_agent_mode)
    return client.extract.document(file, schema_id, space_id=space_id, is_agent_mode=is_agent_mode)
