import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from graph_pipeline import run_graph_pipeline
from db_writer import DBWriter
from schemas import CompanyFull

app = FastAPI(
    title="RADIX Company Intelligence Agentic API",
    description="Backend API to run the LangGraph Company Intelligence research, validation, and self-healing pipeline.",
    version="2.0.0"
)

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

class ResearchRequest(BaseModel):
    company_name: str

class ResearchResponse(BaseModel):
    short_json: Dict[str, Any]
    full_json: Dict[str, Any]
    validation_errors: List[Dict[str, Any]]
    attempts: int
    log: List[str]
    report: str
    consolidated: Dict[str, Any]

class SaveRequest(BaseModel):
    consolidated: Dict[str, Any]

class SaveResponse(BaseModel):
    success: bool
    message: str

@app.post("/api/research", response_model=ResearchResponse)
async def research_company(request: ResearchRequest):
    if not request.company_name.strip():
        raise HTTPException(status_code=400, detail="Company name cannot be empty.")
    
    try:
        # Run graph pipeline in dry-run mode to extract company info without writing to DB yet
        final_state = await run_graph_pipeline(request.company_name, dry_run=True)
        
        consolidated = final_state.get("consolidated", {})
        errors = final_state.get("errors", [])
        attempts = final_state.get("attempts", 0)
        logs = final_state.get("log", [])
        
        # Build Short and Full JSON payloads
        db_writer = DBWriter()
        company_id = consolidated.get("company_id") or 9999
        short_json = db_writer.build_short_json(consolidated, company_id)
        
        full_json = {}
        for key in CompanyFull.model_fields.keys():
            if key == "company_id":
                full_json[key] = company_id
            else:
                full_json[key] = consolidated.get(key, "NA")
                
        # Read the generated pipeline execution log file
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', request.company_name).lower()
        log_file_path = os.path.join("logs", f"{safe_name}_pipeline.log")
        report_content = ""
        if os.path.exists(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as f:
                report_content = f.read()
                
        return ResearchResponse(
            short_json=short_json,
            full_json=full_json,
            validation_errors=errors,
            attempts=attempts,
            log=logs,
            report=report_content,
            consolidated=consolidated
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.post("/api/save", response_model=SaveResponse)
async def save_company(request: SaveRequest):
    if not request.consolidated:
        raise HTTPException(status_code=400, detail="Consolidated profile data is empty.")
        
    try:
        db_writer = DBWriter()
        # Trigger production database write/upsert
        success, db_msg = db_writer.write_company(request.consolidated)
        return SaveResponse(success=success, message=db_msg)
    except Exception as e:
        return SaveResponse(success=False, message=f"Failed to save profile: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
