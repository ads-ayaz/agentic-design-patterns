# registries.py
# Instantiate shared registries

from core.registry import Registry

tool_registry = Registry.create("Tool")
output_type_registry = Registry.create("OutputType")
