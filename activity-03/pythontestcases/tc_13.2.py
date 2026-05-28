import time
import pytest
from typing import Dict, Any, List

# Target Response Time SLAs (in seconds)
SLA_STARTUP_LIMIT_SEC = 15.0
SLA_ENTERPRISE_LIMIT_SEC = 45.0


def simulate_extraction_and_validation(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the pipeline extraction, reasoning, and validation of all 
    163 metadata parameters. The simulated processing time varies depending
    on company size, ownership nature, and overall data density.
    """
    # Baseline overhead representing parsing, regex checks, and schema validation
    processing_time = 2.0  
    
    category = record.get("Category", "Startup")
    nature = record.get("Nature of Company", "Private")
    
    # Model higher data density scaling factors
    if category == "Enterprise":
        processing_time += 15.0  # Simulated parsing of dense financial reports, GICS, and ESG sheets
    if nature == "Public":
        processing_time += 10.0  # Simulated query latencies for SEC registries and global office validation
    if category == "Conglomerate":
        processing_time += 8.0   # Handling complex subsidiaries and multi-market presence
        
    # Introduce the simulated processing sleep
    time.sleep(processing_time)
    
    # Return processed record with execution statistics
    record["generation_time_sec"] = processing_time
    record["status"] = "PROCESSED"
    return record


# --- Pytest Performance Suite ---

def test_startup_generation_response_time():
    """
    Validates that a typical private startup profile with sparse public data 
    is compiled and validated well within the fast SLA threshold of 15 seconds.
    """
    startup_payload = {
        "Company Name": "Acme SaaS",
        "Category": "Startup",
        "Nature of Company": "Private"
    }
    
    start_time = time.perf_counter()
    result = simulate_extraction_and_validation(startup_payload)
    end_time = time.perf_counter()
    
    elapsed_time = end_time - start_time
    
    # Assert execution met the expected startup performance SLA
    assert elapsed_time <= SLA_STARTUP_LIMIT_SEC, (
        f"Performance SLA Violated: Startup processing took {elapsed_time:.2f}s, "
        f"exceeding the limit of {SLA_STARTUP_LIMIT_SEC}s."
    )
    assert result["status"] == "PROCESSED"


def test_fortune_500_enterprise_generation_response_time():
    """
    Validates that a highly complex, public Fortune 500 company profile with dense 
    disclosures is compiled and validated within the maximum SLA threshold of 45 seconds.
    """
    enterprise_payload = {
        "Company Name": "Microsoft Corporation",
        "Category": "Enterprise",
        "Nature of Company": "Public"
    }
    
    start_time = time.perf_counter()
    result = simulate_extraction_and_validation(enterprise_payload)
    end_time = time.perf_counter()
    
    elapsed_time = end_time - start_time
    
    # Assert execution met the expected enterprise performance SLA
    assert elapsed_time <= SLA_ENTERPRISE_LIMIT_SEC, (
        f"Performance SLA Violated: Enterprise processing took {elapsed_time:.2f}s, "
        f"exceeding the limit of {SLA_ENTERPRISE_LIMIT_SEC}s."
    )
    assert result["status"] == "PROCESSED"


def test_public_vs_private_latency_scaling():
    """
    Compares processing speed differences between public and private company profiles.
    Asserts that the system scales efficiently, showing proportional processing 
    speeds relative to data density.
    """
    private_payload = {
        "Company Name": "Alpha Robotics",
        "Category": "Startup",
        "Nature of Company": "Private"
    }
    
    public_payload = {
        "Company Name": "Tesla Inc.",
        "Category": "Enterprise",
        "Nature of Company": "Public"
    }
    
    # Measure Private
    t_start_private = time.perf_counter()
    res_private = simulate_extraction_and_validation(private_payload)
    t_end_private = time.perf_counter()
    private_duration = t_end_private - t_start_private
    
    # Measure Public
    t_start_public = time.perf_counter()
    res_public = simulate_extraction_and_validation(public_payload)
    t_end_public = time.perf_counter()
    public_duration = t_end_public - t_start_public
    
    # Private startup must be faster than public enterprise due to data scale differences
    assert private_duration < public_duration, (
        f"Abnormal Latency Profile: Private startup processing ({private_duration:.2f}s) "
        f"was not faster than public enterprise processing ({public_duration:.2f}s)."
    )
    
    # Confirm both still respect their individual outer boundaries
    assert private_duration <= SLA_STARTUP_LIMIT_SEC
    assert public_duration <= SLA_ENTERPRISE_LIMIT_SEC