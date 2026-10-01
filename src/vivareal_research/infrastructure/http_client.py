"""HTTP transport protocols and implementations for Viva Real research."""

from typing import Any, Protocol, runtime_checkable
import httpx


@runtime_checkable
class HttpClientProtocol(Protocol):
    """Protocol defining network transport contract."""

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """Perform GET request returning decoded JSON payload."""
        ...

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        """Perform GET request returning raw text content."""
        ...


class HttpxHttpClient(HttpClientProtocol):
    """Production HTTP client implementation using HTTPX."""

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        client: httpx.Client | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize HTTP client with configured headers."""
        self._client = client or httpx.Client(
            http2=False,
            timeout=25.0,
            follow_redirects=True,
        )
        self._headers = default_headers or {
            "x-domain": ".vivareal.com.br",
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "application/json, text/plain, text/html, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _merged_headers(self, custom: dict[str, str] | None) -> dict[str, str]:
        """Merge base headers with request-specific headers."""
        if not custom:
            return self._headers
        merged = dict(self._headers)
        merged.update(custom)
        return merged

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """Perform GET request returning JSON dictionary."""
        effective_headers = self._merged_headers(headers)
        response = self._client.get(url, headers=effective_headers)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        """Perform GET request returning decoded string response."""
        effective_headers = self._merged_headers(headers)
        response = self._client.get(url, headers=effective_headers)
        response.raise_for_status()
        return response.text
