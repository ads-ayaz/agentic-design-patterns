# core/env.py
from dotenv import load_dotenv
import os

def load_environment():
    """Load environment variables from a .env file and return key settings."""
    load_dotenv(override=True)
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
        
        "DEFAULT_MODEL": os.getenv("CONF_OPENAI_DEFAULT_MODEL"),
    }