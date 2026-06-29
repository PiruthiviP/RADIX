import asyncio
import json
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import (
    MODEL_CLAUDE,
    MODEL_CLAUDE_FALLBACKS,
    MODEL_GEMINI,
    MODEL_GEMINI_FALLBACKS,
    MODEL_LLAMA,
    MODEL_LLAMA_FALLBACKS,
    USE_SEARCH_TOOL,
    get_client_credentials
)
from schemas import CompanyFull

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ResearchAgents")

# Split CompanyFull fields into chunks of core parameters
def get_parameter_chunks(chunk_size: int = 33) -> List[List[str]]:
    core_fields = [
        "name", "short_name", "logo_url", "category", "nature_of_company",
        "incorporation_year", "overview_text", "headquarters_address",
        "operating_countries", "office_locations", "employee_size",
        "yoy_growth_rate", "website_url", "ceo_name", "primary_contact_email",
        "tech_stack", "annual_revenue", "glassdoor_rating", "google_rating", "linkedin_url"
    ]
    fields_to_query = [f for f in core_fields if f in CompanyFull.model_fields]
    
    chunks = []
    for i in range(0, len(fields_to_query), chunk_size):
        chunks.append(fields_to_query[i:i + chunk_size])
    return chunks

class BaseResearcher:
    def __init__(self, model_name: str, fallback_models: List[str], researcher_name: str, use_search_tool: bool = False):
        self.model_name = model_name
        self.fallback_models = fallback_models or []
        self.researcher_name = researcher_name
        self.use_search_tool = use_search_tool
        
        # Build the model chain: primary model followed by up to 2 fallback models
        self.all_models = [self.model_name] + self.fallback_models[:2]
        
    async def research_chunk_async(self, company_name: str, chunk_keys: List[str]) -> Dict[str, Any]:
        # Build parameter descriptions from schema Fields
        param_desc_list = []
        for key in chunk_keys:
            field = CompanyFull.model_fields[key]
            desc = field.description or ""
            param_desc_list.append(f"- **{key}** ({desc})")
        
        param_descriptions = "\n".join(param_desc_list)
        keys_list_str = ", ".join([f'"{k}"' for k in chunk_keys])
        
        prompt_text = (
            "You are a Corporate Intelligence Analyst and Data Researcher.\n"
            "Search the web for the company '{company_name}' and gather detailed information for the following specific parameters:\n"
            "{param_descriptions}\n\n"
            "INSTRUCTIONS:\n"
            "1. Conduct web searches using your tools or native capabilities to locate accurate facts.\n"
            "2. If no information is found for a parameter, represent the value as 'NA' or null.\n"
            "3. Ensure the values match the expected format (e.g. lists separated by semicolons, percentages as 'X%', numbers as integers, etc.).\n"
            "4. Your response MUST be a single JSON object containing exactly the following keys:\n"
            "   {{{keys_list_str}}}\n"
            "5. Output ONLY the JSON object. Do not include any explanation, markdown backticks, or extra text."
        )
        
        prompt = PromptTemplate(
            template=prompt_text,
            input_variables=["company_name", "param_descriptions", "keys_list_str"]
        )
        
        # Format the prompt
        formatted_prompt = prompt.format(
            company_name=company_name,
            param_descriptions=param_descriptions,
            keys_list_str=keys_list_str
        )
        
        # Try primary model and fallback models in sequence
        for index, model_name in enumerate(self.all_models):
            is_primary = (index == 0)
            role = "primary" if is_primary else f"fallback {index}"
            
            try:
                logger.info(f"[{self.researcher_name}] Trying {role} model '{model_name}' for chunk of {len(chunk_keys)} fields...")
                
                # Configure model kwargs
                extra_body = None
                api_key, api_base, model_slug = get_client_credentials(model_name)
                
                # openrouter:web_search is only valid for OpenRouter endpoints
                if self.use_search_tool and "openrouter.ai" in api_base:
                    extra_body = {
                        "tools": [{"type": "openrouter:web_search"}]
                    }
                    
                llm = ChatOpenAI(
                    openai_api_key=api_key,
                    openai_api_base=api_base,
                    model_name=model_slug,
                    temperature=0.2,
                    max_tokens=4096,
                    extra_body=extra_body
                )
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: llm.invoke(formatted_prompt)
                )
                
                content = response.content.strip()
                
                # Use regex to extract the JSON object block
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                # Pre-process content to fix common unquoted NA issues (e.g., : NA -> : "NA")
                content = re.sub(r':\s*([Nn][Aa])\b', ': "NA"', content)
                
                data = json.loads(content)
                logger.info(f"[{self.researcher_name}] Successfully retrieved and parsed chunk using '{model_name}'.")
                return data
                
            except Exception as e:
                logger.warning(f"[{self.researcher_name}] Model '{model_name}' ({role}) failed: {e}")
                if index < len(self.all_models) - 1:
                    logger.info(f"[{self.researcher_name}] Switching to next fallback model...")
                else:
                    logger.error(f"[{self.researcher_name}] All primary and fallback models failed for this chunk.")
                    
        # Return dict with NA for this chunk if all fail
        return {k: "NA" for k in chunk_keys}

    async def research_company_async(self, company_name: str) -> Dict[str, Any]:
        chunks = get_parameter_chunks()
        results = {}
        
        # Process chunks sequentially to respect rate limits / token safety, but could be run in parallel if API limits allow
        for i, chunk in enumerate(chunks):
            chunk_data = await self.research_chunk_async(company_name, chunk)
            results.update(chunk_data)
            # Sleep longer in free mode to avoid rate limits
            sleep_time = 6 if not USE_SEARCH_TOOL else 1
            await asyncio.sleep(sleep_time)
            
        return results

class ClaudeResearcher(BaseResearcher):
    def __init__(self):
        super().__init__(
            model_name=MODEL_CLAUDE,
            fallback_models=MODEL_CLAUDE_FALLBACKS,
            researcher_name="Claude-Researcher",
            use_search_tool=USE_SEARCH_TOOL
        )

class GeminiResearcher(BaseResearcher):
    def __init__(self):
        super().__init__(
            model_name=MODEL_GEMINI,
            fallback_models=MODEL_GEMINI_FALLBACKS,
            researcher_name="Gemini-Researcher",
            use_search_tool=USE_SEARCH_TOOL
        )

class LlamaResearcher(BaseResearcher):
    def __init__(self):
        super().__init__(
            model_name=MODEL_LLAMA,
            fallback_models=MODEL_LLAMA_FALLBACKS,
            researcher_name="Llama-Researcher",
            use_search_tool=USE_SEARCH_TOOL
        )

async def run_parallel_research(company_name: str) -> Dict[str, Dict[str, Any]]:
    logger.info(f"Initiating parallel research for company: {company_name}")
    
    claude_agent = ClaudeResearcher()
    gemini_agent = GeminiResearcher()
    llama_agent = LlamaResearcher()
    
    results = {}
    
    if not USE_SEARCH_TOOL:
        # Free mode: Run sequentially and stagger requests to avoid OpenRouter free 429 rate limits
        logger.info("Free mode active: Running researchers sequentially with stagger delays to prevent 429 rate limits.")
        try:
            results["claude"] = await claude_agent.research_company_async(company_name)
        except Exception as e:
            logger.error(f"Claude agent failed: {e}")
            results["claude"] = {}
        await asyncio.sleep(6)
        
        try:
            results["gemini"] = await gemini_agent.research_company_async(company_name)
        except Exception as e:
            logger.error(f"Gemini agent failed: {e}")
            results["gemini"] = {}
        await asyncio.sleep(6)
            
        try:
            results["llama"] = await llama_agent.research_company_async(company_name)
        except Exception as e:
            logger.error(f"Llama agent failed: {e}")
            results["llama"] = {}
    else:
        # Production/Paid mode: Run concurrently in parallel for maximum speed
        tasks = {
            "claude": claude_agent.research_company_async(company_name),
            "gemini": gemini_agent.research_company_async(company_name),
            "llama": llama_agent.research_company_async(company_name)
        }
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Agent {name} failed: {e}")
                results[name] = {}
                
    logger.info(f"Completed parallel research for company: {company_name}")
    return results

if __name__ == '__main__':
    # Test script locally
    async def test():
        res = await run_parallel_research("Blinkit")
        print(json.dumps(res, indent=2))
        
    # To run: python3 -m activity_04.research_agents
    # asyncio.run(test())
