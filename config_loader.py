import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (as fallback)
load_dotenv()

def get_secret_or_env(var_name: str) -> str:
    """Return value from Streamlit secrets if present, else environment, else empty."""
    try:
        if hasattr(st, 'secrets') and var_name in st.secrets:
            return st.secrets.get(var_name, '')
    except Exception:
        pass
    return os.getenv(var_name, '')

def validate_api_keys(assemblyai_key: str, gemini_key: str):
    """Validate that required API keys are present based on provided or env/secrets."""
    missing_keys = []
    if not assemblyai_key:
        missing_keys.append("ASSEMBLYAI_API_KEY")
    if not gemini_key:
        missing_keys.append("GEMINI_API_KEY")
    return missing_keys