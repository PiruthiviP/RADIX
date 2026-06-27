# RADIX Company Intelligence Platform - CI/CD & Deployment

This folder contains the complete monorepo structure, Docker configuration, and Jenkins CI/CD pipeline setup for the RADIX Company Intelligence Platform.

## Project Structure

```text
activity-06/
├── frontend/             # React/Vite/TypeScript Client UI (from activity-02)
│   ├── src/
│   ├── package.json
│   ├── Dockerfile        # Production build & serve with Nginx
│   └── nginx.conf        # Nginx SPA router configuration
├── backend/              # FastAPI + LangGraph Agentic Pipeline (from activity-05)
│   ├── api.py            # FastAPI service
│   ├── app_ui.py         # Streamlit administration console
│   ├── graph_pipeline.py # Agentic orchestration layer
│   └── Dockerfile        # Python dependencies setup
├── docker-compose.yml    # Full-stack Docker orchestration
└── Jenkinsfile           # Jenkins declarative CI/CD pipeline script
```

---

## Running with Docker Compose

You can build and start the entire application stack locally using Docker Compose:

1. Ensure you have a `.env` file containing your credentials in the `backend/` directory.
2. Build and launch all services:
   ```bash
   docker compose up -d --build
   ```
3. Once running, you can access the services at:
   - **Frontend React Portal**: http://localhost:8080
   - **FastAPI Backend Server**: http://localhost:8000/docs
   - **Streamlit Admin UI**: http://localhost:8501

To stop the containers:
```bash
docker compose down
```

---

## CI/CD Pipeline (Jenkins)

The included `Jenkinsfile` automates the entire building, testing, and deployment lifecycle. It is structured into three main flows:

1. **Frontend Stage**:
   - Installs dependencies.
   - Compiles and builds the production bundle.
   - Runs validation tests.
   - Builds the Nginx-based Docker image.

2. **Backend Stage**:
   - Sets up a virtual environment and installs Python dependencies.
   - Executes backend unit tests.
   - Builds the Python-based Docker image.

3. **Orchestration Stage**:
   - Safely tears down any running containers.
   - Boots up the complete stack using `docker compose up -d`.
   - Injects the secure environment variables via Jenkins `ENV` credentials.
   - Verifies the availability and health of all three web services.
