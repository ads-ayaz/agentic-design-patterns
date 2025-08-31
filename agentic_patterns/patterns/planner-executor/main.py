# main.py
# Entry point for running the Planner–Executor pattern with a user query

import asyncio

import core.tool_loader
from core.env import load_environment
from core.pattern import PlannerExecutorPattern
from schema.executor import ExecutorResponse


async def main():
    load_environment()

    query = """Produce a briefing document summarizing the most significant developments in climate policy 
    across the US, EU, and China over the past 12 months. Include key policy changes, notable legislation, 
    and international agreements. Conclude with a comparative analysis highlighting similarities and differences.
    Format the output as a markdown document, using paragraphs where possible."""

    print(f"\nSending query to Planner–Executor pattern:\n{query}\n\n...\n\n")

    try:
        result: ExecutorResponse = await PlannerExecutorPattern.run(query)
        print(f"Status: {result.status}")
        print(f"\nFinal Output:\n{result.final_output}")
        if result.reasoning:
            print(f"\nReasoning: {result.reasoning}")
    except Exception as e:
        print(f"❌ Error during execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())