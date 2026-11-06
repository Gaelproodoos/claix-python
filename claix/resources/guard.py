"""Claix Guard: POST https://claix.dev/check-sql.

The check answers allow or deny. Claix does not execute the statement.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from claix.exceptions import ClaixValidationError
from claix.models import CheckSqlResponse

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient

SqlParam = str | int | float | bool | None


def _check_body(
    sql: str,
    params: Sequence[SqlParam] | None,
    connection_id: str | None,
) -> dict[str, Any]:
    statement = sql.strip()
    if not statement:
        raise ClaixValidationError("sql is required.")
    body: dict[str, Any] = {"sql": statement}
    if params is not None:
        body["params"] = list(params)
    if connection_id:
        body["connection_id"] = connection_id
    return body


class GuardResource:
    """Check an INSERT, UPDATE, or DELETE before your code runs it."""

    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def check(
        self,
        sql: str,
        *,
        params: Sequence[SqlParam] | None = None,
        connection_id: str | None = None,
    ) -> CheckSqlResponse:
        """POST /check-sql. Read ``allowed``. A denial is still HTTP 200."""
        payload = self._client.request_json(
            "POST",
            f"{self._client.origin}/check-sql",
            json=_check_body(sql, params, connection_id),
        )
        return CheckSqlResponse.model_validate(payload)


class AsyncGuardResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def check(
        self,
        sql: str,
        *,
        params: Sequence[SqlParam] | None = None,
        connection_id: str | None = None,
    ) -> CheckSqlResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.origin}/check-sql",
            json=_check_body(sql, params, connection_id),
        )
        return CheckSqlResponse.model_validate(payload)
