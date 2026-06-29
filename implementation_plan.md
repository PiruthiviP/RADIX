# Implementation Plan: Enterprise Security, RBAC, and Auditing Layer

This plan describes the design and implementation of the final enterprise-grade security architecture for **RADIX (Research Automation and Decision Intelligence Exchange)** under the `activity-08` directory. 

We will integrate Role-Based Access Control (RBAC), API/Database Auditing, Data Lineage tracking, and route-level UI guards to transition the platform from a prototype to a secure, compliant enterprise intelligence platform.

---

## User Review Required

> [!IMPORTANT]
> - **Mock Authentication Hook:** In this phase, we will implement a mock authentication layer in the frontend header allowing you to change roles (`Admin`, `Student`, `Recruiter`, `Guest`) on-the-fly to test the UI access guards. In production, this switcher would be replaced by a standard Supabase OAuth2 / JWT session provider.
> - **Database Schema:** We will provide a schema script `database_setup.sql` containing tables and trigger logic for audit trails. This will need to be executed on your Supabase instance to enable automatic data auditing.

---

## Proposed Changes

### Backend Component (FastAPI & Database)

#### [NEW] [database_setup.sql](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/database_setup.sql)
- Define a table `database_audit_trail` to store details of database inserts, updates, and deletes.
- Write a PL/pgSQL database trigger function `audit_trigger_func` that logs all row manipulations automatically.
- Attach the trigger to the `companies_json` master table.

#### [NEW] [auth_guards.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/auth_guards.py)
- Create FastAPI dependencies to parse bearer tokens or read role headers.
- Implement guards: `verify_admin`, `verify_student_or_admin`, and `verify_any_user`.
- Return detailed HTTP 401 Unauthorized / HTTP 403 Forbidden exceptions for non-compliant requests.

#### [NEW] [audit_middleware.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/audit_middleware.py)
- Implement an ASGI HTTP middleware that intercepts all API requests.
- Track metrics: user ID, endpoint, request method, status code, execution duration (ms), and client IP.
- Print structured audit logs and simulate writes to the audit database client.

#### [MODIFY] [main.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/main.py)
- Integrate the auditing middleware using `app.add_middleware()`.
- Add FastAPI dependencies (`Depends(verify_admin)`) to `/api/research` and `/api/save`.
- Add dependencies (`Depends(verify_student_or_admin)`) to `/api/predict`, `/api/chatbot`, and `/api/clusters`.
- Expose an `/api/audit-logs` endpoint (restricted to Admins) to view platform activity trails.

#### [MODIFY] [requirements.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/backend/requirements.txt)
- Add PyJWT for JSON Web Token signature verification and parsing.

---

### Frontend Component (React, Tailwind, & Vite)

#### [NEW] [AuthContext.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/frontend/src/context/AuthContext.tsx)
- Create a React Context provider (`AuthContext`) managing the logged-in user state.
- Expose properties: `user` (with fields `name`, `role`, `email`), `setRole(role)`, and `isAuthenticated`.
- Pre-populate roles: `Admin`, `Student`, `Recruiter`, `Guest`.

#### [NEW] [ProtectedRoute.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/frontend/src/components/ProtectedRoute.tsx)
- Implement a route-guard component wrapping pages in the React Router tree.
- Validate if the active role is permitted inside the `allowedRoles` array.
- Redirect unauthorized users to a clean `/unauthorized` explanation landing page.

#### [NEW] [RoleSwitcher.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/frontend/src/components/layout/RoleSwitcher.tsx)
- Design a premium glassmorphic dropdown UI component for the header that lets the user switch their session role (for testing).

#### [MODIFY] [App.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/frontend/src/App.tsx)
- Wrap the main application structure inside `<AuthProvider>`.
- Restructure React Router routes:
  - Wrap `/chatbot` and `/ml-analytics` under Student & Admin access permissions.
  - Require Admin role for accessing ingestion pipelines.
  - Enable general access for Dashboard and list views.

#### [MODIFY] [AppLayout.tsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX/activity-08/frontend/src/components/layout/AppLayout.tsx)
- Intercept the side navigation menu items and filter links according to the current role (e.g., hide "Analytics" or "Chatbot" from unauthorized users).
- Include the new `<RoleSwitcher />` component in the sidebar/header.

---

## Verification Plan

### Automated Verification
- Run local Pytest suite to verify route response codes when headers match / mismatch expected roles.
- Run frontend builds to verify typescript compilation.

### Manual Verification
1. Start the backend with `uvicorn main:app` and frontend with `npm run dev`.
2. Browse the dashboard in Guest mode. Verify that private pages (Chatbot, Analytics) block access.
3. Switch user role to **Student** in the header. Verify that the RAG Chatbot and Predictive Analytics pages become accessible. Verify that the "Trigger Ingestion" button is hidden.
4. Switch user role to **Admin**. Verify that the Admin Research features are visible and fully functional.
5. Review the backend shell logging to verify that request audit trails are correctly captured for every page access.
