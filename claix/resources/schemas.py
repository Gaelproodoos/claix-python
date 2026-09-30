"""Schema CRUD: list, get, create, update, delete."""

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


def _schema_body(
    name: str,
    type: SchemaType,
    schema_definition: dict[str, Any],
    *,
    is_agent_mode: bool | None,
    agent_definition: dict[str, Any] | None,
    resumen_agent: str | None,
    window_context: bool | None,
    window_time: WindowTime | int | str | None,
    cita_por_campo: bool | None,
) -> dict[str, Any]:
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
    if cita_por_campo is not None:
        body["cita_por_campo"] = cita_por_campo
    return body


class SchemasResource:
    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def list(self) -> SchemasListResponse:
        payload = self._client.request_json("GET", f"{self._client.base_url}/schemas")
        return SchemasListResponse.model_validate(payload)

    def get(self, schema_id: str) -> CreateSchemaResponse:
        payload = self._client.request_json(
            "GET",
            f"{self._client.base_url}/get-schema/{schema_id}",
        )
        return CreateSchemaResponse.model_validate(payload)

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
        cita_por_campo: bool | None = None,
    ) -> CreateSchemaResponse:
        payload = self._client.request_json(
            "POST",
            f"{self._client.base_url}/create-schema",
            json=_schema_body(
                name,
                type,
                schema_definition,
                is_agent_mode=is_agent_mode,
                agent_definition=agent_definition,
                resumen_agent=resumen_agent,
                window_context=window_context,
                window_time=window_time,
                cita_por_campo=cita_por_campo,
            ),
        )
        return CreateSchemaResponse.model_validate(payload)

    def update(
        self,
        schema_id: str,
        name: str,
        type: SchemaType,
        schema_definition: dict[str, Any],
        *,
        is_agent_mode: bool | None = None,
        agent_definition: dict[str, Any] | None = None,
        resumen_agent: str | None = None,
        window_context: bool | None = None,
        window_time: WindowTime | int | str | None = None,
        cita_por_campo: bool | None = None,
    ) -> CreateSchemaResponse:
        """PUT /api/update-schema/{schema_id}. Replaces the full configuration."""
        payload = self._client.request_json(
            "PUT",
            f"{self._client.base_url}/update-schema/{schema_id}",
            json=_schema_body(
                name,
                type,
                schema_definition,
                is_agent_mode=is_agent_mode,
                agent_definition=agent_definition,
                resumen_agent=resumen_agent,
                window_context=window_context,
                window_time=window_time,
                cita_por_campo=cita_por_campo,
            ),
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

    async def get(self, schema_id: str) -> CreateSchemaResponse:
        payload = await self._client.request_json(
            "GET",
            f"{self._client.base_url}/get-schema/{schema_id}",
        )
        return CreateSchemaResponse.model_validate(payload)

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
        cita_por_campo: bool | None = None,
    ) -> CreateSchemaResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.base_url}/create-schema",
            json=_schema_body(
                name,
                type,
                schema_definition,
                is_agent_mode=is_agent_mode,
                agent_definition=agent_definition,
                resumen_agent=resumen_agent,
                window_context=window_context,
                window_time=window_time,
                cita_por_campo=cita_por_campo,
            ),
        )
        return CreateSchemaResponse.model_validate(payload)

    async def update(
        self,
        schema_id: str,
        name: str,
        type: SchemaType,
        schema_definition: dict[str, Any],
        *,
        is_agent_mode: bool | None = None,
        agent_definition: dict[str, Any] | None = None,
        resumen_agent: str | None = None,
        window_context: bool | None = None,
        window_time: WindowTime | int | str | None = None,
        cita_por_campo: bool | None = None,
    ) -> CreateSchemaResponse:
        payload = await self._client.request_json(
            "PUT",
            f"{self._client.base_url}/update-schema/{schema_id}",
            json=_schema_body(
                name,
                type,
                schema_definition,
                is_agent_mode=is_agent_mode,
                agent_definition=agent_definition,
                resumen_agent=resumen_agent,
                window_context=window_context,
                window_time=window_time,
                cita_por_campo=cita_por_campo,
            ),
        )
        return CreateSchemaResponse.model_validate(payload)

    async def delete(self, schema_id: str) -> DeleteSchemaResponse:
        payload = await self._client.request_json(
            "POST",
            f"{self._client.base_url}/delete-schema",
            json={"schema_id": schema_id},
        )
        return DeleteSchemaResponse.model_validate(payload)
