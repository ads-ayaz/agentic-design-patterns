# pattern.py
# Coordinates execution of the Planner–Executor pattern from a single interface.

import asyncio
import json
from agents import Runner, trace
from agents.exceptions import MaxTurnsExceeded
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
    async def run(query: str, progress_report: asyncio.Queue = None) -> ExecutorResponse:
        """
        Executes the Planner-Executor pattern for the given query.

        Args:
            query (str): A user goal or instruction to be handled by the agentic system.
            progress_report (asyncio.Queue): Optional queue for consumer to monitor run progress.

        Returns:
            ExecutorResponse: The final synthesized result from executing the Planner's task plan.

        Raises:
            ValueError: If the Planner or Executor fails to return a valid response.
        """

        # Initialize pq with a throwaway queue if none was provided or use progress_report
        pq = asyncio.Queue() if progress_report is None else progress_report

        planner = AgentFactory.get_agent("planner")
        consolidator = AgentFactory.get_agent("consolidator")

        # Step 1: Use Planner to generate a plan
        with trace(planner.name):
            await pq.put(f"Running {planner.name}...\n")
            planner_result = await Runner.run(planner, f"User Goal: {query}")

        if planner_result is None or not planner_result.final_output:
            await pq.put(f" - {planner.name}: failed to produce a plan\n")
            raise ValueError("Planner agent failed to produce a valid plan.")

        plan = planner_result.final_output_as(TasksPlan)
        await pq.put(f" - {planner.name}: returned a TasksPlan\n```json\n{plan.model_dump_json(indent=2)}\n```\n")

        # Step 2: Execute the plan and consolidate the results
        with trace(consolidator.name):
            await pq.put(f"Orchastrating tasks...\n")
            ochestrator_result = await PlannerExecutorPattern._orchestrate_tasks(plan, progress_report=pq)

            await pq.put(f" - orchastration of tasks plan complete\n")
            consolidation_dict = {'tasks_plan': plan.model_dump(), 'tasks_output': ochestrator_result.model_dump()}
            consolidation_str = json.dumps(consolidation_dict)

            await pq.put(f"Running {consolidator.name}...\n")
            consolidator_result = await Runner.run(consolidator, consolidation_str)

        if consolidator_result and consolidator_result.final_output:
            await pq.put(f"- {consolidator.name} returned a valid response\n")
            return consolidator_result.final_output_as(ExecutorResponse)
        else:
            await pq.put(f"- {consolidator.name} failed to returned successfully\n")
            raise ValueError("The Consolidator did not return a valid response.\n")
        
    @staticmethod
    async def _orchestrate_tasks(task_plan: TasksPlan, progress_report: asyncio.Queue = None) -> OrchestratorResponse:
        """
        Pass a plan of tasks to an orchastrator for execution and receive the results of all executed tasks.
        """

        # Initialize pq with a throwaway queue if none was provided or use progress_report
        pq = asyncio.Queue() if progress_report is None else progress_report

        print(f"Started orchestrate_tasks tool")
        if task_plan is None:
            raise ValueError("Cannot orchestrate an empty task plan.")

        completed = OrchestratorResponse()
        if len(task_plan.plan) < 1:
            return completed

        await pq.put(f"There are {len(task_plan.plan)} tasks in the plan.\n")
        task_map = {task.id: task for task in task_plan.plan}
        # running: Set[str] = set()
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
            await pq.put(f"- running {task_id}\n")
            task = task_map[task_id]
            resolved_inputs = {dep: completed.tasks_executed[dep] for dep in task.inputs}
            prompt = (
                f"Task ID: {task_id}\n\n"
                f"Task Instructions:\n{task.instructions}\n\n"
                f"Success Criteria:\n{task.success_criteria}\n\n"
                f"Inputs:\n{resolved_inputs if resolved_inputs else 'None'}\n\n"
                f"Notes:\n{task.notes or 'None'}"
            )
            result = await PlannerExecutorPattern._assign_task(prompt)
            completed.tasks_executed[task_id] = result
            await pq.put(f"- completed {task_id}\n")

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

        try:
            # When calling this function standalone, set enable_trace to True
            if enable_trace:
                with trace(worker.name):
                    result = await Runner.run(worker, task)
            else:
                result = await Runner.run(worker, task)
        except MaxTurnsExceeded as e:
            # The system still returns a result object even when max turns are exceeded
            result = getattr(e, 'result', None)
            if result and result.final_output:
                return result.final_output_as(TaskOutput)
            else:
                try:
                    task_dict = json.loads(task)
                    tid = task_dict.id
                except Exception as json_err:
                    tid = "task-000"
                finally:
                    return TaskOutput(
                        id=tid,
                        output="",
                        errors="Worker exceeded the allowed interaction steps and could not complete the task."
                    )

        return result.final_output_as(TaskOutput)
        