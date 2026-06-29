# ====================================================================
# RADIX Security Guard & Role-Based Access Control (RBAC) Dependency
# Place in: activity-08/backend/auth_guards.py
# ====================================================================

import os
import logging
import jwt
from typing import Optional, List
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SUPABASE_KEY

logger = logging.getLogger("AuthGuards")

# Initialize the token parser
security = HTTPBearer(auto_error=False)

# In production, Supabase uses HS256 with the Supabase JWT secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET") or SUPABASE_KEY or "radix-development-jwt-fallback-secret-key-12345"

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Decodes the user context from the incoming request.
    Supports:
    1. Authorization Bearer Token (Supabase JWT format).
    2. Fallback testing headers: 'X-User-Role' and 'X-User-Email' for instant local switching.
    """
    # 1. Check for standard HTTP Authorization Bearer Token
    if credentials:
        token = credentials.credentials
        try:
            # Decode JWT token (Supabase auth JWT format)
            payload = jwt.decode(
                token, 
                SUPABASE_JWT_SECRET, 
                algorithms=["HS256"], 
                options={"verify_aud": False}
            )
            
            # Map claims (Supabase puts role in user_metadata or app_metadata)
            user_metadata = payload.get("user_metadata", {})
            role = user_metadata.get("role") or payload.get("role") or "Student"
            email = payload.get("email") or "unknown@radix.edu"
            user_id = payload.get("sub") or "unknown_id"
            
            user_ctx = {"id": user_id, "email": email, "role": role}
            # Attach to request state for audit middleware access
            request.state.user = user_ctx
            return user_ctx
            
        except jwt.PyJWTError as e:
            logger.warning(f"Failed JWT authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}"
            )

    # 2. Check for development/test headers (sent by Frontend Role Switcher)
    role_header = request.headers.get("X-User-Role")
    email_header = request.headers.get("X-User-Email")
    
    if role_header:
        user_ctx = {
            "id": "mock_dev_user_uuid_1234",
            "email": email_header or "dev_user@radix.edu",
            "role": role_header
        }
        request.state.user = user_ctx
        return user_ctx

    # 3. Default to guest mode / reject if no auth headers provided
    user_ctx = {
        "id": "anonymous_visitor",
        "email": "anonymous@radix.edu",
        "role": "Guest"
    }
    request.state.user = user_ctx
    return user_ctx


class RoleRequirement:
    """Enforces specific role rules on endpoints."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role")
        if user_role not in self.allowed_roles:
            logger.warning(f"Access Denied: User role '{user_role}' not in allowed roles {self.allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{user_role}' is not authorized to perform this operation."
            )
        return user

# Helper dependency mappings
verify_admin = RoleRequirement(["Admin", "LeadAnalyst"])
verify_student_or_admin = RoleRequirement(["Student", "Admin", "LeadAnalyst"])
verify_recruiter_or_admin = RoleRequirement(["Recruiter", "Admin", "LeadAnalyst"])
verify_any_auth = RoleRequirement(["Student", "Recruiter", "Admin", "LeadAnalyst"])
verify_all_roles = RoleRequirement(["Student", "Recruiter", "Admin", "Guest", "LeadAnalyst"])
