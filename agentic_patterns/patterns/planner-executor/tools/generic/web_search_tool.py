# web_search_tool.py
# A generic tool that performs real-time web searches using the Serper.dev API.

import json
import os
import requests
from agents import function_tool
from typing import Any, Dict, Optional

from core.registries import tool_registry


@function_tool
def web_search_tool(
    query: str, 
    timeout: int = 10, 
    url: str = "https://google.serper.dev/search") -> Dict[str, Any]:
    """
    Performs a web search using the Serper.dev API and returns the parsed JSON response.

    Args:
        query (str): The search query string.
        timeout (int): The number of seconds to wait for a response from the server.
        url (str): Endpoint URL for the Serper API request (default is the official search endpoint).

    Raises:
        EnvironmentError: If the SERPER_API_KEY environment variable is not set.
        requests.RequestException: If the HTTP request fails or times out.

    Returns:
        Dict[str, Any]: A dictionary containing the JSON response from the API.
    """

    # Validate API key
    api_key = os.getenv('SERPER_API_KEY')
    if not api_key:
        raise EnvironmentError("SERPER_API_KEY environment variable not set.")

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    payload = {"q": query}

    # Post request to serper
    with requests.Session() as session:
        response = session.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()        


# Register this tool
tool_registry.register(web_search_tool.name, web_search_tool)