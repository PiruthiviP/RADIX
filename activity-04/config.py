import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or ""

# Researcher Model Configs
MODEL_CLAUDE = os.getenv("MODEL_CLAUDE", "openai/gpt-4o-mini")
MODEL_CLAUDE_FALLBACKS = ["perplexity/sonar-pro-search", "meta-llama/llama-3.2-3b-instruct:free"]

MODEL_GEMINI = os.getenv("MODEL_GEMINI", "perplexity/sonar-pro-search")
MODEL_GEMINI_FALLBACKS = ["openai/gpt-4o-mini", "meta-llama/llama-3.2-3b-instruct:free"]

MODEL_LLAMA = os.getenv("MODEL_LLAMA", "meta-llama/llama-3.3-70b-instruct")
MODEL_LLAMA_FALLBACKS = ["meta-llama/llama-3.1-8b-instant", "google/gemini-2.5-flash"]

# Consolidation Model Config
MODEL_CONSOLIDATOR = os.getenv("MODEL_CONSOLIDATOR", "google/gemini-2.5-pro")
MODEL_CONSOLIDATOR_FALLBACK = os.getenv("MODEL_CONSOLIDATOR_FALLBACK", "google/gemini-2.5-flash")

# Regeneration Model Config
MODEL_REGENERATOR = os.getenv("MODEL_REGENERATOR", "meta-llama/llama-3.3-70b-instruct")
MODEL_REGENERATOR_FALLBACK = os.getenv("MODEL_REGENERATOR_FALLBACK", "meta-llama/llama-3.1-8b-instant")

# Web Search Tool Toggle (paid feature on OpenRouter)
USE_SEARCH_TOOL = os.getenv("USE_SEARCH_TOOL", "False").lower() in ("true", "1", "yes")

def validate_config():
    errors = []
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        errors.append("OPENROUTER_API_KEY is not set or contains the default placeholder.")
    if not SUPABASE_URL or SUPABASE_URL == "your_supabase_url_here":
        errors.append("SUPABASE_URL is not set or contains the default placeholder.")
    if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_anon_key_or_service_role_key_here":
        errors.append("SUPABASE_KEY is not set or contains the default placeholder.")
    return len(errors) == 0, errors

def get_client_credentials(model_name: str) -> tuple[str, str, str]:
    """
    Returns (api_key, api_base, model_slug) based on the model target.
    If the model can be called directly using direct keys (Groq, Gemini), we return the direct endpoints.
    Otherwise, we route it through OpenRouter.
    """
    import os
    
    # Load keys
    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    
    model_lower = model_name.lower()
    
    # Detect Groq models
    if "llama" in model_lower and groq_key:
        if "3.3" in model_lower:
            model_slug = "llama-3.3-70b-versatile"
        elif "8b" in model_lower or "instant" in model_lower:
            model_slug = "llama-3.1-8b-instant"
        else:
            model_slug = "llama-3.3-70b-versatile"
        return groq_key, "https://api.groq.com/openai/v1", model_slug
        
    # Detect Gemini models
    if "gemini" in model_lower and gemini_key:
        model_slug = "models/gemini-2.5-pro" if "pro" in model_lower else "models/gemini-2.5-flash"
        return gemini_key, "https://generativelanguage.googleapis.com/v1beta/openai/", model_slug
        
    # Default to OpenRouter
    openrouter_base = "https://openrouter.ai/api/v1"
    return openrouter_key, openrouter_base, model_name
