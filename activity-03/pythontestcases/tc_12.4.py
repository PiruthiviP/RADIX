import re
import pytest
from typing import Dict, Any, Union

# Brand Sentiment Regex Match: ^(Positive|Neutral|Negative)$|^\d{1,3}$
BRAND_SENTIMENT_REGEX = re.compile(r"^(Positive|Neutral|Negative)$|^\d{1,3}$")

# Glassdoor Rating Regex Match: ^[1-5](\.\d)?$
GLASSDOOR_REGEX = re.compile(r"^[1-5](\.\d)?$")

# Net Promoter Score (NPS) Regex Match: ^-?(100|[1-9]\d?|0)$
NPS_REGEX = re.compile(r"^-?(100|[1-9]\d?|0)$")


def validate_sentiment_metrics(record: Dict[str, Any]) -> bool:
    """
    Validates structural patterns and boundary ranges of brand sentiment, 
    Glassdoor employee scores, and Net Promoter Score (NPS).
    """
    brand_sentiment = record.get("Brand Sentiment Score")
    glassdoor_rating = record.get("Glassdoor Rating")
    nps = record.get("Net Promoter Score (NPS)")
    burnout_risk = record.get("Burnout risk")
    
    # 1. Validate Brand Sentiment Score (Nullable)
    if brand_sentiment is not None:
        val_str = str(brand_sentiment).strip()
        if not BRAND_SENTIMENT_REGEX.match(val_str):
            raise ValueError(
                f"Format Error: Brand Sentiment '{brand_sentiment}' must be "
                f"'Positive', 'Neutral', 'Negative' or an index (0-100)."
            )
            
        # If numeric index, enforce the standard 0-100 range constraints
        if val_str.isdigit():
            index_val = int(val_str)
            if not (0 <= index_val <= 100):
                raise ValueError(f"Boundary Error: Brand Sentiment Index '{index_val}' must be between 0 and 100.")
                
    # 2. Validate Glassdoor Rating (Nullable)
    if glassdoor_rating is not None:
        rating_str = str(glassdoor_rating).strip()
        if not GLASSDOOR_REGEX.match(rating_str):
            raise ValueError(
                f"Format Error: Glassdoor Rating '{glassdoor_rating}' "
                f"must match decimal format between 1.0 and 5.0."
            )
        rating_val = float(rating_str)
        if not (1.0 <= rating_val <= 5.0):
            raise ValueError(f"Boundary Error: Glassdoor Rating '{rating_val}' must be between 1.0 and 5.0.")

    # 3. Validate Net Promoter Score (NPS) (Nullable)
    if nps is not None:
        nps_str = str(nps).strip()
        if not NPS_REGEX.match(nps_str):
            raise ValueError(f"Format Error: NPS '{nps}' must be an integer between -100 and 100.")
            
        nps_val = int(nps_str)
        if not (-100 <= nps_val <= 100):
            raise ValueError(f"Boundary Error: Net Promoter Score '{nps_val}' must be between -100 and 100.")

    # 4. Logical Relational Checks (e.g. Glassdoor vs. Burnout Risk Alignment)
    if glassdoor_rating is not None and burnout_risk:
        rating_val = float(str(glassdoor_rating).strip())
        if rating_val >= 4.5 and str(burnout_risk).strip().title() == "Severe":
            raise ValueError(
                f"Relational Error: High Glassdoor Rating of {rating_val} "
                f"contradicts a 'Severe' Burnout Risk level."
            )

    return True


# --- Pytest Suite ---

def test_valid_categorical_brand_sentiment_success():
    """
    Validates standard categorical brand sentiment representation.
    """
    record = {
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "4.2",
        "Net Promoter Score (NPS)": "75"
    }
    assert validate_sentiment_metrics(record) is True


def test_valid_numeric_brand_sentiment_success():
    """
    Validates numeric index brand sentiment representation.
    """
    record = {
        "Brand Sentiment Score": "82",
        "Glassdoor Rating": "3.8",
        "Net Promoter Score (NPS)": "45"
    }
    assert validate_sentiment_metrics(record) is True


def test_negative_nps_boundary_success():
    """
    Ensures negative NPS boundaries are accepted when within range limits.
    """
    record = {
        "Brand Sentiment Score": "Negative",
        "Glassdoor Rating": "2.5",
        "Net Promoter Score (NPS)": "-40"
    }
    assert validate_sentiment_metrics(record) is True


def test_invalid_brand_sentiment_adjective_fails():
    """
    Ensures invalid adjectives outside 'Positive'/'Neutral'/'Negative' fail.
    """
    record = {
        "Brand Sentiment Score": "Excellent",  # Non-standard term
        "Glassdoor Rating": "4.2"
    }
    with pytest.raises(ValueError, match="must be 'Positive', 'Neutral', 'Negative' or an index"):
        validate_sentiment_metrics(record)


def test_out_of_bound_brand_sentiment_index_fails():
    """
    Flags numerical indexes that exceed 100.
    """
    record = {
        "Brand Sentiment Score": "125",  # Over max index value of 100
        "Glassdoor Rating": "4.2"
    }
    with pytest.raises(ValueError, match="Brand Sentiment Index '125' must be between 0 and 100"):
        validate_sentiment_metrics(record)


def test_out_of_bound_glassdoor_rating_fails():
    """
    Flags Glassdoor ratings that violate the standard 1.0 - 5.0 range.
    """
    record = {
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "5.5"  # Over maximum rating of 5.0
    }
    with pytest.raises(ValueError, match="must match decimal format between 1.0 and 5.0"):
        validate_sentiment_metrics(record)


def test_out_of_bound_nps_fails():
    """
    Flags NPS records that exceed 100 or fall below -100.
    """
    record = {
        "Brand Sentiment Score": "Positive",
        "Net Promoter Score (NPS)": "150"  # Exceeds max NPS of 100
    }
    with pytest.raises(ValueError, match="must be an integer between -100 and 100"):
        validate_sentiment_metrics(record)


def test_contradictory_glassdoor_and_burnout_metrics_fails():
    """
    Flags relational anomalies between high employer score and severe burnout risk.
    """
    record = {
        "Company Name": "FutureTech",
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "4.8",
        "Burnout risk": "Severe"  # High contradiction
    }
    with pytest.raises(ValueError, match="contradicts a 'Severe' Burnout Risk level"):
        validate_sentiment_metrics(record)