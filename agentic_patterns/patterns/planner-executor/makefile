# Makefile for cleaning non-source files

.PHONY: setup clean run

setup:
	@echo "> Seting up planner-executor..."
	@echo "  planner-executor setup is complete"

clean:
	@echo "> Cleaning planner-executor..."

	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name 'tmp' -exec rm -rf {} +
	@find . -type d -name '.gradio' -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*~" -delete

	@echo "  planner-executor is clean"

run:
	@echo "🚀 Launching Planner–Executor demo app..."
	@uv run main.py
