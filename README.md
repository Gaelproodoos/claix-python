# Claix Python SDK

[![PyPI](https://img.shields.io/pypi/v/claix-ai.svg)](https://pypi.org/project/claix-ai/)
[![Python](https://img.shields.io/pypi/pyversions/claix-ai.svg)](https://pypi.org/project/claix-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official Python client for [Claix](https://www.claix.dev), the security layer between your SQL database and AI agents.

Claix connects to your database and lets each agent retrieve only the tables and columns you allow, and run only the changes your rules allow. Your data stays where it is. You pay per use, over REST, MCP, or A2A.

| | |
| --- | --- |
| **Claix Retrieve** | Controlled reads from the live database. The agent asks in plain language and gets raw rows or typed answers. PostgreSQL, MySQL, and MariaDB. `client.retrieve.ask` → `POST /retrieve/{agent_name}` |
| **Claix Guard** | Checks every `INSERT`, `UPDATE`, and `DELETE` an agent proposes. Returns allow or deny, with the reason. Claix does not run the statement. `client.guard.check` → `POST /check-sql` |
| **Claix Ingest** | Turns PDFs, Excel, Word, images, audio, and text into schema-validated JSON, and keeps document context and knowledge spaces. |

Retrieve and Guard are the primary calls. Ingest remains on the same client, with tools for **LangChain / LangGraph**, **CrewAI**, and **LlamaIndex**.

- Site: https://www.claix.dev
- Retrieve: https://www.claix.dev/documentation/call-an-agent
- Guard: https://www.claix.dev/documentation/check-sql
- Ingest docs: https://www.claix.dev/documentation
- TypeScript SDK: https://github.com/Gaelproodoos/claix-typescript
- OpenAPI: https://www.claix.dev/openapi.yaml

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

answers = client.retrieve.ask(
    "orders-agent",
    [
        {"question": "How many orders are confirmed?", "format": "int"},
        "What is the name of the customer with the most orders?",
    ],
)
print(answers.ia_response, answers.log_id)

decision = client.guard.check(
    "UPDATE orders SET discount = $1 WHERE id = $2",
    params=[0.35, 90421],
)
if decision.allowed:
    print(decision.decision_id)  # your code runs the statement
else:
    print(decision.code, decision.reason)  # Claix did not run it
```

Ingest:

```python
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
    # also: ClaixAddToSpaceTool, ClaixRemoveFromSpaceTool, ClaixReplaceDocumentTool
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
tools = spec.to_tool_list()  # extract, ask, add/remove space, replace document
```

## SDK map

| SDK method | HTTP |
| --- | --- |
| `client.retrieve.ask(agent_name, questions)` | `POST /retrieve/{agent_name}` |
| `client.guard.check(sql, params=None, connection_id=None)` | `POST /check-sql` |
| `client.extract.pdf(file, schema_id, space_id=None, is_agent_mode=False)` | `POST /api/pdf-json` or `POST /agent/pdf-json` |
| `client.extract.excel(...)` | `POST /api/excel-json` or `POST /agent/excel-json` |
| `client.extract.document(...)` | `POST /api/doc-json` or `POST /agent/doc-json` |
| `client.extract.image(...)` | `POST /api/img-json` or `POST /agent/img-json` |
| `client.extract.text(content, schema_id, ...)` | `POST /api/txt-json` or `POST /agent/txt-json` |
| `client.extract.audio(...)` | `POST /api/audio-json` or `POST /agent/audio-json` |
| `client.extract.json_to_excel(schema_id=..., data=...)` | `POST /api/json-excel` (binary `.xlsx`) |
| `client.context.get(document_id)` | `GET https://claix.dev/get-document/{document_id}` |
| `client.context.ask(document_id, questions)` | `POST https://claix.dev/document-context/{document_id}` (max 5 × 400 chars, `{question, format}`) |
| `client.context.delete(document_id)` | `DELETE https://claix.dev/delete-document/{document_id}` |
| `client.context.replace(document_id, new_content_document_id)` | `POST https://claix.dev/replace-document` |
| `client.spaces.create(name)` | `POST https://claix.dev/create-space` |
| `client.spaces.add(document_id, space_id)` | `POST https://claix.dev/add-space` |
| `client.spaces.ask(space_id, questions)` | `POST https://claix.dev/space-context/{space_id}` |
| `client.spaces.remove_document(document_id)` | `DELETE https://claix.dev/remove-document-from-space/{document_id}` |
| `client.spaces.delete(space_id)` | `DELETE https://claix.dev/delete-space/{space_id}` |
| `client.schemas.list()` | `GET /api/schemas` |
| `client.schemas.get(schema_id)` | `GET /api/get-schema/{schema_id}` |
| `client.schemas.create(name, type, schema_definition, ...)` | `POST /api/create-schema` |
| `client.schemas.update(schema_id, name, type, schema_definition, ...)` | `PUT /api/update-schema/{schema_id}` |
| `client.schemas.delete(schema_id)` | `POST /api/delete-schema` |

Retrieve questions accept a string (sent as `format: "string"`) or `{"question", "format"}` with `string`, `int`, `boolean`, `timestamp`, `timestamptz`, `date`, `json`, `array:string`, or `array:int`. Up to 5 questions, 400 characters each. In raw mode `format` is ignored and each answer is `{rows, truncated}`.

Guard reads `allowed`. A denial is still HTTP 200. `connection_id` is required only when the account has more than one active connection. PostgreSQL placeholders are `$1`, `$2`. MySQL and MariaDB use `?`.

Document and space questions accept a string or `{"question", "format"}` with `string`, `int`, `boolean`, `timestamp`, or `array`.

Auth header: `x-api-key` (Bearer is also accepted by the API). Default timeout 120s, with retries on 429/502/503/504 and transport errors.

`WindowContextSuccessResponse.ia_response` and `SpaceContextSuccessResponse.ia_response` are typed as `list[str | None]` so orchestrators can branch on deterministic `null`.

## Errors

`ClaixAuthenticationError` (401), `ClaixNotFoundError` (404), `ClaixValidationError` (400/413/422), `ClaixRateLimitError` (429), `ClaixTimeoutError`, `ClaixConnectionError`, `ClaixAPIError` (5xx). All subclass `ClaixError` and expose `status_code` plus the `{error, detalle}` payload.

## License

MIT
