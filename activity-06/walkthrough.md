# Walkthrough - Restructure & Verification of Activity-06

We have completed the restructuring, stabilized the Jenkins pipeline, and verified the entire CI/CD and deployment stack.

---

## 🛠️ Changes Made

1. **Clean Restructure**:
   - Cleared old files in `activity-06` to prevent leftovers.
   - Synchronized a clean React frontend portal from `activity-02/Milestone 2/Session 2/Pre built UI/remix-of-the-dream-weaver-main` to [activity-06/frontend/](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/frontend).
   - Synchronized Python backend components from `activity-05` to [activity-06/backend/](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/backend), restoring [api.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/backend/api.py) and [app_ui.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/backend/app_ui.py).

2. **Dockerization**:
   - Re-created the frontend `Dockerfile` to compile static assets and serve them via Nginx.
   - Re-created the backend `Dockerfile` to wrap the Python LangGraph and FastAPI layers.
   - Recreated [docker-compose.yml](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/docker-compose.yml) to coordinate the services.

3. **Jenkins CI/CD Pipeline Stabilized**:
   - **Bypassed Single Quote Path Bug**: Identified that Jenkins' shell launcher (`sh`) hangs on macOS when the workspace path contains a single quote (due to the user's home folder `/Users/Piruthivi'sMacbook/`). 
   - **Workaround Implementation**: Reconfigured [Jenkinsfile](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/Jenkinsfile) and root [Jenkinsfile](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/Jenkinsfile) to skip automatic checkout in the default workspace using `skipDefaultCheckout()` and wrapped the Git checkout and all build steps in a custom workspace `ws('/Users/Shared/jenkins_workspace/RADIX-Pipeline')` (which contains no special characters).
   - **Resolved Overwrite Permissions**: Pre-emptively deleted `.env` files using `rm -f` in the configuration stage to prevent `Permission denied` errors when copying Jenkins read-only credential files on subsequent runs.
   - **Restored Shell Binary Pathing**: Appended necessary NVM and Homebrew paths (`/Users/Piruthivi'sMacbook/.nvm/versions/node/v22.20.0/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin`) to the environment `PATH` so Jenkins shell commands can resolve `npm`, `node`, and `docker` cleanly.

4. **Frontend Fix (TypeError Repair)**:
   - Fixed a JS TypeError in [CompanyCard.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-06/frontend/src/components/companies/CompanyCard.tsx) where `yoy_growth_rate.startsWith` was crashing because the value from the database is sometimes a number rather than a string. Safely cast the growth rate to a string before executing the query.

---

## 🧪 Validation & Testing

### 1. Jenkins Build 11 Execution Results
The entire pipeline completed successfully with **green ticks on all 10 stages**:
- **SCM Checkout**: Succeeded
- **Inject Environment Configuration**: Succeeded
- **Frontend - Install Dependencies**: Succeeded
- **Frontend - Build & Validate**: Succeeded
- **Frontend - Docker Build**: Succeeded
- **Backend - Install Dependencies**: Succeeded
- **Backend - Execute Tests**: Succeeded
- **Backend - Docker Build**: Succeeded
- **Orchestration - Service Initialization**: Succeeded
- **Orchestration - Workflow Verification**: Succeeded

All verification curls returned successful HTTP status codes:
- FastAPI backend documentation: `http://localhost:8000/docs` -> 200 OK
- Streamlit console portal: `http://localhost:8501/` -> 200 OK
- React frontend portal: `http://localhost:8080/` -> 200 OK

### 2. Browser Verification
We verified using a browser agent that the dashboard and the companies directory both load correctly without any blank screens or runtime exceptions.

#### Dashboard Page
![Dashboard Overview](/Users/Piruthivi'sMacbook/.gemini/antigravity-ide/brain/6dab756e-7ffa-4528-a644-e90a02eefbc9/localhost_8080_initial_1782301590453.png)

#### Companies Page (119 Companies Rendering Correctly)
![Companies Grid Loaded](/Users/Piruthivi'sMacbook/.gemini/antigravity-ide/brain/6dab756e-7ffa-4528-a644-e90a02eefbc9/companies_grid_loaded_1782302281514.png)
