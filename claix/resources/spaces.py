"""Knowledge spaces: create, add, ask, remove a document, delete."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from claix.resources import QuestionInput, validate_questions
from claix.models import (
    AddSpaceSuccessResponse,
    CreateSpaceSuccessResponse,
    DeleteSpaceSuccessResponse,
    RemoveDocumentFromSpaceSuccessResponse,
    SpaceContextSuccessResponse,
)

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient


class SpacesResource:
    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def create(self, name: str) -> CreateSpaceSuccessResponse:
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/create-space",
            json={"name": name},
        )
        return CreateSpaceSuccessResponse.model_validate(payload)

    def add(self, document_id: str, space_id: str) -> AddSpaceSuccessResponse:
        """POST /add-space. The document must not already belong to a space."""
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/add-space",
            json={"document_id": document_id, "space_id": space_id},
        )
        return AddSpaceSuccessResponse.model_validate(payload)

    def ask(
        self,
        space_id: str,
        questions: Sequence[QuestionInput],
    ) -> SpaceContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/space-context/{space_id}",
            json=body,
        )
        return SpaceContextSuccessResponse.model_validate(payload)

    def remove_document(self, document_id: str) -> RemoveDocumentFromSpaceSuccessResponse:
        """DELETE /remove-document-from-space/{document_id}. The document itself is kept."""
        payload = self._client.request_json(
            "DELETE",
            f"{self._client.origin}/remove-document-from-space/{document_id}",
        )
        return RemoveDocumentFromSpaceSuccessResponse.model_validate(payload)

    def delete(self, space_id: str) -> DeleteSpaceSuccessResponse:
        payload = self._client.request_json(
            "DELETE",
            f"{self._client.origin}/delete-space/{space_id}",
        )
        return DeleteSpaceSuccessResponse.model_validate(payload)


class AsyncSpacesResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def create(self, name: str) -> CreateSpaceSuccessResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/create-space",
            json={"name": name},
        )
        return CreateSpaceSuccessResponse.model_validate(payload)

    async def add(self, document_id: str, space_id: str) -> AddSpaceSuccessResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/add-space",
            json={"document_id": document_id, "space_id": space_id},
        )
        return AddSpaceSuccessResponse.model_validate(payload)

    async def ask(
        self,
        space_id: str,
        questions: Sequence[QuestionInput],
    ) -> SpaceContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/space-context/{space_id}",
            json=body,
        )
        return SpaceContextSuccessResponse.model_validate(payload)

    async def remove_document(
        self, document_id: str
    ) -> RemoveDocumentFromSpaceSuccessResponse:
        payload = await self._client.request_json(
            "DELETE",
            f"{self._client.origin}/remove-document-from-space/{document_id}",
        )
        return RemoveDocumentFromSpaceSuccessResponse.model_validate(payload)

    async def delete(self, space_id: str) -> DeleteSpaceSuccessResponse:
        payload = await self._client.request_json(
            "DELETE",
            f"{self._client.origin}/delete-space/{space_id}",
        )
        return DeleteSpaceSuccessResponse.model_validate(payload)
