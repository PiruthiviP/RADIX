import re
import pytest
from typing import Dict, Any, Tuple, Optional
from unittest.mock import MagicMock, patch

# Regex patterns matching metadata constraints exactly
LOGO_RE = re.compile(r"^https?:\/\/.*\.(?:png|jpg|jpeg|svg|webp)(?:\?.*)?$")
WEBSITE_RE = re.compile(r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$")
LINKEDIN_COMPANY_RE = re.compile(r"^https?:\/\/(www\.)?linkedin\.com\/company\/[A-Za-z0-9_\-]+\/?$")
LINKEDIN_PROFILE_RE = re.compile(r"^https?:\/\/(www\.)?linkedin\.com\/in\/[A-Za-z0-9_\-]+\/?$")
VIDEO_RE = re.compile(r"^https?:\/\/(www\.)?(youtube\.com|vimeo\.com|youtu\.be)\/.*$")

class MockNetworkClient:
    """Simulates active HTTP request connections to evaluate URL validity on the wire."""
    def __init__(self):
        self.mock_web_registry = {
            "https://microsoft.com": {"status_code": 200, "content_type": "text/html"},
            "https://example.com/logo.png": {"status_code": 200, "content_type": "image/png"},
            "https://example.com/document.pdf": {"status_code": 200, "content_type": "application/pdf"},
            "https://linkedin.com/company/microsoft": {"status_code": 200, "content_type": "text/html"},
            "https://linkedin.com/in/satyanadella": {"status_code": 200, "content_type": "text/html"},
            "https://youtube.com/watch?v=123": {"status_code": 200, "content_type": "text/html"},
            "https://redirecting-site.com": {"status_code": 301, "redirect_to": "https://microsoft.com"},
            "https://brokenlink404.com": {"status_code": 404},
            "https://linkedin.com/company/deleted-page-404": {"status_code": 404},
            "https://youtube.com/watch?v=deletedvideo": {"status_code": 404}
        }

    def request(self, method: str, url: str, follow_redirects: bool = True) -> Dict[str, Any]:
        target_url = url.strip()
        response = self.mock_web_registry.get(target_url, {"status_code": 404})
        
        if response.get("status_code") in (301, 302) and follow_redirects:
            redirect_url = response.get("redirect_to")
            return self.request(method, redirect_url)
            
        return response

# Instantiate our mock client
network_client = MockNetworkClient()

def validate_website_url(url: str) -> Tuple[bool, str]:
    """Validates Website URL regex and active HTTP resolution (supporting redirects)."""
    if not WEBSITE_RE.match(url):
        return False, "Regex Error: Invalid URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid Website URL resolved successfully."
    return False, f"Connection Error: Server returned status {response.get('status_code')}."

def validate_logo_url(url: str) -> Tuple[bool, str]:
    """Validates Logo URL regex, active HTTP resolution, and image MIME-type."""
    if not LOGO_RE.match(url):
        return False, "Regex Error: Invalid Logo file extension/URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") != 200:
        return False, f"Connection Error: Server returned status {response.get('status_code')}."
        
    mime_type = response.get("content_type", "")
    if not mime_type.startswith("image/"):
        return False, f"Format Error: Resolved URL content-type is '{mime_type}', not a valid image format."
        
    return True, "Valid Logo image resolved successfully."

def validate_linkedin_url(url: str, is_company: bool = True) -> Tuple[bool, str]:
    """Validates LinkedIn URL structure and active profile resolution."""
    regex = LINKEDIN_COMPANY_RE if is_company else LINKEDIN_PROFILE_RE
    if not regex.match(url):
        return False, "Regex Error: Invalid LinkedIn profile URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid profile route resolved successfully."
    return False, f"Routing Error: Profile route returned status {response.get('status_code')}."

def validate_video_url(url: str) -> Tuple[bool, str]:
    """Validates video platform URL structure and active routing."""
    if not VIDEO_RE.match(url):
        return False, "Regex Error: Invalid video platform URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid video route resolved successfully."
    return False, f"Routing Error: Video route returned status {response.get('status_code')}."


# --- Pytest Tests ---

def test_valid_website_url_resolves():
    """Verifies that an active, properly formatted website URL passes validation."""
    success, msg = validate_website_url("https://microsoft.com")
    assert success is True
    assert "resolved successfully" in msg

def test_redirected_website_url_resolves():
    """Verifies that the validation layer follows redirects (301/302) to verify the final destination."""
    success, msg = validate_website_url("https://redirecting-site.com")
    assert success is True
    assert "resolved successfully" in msg

def test_broken_website_url_fails():
    """Verifies that unresolvable website URLs are caught and rejected."""
    success, msg = validate_website_url("https://brokenlink404.com")
    assert success is False
    assert "status 404" in msg

def test_valid_logo_image_resolves():
    """Verifies that logo image links resolving to active image files pass validation."""
    success, msg = validate_logo_url("https://example.com/logo.png")
    assert success is True
    assert "image resolved successfully" in msg

def test_logo_pointing_to_non_image_fails():
    """Verifies that logo image links pointing to non-image resources (like PDFs) are rejected."""
    success, msg = validate_logo_url("https://example.com/document.pdf")
    assert success is False
    assert "not a valid image format" in msg

def test_deleted_linkedin_page_fails():
    """Verifies that unresolvable social media routes are caught and rejected."""
    success, msg = validate_linkedin_url("https://linkedin.com/company/deleted-page-404", is_company=True)
    assert success is False
    assert "returned status 404" in msg

def test_deleted_marketing_video_fails():
    """Verifies that unresolvable video marketing routes are caught and rejected."""
    success, msg = validate_video_url("https://youtube.com/watch?v=deletedvideo")
    assert success is False
    assert "returned status 404" in msg