# assign_task.py
# Executes a single atomic task by routing it to the Worker agent

from agents import Runner, trace

from core.agent_factory import AgentFactory
from schema.orchestrator import TaskOutput

async def assign_task(task: str, enable_trace: bool = False) -> TaskOutput:
    """
    Assigns a single task (in serialized string form) to the Worker agent for execution.

    Args:
        task (str): Serialized task prompt including instructions, inputs, and criteria.
        enable_trace (bool): If True, wraps execution in a trace context for observability.

    Returns:
        TaskOutput: Structured result of the task execution.
    """

    # Retrieve or instantiate the Worker agent
    worker = AgentFactory.get_agent('worker')

    # When calling this function standalone, set enable_trace to True
    if enable_trace:
        with trace(worker.name):
            result = await Runner.run(worker, task)
    else:
        result = await Runner.run(worker, task)
    
    return result.final_output_as(TaskOutput)
