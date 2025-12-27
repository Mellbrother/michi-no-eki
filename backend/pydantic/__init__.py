from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class BaseModel:
    def __init__(self, **data: Any) -> None:
        for field in self.__annotations__:
            if field in data:
                value = data[field]
            elif hasattr(self.__class__, field):
                value = deepcopy(getattr(self.__class__, field))
            else:
                value = None
            setattr(self, field, value)

    def model_dump(self, *, exclude_none: bool = False, exclude_unset: bool = False) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        for field in self.__annotations__:
            value = getattr(self, field)
            if exclude_none and value is None:
                continue
            values[field] = value
        return values

    def model_copy(self, *, update: Dict[str, Any] | None = None) -> "BaseModel":
        data = self.model_dump()
        if update:
            data.update(update)
        return self.__class__(**data)

    def __iter__(self):
        for field in self.__annotations__:
            yield (field, getattr(self, field))

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        fields = ", ".join(f"{k}={v!r}" for k, v in self.model_dump().items())
        return f"{self.__class__.__name__}({fields})"
