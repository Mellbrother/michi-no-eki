from __future__ import annotations

from typing import Any, Dict

from . import FastAPI, Response


class TestClient:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def get(self, path: str, params: Dict[str, Any] | None = None) -> Response:
        return self.request("GET", path, params=params)

    def post(self, path: str, params: Dict[str, Any] | None = None, json: Any | None = None) -> Response:
        return self.request("POST", path, params=params, json=json)

    def patch(self, path: str, params: Dict[str, Any] | None = None, json: Any | None = None) -> Response:
        return self.request("PATCH", path, params=params, json=json)

    def request(self, method: str, path: str, params: Dict[str, Any] | None = None, json: Any | None = None) -> Response:
        params = params or {}
        status, data = self.app._handle_request(method.upper(), path, params=params, json=json)
        return Response(status, data)
