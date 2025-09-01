# main.py
# Entry point for running the Planner–Executor pattern with a user query

import asyncio
import gradio as gr
import os
import threading
import time

import core.tool_loader
from core.env import load_environment
from core.pattern import PlannerExecutorPattern
from schema.executor import ExecutorResponse



async def run(query: str, progress_report: asyncio.Queue = None) -> str:
    """
    Run the Planner-Executor pattern and return the response.
    """

    msg: str = "PATTERN FAILED TO RUN"
    response: str = ""

    try:
        result: ExecutorResponse = await PlannerExecutorPattern.run(query, progress_report=progress_report)
        msg = f"**Status:** {result.status}"

        if result.final_output and result.reasoning:
            msg = f"**Status:** {result.status}\n\n**Reasoning:**\n{result.reasoning}\n---\n"
            response = result.final_output
        elif result.final_output:
            response = result.final_output
        else:
            response = msg
    except Exception as e:
        msg = str(e)
        response = msg
    finally:
        # Signal the end of the progress stream
        await progress_report.put(f"{msg}\n")
        await progress_report.put(None)
        return response


async def wrapped_run(query: str):
    """
    Wrap the run function to handle the UI updates.
    """

    # Initialize the progress queue
    progress_queue = asyncio.Queue()
    
    # Update to show 'running' state and disable the button
    latest_update: str = "⏳ Working..."
    yield (
        gr.Button(value="Running...", interactive=False, variant="primary"),    # run_button
        gr.Markdown(label="Work Product", value=""),                            # report
        gr.Markdown(label="Progress", value=latest_update)                # progress
    )

    # Create the co-routine task object
    response = asyncio.create_task(run(query, progress_report=progress_queue))

    async def progress_consumer():
        """Consume the progress_queue and yield updates to the UI."""
        full_log = ""
        while True:
            update = await progress_queue.get()
            
            # None signals termination
            if update is None:
                break
            
            full_log += f"{update}\n"
            yield full_log

    # Handle progress updates for display in the UI.
    async for update_string in progress_consumer():
        latest_update = update_string
        yield (
            gr.Button(value="Running...", interactive=False, variant="primary"),
            gr.Markdown(label="Work Product", value=""),
            gr.Markdown(label="Progress", value=latest_update)
        )
    
    # Return the final response
    def get_final_status() -> str:
        status_line = "**Status:**"
        last_status_index = -1
        output_list = latest_update.splitlines(keepends=True)

        # Iterate through the list in reverse to find the last match
        for i in range(len(output_list) - 1, -1, -1):
            if output_list[i].startswith(status_line):
                last_status_index = i
                break

        # If a status line was found, return the slice from that index
        if last_status_index != -1:
            return "".join(output_list[last_status_index:])
        else:
            # If no status line was found, return a list containing only the last element
            return output_list[-1]

    work_output = await response
    final_update = get_final_status()
    yield (
        gr.Button(value="Run", interactive=True, variant="primary"),
        gr.Markdown(label="Work Product", value=work_output),
        gr.Markdown(label="Progress", value=final_update)
    )

def on_exit():
    """ 
    Called by the exit button
    """

    # Update UI and disable controls
    yield(
        gr.Dropdown(label="Use a Sample Query: (optional)", interactive=False),
        gr.Textbox(label="Describe the task that you would like to have completed:", lines=6, interactive=False),
        gr.Button(value="Run", interactive=False, variant="primary"),
        gr.Button(value="Server Ended", interactive=False, variant="secondary")
    )

    # Initiate threaded exit
    def threaded_exit():
        # Wait a moment to allow Gradio to process the click event
        time.sleep(0.5)

        # Gracefully shut down the application
        os._exit(0)

    threading.Thread(target=threaded_exit).start()


async def main():
    load_environment()

    with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
        gr.Markdown("# **Planner-Executor** | Agentic Pattern")
        with gr.Row():
            with gr.Column(scale=6):

                # Dropdown for loading sample queries
                sample_selector = gr.Dropdown(
                    label="Use a Sample Query: (Optional)",
                    choices=test_query,
                    value=None,
                    interactive=True
                )

                # Textbox for user to write the query
                query_textbox = gr.Textbox(
                    label="Describe the task that you would like to have completed:",
                    lines=6,
                    interactive=True,
                )

                # Display stream of progress updates
                progress_output = gr.Markdown(label="Progress")

                # Final output goes here
                report = gr.Markdown(label="Work Product")
            with gr.Column(scale=1, min_width=160):
                run_button = gr.Button("Run", variant="primary")
                exit_button = gr.Button("Shutdown Server", variant="stop")

        # Connect the events        
        sample_selector.change(fn=lambda q: gr.Textbox(value=q), inputs=sample_selector, outputs=query_textbox)
        run_button.click(fn=wrapped_run, inputs=query_textbox, outputs=[run_button, report, progress_output])
        exit_button.click(fn=on_exit, inputs=None, outputs=[sample_selector, query_textbox, run_button, exit_button])

    try:
        ui.launch(inbrowser=True, share=False)
    except Exception as e:
        print(f"An error occurred: {e}. Shutting down Gradio server...")
    finally:
        ui.close()
        print("Gradio server is shut down.")



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
    """,

    """
    Analyze the top 10 Pokémon trading cards released since 2022 in terms of long-term value potential.

    Your response must:
    - Research and rank these cards based on rarity, demand trends, grading impact, and tournament relevance.
    - For each card, explain why it was ranked where it was and what factors could cause its value to rise or fall.
    - Conclude with an investment guide for serious collectors: which cards to hold, flip, or avoid.

    Output the final result as a markdown table of ranked cards, followed by a narrative advisory section.
    """,

    """
    Deconstruct and compare the engineering techniques used in the following LEGO set types:
    - Modular buildings
    - LEGO Technic vehicles
    - Large licensed models (e.g., Millennium Falcon, Hogwarts Castle)

    For each category:
    - Identify 3 core construction techniques and explain how they work.
    - Describe the types of pieces and connections used.
    - Evaluate the design complexity from an engineering standpoint.

    Your output should be a markdown document with one section per category, each containing diagrams or ASCII-style illustrations where helpful. Conclude with a comparative matrix.
    """,

    """
    Model three plausible future scenarios for Canada in the year 2035 based on current developments (2022–2024). Your model should consider:
    - Shifting global alliances and trade patterns
    - Immigration and demographic changes
    - Technological and environmental disruptions

    For each scenario:
    - Assign a name and a short narrative description.
    - Detail the key drivers, assumptions, and outcomes.
    - Assess risks and opportunities for Canadian society and policy.

    Present this as a markdown foresight report with structured scenario sections and a summary matrix comparing them.
    """,
]

if __name__ == "__main__":
    asyncio.run(main())
