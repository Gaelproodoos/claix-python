"""CrewAI tools for Claix (extra: ``pip install 'claix-ai[crewai]'``)."""

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field

from claix.client import ClaixClient
from claix.integrations import extract_by_path, require_extra

try:
    from crewai.tools import BaseTool as _CrewBaseTool
except ImportError:  # pragma: no cover
    try:
        from crewai_tools import BaseTool as _CrewBaseTool  # type: ignore[no-redef]
    except ImportError:

        class _CrewBaseTool:  # type: ignore[no-redef]
            name: str = ""
            description: str = ""
            args_schema: Any = None

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                require_extra("crewai", "crewai")


class ClaixDocumentToolArgs(BaseModel):
    file_path: str = Field(description="Path to the file the CrewAI agent should extract.")
    schema_id: str = Field(description="Claix schema UUID for the expected JSON shape.")
    space_id: str | None = Field(
        default=None,
        description="Optional space_id to persist the document in a knowledge space.",
    )
    is_agent_mode: bool = Field(
        default=False,
        description="Use /agent/*-json for semantic Agent Mode extraction.",
    )


class ClaixKnowledgeSpaceToolArgs(BaseModel):
    space_id: str = Field(description="Knowledge-space UUID to query.")
    questions: list[str] = Field(
        description=(
            "Up to 5 cross-document questions, 400 characters each. "
            'Strings are sent as format "string".'
        )
    )


class ClaixDocumentTool(_CrewBaseTool):  # type: ignore[misc]
    """Let CrewAI agents extract typed JSON from files via Claix."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_document"
    description: str = (
        "Read a PDF, Excel, Word, text, or image file and extract schema-typed JSON "
        "with Claix. Use this instead of stuffing the raw file into the prompt."
    )
    args_schema: Type[BaseModel] = ClaixDocumentToolArgs
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


class ClaixKnowledgeSpaceTool(_CrewBaseTool):  # type: ignore[misc]
    """Cross-document reasoning tool for auditor / analyst CrewAI agents."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_knowledge_space"
    description: str = (
        "Ask questions across every document stored in a Claix knowledge space (space_id). "
        "Ideal for auditors comparing invoices, contracts, and spreadsheets."
    )
    args_schema: Type[BaseModel] = ClaixKnowledgeSpaceToolArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, space_id: str, questions: list[str]) -> str:
        result = (self.client or ClaixClient()).spaces.ask(space_id, questions)
        return result.model_dump_json()


class ClaixAddToSpaceArgs(BaseModel):
    document_id: str = Field(description="Persisted document UUID with no space_id.")
    space_id: str = Field(description="Destination knowledge-space UUID.")


class ClaixRemoveFromSpaceArgs(BaseModel):
    document_id: str = Field(description="Document UUID to detach from its space.")


class ClaixReplaceDocumentArgs(BaseModel):
    document_id: str = Field(description="Stable document UUID whose content is replaced.")
    new_content_document_id: str = Field(description="Source document UUID, deleted after the swap.")


class ClaixAddToSpaceTool(_CrewBaseTool):  # type: ignore[misc]
    """Assign a document with no space_id to a knowledge space."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_add_to_space"
    description: str = (
        "Add a persisted Claix document to a knowledge space. "
        "The document must not already have a space_id."
    )
    args_schema: Type[BaseModel] = ClaixAddToSpaceArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str, space_id: str) -> str:
        result = (self.client or ClaixClient()).spaces.add(document_id, space_id)
        return result.model_dump_json()


class ClaixRemoveFromSpaceTool(_CrewBaseTool):  # type: ignore[misc]
    """Detach a document from its knowledge space without deleting the file."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_remove_from_space"
    description: str = (
        "Remove a document from its Claix knowledge space without deleting the file."
    )
    args_schema: Type[BaseModel] = ClaixRemoveFromSpaceArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str) -> str:
        result = (self.client or ClaixClient()).spaces.remove_document(document_id)
        return result.model_dump_json()


class ClaixReplaceDocumentTool(_CrewBaseTool):  # type: ignore[misc]
    """Replace persisted document content while keeping document_id."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = "claix_replace_document"
    description: str = (
        "Replace a persisted document's content from another document, keep document_id, "
        "and delete the source."
    )
    args_schema: Type[BaseModel] = ClaixReplaceDocumentArgs
    client: ClaixClient | None = None

    def __init__(self, client: ClaixClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or ClaixClient()

    def _run(self, document_id: str, new_content_document_id: str) -> str:
        result = (self.client or ClaixClient()).context.replace(
            document_id, new_content_document_id
        )
        return result.model_dump_json()
