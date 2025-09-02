# core/v1/registries.py
# Instantiate shared registries

from .v1.registry import Registry

tool_registry = Registry.create("Tool")
output_type_registry = Registry.create("OutputType")
