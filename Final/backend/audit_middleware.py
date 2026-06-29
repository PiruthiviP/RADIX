# ====================================================================
# RADIX Enterprise API Request Auditing Middleware
# Place in: activity-08/backend/audit_middleware.py
# ====================================================================

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("AuditTrail")

# Create a dedicated console/file handler for compliance auditing
audit_handler = logging.StreamHandler()
audit_formatter = logging.Formatter(
    "[AUDIT COMPLIANCE] %(asctime)s - User: %(message)s"
)
audit_handler.setFormatter(audit_formatter)
audit_logger = logging.getLogger("AuditComplianceLog")
audit_logger.setLevel(logging.INFO)
# Avoid duplicating audits in general server outputs
audit_logger.propagate = False 
if not audit_logger.handlers:
    audit_logger.addHandler(audit_handler)

# Keep an in-memory queue of recent logs for visualization
recent_audit_records = []

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Initialize default state
        request.state.user = {
            "id": "anonymous",
            "email": "anonymous@radix.edu",
            "role": "Guest"
        }
        
        start_time = time.time()
        
        # Execute request downstream
        response = await call_next(request)
        
        duration = time.time() - start_time
        duration_ms = int(duration * 1000)
        
        # Extract user context populated during auth guards processing
        user_ctx = getattr(request.state, "user", {
            "id": "anonymous",
            "email": "anonymous@radix.edu",
            "role": "Guest"
        })
        
        # Skip auditing documentation / auto-generated pages
        path = request.url.path
        if path in ("/docs", "/openapi.json", "/favicon.ico", "/"):
            return response
            
        client_ip = request.client.host if request.client else "unknown_ip"
        
        # Create Structured compliance log message
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_ctx.get("id"),
            "email": user_ctx.get("email"),
            "role": user_ctx.get("role"),
            "method": request.method,
            "endpoint": path,
            "status_code": response.status_code,
            "latency_ms": duration_ms,
            "ip_address": client_ip
        }
        
        # Print audit logging to console for security analysis
        audit_msg = (
            f"Email: {log_entry['email']} | Role: {log_entry['role']} | "
            f"Action: {log_entry['method']} {log_entry['endpoint']} | "
            f"Status: {log_entry['status_code']} | Latency: {log_entry['latency_ms']}ms | IP: {log_entry['ip_address']}"
        )
        audit_logger.info(audit_msg)
        
        # Push to in-memory audit trail cache for admin viewing
        recent_audit_records.insert(0, log_entry)
        if len(recent_audit_records) > 100:
            recent_audit_records.pop()
            
        return response
