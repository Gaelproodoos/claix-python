"""Shared helpers for Claix resource modules."""

from __future__ import annotations

from collections.abc import Sequence
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import BinaryIO

from claix.exceptions import ClaixValidationError

FileInput = str | Path | bytes | bytearray | BinaryIO | tuple[str, bytes]


def validate_questions(questions: Sequence[str]) -> list[str]:
    """Enforce OpenAPI window/space-context limits: 1–5 questions, ≤400 chars."""
    cleaned = [str(q).strip() for q in questions if str(q).strip()]
    if not cleaned:
        raise ClaixValidationError("At least one question is required.")
    if len(cleaned) > 5:
        raise ClaixValidationError("A maximum of 5 questions is allowed per call.")
    for question in cleaned:
        if len(question) > 400:
            raise ClaixValidationError(
                f"Each question must be at most 400 characters (got {len(question)})."
            )
    return cleaned


def prepare_file(file: FileInput, *, default_name: str) -> tuple[str, bytes]:
    """Normalize a file argument into ``(filename, content)``."""
    if isinstance(file, tuple) and len(file) == 2 and isinstance(file[1], (bytes, bytearray)):
        return file[0], bytes(file[1])
    if isinstance(file, (bytes, bytearray)):
        return default_name, bytes(file)
    if isinstance(file, (str, Path)):
        path = Path(file)
        return path.name, path.read_bytes()
    if isinstance(file, (BytesIO, BufferedReader)) or hasattr(file, "read"):
        name = getattr(file, "name", default_name)
        filename = Path(str(name)).name if name else default_name
        data = file.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
        if hasattr(file, "seek"):
            try:
                file.seek(0)
            except OSError:
                pass
        return filename, bytes(data)
    raise TypeError(f"Unsupported file type: {type(file)!r}")
