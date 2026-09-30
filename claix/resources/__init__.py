"""Shared helpers for Claix resource modules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Any, BinaryIO

from claix.exceptions import ClaixValidationError

FileInput = str | Path | bytes | bytearray | BinaryIO | tuple[str, bytes]
QuestionFormat = str
QUESTION_FORMATS = frozenset({"string", "int", "boolean", "timestamp", "array"})
QuestionInput = str | Mapping[str, Any]


def validate_questions(questions: Sequence[QuestionInput]) -> list[dict[str, str]]:
    """Normalize questions to ``{question, format}`` (1–5 items, ≤400 chars).

    A plain string is sent as ``format: "string"``.
    """
    cleaned: list[dict[str, str]] = []
    for raw in questions:
        if isinstance(raw, str):
            question = raw.strip()
            fmt = "string"
        elif isinstance(raw, Mapping):
            question = str(raw.get("question") or "").strip()
            fmt = str(raw.get("format") or "string").strip()
        else:
            raise ClaixValidationError(
                "Each question must be a string or an object with question and format."
            )
        if not question:
            continue
        if fmt not in QUESTION_FORMATS:
            raise ClaixValidationError(
                f"format must be one of: {', '.join(sorted(QUESTION_FORMATS))} (got {fmt!r})."
            )
        cleaned.append({"question": question, "format": fmt})
    if not cleaned:
        raise ClaixValidationError("At least one question is required.")
    if len(cleaned) > 5:
        raise ClaixValidationError("A maximum of 5 questions is allowed per call.")
    for item in cleaned:
        if len(item["question"]) > 400:
            raise ClaixValidationError(
                f"Each question must be at most 400 characters (got {len(item['question'])})."
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
