"""LangChain / LangGraph tools for Claix (extra: ``pip install 'claix-ai[langchain]'``)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from claix.client import ClaixClient
from claix.integrations import extract_by_path, require_extra

try:
    from langchain_core.tools import BaseTool as _LangChainBaseTool
except ImportError:  # pragma: no cover

    class _LangChainBaseTool:  # type: ignore[no-redef]
        name: str = ""
        description: str = ""
        args_schema: Any = None

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            require_extra("langchain_core", "langchain")


class ClaixExtractArgs(BaseModel):
    file_path: str = Field(description="Local path to the PDF, Excel, Word, text, or image file.")
    schema_id: str = Field(description="UUID of a Claix schema matching the file type.")
    space_id: str | None = Field(
        default=None,
        description="Optional knowledge-space UUID to attach the persisted document.",
    )
    is_agent_mode: bool = Field(
        default=False,
        description="If true, call POST /agent/*-json instead of /api/*-json.",
    )


class ClaixDocumentContextArgs(BaseModel):
    document_id: str = Field(
        description="UUID returned by an extraction with window_context enabled."
    )
    questions: list[str] = Field(
        description=(
            "1 to 5 questions (max 400 characters). Each string is sent as "
            'format "string". For int, boolean, timestamp, or array, call '
            "client.context.ask with {question, format} objects."
        )
    )


class ClaixSpaceContextArgs(BaseModel):
    space_id: str = Field(description="Knowledge-space UUID grouping persisted documents.")
    questions: list[str] = Field(
        description=(
            "1 to 5 cross-document questions (max 400 characters). Strings are "
            'sent as format "string".'
        )
    )


class ClaixExtractTool(_LangChainBaseTool):  # type: ignore[misc]
    """Extract typed JSON from a file using a Claix schema."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_extract"
    description: str = (
        "Extract structured JSON from a PDF, Excel/CSV, Word/text document, or image "
        "using a Claix schema_id. Returns schema-validated fields; missing values are null."
    )
    args_schema: type[BaseModel] = ClaixExtractArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(
        self,
        file_path: str,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> str:
        result = extract_by_path(
            self.client or ClaixClient(),
            file_path,
            schema_id,
            space_id=space_id,
            is_agent_mode=is_agent_mode,
        )
        return result.model_dump_json()  # type: ignore[union-attr]

    async def _arun(
        self,
        file_path: str,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> str:
        return self._run(file_path, schema_id, space_id, is_agent_mode)


class ClaixDocumentContextTool(_LangChainBaseTool):  # type: ignore[misc]
    """Ask follow-up questions about a single persisted document."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_document_context"
    description: str = (
        "Query a Claix document by document_id. Sends up to 5 questions to "
        "POST /document-context/{document_id}. Answers may be null when evidence is missing."
    )
    args_schema: type[BaseModel] = ClaixDocumentContextArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str, questions: list[str]) -> str:
        result = (self.client or ClaixClient()).context.ask(document_id, questions)
        return result.model_dump_json()

    async def _arun(self, document_id: str, questions: list[str]) -> str:
        return self._run(document_id, questions)


class ClaixSpaceContextTool(_LangChainBaseTool):  # type: ignore[misc]
    """Cross-document Q&A over a knowledge space for LangGraph graphs."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_space_context"
    description: str = (
        "Query every active document in a Claix knowledge space (space_id). "
        "Use this to compare, sum, and reconcile data across multiple files in one call."
    )
    args_schema: type[BaseModel] = ClaixSpaceContextArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, space_id: str, questions: list[str]) -> str:
        result = (self.client or ClaixClient()).spaces.ask(space_id, questions)
        return result.model_dump_json()

    async def _arun(self, space_id: str, questions: list[str]) -> str:
        return self._run(space_id, questions)


class ClaixAddToSpaceArgs(BaseModel):
    document_id: str = Field(description="Persisted document UUID that has no space_id yet.")
    space_id: str = Field(description="Destination knowledge-space UUID.")


class ClaixRemoveFromSpaceArgs(BaseModel):
    document_id: str = Field(description="Document UUID to detach from its knowledge space.")


class ClaixReplaceDocumentArgs(BaseModel):
    document_id: str = Field(description="Stable document UUID whose content will be replaced.")
    new_content_document_id: str = Field(
        description="Source document UUID. It is deleted after the swap."
    )


class ClaixAddToSpaceTool(_LangChainBaseTool):  # type: ignore[misc]
    """Assign a persisted document that has no space_id to a knowledge space."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_add_to_space"
    description: str = (
        "Add a Claix document (document_id with no space) to a knowledge space (space_id). "
        "POST /add-space. Free call. The document must not already belong to a space."
    )
    args_schema: type[BaseModel] = ClaixAddToSpaceArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str, space_id: str) -> str:
        result = (self.client or ClaixClient()).spaces.add(document_id, space_id)
        return result.model_dump_json()

    async def _arun(self, document_id: str, space_id: str) -> str:
        return self._run(document_id, space_id)


class ClaixRemoveFromSpaceTool(_LangChainBaseTool):  # type: ignore[misc]
    """Detach a document from its knowledge space without deleting it."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_remove_from_space"
    description: str = (
        "Remove a document from its Claix knowledge space. "
        "DELETE /remove-document-from-space/{document_id}. The file stays; space_id becomes null."
    )
    args_schema: type[BaseModel] = ClaixRemoveFromSpaceArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str) -> str:
        result = (self.client or ClaixClient()).spaces.remove_document(document_id)
        return result.model_dump_json()

    async def _arun(self, document_id: str) -> str:
        return self._run(document_id)


class ClaixReplaceDocumentTool(_LangChainBaseTool):  # type: ignore[misc]
    """Replace a persisted document's content while keeping its id."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_replace_document"
    description: str = (
        "Replace the content of a persisted Claix document with another document, "
        "keep document_id, and delete the source. POST /replace-document."
    )
    args_schema: type[BaseModel] = ClaixReplaceDocumentArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str, new_content_document_id: str) -> str:
        result = (self.client or ClaixClient()).context.replace(
            document_id, new_content_document_id
        )
        return result.model_dump_json()

    async def _arun(self, document_id: str, new_content_document_id: str) -> str:
        return self._run(document_id, new_content_document_id)
