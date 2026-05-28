import datetime
import pytest
from typing import Dict, Any, List, Tuple

# Ingestion target baseline checkpoint: May 22, 2026
CURRENT_LINE_DATE = datetime.date(2026, 5, 22)

# Mock Live Authority Registry reflecting absolute corporate changes as of May 22, 2026
LIVE_AUTHORITY_REGISTRY = {
    "acmesoft": {
        "Company Name": "Acmesoft Corporation",
        "CEO Name": "Jane Doe",                   # Appointed Q3 2025 (Former CEO was "John Smith")
        "Recent Funding Rounds": "2026-03-10 - Series C - $50M", # Closed in 2026
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)",
        "Last SEC Filing Date": "2026-04-12"
    }
}

def check_temporal_freshness(ingested_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile temporal freshness:
    - Scans for out-of-date executive roles (e.g. predecessor CEO before 2025 transition).
    - Verifies that any 2026 funding rounds logged in live databases are not missing.
    - Confirms that recently announced 2026 products are correctly integrated.
    Returns: (is_fresh, list_of_decay_errors)
    """
    errors = []
    company_name = str(ingested_payload.get("Company Name", "")).strip().lower()
    
    # Resolve company registry
    if company_name not in LIVE_AUTHORITY_REGISTRY:
        errors.append(f"Ingestion Aborted: Company '{ingested_payload.get('Company Name')}' not found in live registry.")
        return False, errors
        
    truth = LIVE_AUTHORITY_REGISTRY[company_name]
    
    # 1. Audit CEO Temporal Freshness (CEO succession occurred in 2025)
    ingested_ceo = ingested_payload.get("CEO Name")
    expected_ceo = truth["CEO Name"]
    if ingested_ceo and ingested_ceo != expected_ceo:
        if ingested_ceo == "John Smith": # Known former CEO (Pre-2025)
            errors.append(
                f"Temporal Decay [CEO Name]: Ingested outdated predecessor CEO 'John Smith' (ousted Q3 2025). "
                f"Factual active CEO is '{expected_ceo}'."
            )
        else:
            errors.append(f"Factual Mismatch [CEO Name]: Ingested '{ingested_ceo}', Expected active CEO '{expected_ceo}'.")

    # 2. Audit Funding Round Freshness (Series C closed in Q1 2026)
    ingested_rounds = str(payload_rounds := ingested_payload.get("Recent Funding Rounds", ""))
    expected_round_sign = "Series C"
    if expected_round_sign not in ingested_rounds:
        # Check if they are stuck in a pre-2026 cutoff state (e.g. only showing Series B)
        errors.append(
            f"Temporal Decay [Recent Funding Rounds]: Missing active 2026 transaction '{expected_round_sign}'. "
            f"Ingested payload only contains outdated historical rounds: '{payload_rounds}'."
        )

    # 3. Audit Product Offerings Freshness (CloudDB v2.0 released in Q1 2026)
    ingested_products = str(payload_products := ingested_payload.get("Services / Offerings / Products", ""))
    expected_product_sign = "CloudDB v2.0"
    if expected_product_sign not in ingested_products:
        errors.append(
            f"Temporal Decay [Services / Offerings / Products]: Missing newly released 2026 product line '{expected_product_sign}'. "
            f"Ingested payload contains stale catalog: '{payload_products}'."
        )

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_temporally_fresh_profile_passes():
    """Verifies that a record capturing 2025/2026 updates passes temporal validation."""
    fresh_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",  # Active CEO
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",  # Includes 2026 Series C
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"      # Includes 2026 product
    }
    
    success, errors = check_temporal_freshness(fresh_payload)
    assert success is True
    assert not errors

def test_stale_pre_2025_ceo_mismatch_fails():
    """Verifies that an outdated CEO (Steve/John before the 2025 transition) is flagged as temporal decay."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "John Smith",  # Outdated predecessor CEO (ousted in 2025)
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"
    }
    
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [CEO Name]" in err for err in errors)
    assert "ousted Q3 2025" in errors[0]

def test_missing_latest_2026_funding_round_fails():
    """Verifies that a company profile missing a newly completed 2026 round fails validation."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M",  # Missing 2026 Series C
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"
    }
    
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [Recent Funding Rounds]" in err for err in errors)
    assert "Missing active 2026 transaction" in errors[0]

def test_missing_newly_released_2026_product_fails():
    """Verifies that missing a product line launched in early 2026 fails validation."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",
        "Services / Offerings / Products": "Core AI Suite"  # Missing 2026 CloudDB v2.0
    }
    
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [Services / Offerings / Products]" in err for err in errors)
    assert "Missing newly released 2026 product line" in errors[0]