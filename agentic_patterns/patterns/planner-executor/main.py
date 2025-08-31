# main.py
# Entry point for running the Planner–Executor pattern with a user query

import asyncio

import core.tool_loader
from core.env import load_environment
from core.pattern import PlannerExecutorPattern
from schema.executor import ExecutorResponse


async def main():
    load_environment()

    query = test_query[1]

    print(f"\nSending query to Planner–Executor pattern:\n{query}\n\n...\n\n")

    try:
        result: ExecutorResponse = await PlannerExecutorPattern.run(query)
        print(f"Status: {result.status}")
        print(f"\nFinal Output:\n{result.final_output}")
        if result.reasoning:
            print(f"\nReasoning: {result.reasoning}")
    except Exception as e:
        print(f"❌ Error during execution: {e}")


test_query = [
    """Produce a briefing document summarizing the most significant developments in climate policy across the US, EU, 
    and China over the past 12 months. Include key policy changes, notable legislation, and international agreements. 
    Conclude with a comparative analysis highlighting similarities and differences.
    - Unless instructed otherwise, synthesize the final output as a concise narrative document. 
    - In the final output, prefer paragraphs over lists; only use bullets and numbered lists when absolutely necessary.
    - Format the final output as a markdown document.
    """,

    """
    Produce a policy profile on India's renewable energy transition over the past five years. The output should include:
    - A timeline of major policy actions and reforms.
    - Summary of government programs (e.g., subsidies, R&D funding).
    - Key statistics on solar, wind, and hydro adoption.
    - Commentary from recent policy papers and media sources.

    Synthesize all findings into a single markdown document with clearly delineated sections. Use a table for the 
    timeline. Do not include citations—just summarize the most critical content.
    """,

    """
    Summarize the current state of the global semiconductor supply chain. Include:
    - Major manufacturers and suppliers by region.
    - Current geopolitical and economic risks.
    - Recent legislation or trade agreements (past 2 years).
    - Comparative analysis of US, Taiwan, South Korea, and China.

    Present the final result as a well-structured briefing with a neutral tone. Ensure that all key claims are grounded in recent facts and avoid vague generalizations. Use paragraphs only—do not use bullet points or headings.
    """,

    """
    Extract and transform insights from the following workflow:
    1. Identify five notable research papers on large language models (LLMs) from the last 18 months.
    2. Summarize the key contributions and limitations of each paper.
    3. Compare the approaches used and identify recurring challenges or patterns.

    Produce a structured markdown report with three sections: Overview, Comparative Insights, and Conclusions. Use clear transitions between sections. Avoid technical jargon when possible.
    """,

    """ 
    Write a historical summary of the Paris Agreement: how it was formed, what it aims to achieve, and how its implementation has evolved over time. Focus on pivotal moments from 2015 to present.

    Output should be a standalone markdown article. No need to break into multiple tasks unless truly necessary.
    """,

    """ 
    Evaluate how five major tech companies (e.g., Apple, Google, Microsoft, Meta, Amazon) are addressing AI ethics and responsible AI governance. For each company:
    - Identify key public commitments, policies, or frameworks.
    - Assess how comprehensive and enforceable their commitments appear.

    Synthesize the findings into a comparative markdown report and assign a qualitative score (e.g., High, Medium, Low) to each company’s efforts. Present the final output in a table followed by a short narrative summary.
    """,

    """
    blah blah blah
    """
]

if __name__ == "__main__":
    asyncio.run(main())