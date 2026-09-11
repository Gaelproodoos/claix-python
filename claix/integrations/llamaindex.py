"""LlamaIndex tool spec for Claix (extra: ``pip install 'claix-ai[llamaindex]'``)."""

from __future__ import annotations

from typing import Any

from claix.client import ClaixClient
from claix.integrations import extract_by_path, require_extra

try:
    from llama_index.core.tools.tool_spec.base import BaseToolSpec as _LlamaBaseToolSpec
except ImportError:  # pragma: no cover

    class _LlamaBaseToolSpec:  # type: ignore[no-redef]
        spec_functions: list[str] = []

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            require_extra("llama_index.core", "llamaindex")


class ClaixToolSpec(_LlamaBaseToolSpec):  # type: ignore[misc]
    """LlamaIndex ToolSpec exposing extract, document Q&A, and knowledge-space Q&A."""

    spec_functions = ["extract_document", "ask_document", "ask_knowledge_space"]

    def __init__(self, client: ClaixClient | None = None) -> None:
        self.client = client or ClaixClient()

    def extract_document(
        self,
        file_path: str,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> str:
        """Extract typed JSON from a local file using a Claix schema.

        Args:
            file_path: Path to a PDF, Excel/CSV, Word/text, or image file.
            schema_id: UUID of the target Claix schema.
            space_id: Optional knowledge-space UUID for persistence.
            is_agent_mode: Use Agent Mode endpoints under /agent/*-json.
        """
        result = extract_by_path(
            self.client,
            file_path,
            schema_id,
            space_id=space_id,
            is_agent_mode=is_agent_mode,
        )
        return result.model_dump_json()  # type: ignore[union-attr]

    def ask_document(self, document_id: str, questions: list[str]) -> str:
        """Ask up to 5 questions about a persisted document (document_id).

        Missing evidence is returned as native JSON null in ia_response.
        """
        result = self.client.context.ask(document_id, questions)
        return result.model_dump_json()

    def ask_knowledge_space(self, space_id: str, questions: list[str]) -> str:
        """Ask up to 5 cross-document questions over a knowledge space (space_id)."""
        result = self.client.spaces.ask(space_id, questions)
        return result.model_dump_json()
