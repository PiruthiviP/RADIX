import re
import urllib.parse
import urllib.request
import urllib.error
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ResearchEngine:
    def __init__(self, timeout_seconds: int = 8):
        self.timeout_seconds = timeout_seconds

    def _fetch_wikipedia(self, company_name: str) -> str:
        """Fetches the Wikipedia page summary for the company name."""
        quoted_name = urllib.parse.quote(company_name)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_name}"
        
        headers = {
            "User-Agent": "ZagentCompanyIntelligence/2.0 (contact: info@zagent.ai)"
        }
        
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json = urllib.json = urllib.request.json = None
                # Parse JSON summary
                import json
                res_data = json.loads(response.read().decode('utf-8'))
                extract = res_data.get("extract", "")
                if extract:
                    return f"Wikipedia Summary for {company_name}:\n{extract}\n"
        except urllib.error.HTTPError as e:
            # Check 404 which is common if page doesn't exist
            if e.code == 404:
                logger.info(f"Wikipedia page not found for company: {company_name}")
            else:
                logger.warning(f"Wikipedia HTTP error: {e.code} for {company_name}")
        except Exception as e:
            logger.warning(f"Failed to fetch Wikipedia for {company_name}: {str(e)}")
            
        return ""

    def _scrape_website(self, url: str) -> str:
        """Performs a basic HTTP request to the website homepage and extracts sanitized text."""
        if not url or url == "NA":
            return ""
            
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                html_content = response.read().decode(charset, errors='ignore')
                
                # Strip script and style blocks
                clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                
                # Strip all other HTML tags
                text = re.sub(r'<.*?>', ' ', clean_html)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Keep first 2500 characters
                truncated_text = text[:2500]
                return f"Homepage Scrape of {url}:\n{truncated_text}\n"
        except Exception as e:
            logger.warning(f"Failed to scrape company website {url}: {str(e)}")
            return ""

    async def collect(self, company_name: str, website_url: Optional[str] = None) -> Dict[str, str]:
        """Runs Wikipedia fetch and web scraping in parallel thread pools."""
        loop = asyncio.get_running_loop()
        
        # Dispatch to thread pool
        wiki_task = loop.run_in_executor(None, self._fetch_wikipedia, company_name)
        
        web_task = asyncio.sleep(0) # Default placeholder
        if website_url and website_url != "NA":
            web_task = loop.run_in_executor(None, self._scrape_website, website_url)
            
        wiki_res, web_res = await asyncio.gather(wiki_task, web_task)
        
        # Generate guidelines queries
        guidelines = (
            f"Query Guidelines for {company_name}:\n"
            f"- Identify founding history, founders, and executive team.\n"
            f"- Search for revenue figures, currency, margins, and funding data.\n"
            f"- Extract top competitors, partners, and business model traits.\n"
            f"- Find cultural markers, work-life policies, and hiring details.\n"
        )
        
        return {
            "wikipedia": wiki_res or "",
            "homepage": web_res or "",
            "guidelines": guidelines
        }

    def build_context(self, wikipedia: str, homepage: str, guidelines: str) -> str:
        """Merges inputs, sanitizes spaces, deduplicates sentences and limits to 12,000 characters."""
        merged = f"{wikipedia}\n{homepage}\n{guidelines}"
        
        # Sanitize whitespace
        merged = re.sub(r'[ \t]+', ' ', merged)
        merged = re.sub(r'\n+', '\n', merged)
        
        # Deduplicate sentences
        # Simple sentence splitter on punctuation
        sentences = re.split(r'(?<=[.!?])\s+', merged)
        seen_sentences = set()
        deduped_sentences = []
        
        for s in sentences:
            s_clean = s.strip().lower()
            # Ignore empty sentences or generic single word/number sentences
            if not s_clean:
                continue
            if s_clean not in seen_sentences:
                seen_sentences.add(s_clean)
                deduped_sentences.append(s.strip())
                
        context = " ".join(deduped_sentences)
        
        # Limit to 12,000 characters
        return context[:12000]
