"""Calls between services on Railway's private network, guarded by one shared token."""
import hmac

import httpx
from fastapi import Header, HTTPException

from .settings import env

HEADER = "X-Internal-Token"


def internal_token() -> str:
    token = env("INTERNAL_TOKEN")
    if not token:
        raise RuntimeError("INTERNAL_TOKEN is not set")
    return token


def require_internal(x_internal_token: str | None = Header(default=None)) -> None:
    """FastAPI dependency: refuse any internal call without the shared token."""
    expected = env("INTERNAL_TOKEN")
    if not expected or not x_internal_token or not hmac.compare_digest(x_internal_token, expected):
        raise HTTPException(status_code=401, detail={"error": "unauthorised", "message": "Internal call refused."})


class ServiceError(Exception):
    """A non-2xx answer from another service, carrying its error code and message."""

    def __init__(self, status: int, error: str, message: str):
        super().__init__(f"{status} {error}: {message}")
        self.status, self.error, self.message = status, error, message


def error_of(r: httpx.Response) -> ServiceError:
    try:
        body = r.json()
        detail = body.get("detail", body) if isinstance(body, dict) else {}
        if isinstance(detail, dict):
            return ServiceError(r.status_code, detail.get("error", "upstream"), detail.get("message", r.text[:200]))
    except ValueError:
        pass
    return ServiceError(r.status_code, "upstream", r.text[:200] or "The service did not answer.")


def client(base_url: str, timeout: float = 30.0) -> httpx.Client:
    """An httpx client for another service. Tests pass a TestClient instead."""
    return httpx.Client(base_url=base_url, timeout=timeout, headers={HEADER: internal_token()})


def call(c: httpx.Client, method: str, path: str, **kw) -> dict:
    kw.setdefault("headers", {})[HEADER] = internal_token()
    try:
        r = c.request(method, path, **kw)
    except httpx.HTTPError as ex:
        raise ServiceError(502, "upstream", f"Service unreachable: {type(ex).__name__}") from ex
    if r.status_code >= 400:
        raise error_of(r)
    return r.json()
