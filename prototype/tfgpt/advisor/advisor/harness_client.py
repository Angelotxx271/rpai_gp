"""The advisor's calls to the harness. Every model call goes through the harness, never straight to a vendor."""
from collections.abc import Iterator

import httpx

from tfgpt_shared import sse
from tfgpt_shared.internal import HEADER, ServiceError, call, error_of, internal_token


class Harness:
    def __init__(self, client: httpx.Client):
        self.c = client

    def generate(self, **body) -> dict:
        return call(self.c, "POST", "/v1/generate", json=body, timeout=900)

    def stream(self, **body) -> Iterator[tuple[str, dict]]:
        """Yields (event, data) from the harness. Raises ServiceError before the first event if it refuses."""
        try:
            with self.c.stream("POST", "/v1/stream", json=body, headers={HEADER: internal_token()},
                               timeout=httpx.Timeout(900, connect=10)) as r:
                if r.status_code >= 400:
                    r.read()
                    raise error_of(r)
                yield from sse.parse(r.iter_lines())
        except httpx.HTTPError as ex:
            raise ServiceError(502, "upstream", f"Harness unreachable: {type(ex).__name__}") from ex

    def engines(self, student_ref: str | None = None) -> dict:
        return call(self.c, "GET", "/v1/engines", params={"student_ref": student_ref} if student_ref else None)
