# RADIX Company Intelligence Platform - Enterprise Architecture & Security

This folder contains the complete, production-grade enterprise architecture for the **RADIX (Research Automation and Decision Intelligence Exchange)** platform. We have evolved the codebase from a research prototype to a secure, compliant, high-availability system by adding comprehensive security, auditing, and governance features.

---

## Evolved Monorepo Structure

```text
activity-08/
├── frontend/                 # React/Vite/TypeScript Client Portal
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # [NEW] Mock Authentication & Session Role switcher
│   │   ├── components/
│   │   │   ├── ProtectedRoute.tsx # [NEW] React Router security route wrap
│   │   │   └── layout/
│   │   │       ├── AppSidebar.tsx # [MOD] Filters links dynamically per role
│   │   │       └── RoleSwitcher.tsx # [NEW] Dropdown UI in sidebar to switch roles
│   │   └── App.tsx                # [MOD] Enforces route guarding rules
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                  # FastAPI + LangGraph Agentic Pipeline
│   ├── auth_guards.py        # [NEW] FastAPI JWT decoder & Role decorators
│   ├── audit_middleware.py   # [NEW] ASGI HTTP middleware auditing requests
│   ├── database_setup.sql    # [NEW] SQL schema for PostgreSQL auditing triggers
│   ├── main.py               # [MOD] Registers guards & exposes audit logs
│   ├── app_ui.py             # [MOD] Streamlit console passing auth roles
│   ├── graph_pipeline.py     # Agentic orchestration layer
│   └── Dockerfile            # Python dependencies setup
├── docker-compose.yml        # Full-stack Docker orchestration
└── Jenkinsfile               # Jenkins declarative CI/CD pipeline script
```

---

## Key Enterprise Security Features

### 1. Multi-Layer Role-Based Access Control (RBAC)
We enforce permissions at three separate levels to protect intelligence records:
- **Database Layer (RLS):** Supabase Row-Level Security restricts SQL mutations (`INSERT`, `UPDATE`, `DELETE`) strictly to users containing the `Admin` or `LeadAnalyst` claim metadata inside their JWT tokens. Students and Recruiters are limited to `SELECT` (read-only) operations.
- **Backend API Layer (FastAPI):** Every route is wrapped in an authorization guard dependency (`Depends(verify_admin)` or `Depends(verify_student_or_admin)`). If the header matches a restricted role, the API returns a standard `HTTP 403 Forbidden` response.
- **Frontend Layer (React Guard & Sidebar Filtering):** 
  - Routes like `/ml-analytics` and `/chatbot` are wrapped in `<ProtectedRoute>` tags. If a user tries to access these with a restricted role, they are presented with an interactive glassmorphic warning.
  - The side navigation list automatically filters out links that the active user role is not authorized to click, offering a clean, tailored workspace.

### 2. Request & Database Auditing (Compliance)
To comply with security audits (e.g. SOC2, ISO 27001):
- **API Audit Trails:** The custom `AuditLoggingMiddleware` captures the user's ID, email, IP address, request method, route, processing duration, and response status code, outputting standard structured `[AUDIT COMPLIANCE]` console tracks and maintaining a running log for administrators.
- **PostgreSQL Audit Ledger:** The trigger function defined in `database_setup.sql` automatically populates the `database_audit_trail` table on any company record change, tracking the exact difference in payload (`old_data` vs `new_data`), who made the change (`executed_by_email`), and when it happened.

---

## Local Verification & Testing

### 1. Database Setup
To configure PostgreSQL auditing on your Supabase instance, execute the DDL queries located in:
👉 [database_setup.sql](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/database_setup.sql)

### 2. Launching Locally (Manual Mode)
1. **Start the Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
2. **Start the Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. **Open the browser portal** at `http://localhost:5173`.

### 3. Verification Steps
1. Navigate to `/chatbot` or `/ml-analytics` as a **Guest**. Verify that access is blocked and you are prompted to elevate credentials.
2. In the bottom of the sidebar, use the **Access Profile** switcher to change your role to **Student**. Notice that the Chatbot and ML Analytics pages immediately unlock, and their links appear in the navigation bar.
3. Switch your role to **Recruiter**. Notice that the Chatbot and ML Analytics sidebar links vanish, and attempts to access them return the "Unauthorized Access" safety shield.
4. Switch your role to **Admin**. Open the Streamlit Console (`streamlit run app_ui.py`) and verify that triggering a new pipeline research writes to the database successfully. If you change your Streamlit role to **Student** or **Recruiter**, verify that writes are blocked with a `403 Forbidden` database persistence error.
