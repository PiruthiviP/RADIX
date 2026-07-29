from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# 1. Basic Workflow Schemas
class WorkflowRequest(BaseModel):
    company_name: str = Field(..., description="Name of the company to query")
    question: str = Field(default="Provide a high-level summary of the company.", description="Specific query or instructions")
    temperature: float = Field(default=0.2, description="LLM sampling temperature")

class ProviderResult(BaseModel):
    provider: str
    model: str
    content: str
    error: Optional[str] = None
    confidence: float = 0.0

class WorkflowResponse(BaseModel):
    company_name: str
    final_answer: str
    winner_provider: str
    provider_results: List[ProviderResult]

class HealthResponse(BaseModel):
    status: str
    providers_available: List[str]

# 2. Company Intelligence Workflow Schemas
class CompanyIntelligenceRequest(BaseModel):
    # 13 Admin grounding fields
    companyName: Optional[Any] = Field(default=None, description="Full legal name of company")
    shortName: Optional[Any] = Field(default=None, description="Common abbreviated name")
    websiteUrl: Optional[Any] = Field(default=None, description="Company homepage URL")
    logo: Optional[Any] = Field(default=None, description="Logo URL")
    yearOfIncorporation: Optional[Any] = Field(default=None, description="Year of incorporation")
    companyHeadquarters: Optional[Any] = Field(default=None, description="HQ address")
    countriesOperatingIn: Optional[Any] = Field(default=None, description="List/string of countries operating in")
    natureOfCompany: Optional[Any] = Field(default=None, description="Nature/legal ownership category")
    categoryIndustry: Optional[Any] = Field(default=None, description="Primary business sector/category")
    servicesProductsOfferings: Optional[Any] = Field(default=None, description="Primary services/products offered")
    employeeSize: Optional[Any] = Field(default=None, description="FTE headcount range or number")
    ceoName: Optional[Any] = Field(default=None, description="Current Chief Executive Officer name")
    linkedInProfileUrl: Optional[Any] = Field(default=None, description="LinkedIn company page profile link")

    # Config overrides
    temperature: float = Field(default=0.2, description="Sampling temperature override")
    maxRetryRounds: int = Field(default=2, description="Max local verification retry loops")
    strictGroundingRegeneration: bool = Field(default=False, description="Whether to validate grounding of admin fields first")

    def admin_payload(self) -> Dict[str, Any]:
        """Returns a dictionary of the 13 input fields only."""
        return {
            "companyName": self.companyName,
            "shortName": self.shortName,
            "websiteUrl": self.websiteUrl,
            "logo": self.logo,
            "yearOfIncorporation": self.yearOfIncorporation,
            "companyHeadquarters": self.companyHeadquarters,
            "countriesOperatingIn": self.countriesOperatingIn,
            "natureOfCompany": self.natureOfCompany,
            "categoryIndustry": self.categoryIndustry,
            "servicesProductsOfferings": self.servicesProductsOfferings,
            "employeeSize": self.employeeSize,
            "ceoName": self.ceoName,
            "linkedInProfileUrl": self.linkedInProfileUrl
        }

class ProviderDatasetStatus(BaseModel):
    accepted_fields: int
    failed_fields: int
    retries_used: int
    status_message: str

class CompanyIntelligenceResponse(BaseModel):
    company_id: Optional[str] = None
    company_name: str
    generation_timestamp: Optional[str] = None
    generation_status: str
    total_fields: int
    grounded_fields: int
    generated_fields: int
    profile_json: Dict[str, Any]
    provider_stats: Dict[str, ProviderDatasetStatus]

# 3. Running Agent Status Schemas
class AgentRunStatus(BaseModel):
    run_id: str
    company_name: str
    stage: str
    progress_percent: float
    started_at: str
    completed_at: Optional[str] = None
    elapsed_seconds: float
    duration_ms: Optional[int] = None
    generation_status: Optional[str] = None
    error: Optional[str] = None

class AgentStatusResponse(BaseModel):
    service_status: str
    service_started_at: str
    uptime_seconds: float
    active_runs: int
    total_runs: int
    success_runs: int
    failed_runs: int
    current_runs: List[AgentRunStatus]
    last_run: Optional[AgentRunStatus] = None
