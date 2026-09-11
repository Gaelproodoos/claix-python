"""Schema CRUD: GET /api/schemas, POST /api/create-schema, POST /api/delete-schema."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from claix.models import (
    CreateSchemaResponse,
    DeleteSchemaResponse,
    SchemaType,
    SchemasListResponse,
    WindowTime,
)

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient


class SchemasResource:
    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def list(self) -> SchemasListResponse:
        payload = self._client.request_json("GET", f"{self._client.base_url}/schemas")
        return SchemasListResponse.model_validate(payload)

    def create(
        self,
        name: str,
        type: SchemaType,
        schema_definition: dict[str, Any],
        *,
        is_agent_mode: bool | None = None,
        agent_definition: dict[str, Any] | None = None,
        resumen_agent: str | None = None,
        window_context: bool | None = None,
        window_time: WindowTime | int | str | None = None,
    ) -> CreateSchemaResponse:
        body: dict[str, Any] = {
            "name": name,
            "type": type,
            "schema_definition": schema_definition,
        }
        if is_agent_mode is not None:
            body["is_agent_mode"] = is_agent_mode
        if agent_definition is not None:
            body["agent_definition"] = agent_definition
        if resumen_agent is not None:
            body["resumen_agent"] = resumen_agent
        if window_context is not None:
            body["window_context"] = window_context
        if window_time is not None:
            body["window_time"] = window_time
        payload = self._client.request_json(
            "POST",
            f"{self._client.base_url}/create-schema",
            json=body,
        )
        return CreateSchemaResponse.model_validate(payload)

    def delete(self, schema_id: str) -> DeleteSchemaResponse:
        payload = self._client.request_json(
            "POST",
            f"{self._client.base_url}/delete-schema",
            json={"schema_id": schema_id},
        )
        return DeleteSchemaResponse.model_validate(payload)


class AsyncSchemasResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def list(self) -> SchemasListResponse:
        payload = await self._client.request_json("GET", f"{self._client.base_url}/schemas")
        return SchemasListResponse.model_validate(payload)

    async def create(
        self,
        name: str,
        type: SchemaType,
        schema_definition: dict[str, Any],
        *,
        is_agent_mode: bool | None = None,
        agent_definition: dict[str, Any] | None = None,
        resumen_agent: str | None = None,
        window_context: bool | None = None,
        window_time: WindowTime | int | str | None = None,
    ) -> CreateSchemaResponse:
        body: dict[str, Any] = {
            "name": name,
            "type": type,
            "schema_definition": schema_definition,
        }
        if is_agent_mode is not None:
            body["is_agent_mode"] = is_agent_mode
        if agent_definition is not None:
            body["agent_definition"] = agent_definition
        if resumen_agent is not None:
            body["resumen_agent"] = resumen_agent
        if window_context is not None:
            body["window_context"] = window_context
        if window_time is not None:
            body["window_time"] = window_time
        payload = await self._client.request_json(
            "POST",
            f"{self._client.base_url}/create-schema",
            json=body,
        )
        return CreateSchemaResponse.model_validate(payload)

    async def delete(self, schema_id: str) -> DeleteSchemaResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.base_url}/delete-schema",
            json={"schema_id": schema_id},
        )
        return DeleteSchemaResponse.model_validate(payload)
