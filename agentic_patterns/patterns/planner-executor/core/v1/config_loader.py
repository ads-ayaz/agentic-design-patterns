# core/v1/config_loader.py
# Load the agents-config.yaml file

import yaml
from pathlib import Path


class AgentConfigLoader:
    def __init__(self, config_path: str = './config/agents-config.yaml'):
        self.config_path = Path(config_path)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with self.config_path.open('r') as file:
            return yaml.safe_load(file)

    def get_agent_config(self, agent_type: str) -> dict:
        if agent_type not in self.data:
            raise ValueError(f"Agent type '{agent_type}' not found in config.")
        return self.data[agent_type]

