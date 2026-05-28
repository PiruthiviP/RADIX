import re
import pytest
from typing import Dict, Any, List, Tuple

# Mock Live Market Database representing the competitive landscape as of May 22, 2026
LIVE_MARKET_DATABASE = {
    "generative ai": {
        "required_disruptors": {"openai", "anthropic", "google", "meta"},
        "defunct_or_acquired": {"cohere-old", "fake-ai-inc"},
        "market_share_caps": {
            "openai": 60.0,
            "anthropic": 25.0
        }
    },
    "web search": {
        "required_disruptors": {"google", "microsoft", "openai"},
        "defunct_or_acquired": {"yahoo", "ask jeeves"},
        "market_share_caps": {
            "google": 78.0  # Disrupted down from 95% by AI search entrants
        }
    }
}

def validate_competitors_freshness(industry_key: str, ingested_competitors: str) -> Tuple[bool, List[str]]:
    """
    Validates that 'Key Competitors' is temporally accurate.
    - Confirms newly emerged disruptors are included in the list.
    - Rejects or flags old, defunct, or acquired competitors.
    """
    errors = []
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, [] # Skip check if industry is not modeled
        
    ingested_list = [c.strip().lower() for c in ingested_competitors.split(",") if c.strip()]
    
    # Check 1: Ensure new critical disruptors are mentioned
    missing_disruptors = [d for d in industry["required_disruptors"] if d not in ingested_list]
    # If a company is in GenAI, it must list at least some major active disruptors
    if len(missing_disruptors) >= len(industry["required_disruptors"]) - 1:
        errors.append(
            f"Temporal Competitor Error: Ingested competitor list is outdated. "
            f"Failed to include newly emerged dominant disruptors: {missing_disruptors}."
        )
        
    # Check 2: Reject defunct/obsolete competitors
    for defunct in industry["defunct_or_acquired"]:
        if defunct in ingested_list:
            errors.append(f"Obsolete Competitor: Ingested competitor list includes defunct or acquired entity: '{defunct}'.")
            
    return len(errors) == 0, errors

def validate_disrupted_market_share(industry_key: str, company_alias: str, ingested_share_str: str) -> Tuple[bool, str]:
    """
    Enforces that 'Market Share (%)' reflects post-disruption benchmarks.
    - Legacy firms cannot claim legacy monopoly shares if disrupted.
    """
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, "Industry not in active market monitor."
        
    # Parse percentage string
    share_match = re.match(r"^([\d\.]+)\s*%$", ingested_share_str.strip())
    if not share_match:
        return False, f"Format Error: Invalid percentage format '{ingested_share_str}'."
        
    ingested_share = float(share_match.group(1))
    
    # Check if company has an active market cap/share restriction due to disruption
    max_allowed = industry["market_share_caps"].get(company_alias.lower())
    if max_allowed and ingested_share > max_allowed:
        return False, (
            f"Temporal Accuracy Error: Ingested Market Share ({ingested_share}%) is outdated. "
            f"Following 2025/2026 industry disruption, the maximum registered share for '{company_alias}' is {max_allowed}%."
        )
        
    return True, "Market share verified against current-year bounds."

def validate_peer_benchmarks(benchmark_text: str, industry_key: str) -> Tuple[bool, str]:
    """Ensures that peer comparisons do not reference obsolete/defunct entities."""
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, "Industry not monitored."
        
    for defunct in industry["defunct_or_acquired"]:
        if re.search(r"\b" + re.escape(defunct) + r"\b", benchmark_text, re.IGNORECASE):
            return False, f"Obsolete Benchmark: Peer comparison references obsolete or defunct entity: '{defunct}'."
            
    return True, "Benchmark peer group is temporally valid."


# --- Pytest Tests ---

def test_current_competitor_landscape_passes():
    """Verifies that an up-to-date competitor list including active disruptors passes."""
    valid_competitors = "OpenAI, Anthropic, Google, Meta"
    success, errors = validate_competitors_freshness("Generative AI", valid_competitors)
    assert success is True
    assert not errors

def test_outdated_competitor_landscape_fails():
    """Verifies that a competitor list missing newly emerged active disruptors fails validation."""
    outdated_competitors = "CoHere-Old, Fake-AI-Inc"  # Contains defunct entities, missing OpenAI/Anthropic
    success, errors = validate_competitors_freshness("Generative AI", outdated_competitors)
    assert success is False
    assert any("Failed to include newly emerged dominant disruptors" in err for err in errors)
    assert any("Obsolete Competitor" in err for err in errors)

def test_disrupted_monopoly_market_share_fails():
    """Verifies that a legacy search company claiming a pre-disruption 95% share is rejected."""
    success, msg = validate_disrupted_market_share("Web Search", "Google", "95%")
    assert success is False
    assert "outdated" in msg
    assert "maximum registered share" in msg

def test_disrupted_market_share_passes():
    """Verifies that updated market shares following 2025/2026 disruptions pass validation."""
    success, msg = validate_disrupted_market_share("Web Search", "Google", "75%")
    assert success is True

def test_obsolete_peer_benchmark_rejected():
    """Verifies that benchmark narratives comparing the company to defunct legacy entities fail."""
    success, msg = validate_peer_benchmarks("Outperforming Yahoo by 50% in search query volume", "Web Search")
    assert success is False
    assert "Obsolete Benchmark" in msg
    assert "Yahoo" in msg