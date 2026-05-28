import json
import pytest
from typing import Dict, Any, List, Tuple

# Schema Type Map representing key representative fields from the metadata parameter registry
SCHEMA_TYPE_REGISTRY = {
    "Company Name": str,
    "Year of Incorporation": int,
    "Overview of the Company": str,
    "Number of Offices (beyond HQ)": int,
    "Website Rating": float,
    "Glassdoor Rating": float,
    "Social Media Followers – Combined": int,
    "CEO Name": str,
    "Key Business Leaders": list, # Expected parsed JSON array
    "Annual Profits": float,
    "Profitability Status": str
}

def validate_record_data_types(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs holistic, record-level structural type checks.
    - Validates that populated fields match their exact schema-defined Python types.
    - Gracefully handles nullable fields (allows None without throwing type errors).
    - Specifically validates JSON array parsing for 'Key Business Leaders'.
    """
    errors = []

    for field_name, expected_type in SCHEMA_TYPE_REGISTRY.items():
        val = payload.get(field_name)
        
        # Safe skip for optional Nullable parameters set to None
        if val is None:
            continue
            
        # Special case: Key Business Leaders (expects list or valid JSON string parsing to list)
        if field_name == "Key Business Leaders":
            if isinstance(val, str):
                try:
                    parsed_json = json.loads(val)
                    if not isinstance(parsed_json, list):
                        errors.append(f"Type Error: '{field_name}' parsed from JSON string but is not a LIST structure.")
                except json.JSONDecodeError:
                    errors.append(f"JSON Parse Error: '{field_name}' contains invalid JSON formatting.")
            elif not isinstance(val, list):
                errors.append(f"Type Error: Field '{field_name}' must be of type LIST (JSON Array), got {type(val).__name__}.")
            continue

        # General type checking for atomic fields
        if not isinstance(val, expected_type):
            # Attempt safe float/int coercion for numeric types if passed as strings (standard DB practice)
            coerced = False
            if expected_type in (int, float) and isinstance(val, str):
                try:
                    if expected_type == int:
                        int(val)
                    else:
                        float(val)
                    coerced = True
                except ValueError:
                    pass
            
            if not coerced:
                errors.append(
                    f"Type Error: Field '{field_name}' must be of type {expected_type.__name__}, "
                    f"but got {type(val).__name__} (Value: '{val}')."
                )

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_fully_typed_valid_record_passes():
    """Verifies that a record with 100% correct type mappings passes validation successfully."""
    valid_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "Overview of the Company": "Global technology giant.",
        "Number of Offices (beyond HQ)": 120,
        "Website Rating": 9.5,
        "Glassdoor Rating": 4.3,
        "Social Media Followers – Combined": 15000000,
        "CEO Name": "Satya Nadella",
        "Key Business Leaders": [
            {"name": "Amy Hood", "title": "CFO"},
            {"name": "Brad Smith", "title": "President"}
        ],
        "Annual Profits": 72000000000.0,
        "Profitability Status": "Profitable"
    }
    success, errors = validate_record_data_types(valid_payload)
    assert success is True
    assert not errors

def test_record_with_string_representing_numbers_passes_coercion():
    """Verifies that numbers passed as clean numeric strings are successfully coerced and pass."""
    coercible_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": "1975",  # String representing integer
        "Website Rating": "9.5"          # String representing float
    }
    success, errors = validate_record_data_types(coercible_payload)
    assert success is True
    assert not errors

def test_record_with_type_violation_fails():
    """Verifies that passing alphabetical characters to an integer year field fails type validation."""
    invalid_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": "Nineteen-Seventy-Five"  # Explicit type violation (cannot coerce to int)
    }
    success, errors = validate_record_data_types(invalid_payload)
    
    assert success is False
    assert any("must be of type int" in err for err in errors)

def test_record_with_malformed_json_fails():
    """Verifies that passing a flat unformatted text string to a JSON array field fails type validation."""
    invalid_payload = {
        "Company Name": "Microsoft Corporation",
        "Key Business Leaders": "Amy Hood - CFO, Brad Smith - President"  # Flat text instead of valid JSON array
    }
    success, errors = validate_record_data_types(invalid_payload)
    
    assert success is False
    assert any("JSON Parse Error" in err for err in errors)