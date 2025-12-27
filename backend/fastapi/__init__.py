from __future__ import annotations

import inspect
import re
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: Any = None) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _Route:
    def __init__(self, method: str, path: str, handler: Callable[..., Any]) -> None:
        self.method = method
        self.path = path
        self.handler = handler
        self.template = self._compile_template(path)

    def _compile_template(self, path: str) -> re.Pattern[str]:
        pattern = re.sub(r"{[^/]+}", r"([^/]+)", path.rstrip("/"))
        return re.compile(f"^{pattern}$")

    def match(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        if method != self.method:
            return None
        match = self.template.match(path.rstrip("/"))
        if not match:
            return None
        param_names = re.findall(r"{([^/]+)}", self.path)
        return dict(zip(param_names, match.groups()))


class FastAPI:
    def __init__(self, title: str, version: str) -> None:
        self.title = title
        self.version = version
        self.routes: List[_Route] = []

    def _register(self, method: str, path: str, func: Callable[..., Any]):
        self.routes.append(_Route(method, path, func))
        return func

    def get(self, path: str, response_model: Any | None = None):
        def decorator(func: Callable[..., Any]):
            return self._register("GET", path, func)

        return decorator

    def post(self, path: str, response_model: Any | None = None):
        def decorator(func: Callable[..., Any]):
            return self._register("POST", path, func)

        return decorator

    def patch(self, path: str, response_model: Any | None = None):
        def decorator(func: Callable[..., Any]):
            return self._register("PATCH", path, func)

        return decorator

    def _handle_request(self, method: str, path: str, params: Dict[str, Any], json: Any):
        path = path.rstrip("/") or "/"
        for route in self.routes:
            match = route.match(method, path)
            if match is None:
                continue
            try:
                kwargs: Dict[str, Any] = {}
                sig = inspect.signature(route.handler)
                for name, param in sig.parameters.items():
                    if name in match:
                        kwargs[name] = _convert_type(match[name], param.annotation)
                        continue
                    if name in params:
                        kwargs[name] = _convert_type(params[name], param.annotation)
                    elif json is not None:
                        ann = param.annotation
                        if inspect.isclass(ann) and issubclass(ann, BaseModel):
                            kwargs[name] = ann(**json)
                        else:
                            kwargs[name] = json.get(name)
                result = route.handler(**kwargs)
                return 200, result
            except HTTPException as exc:  # pragma: no cover - simple passthrough
                return exc.status_code, {"detail": exc.detail}
        return 404, {"detail": "Not Found"}


class Response:
    def __init__(self, status_code: int, data: Any) -> None:
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        return _to_jsonable(self._data)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _to_jsonable(value.model_dump())
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    return value


def _convert_type(value: Any, annotation: Any) -> Any:
    try:
        if annotation is int:
            return int(value)
        if annotation is float:
            return float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return value
    return value


__all__ = ["FastAPI", "HTTPException", "Response"]
