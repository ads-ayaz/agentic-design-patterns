# pattern.py
# Coordinates execution of the Planner–Executor pattern from a single interface.

import asyncio
import json
from agents import Runner, trace
from collections import defaultdict
from typing import Set

from core.agent_factory import AgentFactory
from schema.executor import ExecutorResponse
from schema.orchestrator import OrchestratorResponse, TaskOutput
from schema.planner import TasksPlan


class PlannerExecutorPattern:
    """
    Coordinates the end-to-end execution of a Planner-Executor agentic workflow.
    Given a user query, it invokes the Planner to produce a plan and the Executor to carry it out.
    """

    @staticmethod
    async def run(query: str) -> ExecutorResponse:
        """
        Executes the Planner-Executor pattern for the given query.

        Args:
            query (str): A user goal or instruction to be handled by the agentic system.

        Returns:
            ExecutorResponse: The final synthesized result from executing the Planner's task plan.

        Raises:
            ValueError: If the Planner or Executor fails to return a valid response.
        """

        planner = AgentFactory.get_agent("planner")
        # executor = AgentFactory.get_agent("executor")
        consolidator = AgentFactory.get_agent("consolidator")

        # Step 1: Use Planner to generate a plan
        with trace(planner.name):
            planner_result = await Runner.run(planner, f"User Goal: {query}")

        if planner_result is None or not planner_result.final_output:
            raise ValueError("Planner agent failed to produce a valid plan.")

        plan = planner_result.final_output_as(TasksPlan)

        # Step 2: Execute the plan and consolidate the results
        with trace(consolidator.name):
            ochestrator_result = await PlannerExecutorPattern._orchestrate_tasks(plan)

            consolidation_dict = {'tasks_plan': plan.model_dump(), 'tasks_output': ochestrator_result.model_dump()}
            consolidation_str = json.dumps(consolidation_dict)

            consolidator_result = await Runner.run(consolidator, consolidation_str)

        if consolidator_result and consolidator_result.final_output:
            return consolidator_result.final_output_as(ExecutorResponse)
        else:
            raise ValueError("The Consolidator did not return a valid response.")
        
    @staticmethod
    async def _orchestrate_tasks(task_plan: TasksPlan) -> OrchestratorResponse:
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
            result = await PlannerExecutorPattern._assign_task(prompt)
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
    
    @staticmethod
    async def _assign_task(task: str, enable_trace: bool = False) -> TaskOutput:
        """
        Assigns a single task (in serialized string form) to the Worker agent for execution.

        Args:
            task (str): Serialized task prompt including instructions, inputs, and criteria.
            enable_trace (bool): If True, wraps execution in a trace context for observability.

        Returns:
            TaskOutput: Structured result of the task execution.
        """

        # Retrieve or instantiate the Worker agent
        worker = AgentFactory.get_agent('worker', from_cache=False)

        # When calling this function standalone, set enable_trace to True
        if enable_trace:
            with trace(worker.name):
                result = await Runner.run(worker, task)
        else:
            result = await Runner.run(worker, task)
        
        return result.final_output_as(TaskOutput)
        