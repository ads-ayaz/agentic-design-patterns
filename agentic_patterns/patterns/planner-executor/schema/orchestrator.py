# orchestrator.py
# Define structured output types for Orchestrator

from pydantic import BaseModel, Field
from typing import Dict, Optional

from core.registries import output_type_registry

class TaskOutput(BaseModel):
    """Represents the result of executing a single task in the plan."""

    id: str = Field(..., description='Task ID of executed task.')
    output: str = Field(None, description='Output result from executing the task.')
    errors: Optional[str] = Field(None, description='Description of errors encountered (if any) while executing the task.')

class OrchestratorResponse(BaseModel):
    """Represents the full output of the orchestrator after executing a task plan."""
    
    tasks_executed: Dict[str,TaskOutput] = Field(
        default_factory=dict, 
        description="Outputs from all executed tasks, keyed by task ID."
    )

output_type_registry.register(TaskOutput.__name__, TaskOutput)
output_type_registry.register(OrchestratorResponse.__name__, OrchestratorResponse)
