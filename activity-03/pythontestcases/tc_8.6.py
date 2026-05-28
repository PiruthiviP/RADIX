import pytest
from typing import Dict, Any, Tuple

# Schema Length limits parsed directly from metadata setting boundaries
# Key: (min_characters, max_characters)
SCHEMA_LENGTH_REGISTRY = {
    "Company Name": (2, 255),
    "Short Name": (2, 100),
    "Overview of the Company": (50, 5000),
    "Core Value Proposition": (20, 2000),
    "Vision": (10, 500),
    "CEO Name": (2, 100)
}

def validate_text_length(field_name: str, value: Any) -> Tuple[bool, str]:
    """
    Validates that a string's character length strictly falls within
    the defined [min_len, max_len] boundaries.
    """
    bounds = SCHEMA_LENGTH_REGISTRY.get(field_name)
    if not bounds:
        raise ValueError(f"No length boundaries registered for field '{field_name}'.")

    if value is None:
        return False, f"Null Error: Field '{field_name}' cannot be NULL."
        
    if not isinstance(value, str):
        return False, f"Type Error: Field '{field_name}' must be of type STRING (got {type(value).__name__})."

    val_len = len(value)
    min_len, max_len = bounds

    if val_len < min_len:
        return False, f"Length Error: Field '{field_name}' must be at least {min_len} characters (got {val_len})."
        
    if val_len > max_len:
        return False, f"Length Error: Field '{field_name}' cannot exceed {max_len} characters (got {val_len})."

    return True, "Length validation successful."


# --- Pytest Tests ---

@pytest.mark.parametrize("field_name, valid_input", [
    ("Company Name", "Microsoft Corporation"),
    ("Short Name", "Apple"),
    ("Overview of the Company", "A" * 250),
    ("Core Value Proposition", "A" * 150),
    ("Vision", "To empower everyone on the planet."),
    ("CEO Name", "Tim Cook")
])
def test_valid_text_lengths(field_name, valid_input):
    """Verifies that strings falling within normal character boundaries pass validation."""
    success, msg = validate_text_length(field_name, valid_input)
    assert success is True
    assert "successful" in msg

@pytest.mark.parametrize("field_name, short_input", [
    ("Company Name", "A"),                    # Below 2 min limit
    ("Short Name", "A"),                      # Below 2 min limit
    ("Overview of the Company", "A" * 49),    # Below 50 min limit
    ("Core Value Proposition", "A" * 19),     # Below 20 min limit
    ("Vision", "To do"),                      # Below 10 min limit
    ("CEO Name", "A")                         # Below 2 min limit
])
def test_insufficient_text_lengths_rejected(field_name, short_input):
    """Verifies that strings below the minimum character limit fail validation."""
    success, msg = validate_text_length(field_name, short_input)
    assert success is False
    assert "at least" in msg

@pytest.mark.parametrize("field_name, bloated_input", [
    ("Company Name", "A" * 256),             # Exceeds 255 max
    ("Short Name", "A" * 101),               # Exceeds 100 max
    ("Overview of the Company", "A" * 5001), # Exceeds 5000 max
    ("Core Value Proposition", "A" * 2001),  # Exceeds 2000 max
    ("Vision", "A" * 501),                   # Exceeds 500 max
    ("CEO Name", "A" * 101)                  # Exceeds 100 max
])
def test_excessive_text_lengths_rejected(field_name, bloated_input):
    """Verifies that strings exceeding the maximum character limit fail validation."""
    success, msg = validate_text_length(field_name, bloated_input)
    assert success is False
    assert "cannot exceed" in msg

def test_non_string_input_rejected():
    """Verifies that type mismatch checks fail type boundaries before assessing character length."""
    success, msg = validate_text_length("Company Name", 12345)
    assert success is False
    assert "must be of type STRING" in msg