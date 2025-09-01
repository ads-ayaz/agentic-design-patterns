# Planner–Executor Pattern

This project demonstrates the **Planner–Executor agentic pattern** using the [OpenAI Agents SDK](https://github.com/openai/openai-python). It features an interactive Gradio UI for executing structured, multi-agent workflows powered by real-time web search and task orchestration.


## 🚀 Quick Start

Follow the steps below to set up and run the application.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/agentic-design-patterns.git
cd agentic-design-patterns/patterns/planner-executor
```

### 2. Set Up the Environment

Use the provided `Makefile` to initialize the project environment and install dependencies via [`uv`](https://github.com/astral-sh/uv):

```bash
make setup
```

> **Note:** You must have `uv` installed. If not, install it via:
```bash
pip install uv
```

This will:
- Create a virtual environment (if needed)
- Install all required dependencies from `uv.lock`

### 3. Run the App

Launch the Gradio UI:
```bash
make run
```

This will:
- Start the demo app in your browser
- Let you enter complex task queries to test the Planner–Executor pipeline


## 🧹 Cleanup

To remove non-source files and temporary artifacts:

```bash
make clean
```

This deletes:
- `__pycache__/` folders
- Compiled `.pyc` / `.pyo` files
- Temporary `tmp/` and `.gradio/` folders


## 📁 Project Structure

```
planner-executor/
├── config/                     # YAML agent configurations
├── core/                       # Core logic: agents, pattern runner, registries
├── schema/                     # Pydantic models for agent communication
├── tools/                      # Reusable tool implementations (e.g., web search)
├── main.py                     # Entry point (Gradio UI)
├── planner-executor-nb.ipynb   # Notebook walkthrough of the pattern
├── makefile                    # setup / clean / run commands
```


## 🧠 Pattern Overview

The app is structured around the `Planner–Executor` agentic pattern:

- **`Planner`**: Breaks down the user’s query into atomic tasks.
- **`Executor`**: Manages task execution and dependencies using `Worker` and `Consolidator` agents.
- **`Worker`**: Executes atomic tasks; uses `web_search_tool` if needed.
- **`Consolidator`**: Synthesizes results into a cohesive final output.


## 🛠 Requirements

- Python 3.12
- `uv` (for environment and package management)
- OpenAI API key
- Serper API key (for web search tool)

### Environment Configuration

Create a `.env` file in the `planner-executor/` directory with:

```env
OPENAI_API_KEY=your-api-key-here
SERPER_API_KEY=your-serper-api-key
```
