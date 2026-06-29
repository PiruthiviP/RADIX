import requests
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger("Embedder")

def get_embedding(text: str) -> list[float]:
    """
    Generates a 3072-dimensional embedding vector for the input text using Gemini's gemini-embedding-001 model.
    """
    if not GEMINI_API_KEY:
        # Check if empty
        logger.error("GEMINI_API_KEY is empty.")
        return [0.0] * 3072

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        res_json = response.json()
        embedding = res_json.get("embedding", {}).get("values", [])
        if not embedding:
            raise ValueError("No embedding values found in response.")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return a zero vector of 3072 dims as fallback if API call fails to prevent crashing
        return [0.0] * 3072
