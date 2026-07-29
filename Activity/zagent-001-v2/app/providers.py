import asyncio
import logging
from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel

# Attempt imports for LangChain model integrations
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

from app.config import ModelConfig

logger = logging.getLogger(__name__)

class ProviderAdapter:
    def __init__(self, provider_name: str, model_name: str, llm_instance: Optional[BaseChatModel]):
        self.provider_name = provider_name
        self.model_name = model_name
        self.llm = llm_instance

    def calculate_confidence(self, response_text: str) -> float:
        """Calculates a simple confidence metric based on response length and character structures."""
        if not response_text or response_text.strip() == "NA":
            return 0.0
            
        score = 0.5
        # Check if response looks like structured JSON
        has_brackets = "{" in response_text and "}" in response_text
        has_colons = ":" in response_text
        
        if has_brackets:
            score += 0.2
        if has_colons:
            score += 0.1
        if len(response_text) > 200:
            score += 0.1
        if len(response_text) > 800:
            score += 0.1
            
        return min(max(score, 0.0), 1.0)

    async def ainvoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        """Asynchronously invoke the model."""
        if not self.llm:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": "",
                "confidence": 0.0,
                "error": f"Provider {self.provider_name} is not initialized (missing API key)."
            }
        try:
            # Let subclass or custom logic handle grounding
            response = await self.llm.ainvoke(prompt, **kwargs)
            content = getattr(response, "content", str(response))
            confidence = self.calculate_confidence(content)
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": content,
                "confidence": confidence,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in ainvoke for provider {self.provider_name}: {str(e)}")
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": "",
                "confidence": 0.0,
                "error": str(e)
            }

    def invoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        """Synchronously invoke the model."""
        if not self.llm:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": "",
                "confidence": 0.0,
                "error": f"Provider {self.provider_name} is not initialized."
            }
        try:
            response = self.llm.invoke(prompt, **kwargs)
            content = getattr(response, "content", str(response))
            confidence = self.calculate_confidence(content)
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": content,
                "confidence": confidence,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in invoke for provider {self.provider_name}: {str(e)}")
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "content": "",
                "confidence": 0.0,
                "error": str(e)
            }


class GeminiAdapter(ProviderAdapter):
    def __init__(self, api_key: str, model: str, web_search_enabled: bool):
        llm = None
        if ChatGoogleGenerativeAI and api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    google_api_key=api_key,
                    model=model,
                    temperature=0.2
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {str(e)}")
        super().__init__("gemini", model, llm)
        self.web_search_enabled = web_search_enabled

    async def ainvoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        # Google search grounding inside the invoke call by supplying tool parameters
        if self.web_search_enabled and self.llm:
            kwargs["tools"] = [{"google_search": {}}]
        return await super().ainvoke(prompt, company_name, batch_name, **kwargs)

    def invoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        if self.web_search_enabled and self.llm:
            kwargs["tools"] = [{"google_search": {}}]
        return super().invoke(prompt, company_name, batch_name, **kwargs)


class GroqAdapter(ProviderAdapter):
    def __init__(self, api_key: str, model: str, use_tavily_search: bool, tavily_api_key: str, tavily_max_results: int):
        llm = None
        if ChatGroq and api_key:
            try:
                llm = ChatGroq(
                    groq_api_key=api_key,
                    model=model,
                    temperature=0.2
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChatGroq: {str(e)}")
        super().__init__("groq", model, llm)
        self.use_tavily_search = use_tavily_search
        self.tavily_api_key = tavily_api_key
        self.tavily_max_results = tavily_max_results

    async def _enrich_prompt(self, prompt: str, company_name: str, batch_name: str) -> str:
        if not self.use_tavily_search or not self.tavily_api_key:
            return prompt
            
        search_query = f"{company_name} {batch_name or 'intelligence'}"
        logger.info(f"Enriching Groq prompt via Tavily search for: '{search_query}'")
        
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # Run Tavily search in thread pool
            def run_tavily():
                return client.search(query=search_query, max_results=self.tavily_max_results)
            
            response = await asyncio.to_thread(run_tavily)
            results = response.get("results", [])
            
            if results:
                tavily_block = "=== Tavily Search Grounding Context ===\n"
                for i, r in enumerate(results):
                    tavily_block += f"[{i+1}] Title: {r.get('title')}\nURL: {r.get('url')}\nSnippets: {r.get('content')}\n\n"
                tavily_block += "========================================\n\n"
                return tavily_block + prompt
        except Exception as e:
            logger.error(f"Tavily search grounding failed for Groq: {str(e)}")
            
        return prompt

    async def ainvoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        enriched = await self._enrich_prompt(prompt, company_name, batch_name)
        return await super().ainvoke(enriched, company_name, batch_name, **kwargs)

    def invoke(self, prompt: str, company_name: str = "", batch_name: str = "", **kwargs) -> Dict[str, Any]:
        # For sync invoke, we run prompt enrichment using an event loop or run synchronous search
        if self.use_tavily_search and self.tavily_api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=self.tavily_api_key)
                search_query = f"{company_name} {batch_name or 'intelligence'}"
                response = client.search(query=search_query, max_results=self.tavily_max_results)
                results = response.get("results", [])
                if results:
                    tavily_block = "=== Tavily Search Grounding Context ===\n"
                    for i, r in enumerate(results):
                        tavily_block += f"[{i+1}] Title: {r.get('title')}\nURL: {r.get('url')}\nSnippets: {r.get('content')}\n\n"
                    tavily_block += "========================================\n\n"
                    prompt = tavily_block + prompt
            except Exception as e:
                logger.error(f"Sync Tavily search failed: {str(e)}")
        return super().invoke(prompt, company_name, batch_name, **kwargs)


class OpenRouterAdapter(ProviderAdapter):
    def __init__(self, api_key: str, model: str, base_url: str, web_search_enabled: bool):
        llm = None
        if ChatOpenAI and api_key:
            try:
                llm = ChatOpenAI(
                    openai_api_key=api_key,
                    base_url=base_url,
                    model_name=model,
                    temperature=0.2
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChatOpenAI for OpenRouter: {str(e)}")
        super().__init__("openrouter", model, llm)
        self.web_search_enabled = web_search_enabled


class ProviderFactory:
    @staticmethod
    def create_providers(config: ModelConfig) -> Dict[str, ProviderAdapter]:
        providers = {}
        
        # 1. Gemini
        if config.gemini.api_key:
            providers["gemini"] = GeminiAdapter(
                api_key=config.gemini.api_key,
                model=config.gemini.model,
                web_search_enabled=config.gemini.web_search_enabled
            )
            
        # 2. Groq
        if config.groq.api_key:
            providers["groq"] = GroqAdapter(
                api_key=config.groq.api_key,
                model=config.groq.model,
                use_tavily_search=config.groq.use_tavily_search,
                tavily_api_key=config.groq.tavily_api_key,
                tavily_max_results=config.groq.tavily_max_results
            )
            
        # 3. OpenRouter
        if config.openrouter.api_key:
            providers["openrouter"] = OpenRouterAdapter(
                api_key=config.openrouter.api_key,
                model=config.openrouter.model,
                base_url=config.openrouter.base_url,
                web_search_enabled=config.openrouter.web_search_enabled
            )
            
        return providers
