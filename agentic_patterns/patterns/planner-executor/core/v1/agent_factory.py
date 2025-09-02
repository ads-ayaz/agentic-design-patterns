# core/v1/agent_factory.py
# Central factory for creating and caching agents defined in the YAML configuration


import os
from datetime import datetime
from agents import Agent, ModelSettings

from .config_loader import AgentConfigLoader
from ..registries import tool_registry, output_type_registry


class AgentFactory:
    _agents = {}  # Cache of instantiated agents to enforce singleton behavior
    _config_loader = AgentConfigLoader()  # Loads YAML agent configurations

    @classmethod
    def get_agent(cls, agent_type: str, from_cache: bool = True) -> Agent:
        """
        Retrieves an instance of an agent, skipping the cache if `from_cache` is False
        """
        # Return cached agent if already created
        if from_cache and agent_type in cls._agents:
            print(f"- Retrieving {agent_type} agent from cache.")
            return cls._agents[agent_type]

        # Create a new agent instance
        agent = AgentFactory._create_agent(agent_type=agent_type)

        # Store instance in cache and return it
        if from_cache:
            cls._agents[agent_type] = agent
            print(f"- Cached {agent_type} agent.")

        return agent

    
    @classmethod
    def _create_agent(cls, agent_type: str) -> Agent:
        """
        Create and return a new instance of the requested agent type.
        """

        # Load agent configuration from YAML
        agent_config = cls._config_loader.get_agent_config(agent_type)

        # Unique timestamp for naming
        now_string = datetime.now().strftime("%Y-%m-%dT%H:%M:%SU%s")
        agent_name = agent_config.get('name') or f"{agent_type}_{now_string}"

        # Build model settings from config
        model_settings = ModelSettings(
            temperature=agent_config.get('temperature'),
            max_tokens=agent_config.get('max_tokens'),
        )

        # Resolve tools from registry
        tool_names = agent_config.get('tools', [])
        resolved_tools = [
            tool_registry.get(name) or cls._raise_tool_error(name, agent_type) for name in tool_names
        ]

        # Resolve output type
        output_type = output_type_registry.get(agent_config.get('output_type'))

        # Load instructions and inject today's date
        instructions = agent_config.get('instructions')
        if not instructions:
            raise ValueError(f"No instructions provided for agent type '{agent_type}'.")
        dated_instructions = f"Today is {datetime.now().strftime('%Y-%m-%d')}\n\n{instructions}"

        # Create agent
        agent = Agent(
            name=agent_name,
            instructions=dated_instructions,
            tools=resolved_tools,
            model=agent_config.get('model') or os.getenv("CONF_OPENAI_DEFAULT_MODEL"),
            output_type=output_type,
            model_settings=model_settings
        )

        print(f"Created a new {agent_type} agent.")
        return agent

    @staticmethod
    def _raise_tool_error(name, agent_type):
        raise ValueError(f"Tool '{name}' specified in config for agent '{agent_type}' is not registered.")

