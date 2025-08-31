# pattern.py
# Coordinates execution of the Planner–Executor pattern from a single interface.

from agents import Runner, trace
from core.agent_factory import AgentFactory
from schema.executor import ExecutorResponse
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
        executor = AgentFactory.get_agent("executor")

        # Step 1: Use Planner to generate a plan
        with trace(planner.name):
            planner_result = await Runner.run(planner, f"User Goal: {query}")

        if planner_result is None or not planner_result.final_output:
            raise ValueError("Planner agent failed to produce a valid plan.")

        plan = planner_result.final_output_as(TasksPlan)
        plan_str = plan.model_dump_json()

        # Step 2: Use Executor to execute the plan
        with trace(executor.name):
            executor_result = await Runner.run(executor, plan_str)

        if executor_result and executor_result.final_output:
            return executor_result.final_output_as(ExecutorResponse)
        else:
            raise ValueError("The Executor did not return a valid response.")