"""Synchronous and asynchronous Claix HTTP clients (OpenAPI 1.8.2)."""

from __future__ import annotations

import os
import random
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import httpx

from claix.exceptions import (
    ClaixAPIError,
    ClaixAuthenticationError,
    ClaixConnectionError,
    ClaixError,
    ClaixNotFoundError,
    ClaixRateLimitError,
    ClaixTimeoutError,
    ClaixValidationError,
)
from claix.resources.context import AsyncContextResource, ContextResource
from claix.resources.extraction import AsyncExtractionResource, ExtractionResource
from claix.resources.schemas import AsyncSchemasResource, SchemasResource
from claix.resources.spaces import AsyncSpacesResource, SpacesResource

DEFAULT_API_BASE_URL = "https://claix.dev/api"
DEFAULT_ORIGIN = "https://claix.dev"
DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_RETRIES = 3
RETRYABLE_STATUS = frozenset({429, 502, 503, 504})
USER_AGENT = "claix-python/1.0.0"


def _origin_from_base(base_url: str) -> str:
    parsed = urlparse(base_url.rstrip("/"))
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else DEFAULT_ORIGIN
    path = parsed.path.rstrip("/")
    if path.endswith("/api"):
        return origin
    return origin if origin else DEFAULT_ORIGIN


def raise_for_status(response: httpx.Response) -> None:
    status = response.status_code
    if status < 400:
        return

    payload: Any
    try:
        payload = response.json()
    except ValueError:
        payload = {"error": response.text}

    error_text = ""
    detalle = ""
    if isinstance(payload, dict):
        error_text = str(payload.get("error") or "")
        detalle = str(payload.get("detalle") or "")
    message = error_text or detalle or f"Claix API error (HTTP {status})"
    if error_text and detalle and detalle not in error_text:
        message = f"{error_text} ({detalle})"

    kwargs: dict[str, Any] = {"status_code": status, "payload": payload}
    if status == 401:
        raise ClaixAuthenticationError(message, **kwargs)
    if status == 404:
        raise ClaixNotFoundError(message, **kwargs)
    if status in {400, 405, 413, 422}:
        raise ClaixValidationError(message, **kwargs)
    if status == 429:
        retry_after: float | None = None
        header = response.headers.get("Retry-After")
        if header:
            try:
                retry_after = float(header)
            except ValueError:
                retry_after = None
        raise ClaixRateLimitError(message, retry_after=retry_after, **kwargs)
    raise ClaixAPIError(message, **kwargs)


def _retry_delay(attempt: int, retry_after: float | None = None) -> float:
    if retry_after is not None:
        return max(0.0, retry_after)
    return min(8.0, (2**attempt) + random.random())


class ClaixClient:
    """Synchronous Claix client.

    Auth: ``api_key`` argument or ``CLAIX_API_KEY`` environment variable.
    Header: ``x-api-key``.
    Default base: ``https://claix.dev/api``.
    Context and space endpoints use the site origin ``https://claix.dev``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_API_BASE_URL,
        origin: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        key = api_key or os.environ.get("CLAIX_API_KEY")
        if not key:
            raise ClaixAuthenticationError(
                "Missing Claix API key. Pass api_key=... or set CLAIX_API_KEY."
            )
        self.api_key = key
        self.base_url = base_url.rstrip("/")
        self.origin = (origin or _origin_from_base(self.base_url)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._owns_client = http_client is None
        self._http = http_client or httpx.Client(
            timeout=httpx.Timeout(timeout, connect=15.0),
            headers=self._default_headers(),
            follow_redirects=True,
        )
        self.extract = ExtractionResource(self)
        self.context = ContextResource(self)
        self.spaces = SpacesResource(self)
        self.schemas = SchemasResource(self)

    def _default_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> ClaixClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        json: Any = None,
        data: Mapping[str, str] | None = None,
        files: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        expect_json: bool = True,
    ) -> Any:
        last_error: ClaixError | None = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                response = self._http.request(
                    method,
                    url,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                    headers=dict(headers) if headers else None,
                )
            except httpx.TimeoutException as exc:
                last_error = ClaixTimeoutError(f"Request timed out after {self.timeout}s: {exc}")
                if attempt >= attempts - 1:
                    raise last_error from exc
                time.sleep(_retry_delay(attempt))
                continue
            except httpx.TransportError as exc:
                last_error = ClaixConnectionError(f"Connection error: {exc}")
                if attempt >= attempts - 1:
                    raise last_error from exc
                time.sleep(_retry_delay(attempt))
                continue

            if response.status_code in RETRYABLE_STATUS and attempt < attempts - 1:
                retry_after: float | None = None
                header = response.headers.get("Retry-After")
                if header:
                    try:
                        retry_after = float(header)
                    except ValueError:
                        retry_after = None
                time.sleep(_retry_delay(attempt, retry_after))
                continue

            raise_for_status(response)
            if not expect_json:
                return response.content
            if not response.content:
                return {}
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                return response.content
            return response.json()
        if last_error:
            raise last_error
        raise ClaixAPIError("Request failed after retries")

    def request_json(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(method, url, expect_json=True, **kwargs)


class AsyncClaixClient:
    """Asynchronous Claix client with the same resource surface as :class:`ClaixClient`."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_API_BASE_URL,
        origin: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        key = api_key or os.environ.get("CLAIX_API_KEY")
        if not key:
            raise ClaixAuthenticationError(
                "Missing Claix API key. Pass api_key=... or set CLAIX_API_KEY."
            )
        self.api_key = key
        self.base_url = base_url.rstrip("/")
        self.origin = (origin or _origin_from_base(self.base_url)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=15.0),
            headers={
                "x-api-key": self.api_key,
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )
        self.extract = AsyncExtractionResource(self)
        self.context = AsyncContextResource(self)
        self.spaces = AsyncSpacesResource(self)
        self.schemas = AsyncSchemasResource(self)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncClaixClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: Any = None,
        data: Mapping[str, str] | None = None,
        files: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        expect_json: bool = True,
    ) -> Any:
        import asyncio

        last_error: ClaixError | None = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                response = await self._http.request(
                    method,
                    url,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                    headers=dict(headers) if headers else None,
                )
            except httpx.TimeoutException as exc:
                last_error = ClaixTimeoutError(f"Request timed out after {self.timeout}s: {exc}")
                if attempt >= attempts - 1:
                    raise last_error from exc
                await asyncio.sleep(_retry_delay(attempt))
                continue
            except httpx.TransportError as exc:
                last_error = ClaixConnectionError(f"Connection error: {exc}")
                if attempt >= attempts - 1:
                    raise last_error from exc
                await asyncio.sleep(_retry_delay(attempt))
                continue

            if response.status_code in RETRYABLE_STATUS and attempt < attempts - 1:
                retry_after: float | None = None
                header = response.headers.get("Retry-After")
                if header:
                    try:
                        retry_after = float(header)
                    except ValueError:
                        retry_after = None
                await asyncio.sleep(_retry_delay(attempt, retry_after))
                continue

            raise_for_status(response)
            if not expect_json:
                return response.content
            if not response.content:
                return {}
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                return response.content
            return response.json()
        if last_error:
            raise last_error
        raise ClaixAPIError("Request failed after retries")

    async def request_json(self, method: str, url: str, **kwargs: Any) -> Any:
        return await self.request(method, url, expect_json=True, **kwargs)
