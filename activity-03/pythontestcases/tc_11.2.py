import pytest
from typing import Dict, Any, List, Tuple

# Mock Corporate Knowledge Base containing strict Parent/Subsidiary schemas
CORPORATE_RECORDS_DB = {
    "meta platforms, inc.": {
        "type": "Parent",
        "legal_name": "Meta Platforms, Inc.",
        "expected_nature": "Public",
        "verified_ceo": "Mark Zuckerberg",
        "verified_domain": "meta.com",
        "consolidated_revenue_min": 1e11 # $100B+
    },
    "instagram": {
        "type": "Subsidiary",
        "legal_name": "Instagram LLC",
        "expected_nature": "Subsidiary",
        "parent_key": "meta platforms, inc.",
        "verified_ceo": "Adam Mosseri",
        "verified_domain": "instagram.com",
        "standalone_revenue_max": 6e10 # Max $60B estimated
    }
}

def validate_parent_subsidiary_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a subsidiary's profile does not suffer from parent data-bleeding:
    - If the ingested company is a registered Subsidiary:
        1. Nature of Company must be "Subsidiary" (not "Public" or "Private" standalone).
        2. CEO Name must be the subsidiary's distinct head, not the parent's CEO.
        3. Website URL must point to the subsidiary's domain, not the parent's domain.
        4. Annual Revenues must not equal the parent's full consolidated group revenues.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip().lower()

    if company_name not in CORPORATE_RECORDS_DB:
        return True, [] # Skip if company structure is not modeled in registry
        
    truth = CORPORATE_RECORDS_DB[company_name]

    if truth["type"] == "Subsidiary":
        # 1. Validate Legal Nature
        nature = payload.get("Nature of Company")
        expected_nature = truth["expected_nature"]
        if nature != expected_nature:
            errors.append(
                f"Lineage Contradiction [Nature of Company]: Subsidiary '{payload.get('Company Name')}' "
                f"must be classified as '{expected_nature}' (Ingested: '{nature}')."
            )

        # 2. Prevent CEO Bleeding
        ingested_ceo = payload.get("CEO Name")
        expected_ceo = truth["verified_ceo"]
        parent_truth = CORPORATE_RECORDS_DB[truth["parent_key"]]
        parent_ceo = parent_truth["verified_ceo"]
        
        if ingested_ceo == parent_ceo:
            errors.append(
                f"Data Bleeding Error [CEO Name]: Ingested parent CEO '{parent_ceo}' "
                f"on subsidiary record '{payload.get('Company Name')}'. Expected subsidiary head: '{expected_ceo}'."
            )
        elif ingested_ceo != expected_ceo:
            errors.append(f"Factual Error [CEO Name]: Ingested '{ingested_ceo}', Expected '{expected_ceo}'.")

        # 3. Prevent Domain Bleeding
        ingested_url = str(payload.get("Website URL", "")).lower()
        expected_domain = truth["verified_domain"]
        parent_domain = parent_truth["verified_domain"]
        
        if parent_domain in ingested_url:
            errors.append(
                f"Data Bleeding Error [Website URL]: Ingested parent domain '{parent_domain}' "
                f"on subsidiary record. Expected subsidiary domain: '{expected_domain}'."
            )
        elif expected_domain not in ingested_url:
            errors.append(f"Factual Error [Website URL]: Expected domain '{expected_domain}' in URL.")

        # 4. Prevent Consolidated Revenue Bleeding
        raw_rev = payload.get("Annual Revenues")
        if raw_rev:
            # Parse simple decimal from string (e.g. "$134B" -> 134,000,000,000)
            clean_rev = str(raw_rev).replace("$", "").replace(",", "").strip().upper()
            multiplier = 1.0
            if clean_rev.endswith("B"):
                multiplier = 1e9
                clean_rev = clean_rev[:-1]
            elif clean_rev.endswith("M"):
                multiplier = 1e6
                clean_rev = clean_rev[:-1]
                
            try:
                ingested_rev = float(clean_rev) * multiplier
                parent_group_revenue = parent_truth["consolidated_revenue_min"]
                if ingested_rev >= parent_group_revenue:
                    errors.append(
                        f"Data Bleeding Error [Annual Revenues]: Ingested value '{raw_rev}' matches the "
                        f"parent group's consolidated revenues. Subsidiary revenues must represent its standalone estimate."
                    )
            except ValueError:
                pass

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_distinct_subsidiary_profile_passes():
    """Verifies that a subsidiary record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",  # Correct subsidiary head
        "Website URL": "https://www.instagram.com",  # Correct subsidiary domain
        "Annual Revenues": "$50B"  # Valid standalone estimate
    }
    success, errors = validate_parent_subsidiary_coherence(valid_payload)
    assert success is True
    assert not errors

def test_parent_ceo_bleeding_fails():
    """Verifies that assigning the parent holding company CEO to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Mark Zuckerberg",  # Parent CEO (Data bleeding)
        "Website URL": "https://www.instagram.com",
        "Annual Revenues": "$50B"
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [CEO Name]" in err for err in errors)
    assert "Mark Zuckerberg" in errors[0]

def test_parent_domain_bleeding_fails():
    """Verifies that assigning the parent domain URL to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",
        "Website URL": "https://www.meta.com/instagram",  # Parent domain (Data bleeding)
        "Annual Revenues": "$50B"
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Website URL]" in err for err in errors)
    assert "meta.com" in errors[0]

def test_parent_consolidated_revenue_bleeding_fails():
    """Verifies that assigning parent consolidated group revenues to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",
        "Website URL": "https://www.instagram.com",
        "Annual Revenues": "$134B"  # Parent consolidated revenue (Data bleeding)
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Annual Revenues]" in err for err in errors)