"""Extraction endpoints: /api/*-json, /agent/*-json, and JSON → Excel."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from claix.models import (
    AgentDocJsonSuccessResponse,
    AgentExcelJsonSuccessResponse,
    AgentImgJsonSuccessResponse,
    AgentAudioJsonSuccessResponse,
    AgentPdfJsonSuccessResponse,
    DocJsonSuccessResponse,
    ExcelJsonSuccessResponse,
    ImgJsonSuccessResponse,
    AudioJsonSuccessResponse,
    PdfJsonSuccessResponse,
)
from claix.resources import FileInput, prepare_file

if TYPE_CHECKING:
    from claix.client import AsyncClaixClient, ClaixClient


class ExtractionResource:
    def __init__(self, client: ClaixClient) -> None:
        self._client = client

    def pdf(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> PdfJsonSuccessResponse | AgentPdfJsonSuccessResponse:
        payload = self._upload(
            "pdf-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="document.pdf",
            content_type="application/pdf",
        )
        if is_agent_mode:
            return AgentPdfJsonSuccessResponse.model_validate(payload)
        return PdfJsonSuccessResponse.model_validate(payload)

    def excel(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> ExcelJsonSuccessResponse | AgentExcelJsonSuccessResponse:
        payload = self._upload(
            "excel-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="workbook.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        if is_agent_mode:
            return AgentExcelJsonSuccessResponse.model_validate(payload)
        return ExcelJsonSuccessResponse.model_validate(payload)

    def document(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> DocJsonSuccessResponse | AgentDocJsonSuccessResponse:
        payload = self._upload(
            "doc-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="document.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        if is_agent_mode:
            return AgentDocJsonSuccessResponse.model_validate(payload)
        return DocJsonSuccessResponse.model_validate(payload)

    def image(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> ImgJsonSuccessResponse | AgentImgJsonSuccessResponse:
        payload = self._upload(
            "img-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="image.jpg",
            content_type="image/jpeg",
        )
        if is_agent_mode:
            return AgentImgJsonSuccessResponse.model_validate(payload)
        return ImgJsonSuccessResponse.model_validate(payload)

    def audio(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> AudioJsonSuccessResponse | AgentAudioJsonSuccessResponse:
        payload = self._upload(
            "audio-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="audio.mp3",
            content_type="audio/mpeg",
        )
        if is_agent_mode:
            return AgentAudioJsonSuccessResponse.model_validate(payload)
        return AudioJsonSuccessResponse.model_validate(payload)

    def text(
        self,
        content: str,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> DocJsonSuccessResponse | AgentDocJsonSuccessResponse:
        """POST multipart ``content`` + ``schema_id`` to ``/api/txt-json`` or ``/agent/txt-json``."""
        data: dict[str, str] = {"content": content, "schema_id": schema_id}
        if space_id:
            data["space_id"] = space_id
        url = (
            f"{self._client.origin}/agent/txt-json"
            if is_agent_mode
            else f"{self._client.base_url}/txt-json"
        )
        payload = self._client.request_json("POST", url, data=data)
        if is_agent_mode:
            return AgentDocJsonSuccessResponse.model_validate(payload)
        return DocJsonSuccessResponse.model_validate(payload)

    def json_to_excel(
        self,
        *,
        schema_id: str,
        data: Sequence[dict[str, Any]] | dict[str, Any] | None = None,
        records: Sequence[dict[str, Any]] | None = None,
    ) -> bytes:
        """POST ``/api/json-excel`` and return the binary ``.xlsx`` payload."""
        body: dict[str, Any] = {"schema_id": schema_id}
        if data is not None:
            body["data"] = list(data) if not isinstance(data, dict) else [data]
        if records is not None:
            body["records"] = list(records)
        result = self._client.request(
            "POST",
            f"{self._client.base_url}/json-excel",
            json=body,
            expect_json=False,
        )
        return bytes(result)

    def _upload(
        self,
        slug: str,
        file: FileInput,
        schema_id: str,
        space_id: str | None,
        is_agent_mode: bool,
        *,
        default_name: str,
        content_type: str,
    ) -> Any:
        filename, content = prepare_file(file, default_name=default_name)
        form: dict[str, str] = {"schema_id": schema_id}
        if space_id:
            form["space_id"] = space_id
        url = (
            f"{self._client.origin}/agent/{slug}"
            if is_agent_mode
            else f"{self._client.base_url}/{slug}"
        )
        return self._client.request_json(
            "POST",
            url,
            data=form,
            files={"file": (filename, content, content_type)},
        )


class AsyncExtractionResource:
    def __init__(self, client: AsyncClaixClient) -> None:
        self._client = client

    async def pdf(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> PdfJsonSuccessResponse | AgentPdfJsonSuccessResponse:
        payload = await self._upload(
            "pdf-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="document.pdf",
            content_type="application/pdf",
        )
        if is_agent_mode:
            return AgentPdfJsonSuccessResponse.model_validate(payload)
        return PdfJsonSuccessResponse.model_validate(payload)

    async def excel(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> ExcelJsonSuccessResponse | AgentExcelJsonSuccessResponse:
        payload = await self._upload(
            "excel-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="workbook.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        if is_agent_mode:
            return AgentExcelJsonSuccessResponse.model_validate(payload)
        return ExcelJsonSuccessResponse.model_validate(payload)

    async def document(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> DocJsonSuccessResponse | AgentDocJsonSuccessResponse:
        payload = await self._upload(
            "doc-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="document.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        if is_agent_mode:
            return AgentDocJsonSuccessResponse.model_validate(payload)
        return DocJsonSuccessResponse.model_validate(payload)

    async def image(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> ImgJsonSuccessResponse | AgentImgJsonSuccessResponse:
        payload = await self._upload(
            "img-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="image.jpg",
            content_type="image/jpeg",
        )
        if is_agent_mode:
            return AgentImgJsonSuccessResponse.model_validate(payload)
        return ImgJsonSuccessResponse.model_validate(payload)

    async def audio(
        self,
        file: FileInput,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> AudioJsonSuccessResponse | AgentAudioJsonSuccessResponse:
        payload = await self._upload(
            "audio-json",
            file,
            schema_id,
            space_id,
            is_agent_mode,
            default_name="audio.mp3",
            content_type="audio/mpeg",
        )
        if is_agent_mode:
            return AgentAudioJsonSuccessResponse.model_validate(payload)
        return AudioJsonSuccessResponse.model_validate(payload)

    async def text(
        self,
        content: str,
        schema_id: str,
        space_id: str | None = None,
        is_agent_mode: bool = False,
    ) -> DocJsonSuccessResponse | AgentDocJsonSuccessResponse:
        data: dict[str, str] = {"content": content, "schema_id": schema_id}
        if space_id:
            data["space_id"] = space_id
        url = (
            f"{self._client.origin}/agent/txt-json"
            if is_agent_mode
            else f"{self._client.base_url}/txt-json"
        )
        payload = await self._client.request_json("POST", url, data=data)
        if is_agent_mode:
            return AgentDocJsonSuccessResponse.model_validate(payload)
        return DocJsonSuccessResponse.model_validate(payload)

    async def json_to_excel(
        self,
        *,
        schema_id: str,
        data: Sequence[dict[str, Any]] | dict[str, Any] | None = None,
        records: Sequence[dict[str, Any]] | None = None,
    ) -> bytes:
        body: dict[str, Any] = {"schema_id": schema_id}
        if data is not None:
            body["data"] = list(data) if not isinstance(data, dict) else [data]
        if records is not None:
            body["records"] = list(records)
        result = await self._client.request(
            "POST",
            f"{self._client.base_url}/json-excel",
            json=body,
            expect_json=False,
        )
        return bytes(result)

    async def _upload(
        self,
        slug: str,
        file: FileInput,
        schema_id: str,
        space_id: str | None,
        is_agent_mode: bool,
        *,
        default_name: str,
        content_type: str,
    ) -> Any:
        filename, content = prepare_file(file, default_name=default_name)
        form: dict[str, str] = {"schema_id": schema_id}
        if space_id:
            form["space_id"] = space_id
        url = (
            f"{self._client.origin}/agent/{slug}"
            if is_agent_mode
            else f"{self._client.base_url}/{slug}"
        )
        return await self._client.request_json(
            "POST",
            url,
            data=form,
            files={"file": (filename, content, content_type)},
        )
