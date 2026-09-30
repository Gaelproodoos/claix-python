"""Pydantic v2 models for the Claix API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ClaixModel(BaseModel):
    """Forward-compatible base: unknown API fields are preserved."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


SchemaType = Literal[
    "excel-json",
    "json-excel",
    "pdf-json",
    "doc-json",
    "img-json",
    "txt-json",
    "audio-json",
]

FieldType = Literal["string", "integer", "number", "boolean"]
AgentFieldType = Literal["boolean", "string", "closed", "integer"]
WindowTimeMinutes = Literal[5, 10, 15, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 1440, 0]
WindowTime = WindowTimeMinutes | Literal["infinity"]


class ErrorResponse(ClaixModel):
    error: str | None = Field(
        default=None,
        description="Descripción legible del problema.",
    )
    detalle: str | None = Field(
        default=None,
        description="Información técnica adicional (solo presente en algunos casos).",
    )


class ExcelJsonSuccessResponse(ClaixModel):
    success: bool | None = None
    schema_utilizado: str | None = Field(default=None, description="Nombre del schema aplicado.")
    total_filas_procesadas: int | None = Field(
        default=None,
        description="Número de filas de datos transformadas.",
    )
    mapa_columnas: dict[str, str] | None = Field(
        default=None,
        description="Diccionario que muestra qué columna original se emparejó con qué propiedad del schema.",
    )
    data: list[dict[str, Any]] | None = Field(
        default=None,
        description="Registros transformados según el schema. Missing fields are null.",
    )
    document_id: str | None = Field(
        default=None,
        description="Present when window_context is enabled on the schema.",
    )


class PdfJsonSuccessResponse(ClaixModel):
    success: bool | None = None
    schema_utilizado: str | None = None
    total_registros: int | None = Field(
        default=None,
        description="Siempre 1: el documento completo se trata como una única fuente de datos.",
    )
    data: list[dict[str, Any]] | None = Field(
        default=None,
        description="Un objeto extraído. Datos no encontrados se devuelven como null.",
    )
    document_id: str | None = None


class DocJsonSuccessResponse(ClaixModel):
    success: bool | None = None
    schema_utilizado: str | None = None
    total_registros: int | None = None
    data: list[dict[str, Any]] | None = None
    document_id: str | None = None


class ImgJsonSuccessResponse(ClaixModel):
    success: bool | None = None
    schema_utilizado: str | None = None
    total_registros: int | None = None
    data: list[dict[str, Any]] | None = None
    document_id: str | None = None


TxtJsonSuccessResponse = DocJsonSuccessResponse
AudioJsonSuccessResponse = ImgJsonSuccessResponse


class AgentData(ClaixModel):
    """Typed Agent Mode payload. Keys match agent_definition; extra keys are allowed."""

    model_config = ConfigDict(extra="allow")


class AgentExcelJsonSuccessResponse(ExcelJsonSuccessResponse):
    agent_data: dict[str, Any] | AgentData | None = None


class AgentPdfJsonSuccessResponse(PdfJsonSuccessResponse):
    agent_data: dict[str, Any] | AgentData | None = None


class AgentDocJsonSuccessResponse(DocJsonSuccessResponse):
    agent_data: dict[str, Any] | AgentData | None = None


class AgentImgJsonSuccessResponse(ImgJsonSuccessResponse):
    agent_data: dict[str, Any] | AgentData | None = None


class AgentAudioJsonSuccessResponse(AudioJsonSuccessResponse):
    agent_data: dict[str, Any] | AgentData | None = None


class GetDocumentSuccessResponse(ClaixModel):
    success: bool
    document_id: str
    file_name: str
    schema_id: str
    processed_at: datetime | str
    content: str


class DeleteDocumentSuccessResponse(ClaixModel):
    document_id: str


class WindowContextRequest(ClaixModel):
    questions: list[Any] = Field(min_length=1, max_length=5)


class WindowContextSuccessResponse(ClaixModel):
    user_ask: list[Any]
    ia_response: list[Any] = Field(
        description="Answers aligned 1:1 with user_ask. Typed by format, or {value, source} when source verification is on. Native null when missing.",
    )


class CreateSpaceRequest(ClaixModel):
    name: str = Field(min_length=1, max_length=200)


class SpaceRecord(ClaixModel):
    space_id: str
    name: str
    created_at: datetime | str


class CreateSpaceSuccessResponse(ClaixModel):
    success: bool
    space: SpaceRecord


class DeleteSpaceSuccessResponse(ClaixModel):
    space_id: str


class SpaceContextRequest(ClaixModel):
    questions: list[Any] = Field(min_length=1, max_length=5)


class SpaceContextSuccessResponse(ClaixModel):
    user_ask: list[Any]
    ia_response: list[Any] = Field(
        description="Answers aligned 1:1 with user_ask. Typed by format, or {value, source} when source verification is on. Native null when missing.",
    )


class AddSpaceSuccessResponse(ClaixModel):
    success: bool | None = None
    document_id: str | None = None
    space_id: str | None = None
    space_name: str | None = None
    file_name: str | None = None
    version: int | float | None = None
    message: str | None = None


class ReplaceDocumentSuccessResponse(ClaixModel):
    success: bool | None = None
    swap_id: str | None = None
    document_id: str | None = None
    source_document_id: str | None = None
    file_name: str | None = None
    version: int | float | None = None
    swaps_count: int | float | None = None
    message: str | None = None


class RemoveDocumentFromSpaceSuccessResponse(ClaixModel):
    success: bool | None = None
    document_id: str | None = None
    previous_space_id: str | None = None
    espacio_id: str | None = None
    file_name: str | None = None
    version: int | float | None = None
    message: str | None = None


class AgentFieldDefinition(ClaixModel):
    type: AgentFieldType
    description: str
    options: list[str] | None = None


class SchemaFieldDefinition(ClaixModel):
    type: FieldType
    description: str


class SchemaItem(ClaixModel):
    id: str | None = None
    name: str | None = None
    type: SchemaType | str | None = None
    schema_definition: dict[str, Any] | None = None
    is_agent_mode: bool | None = None
    agent_definition: dict[str, AgentFieldDefinition | dict[str, Any]] | None = None
    resumen_agent: str | None = None
    window_context: bool | None = None
    window_time: WindowTime | int | str | None = None
    cita_por_campo: bool | None = None
    created_at: datetime | str | None = None


class SchemasListResponse(ClaixModel):
    success: bool | None = None
    total_schemas: int | None = None
    schemas: list[SchemaItem] | None = None


class CreateSchemaRequest(ClaixModel):
    name: str = Field(max_length=200)
    type: SchemaType
    schema_definition: dict[str, SchemaFieldDefinition | dict[str, Any]]
    is_agent_mode: bool | None = None
    agent_definition: dict[str, AgentFieldDefinition | dict[str, Any]] | None = None
    resumen_agent: str | None = Field(default=None, max_length=500)
    window_context: bool | None = None
    window_time: WindowTime | int | str | None = None
    cita_por_campo: bool | None = None


class CreateSchemaResponse(ClaixModel):
    success: bool | None = None
    schema_: SchemaItem | None = Field(default=None, alias="schema")


class DeleteSchemaRequest(ClaixModel):
    schema_id: str


class DeleteSchemaResponse(ClaixModel):
    success: bool | None = None
    deleted: bool | None = None
    id: str | None = None


class JsonExcelEnvelopeRequest(ClaixModel):
    schema_id: str
    data: list[dict[str, Any]] | None = None
    records: list[dict[str, Any]] | None = None
