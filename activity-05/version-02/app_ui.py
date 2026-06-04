import streamlit as st
import requests
import json

st.set_page_config(
    page_title="RADIX Company Intelligence Console",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        color: #a3a8b4;
        font-size: 1.1em;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #1a1b23;
        border: 1px solid #2d313e;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #667eea;
    }
    .metric-label {
        font-size: 0.85em;
        color: #a3a8b4;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.25em;
        color: #ffffff;
        font-weight: 700;
        margin-top: 8px;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "research_data" not in st.session_state:
    st.session_state.research_data = None
if "save_status" not in st.session_state:
    st.session_state.save_status = None

# Sidebar Config
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=70)
    st.markdown("### RADIX Settings")
    backend_url = st.text_input("Backend API Base URL", value="http://localhost:8000")
    
    st.markdown("---")
    st.markdown("### Agent Architecture")
    st.markdown("""
    - **Researchers**:
      - Claude (GPT-4o-mini)
      - Gemini (Sonar Pro)
      - Llama (Llama 3.3 70B)
    - **Consolidator**: Gemini 2.5 Pro
    - **Self-Healer**: Llama 3.3 70B
    """)
    st.markdown("---")
    st.caption("RADIX v2.0 • LangGraph orchestrator")

# App Header
st.markdown("<div class='main-header'>📡 RADIX Intelligence Console</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Agentic Multi-Model Pipeline for Automated Company Research & Validation</div>", unsafe_allow_html=True)

# Main UI Columns
col_input, col_action = st.columns([3, 1])

with col_input:
    company_name = st.text_input("Enter Company Name to Research", placeholder="e.g. Blinkit, Rubrik, Microsoft...")

with col_action:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Run Pipeline", use_container_width=True)

if run_btn:
    if not company_name.strip():
        st.warning("Please enter a valid company name.")
    else:
        st.session_state.research_data = None
        st.session_state.save_status = None
        
        with st.spinner(f"Extracting intelligence for '{company_name}'... (Running parallel researchers & self-healing validation)"):
            try:
                res = requests.post(
                    f"{backend_url}/api/research",
                    json={"company_name": company_name},
                    timeout=300  # long timeout for multi-agent execution
                )
                if res.status_code == 200:
                    st.session_state.research_data = res.json()
                    st.success(f"Successfully compiled profile for '{company_name}'!")
                else:
                    st.error(f"Error from API server ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"Failed to connect to API server: {e}")

# Display Results Workspace
if st.session_state.research_data:
    data = st.session_state.research_data
    short_json = data["short_json"]
    full_json = data["full_json"]
    logs = data["log"]
    report = data["report"]
    consolidated = data["consolidated"]
    
    st.markdown("---")
    
    # Left and Right layout for results
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### 📊 Metadata Card (CompanyShort)")
        
        # Display logo if exists and is not NA
        logo_url = short_json.get("logo_url")
        if logo_url and logo_url != "NA" and logo_url.startswith("http"):
            try:
                st.image(logo_url, width=120)
            except:
                pass
                
        # 3x3 Card layout for the 9 short parameters
        metrics = [
            ("Company Name", short_json.get("name", "NA")),
            ("Short Name", short_json.get("short_name", "NA")),
            ("Category", short_json.get("category", "NA")),
            ("Employee Size", short_json.get("employee_size", "NA")),
            ("YoY Growth Rate", short_json.get("yoy_growth_rate", "NA")),
            ("Headquarters", full_json.get("headquarters_address", "NA")), # falls back to headquarters address
            ("Operating Countries", short_json.get("operating_countries", "NA")),
            ("Office Locations", short_json.get("office_locations", "NA")),
            ("Database status", "UNSAVED (Verified Golden Record)")
        ]
        
        # Render metrics in neat grid rows
        for i in range(0, len(metrics), 3):
            grid_cols = st.columns(3)
            for j in range(3):
                if i + j < len(metrics):
                    label, val = metrics[i + j]
                    with grid_cols[j]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        # Save to Database Section
        st.markdown("### 💾 Database Persistence")
        save_col_btn, save_col_status = st.columns([2, 3])
        
        with save_col_btn:
            save_btn = st.button("💾 Save Verified Golden Record to Supabase", type="primary", use_container_width=True)
            if save_btn:
                with st.spinner("Writing payloads to Supabase..."):
                    try:
                        save_res = requests.post(
                            f"{backend_url}/api/save",
                            json={"consolidated": consolidated}
                        )
                        if save_res.status_code == 200:
                            st.session_state.save_status = save_res.json()
                        else:
                            st.session_state.save_status = {"success": False, "message": f"Server error: {save_res.text}"}
                    except Exception as ex:
                        st.session_state.save_status = {"success": False, "message": f"Connection error: {ex}"}
                        
        with save_col_status:
            if st.session_state.save_status:
                s_data = st.session_state.save_status
                if s_data.get("success"):
                    st.success(s_data.get("message"))
                else:
                    st.error(s_data.get("message"))

    with col_right:
        st.markdown("### 🔍 Golden Record Explorer (CompanyFull)")
        
        # Expandable Detailed Record JSON
        with st.expander("🔍 Show Detailed Golden Record (163 Fields)", expanded=False):
            st.json(full_json)
            
        # Expandable Execution Logs
        with st.expander("📝 Detailed Pipeline Execution Logs & Trace", expanded=False):
            if report:
                st.code(report, language="text")
            else:
                st.write("Logs:")
                st.write(logs)
