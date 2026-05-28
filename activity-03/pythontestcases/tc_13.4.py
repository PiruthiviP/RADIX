import re
import pytest
from typing import List, Dict, Any, Set

# Standard dictionary terms and generic English stop words to exclude from signature checks
COMMON_STOP_WORDS = {
    "and", "the", "for", "with", "from", "company", "inc", "corp", "llc", "global", 
    "technologies", "services", "solutions", "limited", "incorporated", "private", 
    "public", "systems", "group", "co", "management", "industries", "partner"
}


def extract_unique_signatures(record: Dict[str, Any]) -> Set[str]:
    """
    Extracts highly specific, lowercase alphanumeric word tokens from a record.
    These tokens serve as the 'data footprint' of the company to detect context leaks.
    """
    signatures: Set[str] = set()
    
    # Target fields that hold highly entity-specific data
    target_fields = [
        "Company Name", "Short Name", "Website URL", "CEO Name", 
        "Company Headquarters", "Key Investors / Backers"
    ]
    
    for field in target_fields:
        val = record.get(field)
        if val:
            # Tokenize and clean the text values
            words = re.findall(r"\b[a-zA-Z]{3,20}\b", str(val).lower())
            for word in words:
                if word not in COMMON_STOP_WORDS:
                    signatures.add(word)
                    
    return signatures


def detect_memory_contamination(company_a: Dict[str, Any], company_b: Dict[str, Any]) -> None:
    """
    Asserts that no highly unique signature tokens from Company A's profile 
    exist in Company B's profile, validating clean memory isolation.
    """
    signatures_a = extract_unique_signatures(company_a)
    
    # Concatenate all values of Company B to search for leakages
    all_b_text = " ".join([str(v) for v in company_b.values() if v is not None]).lower()
    
    # Check for leaks
    leaked_tokens = []
    for token in signatures_a:
        # Enforce boundary checking so standard substrings aren't flagged as leaks
        pattern = re.compile(rf"\b{token}\b")
        if pattern.search(all_b_text):
            leaked_tokens.append(token)
            
    if leaked_tokens:
        raise ValueError(
            f"Memory Contamination Leak Detected: Unique tokens {leaked_tokens} from "
            f"'{company_a.get('Company Name')}' leaked into the record of "
            f"'{company_b.get('Company Name')}'."
        )


# --- Pytest Isolation Suite ---

def test_sequential_requests_perfect_isolation_success():
    """
    Validates that two highly distinct sequential requests preserve 
    complete context isolation and do not trigger leak detection.
    """
    # Record A generated in step 1
    company_a = {
        "Company Name": "Space Exploration Technologies Corp.",
        "Short Name": "SpaceX",
        "Website URL": "https://www.spacex.com",
        "CEO Name": "Elon Musk",
        "Company Headquarters": "Hawthorne, California",
        "Key Investors / Backers": "Founders Fund, Fidelity"
    }
    
    # Record B generated in step 2
    company_b = {
        "Company Name": "Blue Origin LLC",
        "Short Name": "Blue Origin",
        "Website URL": "https://www.blueorigin.com",
        "CEO Name": "Jeff Bezos",
        "Company Headquarters": "Kent, Washington",
        "Key Investors / Backers": "Bezos Expeditions"
    }
    
    # Ensure no variables cross-bleed
    detect_memory_contamination(company_a, company_b)


def test_sequential_requests_contamination_failure():
    """
    Asserts that the memory leak detector successfully catches and flags 
    cross-contamination if a preceding company's attributes bleed into the next record.
    """
    company_a = {
        "Company Name": "Space Exploration Technologies Corp.",
        "Short Name": "SpaceX",
        "Website URL": "https://www.spacex.com",
        "CEO Name": "Elon Musk",
        "Company Headquarters": "Hawthorne, California",
        "Key Investors / Backers": "Founders Fund, Fidelity"
    }
    
    # Faulty Record B which has context leakage from Record A (Elon Musk, SpaceX URL)
    contaminated_company_b = {
        "Company Name": "Blue Origin LLC",
        "Short Name": "Blue Origin",
        "Website URL": "https://www.spacex.com",  # Leaked domain
        "CEO Name": "Elon Musk",                 # Leaked CEO
        "Company Headquarters": "Kent, Washington",
        "Key Investors / Backers": "Bezos Expeditions"
    }
    
    # Expect the contamination check to raise a ValueError identifying the leak
    with pytest.raises(ValueError, match="Memory Contamination Leak Detected"):
        detect_memory_contamination(company_a, contaminated_company_b)


def test_batch_run_similar_companies_isolation():
    """
    Checks that highly similar automotive entities parsed concurrently 
    do not experience cross-contamination of their specific identifiers.
    """
    tesla = {
        "Company Name": "Tesla Inc.",
        "Short Name": "Tesla",
        "Website URL": "https://www.tesla.com",
        "CEO Name": "Elon Musk",
        "Company Headquarters": "Austin, Texas"
    }
    
    rivian = {
        "Company Name": "Rivian Automotive",
        "Short Name": "Rivian",
        "Website URL": "https://www.rivian.com",
        "CEO Name": "RJ Scaringe",
        "Company Headquarters": "Irvine, California"
    }
    
    # Validate mutual isolation
    detect_memory_contamination(tesla, rivian)
    detect_memory_contamination(rivian, tesla)