# Activity 05: LangGraph & LangSmith Company Intelligence Pipeline

This project migrates the multi-agent company intelligence research pipeline to **LangGraph**, enabling a formal state-machine execution flow with parallel research, rule-based validations, LLM conflict resolution, and self-healing cycles.

Additionally, this pipeline includes native telemetry tracking using **LangSmith** for full visibility and debugging.

---

## System Workflow & State Machine

The pipeline execution flow is structured as a Directed Acyclic Graph (DAG) state machine:

![LangGraph Visualization](Company_Intelligence_LangGraph.png)

### State Graph Nodes
1. **`research`**: Invokes LLM 1 (Claude), LLM 2 (Gemini), and LLM 3 (Llama) in parallel to retrieve data for 163 parameters across schema chunks.
2. **`consolidation`**: Reconciles the three datasets into a single Golden Record, resolving conflicting values via an LLM.
3. **`validation_check`**: Runs programmatic data quality assertions.
4. **`regeneration`** *(Self-Healing)*: If validation errors are present, it performs targeted repairs on the failed fields only. It loops back to validation for re-evaluation (up to 3 attempts).
5. **`supabase_write`**: Writes the clean verified record to Supabase.

---

## LangSmith Setup Guide (Step-by-Step)

LangSmith is a platform for debugging, testing, evaluating, and monitoring LLM applications. It traces every LLM API call made in this pipeline (including parameters, latency, cost, and fallbacks).

Follow these instructions to set it up:

### 1. Sign Up for LangSmith
- Go to [smith.langchain.com](https://smith.langchain.com/).
- Sign up using your Email, Google, or GitHub account. It offers a generous free tier for developers.

### 2. Fetch Your API Key
- Navigate to the **Settings** menu by clicking on the gear icon (⚙️) in the bottom-left corner of the sidebar.
- Scroll down to the **API Keys** section.
- Click **Create API Key**.
- Give your key a name (e.g. `radix-pipeline-key`) and click **Create**.
- **Copy the key immediately** (it starts with `lsv2_pt_...`). *You will not be able to see it again.*

### 3. Add Keys to Your `.env` File
Open your `.env` file in the `activity-05/` directory and append the following variables:
```env
# LangSmith Telemetry Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="lsv2_pt_YOUR_API_KEY_HERE"
LANGCHAIN_PROJECT="RADIX"
```

---

## How to Track Progress in LangSmith

Once you run the pipeline, LangSmith automatically starts capturing logs in real time.

### 1. View Your Projects
- Open the LangSmith Dashboard.
- Under **Projects**, click on **`RADIX`**.

### 2. Inspect a Run
- You will see a chronological list of runs. Click on any run (e.g., `run_graph_pipeline`).
- The left-hand panel shows the execution tree (the LangGraph steps, LLM calls, and retrievals).
- The right-hand panel shows the exact input prompts, raw responses, latencies, tokens used, and fallback routing for each individual node.

---

## How to Run

### Set Up Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dry Run (Recommended for testing API keys and tracing)
Runs research and validation but skips database persistence:
```bash
venv/bin/python main.py --company "Blinkit" --dry-run
```

### Production Run (Writes results to Supabase)
```bash
venv/bin/python main.py --company "Blinkit"
```
*(Every run automatically exports or updates `Company_Intelligence_LangGraph.png` to map the graph layout).*
