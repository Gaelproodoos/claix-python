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
        description="1 to 5 questions (max 400 characters each) about that document."
    )


class ClaixSpaceContextArgs(BaseModel):
    space_id: str = Field(description="Knowledge-space UUID grouping persisted documents.")
    questions: list[str] = Field(
        description="1 to 5 cross-document questions (max 400 characters each)."
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
