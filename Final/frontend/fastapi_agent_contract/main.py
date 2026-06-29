from fastapi import FastAPI, HTTPException

from orchestrator import run_orchestration
from rules import check_grounding_completeness, ensure_exact_163, grounding_coverage_issues
from schemas import GenerateRequest, GeneratedOutput, ValidateRequest, ValidateResponse


app = FastAPI(title="LLM Orchestration Contract API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/orchestration/generate", response_model=GeneratedOutput)
def generate(request: GenerateRequest) -> GeneratedOutput:
    try:
        result = run_orchestration(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected orchestration error: {exc}") from exc

    return result


@app.post("/orchestration/validate", response_model=ValidateResponse)
def validate(request: ValidateRequest) -> ValidateResponse:
    ok, missing_grounding = check_grounding_completeness(request.grounding)
    if not ok:
        return ValidateResponse(
            valid=False,
            missingKeys=[],
            emptyKeys=[],
            groundingCoverageIssues=[f"Missing grounding fields: {', '.join(missing_grounding)}"],
            message="Grounding payload incomplete.",
        )

    missing, extra = ensure_exact_163(request.generatedParameters)
    empty = sorted([k for k, v in request.generatedParameters.items() if not str(v).strip()])
    coverage_issues = grounding_coverage_issues(request.grounding, request.generatedParameters)

    if extra:
        coverage_issues.append(f"Unexpected keys present: {', '.join(extra[:10])}{'...' if len(extra) > 10 else ''}")

    valid = len(missing) == 0 and len(empty) == 0 and len(coverage_issues) == 0

    return ValidateResponse(
        valid=valid,
        missingKeys=missing,
        emptyKeys=empty,
        groundingCoverageIssues=coverage_issues,
        message="Validation passed." if valid else "Validation failed. Review missing/empty/coverage issues.",
    )
