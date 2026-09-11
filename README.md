# Claix Python SDK

[![PyPI](https://img.shields.io/pypi/v/claix-ai.svg)](https://pypi.org/project/claix-ai/)
[![Python](https://img.shields.io/pypi/pyversions/claix-ai.svg)](https://pypi.org/project/claix-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official typed Python client for the [Claix](https://www.claix.dev) document intelligence API (**OpenAPI 1.8.2**).

Extract PDFs, Excel, Word, images, and text into schema-validated JSON. Query persisted documents and knowledge spaces. Drop the same client into **LangChain / LangGraph**, **CrewAI**, and **LlamaIndex**.

- Docs: https://www.claix.dev/documentation
- OpenAPI: https://www.claix.dev/openapi.yaml
- Agent Card: https://claix.dev/.well-known/agent.json

## Install

```bash
pip install claix-ai
pip install 'claix-ai[langchain]'
pip install 'claix-ai[crewai]'
pip install 'claix-ai[llamaindex]'
pip install 'claix-ai[all]'
```

Requires **Python ≥ 3.10**. Set `CLAIX_API_KEY` or pass `api_key=` to the client.

## Quickstart

```python
from claix import ClaixClient

client = ClaixClient()  # reads CLAIX_API_KEY
result = client.extract.pdf("invoice.pdf", schema_id="3c7a9f21-4b8e-4d1a-9c6f-2e0d8a5b7c4f")
print(result.data)
```

Async:

```python
from claix import AsyncClaixClient

async with AsyncClaixClient() as client:
    doc = await client.extract.pdf("invoice.pdf", schema_id="...")
    answers = await client.context.ask(doc.document_id, ["What is the total?"])
```

## Extraction, context, and spaces

```python
from claix import ClaixClient

client = ClaixClient(api_key="ck_...")

# Standard extraction → POST https://claix.dev/api/pdf-json
extracted = client.extract.pdf("scan.pdf", schema_id="...", space_id=None, is_agent_mode=False)

# Agent Mode → POST https://claix.dev/agent/pdf-json
agented = client.extract.pdf("contract.pdf", schema_id="...", is_agent_mode=True)
print(agented.agent_data)

space = client.spaces.create("Vendors 2026")
client.extract.excel("ledger.xlsx", schema_id="...", space_id=space.space.space_id)

# Cross-document Q&A — ia_response is list[str | None] (native null when missing)
qa = client.spaces.ask(space.space.space_id, ["Which vendor billed the most?"])
print(qa.user_ask, qa.ia_response)
```

## LangGraph (ReAct)

```python
from claix import ClaixClient
from claix.integrations.langchain import (
    ClaixDocumentContextTool,
    ClaixExtractTool,
    ClaixSpaceContextTool,
)
from langgraph.prebuilt import create_react_agent

client = ClaixClient()
tools = [
    ClaixExtractTool(client=client),
    ClaixDocumentContextTool(client=client),
    ClaixSpaceContextTool(client=client),
]
agent = create_react_agent("openai:gpt-4.1", tools)
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Extract invoice.pdf with schema 3c7a9f21-4b8e-4d1a-9c6f-2e0d8a5b7c4f, "
                   "then ask the document_id for the VAT total.",
    }]
})
```

`create_react_agent` builds a StateGraph that loops until the model stops calling tools. `ClaixSpaceContextTool` is the right primitive for multi-file nodes (compare, sum, reconcile under a `space_id`).

## CrewAI

```python
from crewai import Agent, Crew, Task
from claix import ClaixClient
from claix.integrations.crewai import ClaixDocumentTool, ClaixKnowledgeSpaceTool

client = ClaixClient()
analyst = Agent(
    role="Document auditor",
    goal="Extract contracts and reconcile them against invoices",
    backstory="You never guess missing fields; you trust Claix nulls.",
    tools=[ClaixDocumentTool(client=client), ClaixKnowledgeSpaceTool(client=client)],
)
task = Task(
    description="Extract contracts/ and invoices/ into space {space_id}, then list discrepancies.",
    expected_output="A JSON list of mismatches. Use null when a field is absent.",
    agent=analyst,
)
Crew(agents=[analyst], tasks=[task]).kickoff()
```

## LlamaIndex

```python
from claix import ClaixClient
from claix.integrations.llamaindex import ClaixToolSpec

spec = ClaixToolSpec(client=ClaixClient())
tools = spec.to_tool_list()  # extract_document, ask_document, ask_knowledge_space
```

## SDK map (OpenAPI 1.8.2)

| SDK method | HTTP |
| --- | --- |
| `client.extract.pdf(file, schema_id, space_id=None, is_agent_mode=False)` | `POST /api/pdf-json` or `POST /agent/pdf-json` |
| `client.extract.excel(...)` | `POST /api/excel-json` or `POST /agent/excel-json` |
| `client.extract.document(...)` | `POST /api/doc-json` or `POST /agent/doc-json` |
| `client.extract.image(...)` | `POST /api/img-json` or `POST /agent/img-json` |
| `client.extract.text(content, schema_id, ...)` | `POST /api/txt-json` or `POST /agent/txt-json` |
| `client.extract.json_to_excel(schema_id=..., data=...)` | `POST /api/json-excel` (binary `.xlsx`) |
| `client.context.get(document_id)` | `GET https://claix.dev/get-document/{document_id}` |
| `client.context.ask(document_id, questions)` | `POST https://claix.dev/document-context/{document_id}` (max 5 × 400 chars) |
| `client.context.delete(document_id)` | `DELETE https://claix.dev/delete-document/{document_id}` |
| `client.spaces.create(name)` | `POST https://claix.dev/create-space` |
| `client.spaces.ask(space_id, questions)` | `POST https://claix.dev/space-context/{space_id}` |
| `client.spaces.delete(space_id)` | `DELETE https://claix.dev/delete-space/{space_id}` |
| `client.schemas.list()` | `GET /api/schemas` |
| `client.schemas.create(name, type, schema_definition, ...)` | `POST /api/create-schema` |
| `client.schemas.delete(schema_id)` | `POST /api/delete-schema` |

Auth header: `x-api-key` (Bearer is also accepted by the API). Default timeout 120s, with retries on 429/502/503/504 and transport errors.

`WindowContextSuccessResponse.ia_response` and `SpaceContextSuccessResponse.ia_response` are typed as `list[str | None]` so orchestrators can branch on deterministic `null`.

## Errors

`ClaixAuthenticationError` (401), `ClaixNotFoundError` (404), `ClaixValidationError` (400/413/422), `ClaixRateLimitError` (429), `ClaixTimeoutError`, `ClaixConnectionError`, `ClaixAPIError` (5xx). All subclass `ClaixError` and expose `status_code` plus the `{error, detalle}` payload.

## License

MIT
