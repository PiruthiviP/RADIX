import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load .env file at module import time
load_dotenv()

@dataclass
class AppConfig:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "zagent-001-v2"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8010")))
    db_path: str = field(default_factory=lambda: os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "company_intelligence.db")))
    metadata_path: str = field(default_factory=lambda: os.getenv("METADATA_PATH", "meta_data_complete.json"))
    max_retry_rounds: int = field(default_factory=lambda: int(os.getenv("MAX_RETRY_ROUNDS", "2")))
    research_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("RESEARCH_TIMEOUT_SECONDS", "8")))

    def __post_init__(self):
        # Resolve db_path directory
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # Resolve metadata_path. We will check both local directory and the parent directory
        if not os.path.exists(self.metadata_path):
            parent_metadata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "meta_data_complete.json")
            if os.path.exists(parent_metadata_path):
                self.metadata_path = parent_metadata_path

@dataclass
class LangSmithConfig:
    api_key: str = field(default_factory=lambda: os.getenv("LANGSMITH_API_KEY", ""))
    project: str = field(default_factory=lambda: os.getenv("LANGSMITH_PROJECT", "zagent-001-v2"))
    endpoint: str = field(default_factory=lambda: os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"))
    tracing_v2: str = field(default_factory=lambda: os.getenv("LANGCHAIN_TRACING_V2", "true"))

    def apply(self) -> None:
        if self.api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project
            os.environ["LANGCHAIN_ENDPOINT"] = self.endpoint
            os.environ["LANGCHAIN_TRACING_V2"] = self.tracing_v2

@dataclass
class GeminiConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    web_search_enabled: bool = field(default_factory=lambda: os.getenv("GEMINI_WEB_SEARCH_ENABLED", "true").lower() == "true")

@dataclass
class GroqConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    use_tavily_search: bool = field(default_factory=lambda: os.getenv("GROQ_USE_TAVILY_SEARCH", "true").lower() == "true")
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    tavily_max_results: int = field(default_factory=lambda: int(os.getenv("TAVILY_MAX_RESULTS", "5")))

@dataclass
class OpenRouterConfig:
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"))
    base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    web_search_enabled: bool = field(default_factory=lambda: os.getenv("OPENROUTER_WEB_SEARCH_ENABLED", "true").lower() == "true")

@dataclass
class ModelConfig:
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    groq: GroqConfig = field(default_factory=GroqConfig)
    openrouter: OpenRouterConfig = field(default_factory=OpenRouterConfig)

@dataclass
class SupabaseConfig:
    url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    key: str = field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", ""))
    use_supabase: bool = field(default_factory=lambda: os.getenv("USE_SUPABASE", "true").lower() == "true")

    @property
    def enabled(self) -> bool:
        return self.use_supabase and bool(self.url) and bool(self.key)

def validate_provider_config(model_config: ModelConfig) -> bool:
    """Ensures at least one of GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY is set."""
    return bool(
        model_config.gemini.api_key or
        model_config.groq.api_key or
        model_config.openrouter.api_key
    )
