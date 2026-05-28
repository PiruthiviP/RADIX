import datetime
import pytest
from typing import Dict, Any, List, Tuple

# Allowed source mappings as defined by the metadata schema
ALLOWED_SOURCES_BY_FIELD = {
    "Company Name": ["Company Registry", "SEC Filings", "Government Database"],
    "Logo": ["Official Website", "LinkedIn"],
    "Employee Size": ["LinkedIn", "HR Tools", "Crunchbase"],
    "Annual Revenues": ["SEC Filings", "Annual Reports", "Company Registry"],
    "Website URL": ["Official Registry", "Company Registry"],
    "Recent News": ["PR Newswire", "Crunchbase", "Official Press Releases"]
}

# Simple list of blacklisted non-credible domains to simulate credibility filtering
CREDIBILITY_BLACKLIST = ["random-blog.com", "leakforums.net", "wikipedia.org", "blogspot.com"]

def validate_lineage_attribution(record_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates the source attribution and lineage of the company record.
    - Checks that every populated field in ALLOWED_SOURCES_BY_FIELD has a source block.
    - Ensures the source_type matches allowed origins.
    - Confirms the source_url does not resolve to a blacklisted non-credible domain.
    - Verifies the extraction timestamp is not in the future and is reasonably fresh.
    """
    errors = []
    current_date = datetime.date(2026, 5, 22)
    min_acceptable_date = current_date - datetime.timedelta(days=365) # max 1 year old source

    for field_name, allowed_origins in ALLOWED_SOURCES_BY_FIELD.items():
        field_value = record_payload.get(field_name)
        
        # We only validate attribution if the field itself is populated
        if field_value is not None:
            attribution = record_payload.get(f"_attribution_{field_name}")
            
            if not attribution:
                errors.append(f"Lineage Error: Field '{field_name}' is populated but lacks an '_attribution_{field_name}' block.")
                continue
                
            source_type = attribution.get("source_type")
            source_url = attribution.get("source_url", "")
            timestamp_str = attribution.get("timestamp", "")
            
            # Check 1: Verify source type credibility mapping
            if source_type not in allowed_origins:
                errors.append(f"Credibility Error: Field '{field_name}' cites source '{source_type}'. Allowed sources are: {allowed_origins}.")
                
            # Check 2: Verify domain blacklist
            if any(blacklisted in source_url.lower() for blacklisted in CREDIBILITY_BLACKLIST):
                errors.append(f"Credibility Error: Field '{field_name}' cites a blacklisted untrusted domain: '{source_url}'.")
                
            # Check 3: Verify timestamp validity
            try:
                source_date = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d").date()
                if source_date > current_date:
                    errors.append(f"Temporal Lineage Error: Field '{field_name}' has a future source timestamp: '{timestamp_str}'.")
                elif source_date < min_acceptable_date:
                    errors.append(f"Temporal Lineage Error: Field '{field_name}' has an expired source timestamp: '{timestamp_str}' (older than {min_acceptable_date}).")
            except ValueError:
                errors.append(f"Lineage Format Error: Field '{field_name}' has an invalid timestamp format '{timestamp_str}'. Use YYYY-MM-DD.")
                
    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_valid_lineage_profile_passes():
    """Verifies that a fully traceable, credible profile record passes validation."""
    valid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "timestamp": "2026-04-15"
        },
        "Logo": "https://logo.com/ms",
        "_attribution_Logo": {
            "source_type": "LinkedIn",
            "source_url": "https://www.linkedin.com/company/microsoft",
            "timestamp": "2026-05-10"
        },
        "Annual Revenues": "$245B",
        "_attribution_Annual Revenues": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "timestamp": "2026-04-15"
        }
    }
    
    success, errors = validate_lineage_attribution(valid_record)
    assert success is True
    assert not errors

def test_missing_attribution_block_fails():
    """Verifies that populating a field without providing its source attribution fails validation."""
    invalid_record = {
        "Company Name": "Microsoft Corporation"
        # Missing '_attribution_Company Name' block
    }
    
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("lacks an '_attribution_Company Name' block" in err for err in errors)

def test_untrusted_blacklisted_source_fails():
    """Verifies that citing a blacklisted or non-credible domain for a metric fails validation."""
    invalid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://random-blog.com/leak/microsoft-details",  # Blacklisted domain
            "timestamp": "2026-04-15"
        }
    }
    
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("blacklisted untrusted domain" in err for err in errors)

def test_unpermitted_source_type_fails():
    """Verifies that using an unpermitted source type for a specific parameter fails validation."""
    invalid_record = {
        "Annual Revenues": "$245B",
        "_attribution_Annual Revenues": {
            "source_type": "LinkedIn",  # Not a permitted source type for financial metrics
            "source_url": "https://www.linkedin.com/company/microsoft",
            "timestamp": "2026-04-15"
        }
    }
    
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Allowed sources are" in err for err in errors)

def test_future_attribution_timestamp_fails():
    """Verifies that an attribution timestamp set in the future is caught and rejected."""
    invalid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar",
            "timestamp": "2027-10-12"  # Future date relative to May 22, 2026
        }
    }
    
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("future source timestamp" in err for err in errors)