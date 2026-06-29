from typing import Dict, List

from pydantic import BaseModel, Field, HttpUrl, field_validator


TOTAL_GENERATED_PARAMETERS = 163


def generated_key(index: int) -> str:
    return f"parameter_{index:03d}"


def generated_key_list() -> List[str]:
    return [generated_key(i) for i in range(1, TOTAL_GENERATED_PARAMETERS + 1)]


class GroundingInput(BaseModel):
    # The exact 13 fields used by your web app
    companyName: str = Field(min_length=1)
    shortName: str = Field(min_length=1)
    websiteUrl: HttpUrl
    logo: HttpUrl
    yearOfIncorporation: str = Field(min_length=4, max_length=4)
    companyHeadquarters: str = Field(min_length=1)
    countriesOperatingIn: str = Field(min_length=1)
    natureOfCompany: str = Field(min_length=1)
    categoryIndustry: str = Field(min_length=1)
    servicesProductsOfferings: str = Field(min_length=1)
    employeeSize: str = Field(min_length=1)
    ceoName: str = Field(min_length=1)
    linkedInProfileUrl: HttpUrl

    @field_validator("yearOfIncorporation")
    @classmethod
    def validate_year(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 4:
            raise ValueError("yearOfIncorporation must be a 4-digit year")
        return value


class GenerateRequest(BaseModel):
    grounding: GroundingInput
    # Optional run controls
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=1)


class GeneratedOutput(BaseModel):
    generatedParameters: Dict[str, str]
    coverageScore: float = Field(ge=0, le=1)
    warnings: List[str] = Field(default_factory=list)
    usedGroundingFields: List[str]


class ValidateRequest(BaseModel):
    grounding: GroundingInput
    generatedParameters: Dict[str, str]


class ValidateResponse(BaseModel):
    valid: bool
    missingKeys: List[str]
    emptyKeys: List[str]
    groundingCoverageIssues: List[str]
    message: str
