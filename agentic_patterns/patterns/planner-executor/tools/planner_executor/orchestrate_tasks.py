# orchestrate_tasks.py
# Tool that executes a Planner-generated task plan by dispatching tasks in dependency order.

import asyncio
from agents import function_tool
from collections import defaultdict
from typing import Set

from core.registries import tool_registry
from schema.planner import TasksPlan
from schema.orchestrator import OrchestratorResponse
from tools.planner_executor.assign_task import assign_task


@function_tool
async def orchestrate_tasks(task_plan: TasksPlan) -> OrchestratorResponse:
    """
    Pass a plan of tasks to an orchastrator for execution and receive the results of all executed tasks.
    """

    print(f"Started orchestrate_tasks tool")
    if task_plan is None:
        raise ValueError("Cannot orchestrate an empty task plan.")

    completed = OrchestratorResponse()
    if len(task_plan.plan) < 1:
        return completed

    print(f"There are {len(task_plan.plan)} tasks in the plan.")
    task_map = {task.id: task for task in task_plan.plan}
    running: Set[str] = set()
    dependents = defaultdict(list)
    dependency_count = {task.id: len(task.inputs) for task in task_plan.plan}

    # Build reverse dependency map
    for task in task_plan.plan:
        for dep in task.inputs:
            dependents[dep].append(task.id)

    # Track tasks ready to run (no unresolved dependencies)
    ready = [task_id for task_id, count in dependency_count.items() if count == 0]

    # Executes a single task once its dependencies are resolved.
    async def run_task(task_id: str):
        print(f"running {task_id}")
        task = task_map[task_id]
        resolved_inputs = {dep: completed.tasks_executed[dep] for dep in task.inputs}
        prompt = (
            f"Task Instructions:\n{task.instructions}\n\n"
            f"Success Criteria:\n{task.success_criteria}\n\n"
            f"Inputs:\n{resolved_inputs if resolved_inputs else 'None'}\n\n"
            f"Notes:\n{task.notes or 'None'}"
        )
        result = await assign_task(prompt)
        completed.tasks_executed[task_id] = result
        print(f"completed {task_id}")

        # Mark dependents as potentially ready
        for dependent in dependents[task_id]:
            dependency_count[dependent] -= 1
            if dependency_count[dependent] == 0:
                ready.append(dependent)

    # Task execution loop
    while ready:
        batch = ready.copy()
        ready.clear()
        tasks = [asyncio.create_task(run_task(task_id)) for task_id in batch]
        for coro in asyncio.as_completed(tasks):
            await coro

    return completed

# Register this tool
tool_registry.register(orchestrate_tasks.name, orchestrate_tasks)