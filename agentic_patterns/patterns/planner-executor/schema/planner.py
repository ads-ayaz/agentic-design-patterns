# planner.py
# Define structured output types for Planner

from pydantic import BaseModel, Field
from typing import Optional

from core.registries import output_type_registry


class PlannerTask(BaseModel):
    """Represents a single atomic task produced by the Planner."""

    id: str = Field(..., pattern=r'^task-\d{3}$', description="Unique, sequential task ID (e.g., task-001, task-002)")
    instructions: str = Field(..., description="Specific instruction to be passed to an Executor.")
    success_criteria: str = Field(..., description="An objective condition or check that defines what it means for this task to be successfully completed.")
    inputs: list[str] = Field(default_factory=list, description="List any task dependencies (task IDs) or required outputs from other tasks.")
    notes: Optional[str] = Field(None, description="Optional field for hints, assumptions, or constraints.")

class TasksPlan(BaseModel):
    """Represents the Planner’s full response containing the goal and task list."""

    goal: str = Field(..., description="Your interpretation of the original objective.")
    plan: list[PlannerTask] = Field(
        default_factory=list, 
        description="Set of tasks that collectively fulfill the objective."
    )

output_type_registry.register(PlannerTask.__name__, PlannerTask)
output_type_registry.register(TasksPlan.__name__, TasksPlan)
