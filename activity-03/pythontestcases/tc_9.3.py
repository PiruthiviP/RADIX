import pytest
from typing import List, Dict, Any

def validate_batch_isolation(records: List[Dict[str, Any]]) -> bool:
    """
    Validates that sequential or batched records of highly similar entities 
    do not suffer from cross-contamination, context confusion, or data leakage.
    
    Args:
        records (List[Dict[str, Any]]): A list of processed company records containing metadata.
        
    Raises:
        ValueError: If duplicate fields or context-bleeding attributes are discovered.
    """
    seen_domains = set()
    
    for i, record in enumerate(records):
        # Basic constraints validation based on metadata rules
        company_name = record.get("Company Name")
        website_url = record.get("Website URL")
        
        if not company_name or not website_url:
            raise ValueError("Incomplete record: Missing required identifying fields.")
            
        # 1. Ensure absolute uniqueness of primary web domains within a batch
        if website_url in seen_domains:
            raise ValueError(
                f"Context Confusion Detected: Duplicate Website URL '{website_url}' "
                f"found across distinct records. Possible context leakage."
            )
        seen_domains.add(website_url)
        
        # 2. Check for attribute bleeding between sequentially similar company names
        if i > 0:
            prev_record = records[i - 1]
            prev_name = prev_record.get("Company Name", "")
            
            # Determine if the names are similar (sharing the first token, e.g., 'Apple' or 'Delta')
            current_first_token = company_name.split()[0].lower()
            prev_first_token = prev_name.split()[0].lower()
            
            if current_first_token == prev_first_token and company_name != prev_name:
                # Fields that must remain completely distinct for different entities
                distinct_fields = [
                    "Website URL", 
                    "Overview of the Company", 
                    "CEO Name", 
                    "Focus Sectors / Industries"
                ]
                
                for field in distinct_fields:
                    current_val = record.get(field)
                    prev_val = prev_record.get(field)
                    
                    if current_val and prev_val:
                        # Clean and compare fields for absolute matches (indicating context bleed)
                        if str(current_val).strip().lower() == str(prev_val).strip().lower():
                            raise ValueError(
                                f"Context Bleed Warning: Attribute '{field}' is identical between similar sequential entities "
                                f"'{prev_name}' and '{company_name}'. Values: '{current_val}'."
                            )
                            
    return True

# --- Pytest Test Cases ---

def test_sequential_names_isolated_success():
    """
    Verifies that distinct companies with similar names (e.g., Apple Inc. & Apple Bank)
    are successfully processed when metadata is correctly isolated.
    """
    test_data = [
        {
            "Company Name": "Apple Inc.",
            "Short Name": "Apple",
            "Website URL": "https://www.apple.com",
            "CEO Name": "Tim Cook",
            "Focus Sectors / Industries": "Consumer Electronics, Technology",
            "Overview of the Company": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, and wearables."
        },
        {
            "Company Name": "Apple Bank",
            "Short Name": "Apple Bank",
            "Website URL": "https://www.applebank.com",
            "CEO Name": "Steven C. Schuster",
            "Focus Sectors / Industries": "Banking, Financial Services",
            "Overview of the Company": "Apple Bank provides commercial and individual retail banking services."
        }
    ]
    
    assert validate_batch_isolation(test_data) is True


def test_batch_homonymous_entities_success():
    """
    Verifies that multiple 'Delta' entities are successfully isolated when no data leaks occur.
    """
    test_data = [
        {
            "Company Name": "Delta Air Lines",
            "Website URL": "https://www.delta.com",
            "CEO Name": "Ed Bastian",
            "Focus Sectors / Industries": "Airlines, Transportation",
            "Overview of the Company": "Delta Air Lines, Inc. provides scheduled air transportation for passengers and cargo."
        },
        {
            "Company Name": "Delta Faucet Company",
            "Website URL": "https://www.deltafaucet.com",
            "CEO Name": "Ken Roberts",
            "Focus Sectors / Industries": "Manufacturing, Consumer Goods",
            "Overview of the Company": "Delta Faucet Company is a manufacturer of residential and commercial kitchen and bath faucets."
        }
    ]
    
    assert validate_batch_isolation(test_data) is True


def test_context_confusion_duplicate_url_failure():
    """
    Verifies that the validator flags an error if a similar sequential company
    leaks the previous company's URL.
    """
    faulty_data = [
        {
            "Company Name": "Delta Air Lines",
            "Website URL": "https://www.delta.com",
            "CEO Name": "Ed Bastian"
        },
        {
            "Company Name": "Delta Faucet Company",
            "Website URL": "https://www.delta.com",  # Leaked/duplicate URL
            "CEO Name": "Ken Roberts"
        }
    ]
    
    with pytest.raises(ValueError, match="Context Confusion Detected: Duplicate Website URL"):
        validate_batch_isolation(faulty_data)


def test_context_confusion_ceo_bleed_failure():
    """
    Verifies that the validator flags an error if key unique parameters like
    CEO Name bleed between two highly similar consecutive entries.
    """
    faulty_data = [
        {
            "Company Name": "Apple Inc.",
            "Website URL": "https://www.apple.com",
            "CEO Name": "Tim Cook",
            "Focus Sectors / Industries": "Consumer Electronics"
        },
        {
            "Company Name": "Apple Bank",
            "Website URL": "https://www.applebank.com",
            "CEO Name": "Tim Cook",  # Bleed error: Apple Inc.'s CEO assigned to Apple Bank
            "Focus Sectors / Industries": "Banking"
        }
    ]
    
    with pytest.raises(ValueError, match="Context Bleed Warning: Attribute 'CEO Name' is identical"):
        validate_batch_isolation(faulty_data)