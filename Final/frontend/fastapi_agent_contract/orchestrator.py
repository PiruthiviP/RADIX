from typing import Dict, List

from schemas import (
    GenerateRequest,
    GeneratedOutput,
    GroundingInput,
    TOTAL_GENERATED_PARAMETERS,
    generated_key,
)
from rules import GROUNDING_FIELDS, SYSTEM_OBJECTIVE, check_grounding_completeness


def build_grounding_context(grounding: GroundingInput) -> str:
    payload = grounding.model_dump()
    lines = [f"- {field}: {payload[field]}" for field in GROUNDING_FIELDS]
    return "\n".join(lines)


def mock_llm_generate(index: int, grounding: GroundingInput) -> str:
    """
    Replace with your real LLM provider call.
    Keep this deterministic and short so admin can review/edit quickly.
    """
    patterns = [
        f"{grounding.companyName} profile signal {index}: category alignment with {grounding.categoryIndustry}.",
        f"{grounding.shortName} parameter {index}: operating footprint includes {grounding.countriesOperatingIn}.",
        f"Round-readiness note {index}: {grounding.natureOfCompany} hiring posture with size {grounding.employeeSize}.",
        f"Leadership-grounded note {index}: context references {grounding.ceoName} and HQ {grounding.companyHeadquarters}.",
        f"Offering-backed note {index}: {grounding.servicesProductsOfferings[:100]}.",
    ]
    return patterns[(index - 1) % len(patterns)]


def generate_163_parameters(grounding: GroundingInput) -> Dict[str, str]:
    return {generated_key(i): mock_llm_generate(i, grounding) for i in range(1, TOTAL_GENERATED_PARAMETERS + 1)}


def run_orchestration(request: GenerateRequest) -> GeneratedOutput:
    ok, missing = check_grounding_completeness(request.grounding)
    if not ok:
        raise ValueError(f"Grounding validation failed. Missing fields: {', '.join(missing)}")

    _ = SYSTEM_OBJECTIVE
    _ = build_grounding_context(request.grounding)

    generated = generate_163_parameters(request.grounding)

    return GeneratedOutput(
        generatedParameters=generated,
        coverageScore=1.0,
        warnings=[],
        usedGroundingFields=GROUNDING_FIELDS,
    )
