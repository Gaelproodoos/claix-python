"""Knowledge spaces: create, ask, delete (OpenAPI 1.8.2)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from claix.resources import validate_questions
from claix.models import (
    CreateSpaceSuccessResponse,
    DeleteSpaceSuccessResponse,
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

    def ask(
        self,
        space_id: str,
        questions: Sequence[str],
    ) -> SpaceContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/space-context/{space_id}",
            json=body,
        )
        return SpaceContextSuccessResponse.model_validate(payload)

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

    async def ask(
        self,
        space_id: str,
        questions: Sequence[str],
    ) -> SpaceContextSuccessResponse:
        body = {"questions": validate_questions(questions)}
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/space-context/{space_id}",
            json=body,
        )
        return SpaceContextSuccessResponse.model_validate(payload)

    async def delete(self, space_id: str) -> DeleteSpaceSuccessResponse:
        payload = await self._client.request_json(
            "DELETE",
            f"{self._client.origin}/delete-space/{space_id}",
        )
        return DeleteSpaceSuccessResponse.model_validate(payload)
