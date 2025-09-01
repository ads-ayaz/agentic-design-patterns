# Makefile for cleaning non-source files

.PHONY: setup clean

setup:
	@echo "🔧 Setting up environment using uv..."
	@command -v uv >/dev/null 2>&1 || { echo "You don't have uv. Install it and try again"; }
	@uv sync

	-@$(MAKE) -C patterns/planner-executor setup 2>/dev/null
	-@$(MAKE) -C patterns/worker setup 2>/dev/null
	-@$(MAKE) -C patterns/worker-validator setup 2>/dev/null
	@echo "Setup complete."

clean:
	@echo "Cleaning up compiled Python files, caches, and temporary files..."
	
	-@$(MAKE) -C patterns/planner-executor clean 2>/dev/null
	-@$(MAKE) -C patterns/worker clean 2>/dev/null
	-@$(MAKE) -C patterns/worker-validator clean 2>/dev/null
	@echo "Cleanup complete."