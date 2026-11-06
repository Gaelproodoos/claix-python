"""Claix Retrieve: POST https://claix.dev/retrieve/{agent_name}."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from urllib.parse import quote

from claix.exceptions import ClaixValidationError
from claix.models import RetrieveSuccessResponse
from claix.resources import QuestionInput, validate_retrieve_questions

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient


def _retrieve_url(origin: str, agent_name: str) -> str:
    name = agent_name.strip()
    if not name:
        raise ClaixValidationError("agent_name is required.")
    return f"{origin}/retrieve/{quote(name, safe='')}"


class RetrieveResource:
    """Ask a Retrieve agent. The agent reads only the tables and columns you allowed."""

    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def ask(
        self,
        agent_name: str,
        questions: Sequence[QuestionInput],
    ) -> RetrieveSuccessResponse:
        payload = self._client.request_json(
            "POST",
            _retrieve_url(self._client.origin, agent_name),
            json={"questions": validate_retrieve_questions(questions)},
        )
        return RetrieveSuccessResponse.model_validate(payload)


class AsyncRetrieveResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def ask(
        self,
        agent_name: str,
        questions: Sequence[QuestionInput],
    ) -> RetrieveSuccessResponse:
        payload = await self._client.request_json(
            "POST",
            _retrieve_url(self._client.origin, agent_name),
            json={"questions": validate_retrieve_questions(questions)},
        )
        return RetrieveSuccessResponse.model_validate(payload)
