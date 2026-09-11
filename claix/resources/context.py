"""Document context window: GET/POST/DELETE on https://claix.dev/*-document."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from claix.resources import validate_questions
from claix.models import (
    DeleteDocumentSuccessResponse,
    GetDocumentSuccessResponse,
    WindowContextSuccessResponse,
)

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient


class ContextResource:
    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def get(self, document_id: str) -> GetDocumentSuccessResponse:
        payload = self._client.request_json(
            "GET",
            f"{self._client.origin}/get-document/{document_id}",
        )
        return GetDocumentSuccessResponse.model_validate(payload)

    def ask(
        self,
        document_id: str,
        questions: Sequence[str],
    ) -> WindowContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/document-context/{document_id}",
            json=body,
        )
        return WindowContextSuccessResponse.model_validate(payload)

    def delete(self, document_id: str) -> DeleteDocumentSuccessResponse:
        payload = self._client.request_json(
            "DELETE",
            f"{self._client.origin}/delete-document/{document_id}",
        )
        return DeleteDocumentSuccessResponse.model_validate(payload)


class AsyncContextResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def get(self, document_id: str) -> GetDocumentSuccessResponse:
        payload = await self._client.request_json(
            "GET",
            f"{self._client.origin}/get-document/{document_id}",
        )
        return GetDocumentSuccessResponse.model_validate(payload)

    async def ask(
        self,
        document_id: str,
        questions: Sequence[str],
    ) -> WindowContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/document-context/{document_id}",
            json=body,
        )
        return WindowContextSuccessResponse.model_validate(payload)

    async def delete(self, document_id: str) -> DeleteDocumentSuccessResponse:
        payload = await self._client.request_json(
            "DELETE",
            f"{self._client.origin}/delete-document/{document_id}",
        )
        return DeleteDocumentSuccessResponse.model_validate(payload)
