import os
import re
import logging
import requests
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from config import GEMINI_API_KEY
from db_client import DBClient
from vector_store import VectorStore
from ml_analytics import MLAnalytics

from auth_guards import verify_admin, verify_student_or_admin, verify_all_roles
from audit_middleware import AuditLoggingMiddleware, recent_audit_records

# Original activity-06 imports for research/save
from graph_pipeline import run_graph_pipeline
from db_writer import DBWriter
from schemas import CompanyFull

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RADIXServer")

app = FastAPI(
    title="RADIX Semantic Intelligence & Analytics Server",
    description="Unified Backend API for LangGraph Company Research, Semantic Vector Search, ML Clustering, YoY Growth Forecasting, and RAG Chatbot.",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Auditing compliance middleware
app.add_middleware(AuditLoggingMiddleware)

# Global instances
db_client = DBClient()
vector_store = VectorStore()
ml_analytics = MLAnalytics()

# Keep a local copy of feature importance after training
feature_importance_cache = []

def post_gemini_with_retry(url: str, json_payload: dict, max_retries: int = 3) -> dict:
    import time
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=json_payload, timeout=20)
            if response.status_code in (503, 429):
                logger.warning(f"Gemini API returned {response.status_code}. Retrying in 2 seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(2)
                continue
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Error calling Gemini API: {e}. Retrying in 2 seconds...")
            time.sleep(2)
    raise RuntimeError("Failed to reach Gemini API after retries.")

import threading

def run_indexing_and_training():
    logger.info("Background indexing and training thread started...")
    try:
        # Fetch companies from Supabase
        companies = db_client.fetch_all_companies()
        if not companies:
            logger.warning("No companies retrieved from database during startup.")
            return

        # Index companies into local Vector Store
        vector_store.index_companies(companies)
        
        # Train ML models
        training_res = ml_analytics.train_predictive_model(companies)
        if training_res.get("status") == "trained":
            global feature_importance_cache
            feature_importance_cache = training_res.get("feature_importances", [])
            logger.info("Background indexing and ML training completed successfully.")
        else:
            logger.warning(f"ML Model training skipped in background: {training_res.get('reason')}")
    except Exception as e:
        logger.error(f"Error in background startup indexing: {e}")

@app.on_event("startup")
def startup_event():
    logger.info("RADIX Backend Service starting up (initializing background thread)...")
    thread = threading.Thread(target=run_indexing_and_training, daemon=True)
    thread.start()
    logger.info("FastAPI startup finished (indexing deferred to background).")

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# --- ORIGINAL AGENT RESEARCH ENDPOINTS ---

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

@app.post("/api/research", response_model=ResearchResponse, dependencies=[Depends(verify_student_or_admin)])
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
        writer = DBWriter()
        company_id = consolidated.get("company_id") or 9999
        short_json = writer.build_short_json(consolidated, company_id)
        
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

@app.post("/api/save", response_model=SaveResponse, dependencies=[Depends(verify_admin)])
async def save_company(request: SaveRequest):
    if not request.consolidated:
        raise HTTPException(status_code=400, detail="Consolidated profile data is empty.")
        
    try:
        writer = DBWriter()
        # Trigger production database write/upsert
        success, db_msg = writer.write_company(request.consolidated)
        
        # Synchronize Vector Store index dynamically
        if success:
            try:
                companies = db_client.fetch_all_companies()
                company_name = request.consolidated.get("name", "").strip().lower()
                target_comp = None
                for c in companies:
                    if c.get("name", "").strip().lower() == company_name:
                        target_comp = c
                        break
                if target_comp:
                    c_id = target_comp.get("company_id")
                    vector_store.remove_company(c_id)
                    vector_store.index_companies([target_comp])
            except Exception as index_err:
                logger.error(f"Failed to sync vector store for updated company: {index_err}")
                
        return SaveResponse(success=success, message=db_msg)
    except Exception as e:
        return SaveResponse(success=False, message=f"Failed to save profile: {str(e)}")

@app.delete("/api/companies/{company_id}", dependencies=[Depends(verify_admin)])
def delete_company(company_id: int):
    if not db_client.enabled or not db_client.client:
        raise HTTPException(status_code=400, detail="Database connection is not configured.")
    try:
        # Delete from Supabase companies_json table
        db_client.client.table("companies_json").delete().eq("company_id", company_id).execute()
        
        # Remove from vector store cache
        vector_store.remove_company(company_id)
        
        return {"success": True, "message": f"Company {company_id} deleted successfully."}
    except Exception as e:
        logger.error(f"Error deleting company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- NEW SEMANTIC, ML, AND CHATBOT ENDPOINTS ---

class SearchRequest(BaseModel):
    query: str
    top_n: Optional[int] = 5

class PredictRequest(BaseModel):
    category: str = "Enterprise"
    employee_size: str = "500"
    ai_adoption: str = "High"
    nature: str = "Private"
    age: int = 15
    social_followers: int = 5000

class Message(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    prompt: str

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "supabase_connected": db_client.enabled,
        "vector_db_size": len(vector_store.get_cached_ids()),
        "ml_model_ready": ml_analytics.model_trained
    }

@app.get("/api/companies", dependencies=[Depends(verify_all_roles)])
def get_companies():
    try:
        companies = db_client.fetch_all_companies()
        return {"companies": companies}
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", dependencies=[Depends(verify_all_roles)])
def search_companies(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        results = vector_store.semantic_search(req.query, req.top_n)
        return {"query": req.query, "results": results}
    except Exception as e:
        logger.error(f"Search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/similarity/{company_id}", dependencies=[Depends(verify_all_roles)])
def get_similar(company_id: int, top_n: Optional[int] = 5):
    try:
        results = vector_store.get_similar_companies(company_id, top_n)
        return {"company_id": company_id, "results": results}
    except Exception as e:
        logger.error(f"Similarity API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clusters", dependencies=[Depends(verify_all_roles)])
def get_clusters():
    try:
        all_companies = vector_store.load_all()
        if not all_companies:
            return {"clusters": []}
        clusters = ml_analytics.perform_clustering_and_projection(all_companies, n_clusters=5)
        return {"clusters": clusters}
    except Exception as e:
        logger.error(f"Clusters API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml-metadata", dependencies=[Depends(verify_all_roles)])
def get_ml_metadata():
    return {
        "model_ready": ml_analytics.model_trained,
        "feature_importances": feature_importance_cache
    }

@app.post("/api/predict", dependencies=[Depends(verify_all_roles)])
def predict_growth(req: PredictRequest):
    try:
        predicted = ml_analytics.predict_growth_rate(req.dict())
        return {"prediction": predicted}
    except Exception as e:
        logger.error(f"Predict API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chatbot", dependencies=[Depends(verify_all_roles)])
def chat(req: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured on server.")
        
    try:
        # 1. Semantic search for RAG context
        context_records = vector_store.semantic_search(req.prompt, top_n=3)
        context_str = ""
        if context_records:
            context_str += "Relevant Company Context:\n"
            for rec in context_records:
                meta = rec["metadata"]
                context_str += (
                    f"- Company: {rec['name']}\n"
                    f"  Category: {meta.get('category', 'NA')}\n"
                    f"  Overview: {meta.get('overview_text', 'NA')}\n"
                    f"  YoY Growth: {meta.get('yoy_growth_rate', 'NA')}\n"
                    f"  Key Differentiators: {meta.get('unique_differentiators', 'NA')}\n"
                    f"  AI/ML Level: {meta.get('ai_ml_adoption_level', 'NA')}\n\n"
                )
        
        # 2. Build Gemini contents request
        # Map assistant -> model
        contents = []
        for msg in req.messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
            
        # Append latest prompt with context
        system_instruction = (
            "You are Antigravity, the Conversational AI Chatbot for the RADIX Platform. "
            "Your objective is to provide high-quality strategic business intelligence to analysts. "
            "Use the provided context companies below to construct accurate, fact-based answers. "
            "If the question cannot be answered using the context, use your general knowledge but declare so. "
            "Be precise, clear, and professional.\n\n"
        )
        
        full_prompt = f"{system_instruction}{context_str}\nUser Question: {req.prompt}"
        contents.append({
            "role": "user",
            "parts": [{"text": full_prompt}]
        })
        
        # Call Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": contents}
        res_json = post_gemini_with_retry(url, payload)
        
        # Extract reply text
        reply = ""
        candidates = res_json.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                reply = parts[0].get("text", "")
                
        if not reply:
            reply = "I apologize, but I was unable to generate a response from the model. Please check the context and try again."
            
        return {"response": reply, "context": [r["name"] for r in context_records]}
        
    except Exception as e:
        logger.error(f"Chatbot API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommend/{company_id}", dependencies=[Depends(verify_student_or_admin)])
def generate_recommendation(company_id: int):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured on server.")
        
    # Get company
    all_companies = vector_store.load_all()
    target_comp = None
    for rec in all_companies:
        if rec["company_id"] == company_id:
            target_comp = rec
            break
            
    if not target_comp:
        raise HTTPException(status_code=404, detail="Company not found in cache database.")
        
    # Get similar companies
    similar_records = vector_store.get_similar_companies(company_id, top_n=2)
    competitors_str = ""
    for rec in similar_records:
        meta = rec["metadata"]
        competitors_str += f"- {rec['name']} (Industry: {meta.get('category')}, AI Adoption: {meta.get('ai_ml_adoption_level')})\n"
        
    meta = target_comp["metadata"]
    prompt = (
        f"You are a Senior Strategic Consultant. Generate a detailed executive report for the company:\n\n"
        f"Company Name: {target_comp['name']}\n"
        f"Industry/Category: {meta.get('category')}\n"
        f"Overview: {meta.get('overview_text')}\n"
        f"Weaknesses/Gaps: {meta.get('weaknesses_gaps')}\n"
        f"Key Challenges: {meta.get('key_challenges_needs')}\n"
        f"AI/ML Adoption Level: {meta.get('ai_ml_adoption_level')}\n\n"
        f"Direct Competitors:\n{competitors_str}\n"
        f"Please provide:\n"
        f"1. A strategic SWOT Analysis focusing on their gaps.\n"
        f"2. Three (3) Prescriptive Recommendations for strategic growth, leveraging AI/ML capabilities or addressing market opportunities relative to their competitors."
    )
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        res_json = post_gemini_with_retry(url, payload)
        
        reply = ""
        candidates = res_json.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                reply = parts[0].get("text", "")
                
        return {"company_name": target_comp["name"], "recommendation": reply}
    except Exception as e:
        logger.error(f"Recommendations API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/audit-logs", dependencies=[Depends(verify_admin)])
def get_audit_logs():
    """Endpoint for viewing platform action audit trails."""
    return {"audit_logs": recent_audit_records}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
