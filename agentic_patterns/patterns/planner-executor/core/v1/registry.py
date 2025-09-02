# core/v1/registry.py
# Defines reusable registry class for tools, output types, and other named entities.

from __future__ import annotations
from typing import Any, Dict


class Registry:
    """A simple, reusable named-item registry with static access to named registries."""

    _named_registries: Dict[str, Registry] = {}

    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Any] = {}
        Registry._named_registries[name] = self

    def register(self, key: str, item: Any):
        if key in self._registry:
            raise ValueError(f"{self.name} registry already contains an item with key: '{key}'")
        self._registry[key] = item

    def get(self, key: str) -> Any:
        if key not in self._registry:
            raise KeyError(f"{self.name} registry has no entry for key: '{key}'")
        return self._registry[key]

    def all(self) -> Dict[str, Any]:
        return dict(self._registry)

    def __contains__(self, key: str) -> bool:
        return key in self._registry

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __repr__(self):
        return f"<Registry '{self.name}' with {len(self._registry)} items>"

    @staticmethod
    def create(name: str) -> Registry:
        if name in Registry._named_registries:
            raise ValueError(f"A registry with name '{name}' already exists.")
        return Registry(name)

    @staticmethod
    def get_named(name: str) -> Registry:
        if name not in Registry._named_registries:
            raise KeyError(f"No registry found with name '{name}'")
        return Registry._named_registries[name]

    @staticmethod
    def all_named() -> Dict[str, Registry]:
        return dict(Registry._named_registries)

