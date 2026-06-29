from typing import Dict, List, Tuple

from schemas import GroundingInput, generated_key_list


SYSTEM_OBJECTIVE = """
You are a company-intelligence orchestration agent for an admin workflow.
Primary objective: transform 13 grounding parameters into 163 editable, structured parameters.

Hard requirements:
1) Use all 13 grounding fields as first-class evidence.
2) Do not rely only on companyName.
3) If data is uncertain, return explicit placeholder text instead of fabrication.
4) Output must contain exactly parameter_001 ... parameter_163.
5) Keep outputs concise, admin-editable, and auditable.
""".strip()


GROUNDING_FIELDS = [
    "companyName",
    "shortName",
    "websiteUrl",
    "logo",
    "yearOfIncorporation",
    "companyHeadquarters",
    "countriesOperatingIn",
    "natureOfCompany",
    "categoryIndustry",
    "servicesProductsOfferings",
    "employeeSize",
    "ceoName",
    "linkedInProfileUrl",
]


def check_grounding_completeness(grounding: GroundingInput) -> Tuple[bool, List[str]]:
    missing = []
    payload = grounding.model_dump()
    for field in GROUNDING_FIELDS:
        value = str(payload.get(field, "")).strip()
        if not value:
            missing.append(field)
    return (len(missing) == 0, missing)


def ensure_exact_163(generated_parameters: Dict[str, str]) -> Tuple[List[str], List[str]]:
    expected = set(generated_key_list())
    provided = set(generated_parameters.keys())

    missing = sorted(list(expected - provided))
    extra = sorted(list(provided - expected))
    return missing, extra


def grounding_coverage_issues(grounding: GroundingInput, generated_parameters: Dict[str, str]) -> List[str]:
    """
    Lightweight heuristic to catch company-name-only behavior:
    - We expect signals from non-name fields to appear somewhere in output.
    """
    issues: List[str] = []
    joined = "\n".join(generated_parameters.values()).lower()

    probes = {
        "categoryIndustry": grounding.categoryIndustry.lower(),
        "natureOfCompany": grounding.natureOfCompany.lower(),
        "companyHeadquarters": grounding.companyHeadquarters.lower(),
        "employeeSize": grounding.employeeSize.lower(),
        "ceoName": grounding.ceoName.lower(),
    }

    for field, token in probes.items():
        if token and token not in joined:
            issues.append(
                f"Generated output shows weak coverage for '{field}'. Agent may be over-indexing on company name retrieval."
            )

    return issues
