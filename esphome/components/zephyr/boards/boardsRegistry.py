from collections import UserDict
from typing import Type

from .baseBoardValidator import BaseZephyrBoard

__all__ = ("registry", )


class _BoardsRegistry(UserDict):
    def register(self, name: str):
        def wrapped_registrer(validator: Type[BaseZephyrBoard]):
            if name in self:
                raise KeyError(f"Board {name} is already registered")
            self[name] = validator
        return wrapped_registrer


registry = _BoardsRegistry()
