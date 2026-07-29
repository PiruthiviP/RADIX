import logging
import asyncio
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    WorkflowRequest,
    WorkflowResponse,
    HealthResponse,
    CompanyIntelligenceRequest,
    CompanyIntelligenceResponse,
    AgentStatusResponse
)
from app.service import WorkflowService

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zagent_001V2 Company Intelligence API",
    description="Production-grade asynchronous multi-provider company intelligence extraction pipeline using LangGraph.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service globally
service: Optional[WorkflowService] = None

@app.on_event("startup")
def startup_event():
    global service
    try:
        logger.info("Initializing WorkflowService...")
        service = WorkflowService()
        logger.info("WorkflowService successfully started.")
    except Exception as e:
        logger.critical(f"Fatal error on service startup: {str(e)}", exc_info=True)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@app.get("/v1/health", response_model=HealthResponse, tags=["Health"])
async def get_health():
    """Returns service health status and active providers."""
    if not service:
        raise HTTPException(status_code=503, detail="Service is starting up or failed to initialize.")
    health = service.get_health_status()
    return HealthResponse(
        status=health["status"],
        providers_available=health["providers_available"]
    )


@app.get("/v1/agent/status", response_model=AgentStatusResponse, tags=["Agent Status"])
@app.get("/v1/workflow/status", response_model=AgentStatusResponse, tags=["Agent Status"])
async def get_agent_status():
    """Returns global statistics and active runs list."""
    if not service:
        raise HTTPException(status_code=503, detail="Service is starting up.")
    return service.get_global_status()


@app.get("/v1/agent/status/{run_id}", tags=["Agent Status"])
async def get_run_status(run_id: str):
    """Returns the status and progress of a specific execution run."""
    if not service:
        raise HTTPException(status_code=503, detail="Service is starting up.")
    run = service.get_run_status(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run with ID {run_id} not found.")
    return run


@app.post("/v1/company-intelligence/generate", response_model=CompanyIntelligenceResponse, tags=["Workflow"])
@app.post("/v1/workflow/invoke", response_model=CompanyIntelligenceResponse, tags=["Workflow"])
async def generate_company_intelligence(request: CompanyIntelligenceRequest):
    """Triggers the company intelligence extraction workflow synchronously."""
    if not service:
        raise HTTPException(status_code=503, detail="Service is starting up.")
        
    company_name = request.companyName or (request.shortName)
    if not company_name:
        raise HTTPException(status_code=400, detail="Missing required parameter: companyName or shortName.")

    try:
        # Execute workflow
        response = await service.execute_workflow(request)
        return response
    except Exception as e:
        logger.error(f"Generate endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_index():
    """Renders the Zagent_001V2 system management dashboard."""
    if not service:
        return HTMLResponse(content="<h2>Zagent Service is starting up... Please reload in a moment.</h2>", status_code=503)

    stats = service.get_global_status()
    health = service.get_health_status()
    
    # 1. Format providers list
    providers_html = ""
    for p in health["providers_available"]:
        providers_html += f"<li style='margin-bottom: 0.5rem;'><span style='color: var(--success)'>●</span> {p.upper()}</li>"
    if not providers_html:
        providers_html = "<li style='color: var(--failed)'>No active providers configured</li>"

    # 2. Format runs table rows
    rows_html = ""
    # Retrieve runs directly from service registry
    all_runs = list(service.active_runs.values()) + service.history_runs
    for run in all_runs:
        color = "var(--success)" if run.generation_status == "SUCCESS" else ("var(--failed)" if run.generation_status == "FAILED" else "var(--accent-cyan)")
        status_text = run.generation_status or "RUNNING"
        dur = run.duration_ms if run.duration_ms else "-"
        rows_html += f"""
        <tr>
            <td><code>{run.run_id[:8]}...</code></td>
            <td><strong>{run.company_name}</strong></td>
            <td>{run.stage}</td>
            <td>
                <div class='progress-container'>
                    <div class='progress-bar'>
                        <div class='progress-fill' style='width: {run.progress_percent}%'></div>
                    </div>
                    <span>{run.progress_percent:.0f}%</span>
                </div>
            </td>
            <td>{run.started_at[11:19]}</td>
            <td>{dur}</td>
            <td><span style='color: {color}; font-weight: bold;'>{status_text}</span></td>
        </tr>
        """
    if not rows_html:
        rows_html = "<tr><td colspan='7' style='text-align: center; color: var(--text-secondary)'>No runs logged yet. Try triggering the pipeline above!</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zagent_001V2 Intelligence Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-primary: #0a0e1a;
                --bg-secondary: #131a30;
                --bg-tertiary: #1b2542;
                --accent-cyan: #00f2fe;
                --accent-blue: #4facfe;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --success: #10b981;
                --failed: #ef4444;
                --border-color: #293556;
                --glass-bg: rgba(19, 26, 48, 0.7);
                --glass-border: rgba(255, 255, 255, 0.05);
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.5;
                padding: 2rem;
                overflow-x: hidden;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            /* Header styles */
            header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2.5rem;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 1.5rem;
            }}

            .logo-section h1 {{
                font-size: 2.2rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -1px;
            }}

            .logo-section p {{
                color: var(--text-secondary);
                font-size: 0.95rem;
                margin-top: 0.25rem;
            }}

            .badge {{
                display: inline-block;
                padding: 0.35rem 0.85rem;
                border-radius: 50px;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                background: rgba(16, 185, 129, 0.1);
                color: var(--success);
                border: 1px solid var(--success);
            }}

            .badge.degraded {{
                background: rgba(239, 68, 68, 0.1);
                color: var(--failed);
                border: 1px solid var(--failed);
            }}

            /* Grid Layout */
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}

            .card {{
                background: var(--glass-bg);
                backdrop-filter: blur(10px);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                padding: 1.5rem;
                transition: transform 0.2s, border-color 0.2s;
            }}

            .card:hover {{
                transform: translateY(-2px);
                border-color: var(--border-color);
            }}

            .card h3 {{
                font-size: 0.9rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.5rem;
            }}

            .card .value {{
                font-size: 2rem;
                font-weight: 700;
                color: var(--text-primary);
            }}

            /* Custom form & actions card */
            .main-content {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }}

            .action-panel {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 2rem;
            }}

            .action-panel h2 {{
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                background: linear-gradient(135deg, #fff, var(--text-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .form-group {{
                margin-bottom: 1.25rem;
            }}

            .form-group label {{
                display: block;
                font-size: 0.85rem;
                font-weight: 600;
                color: var(--text-secondary);
                margin-bottom: 0.5rem;
            }}

            .form-group input, .form-group select {{
                width: 100%;
                background: var(--bg-tertiary);
                border: 1px solid var(--border-color);
                color: var(--text-primary);
                padding: 0.75rem 1rem;
                border-radius: 8px;
                outline: none;
                font-family: inherit;
                transition: border-color 0.2s;
            }}

            .form-group input:focus {{
                border-color: var(--accent-cyan);
            }}

            .submit-btn {{
                background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
                color: var(--bg-primary);
                font-weight: 700;
                border: none;
                padding: 0.9rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
                font-family: inherit;
                transition: opacity 0.2s;
            }}

            .submit-btn:hover {{
                opacity: 0.9;
            }}

            /* Table/Lists section */
            .runs-table-panel {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 2rem;
                margin-top: 2rem;
            }}

            .runs-table-panel h2 {{
                margin-bottom: 1.25rem;
                font-size: 1.4rem;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }}

            th {{
                text-align: left;
                padding: 0.75rem 1rem;
                color: var(--text-secondary);
                font-size: 0.85rem;
                border-bottom: 2px solid var(--border-color);
            }}

            td {{
                padding: 1rem;
                border-bottom: 1px solid var(--border-color);
                font-size: 0.9rem;
            }}

            .progress-container {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .progress-bar {{
                flex-grow: 1;
                background: var(--border-color);
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
            }}

            .progress-fill {{
                background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue));
                height: 100%;
                border-radius: 4px;
            }}

            .refresh-link {{
                color: var(--accent-cyan);
                text-decoration: none;
                font-size: 0.85rem;
                font-weight: 600;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-section">
                    <h1>Zagent_001V2</h1>
                    <p>Company Intelligence Extraction System Dashboard</p>
                </div>
                <div>
                    <span class="badge {'degraded' if health['status'] == 'DEGRADED' else ''}">{health['status']}</span>
                </div>
            </header>

            <div class="grid">
                <div class="card">
                    <h3>Service Uptime</h3>
                    <div class="value">{stats.uptime_seconds:.1f}s</div>
                </div>
                <div class="card">
                    <h3>Active Jobs</h3>
                    <div class="value">{stats.active_runs}</div>
                </div>
                <div class="card">
                    <h3>Successful Runs</h3>
                    <div class="value">{stats.success_runs}</div>
                </div>
                <div class="card">
                    <h3>Failed Runs</h3>
                    <div class="value">{stats.failed_runs}</div>
                </div>
            </div>

            <div class="main-content">
                <div class="action-panel">
                    <h2>Trigger Company Intelligence pipeline</h2>
                    <form id="extractForm">
                        <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0;">
                            <div class="form-group">
                                <label for="companyName">Company Name</label>
                                <input type="text" id="companyName" required placeholder="e.g. OpenAI">
                            </div>
                            <div class="form-group">
                                <label for="websiteUrl">Website URL</label>
                                <input type="text" id="websiteUrl" placeholder="e.g. openai.com">
                            </div>
                        </div>
                        <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0;">
                            <div class="form-group">
                                <label for="yearOfIncorporation">Year Founded</label>
                                <input type="number" id="yearOfIncorporation" placeholder="e.g. 2015">
                            </div>
                            <div class="form-group">
                                <label for="ceoName">CEO Name</label>
                                <input type="text" id="ceoName" placeholder="e.g. Sam Altman">
                            </div>
                        </div>
                        <button type="submit" class="submit-btn">Run Extraction Pipeline</button>
                    </form>
                    
                    <div id="resultBox" style="margin-top: 1.5rem; display: none; background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); max-height: 250px; overflow-y: auto;">
                        <h4 style="margin-bottom: 0.5rem; color: var(--accent-cyan)">Generation Result Payload:</h4>
                        <pre id="jsonResult" style="font-size: 0.8rem; font-family: monospace;"></pre>
                    </div>
                </div>

                <div class="card">
                    <h3>Active Providers</h3>
                    <ul style="list-style: none; margin-top: 1rem;">
                        {providers_html}
                    </ul>
                    <h3 style="margin-top: 1.5rem;">Metadata Stats</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">Total fields: 165</p>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Admin grounded fields: 13</p>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Enriched generated fields: 152</p>
                </div>
            </div>

            <div class="runs-table-panel">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>Active and Completed Runs Log</h2>
                    <span class="refresh-link" onclick="window.location.reload()">Refresh Page</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Run ID</th>
                            <th>Company Name</th>
                            <th>Current Stage</th>
                            <th>Progress</th>
                            <th>Started At</th>
                            <th>Duration (ms)</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            document.getElementById("extractForm").addEventListener("submit", async (e) => {{
                e.preventDefault();
                const companyName = document.getElementById("companyName").value;
                const websiteUrl = document.getElementById("websiteUrl").value || null;
                const yearOfIncorporation = document.getElementById("yearOfIncorporation").value || null;
                const ceoName = document.getElementById("ceoName").value || null;
                
                const submitBtn = document.querySelector(".submit-btn");
                submitBtn.innerText = "Extracting... Please Wait";
                submitBtn.disabled = true;

                try {{
                    const response = await fetch("/v1/company-intelligence/generate", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            companyName,
                            websiteUrl,
                            yearOfIncorporation,
                            ceoName
                        }})
                    }});
                    const data = await response.json();
                    
                    document.getElementById("resultBox").style.display = "block";
                    document.getElementById("jsonResult").innerText = JSON.stringify(data, null, 2);
                }} catch(err) {{
                    alert("Extraction trigger failed. Check console for logs.");
                    console.error(err);
                }} finally {{
                    submitBtn.innerText = "Run Extraction Pipeline";
                    submitBtn.disabled = false;
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
