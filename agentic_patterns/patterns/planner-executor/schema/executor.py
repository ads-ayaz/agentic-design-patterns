# executor.py
# Define the structured output for the Executor

from pydantic import BaseModel, Field
from typing import Literal, Optional

from core.registries import output_type_registry


class ExecutorResponse(BaseModel):
    """Represents the Executor’s final response after completing a task plan."""
    
    status: Literal["success", "partial", "failed"]
    final_output: str = Field(
        None, 
        description="The best response to the Planner's goal synthesized from the task results."
    )
    reasoning: Optional[str] = Field(
        None, 
        description="Explanation in case you return a 'partial' or 'failed' status."
    )

output_type_registry.register(ExecutorResponse.__name__, ExecutorResponse)