# FastAPI Orchestration Contract (13 -> 163)

This blueprint aligns your LLM orchestration with the web app flow:

1. Admin submits 13 grounding parameters.
2. Orchestrator must use those 13 fields as primary grounding (not company-name-only lookup).
3. Service returns exactly 163 generated parameters.
4. Admin reviews/edits in UI, validates, then enters hiring rounds.

## Core Repair Objective

Your current agent over-relies on `companyName` retrieval. This contract enforces:

- Hard validation of all 13 grounding fields before generation.
- Strict instruction that generated content must reflect all 13 fields.
- Exactly 163 output keys in the format `parameter_001` ... `parameter_163`.
- Safety fallback: unknown details become explicit placeholders instead of fabricated facts.

## Files

- `schemas.py`: request/response models and output key utilities
- `rules.py`: objective + hard rules + guardrail checks
- `orchestrator.py`: generation pipeline (replace mock LLM call with your provider)
- `main.py`: FastAPI app and endpoints

## Suggested Endpoints

- `POST /orchestration/generate`
- `POST /orchestration/validate`
- `GET /health`

## Integration Note for Current UI

Your current Add Company page expects 163 editable fields and can use this output directly:

```json
{
  "generatedParameters": {
    "parameter_001": "...",
    "parameter_002": "...",
    "...": "...",
    "parameter_163": "..."
  }
}
```

## Run (example)

```bash
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
```
