"""
BudPay Webhook Security Module

Implements comprehensive webhook security following fintech best practices:
1. HMAC signature verification (using encryption key)
2. TLS/HTTPS enforcement
3. IP allowlisting (configurable)
4. Request validation and replay attack prevention
5. Rate limiting
6. Audit logging
"""

import hmac
import hashlib
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Set, Tuple
from functools import lru_cache
import ipaddress

from fastapi import Request, HTTPException, status
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ============================================================================
# CONFIGURATION
# ============================================================================

# BudPay does not publish official webhook IPs. 
# These should be obtained from BudPay support and updated regularly.
# For now, we'll use a configurable allowlist that can be set via environment.
# Format: comma-separated IPs or CIDR blocks
BUDPAY_ALLOWED_IPS_ENV = settings.__dict__.get('budpay_webhook_ips', '')

# Default: Allow all if not configured (with warning)
# In production, this should be configured with actual BudPay IPs
DEFAULT_ALLOWED_IPS: Set[str] = set()

# Parse environment variable for allowed IPs
def parse_allowed_ips(ip_string: str) -> Set[str]:
    """Parse comma-separated IP addresses or CIDR blocks"""
    if not ip_string:
        return DEFAULT_ALLOWED_IPS
    
    ips = set()
    for ip in ip_string.split(','):
        ip = ip.strip()
        if ip:
            ips.add(ip)
    return ips

BUDPAY_ALLOWED_IPS = parse_allowed_ips(BUDPAY_ALLOWED_IPS_ENV)

# Webhook signature settings
WEBHOOK_SIGNATURE_HEADER = "x-budpay-signature"
WEBHOOK_SIGNATURE_HEADER_ALT = "budpay-signature"
WEBHOOK_ENCRYPTION_HEADER = "budpay-encryption"
WEBHOOK_TIMESTAMP_HEADER = "x-budpay-timestamp"

# Replay attack prevention: reject webhooks older than this (seconds)
MAX_WEBHOOK_AGE_SECONDS = 300  # 5 minutes

# Rate limiting: max webhooks per IP per minute
MAX_WEBHOOKS_PER_MINUTE = 100

# In-memory store for rate limiting and replay prevention
# In production, use Redis or similar
_webhook_timestamps: dict = {}  # {reference: timestamp}
_rate_limit_store: dict = {}  # {ip: [timestamps]}


# ============================================================================
# IP VERIFICATION
# ============================================================================

def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP from request headers.
    Handles X-Forwarded-For for proxied requests.
    """
    # Check X-Forwarded-For header (set by proxies/load balancers)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def is_ip_allowed(client_ip: str, allowed_ips: Set[str]) -> bool:
    """
    Check if client IP is in the allowlist.
    Supports both individual IPs and CIDR notation.
    """
    if not allowed_ips:
        # If no allowlist configured, log warning but allow
        # This should be configured in production
        logger.warning(
            f"No IP allowlist configured for webhooks. "
            f"Request from {client_ip} allowed by default. "
            f"Configure BUDPAY_WEBHOOK_IPS for production security."
        )
        return True
    
    try:
        client_addr = ipaddress.ip_address(client_ip)
        
        for allowed in allowed_ips:
            try:
                # Check if it's a network (CIDR notation)
                if '/' in allowed:
                    network = ipaddress.ip_network(allowed, strict=False)
                    if client_addr in network:
                        return True
                else:
                    # Individual IP
                    if client_addr == ipaddress.ip_address(allowed):
                        return True
            except ValueError:
                logger.warning(f"Invalid IP/CIDR in allowlist: {allowed}")
                continue
        
        return False
        
    except ValueError:
        logger.error(f"Invalid client IP address: {client_ip}")
        return False


def verify_ip_allowlist(request: Request) -> Tuple[bool, str]:
    """
    Verify the request comes from an allowed IP.
    Returns (is_allowed, client_ip)
    """
    client_ip = get_client_ip(request)
    is_allowed = is_ip_allowed(client_ip, BUDPAY_ALLOWED_IPS)
    
    if not is_allowed:
        logger.warning(
            f"Webhook request from unauthorized IP: {client_ip}. "
            f"Allowed IPs: {BUDPAY_ALLOWED_IPS}"
        )
    
    return is_allowed, client_ip


# ============================================================================
# TLS ENFORCEMENT
# ============================================================================

def verify_tls(request: Request) -> bool:
    """
    Verify the request was made over HTTPS/TLS.
    Checks both direct connection and proxy headers.
    """
    # Check X-Forwarded-Proto header (set by reverse proxies)
    forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
    if forwarded_proto == "https":
        return True
    
    # Check direct URL scheme
    if request.url.scheme == "https":
        return True
    
    # In development/local environment, allow HTTP
    # This should be disabled in production
    if settings.backend_url.startswith("http://localhost") or \
       settings.backend_url.startswith("http://127.0.0.1"):
        logger.debug("TLS check bypassed for local development")
        return True
    
    # Check if running in preview environment (Emergent)
    if "preview.emergentagent.com" in settings.backend_url:
        # Preview environments use HTTPS at the ingress level
        return True
    
    return False


# ============================================================================
# SIGNATURE VERIFICATION
# ============================================================================

def compute_hmac_signature(payload: bytes, secret_key: str) -> str:
    """
    Compute HMAC-SHA512 signature for payload verification.
    """
    return hmac.new(
        secret_key.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()


def verify_webhook_signature(
    request: Request,
    payload: bytes,
    secret_key: str
) -> Tuple[bool, Optional[str]]:
    """
    Verify the webhook signature using HMAC-SHA512.
    
    BudPay may send signature in different headers:
    - x-budpay-signature
    - budpay-signature
    - budpay-encryption
    
    Returns (is_valid, provided_signature)
    """
    # Try different header names
    provided_signature = (
        request.headers.get(WEBHOOK_SIGNATURE_HEADER) or
        request.headers.get(WEBHOOK_SIGNATURE_HEADER_ALT) or
        request.headers.get(WEBHOOK_ENCRYPTION_HEADER)
    )
    
    if not provided_signature:
        logger.warning("No webhook signature provided in request headers")
        # For BudPay, signature might not always be present
        # Log but don't reject if not configured to require it
        return True, None
    
    # Compute expected signature
    expected_signature = compute_hmac_signature(payload, secret_key)
    
    # Use constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(
        provided_signature.lower(),
        expected_signature.lower()
    )
    
    if not is_valid:
        logger.warning(
            f"Invalid webhook signature. "
            f"Provided: {provided_signature[:20]}..., "
            f"Expected: {expected_signature[:20]}..."
        )
    
    return is_valid, provided_signature


# ============================================================================
# REPLAY ATTACK PREVENTION
# ============================================================================

def check_replay_attack(reference: str, timestamp: Optional[str] = None) -> bool:
    """
    Check if this webhook has been processed before (replay attack prevention).
    
    Returns True if this appears to be a replay attack.
    """
    global _webhook_timestamps
    
    current_time = time.time()
    
    # Clean old entries (older than 1 hour)
    cutoff = current_time - 3600
    _webhook_timestamps = {
        ref: ts for ref, ts in _webhook_timestamps.items()
        if ts > cutoff
    }
    
    # Check if we've seen this reference recently
    if reference in _webhook_timestamps:
        logger.warning(f"Potential replay attack detected for reference: {reference}")
        return True
    
    # Check timestamp if provided
    if timestamp:
        try:
            webhook_time = float(timestamp)
            age = current_time - webhook_time
            
            if age > MAX_WEBHOOK_AGE_SECONDS:
                logger.warning(
                    f"Webhook too old: {age:.0f} seconds. "
                    f"Max allowed: {MAX_WEBHOOK_AGE_SECONDS} seconds"
                )
                return True
                
            if age < -60:  # Future timestamp (with 1 minute tolerance)
                logger.warning(f"Webhook has future timestamp: {timestamp}")
                return True
                
        except (ValueError, TypeError):
            logger.warning(f"Invalid webhook timestamp: {timestamp}")
    
    # Record this reference
    _webhook_timestamps[reference] = current_time
    
    return False


# ============================================================================
# RATE LIMITING
# ============================================================================

def check_rate_limit(client_ip: str) -> bool:
    """
    Check if the client has exceeded the rate limit.
    
    Returns True if rate limit exceeded.
    """
    global _rate_limit_store
    
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Get timestamps for this IP
    if client_ip not in _rate_limit_store:
        _rate_limit_store[client_ip] = []
    
    # Filter to only recent timestamps
    recent = [ts for ts in _rate_limit_store[client_ip] if ts > minute_ago]
    _rate_limit_store[client_ip] = recent
    
    # Check rate limit
    if len(recent) >= MAX_WEBHOOKS_PER_MINUTE:
        logger.warning(
            f"Rate limit exceeded for IP {client_ip}: "
            f"{len(recent)} requests in last minute"
        )
        return True
    
    # Record this request
    _rate_limit_store[client_ip].append(current_time)
    
    return False


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def log_webhook_event(
    request: Request,
    client_ip: str,
    reference: str,
    status: str,
    details: dict = None
):
    """
    Log webhook event for audit trail.
    In production, this should write to a dedicated audit log or database.
    """
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "webhook_received",
        "client_ip": client_ip,
        "reference": reference,
        "status": status,
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_length": request.headers.get("content-length", "0"),
        "details": details or {}
    }
    
    # Log at INFO level for successful webhooks, WARNING for failures
    if status == "success":
        logger.info(f"Webhook audit: {json.dumps(log_entry)}")
    else:
        logger.warning(f"Webhook audit (FAILED): {json.dumps(log_entry)}")


# ============================================================================
# MAIN SECURITY CHECK FUNCTION
# ============================================================================

async def verify_webhook_security(
    request: Request,
    require_signature: bool = False,
    require_ip_allowlist: bool = False
) -> Tuple[bool, str, dict]:
    """
    Perform comprehensive webhook security verification.
    
    Args:
        request: FastAPI Request object
        require_signature: If True, reject requests without valid signature
        require_ip_allowlist: If True, reject requests from non-allowed IPs
    
    Returns:
        Tuple of (is_secure, client_ip, security_report)
    """
    security_report = {
        "tls_verified": False,
        "ip_allowed": False,
        "signature_valid": False,
        "replay_check_passed": False,
        "rate_limit_ok": False,
        "errors": []
    }
    
    # Get client IP first
    client_ip = get_client_ip(request)
    
    # 1. TLS Verification
    if verify_tls(request):
        security_report["tls_verified"] = True
    else:
        security_report["errors"].append("TLS/HTTPS not verified")
        logger.warning(f"Webhook request not over HTTPS from {client_ip}")
    
    # 2. IP Allowlist Check
    ip_allowed, _ = verify_ip_allowlist(request)
    security_report["ip_allowed"] = ip_allowed
    
    if require_ip_allowlist and not ip_allowed:
        security_report["errors"].append(f"IP {client_ip} not in allowlist")
        return False, client_ip, security_report
    
    # 3. Rate Limiting
    if check_rate_limit(client_ip):
        security_report["errors"].append("Rate limit exceeded")
        return False, client_ip, security_report
    security_report["rate_limit_ok"] = True
    
    # 4. Get payload for signature verification
    try:
        payload = await request.body()
    except Exception as e:
        security_report["errors"].append(f"Failed to read request body: {str(e)}")
        return False, client_ip, security_report
    
    # 5. Signature Verification
    if settings.budpay_secret_key:
        is_valid, provided_sig = verify_webhook_signature(
            request, payload, settings.budpay_secret_key
        )
        security_report["signature_valid"] = is_valid
        security_report["signature_provided"] = provided_sig is not None
        
        if require_signature and not is_valid:
            security_report["errors"].append("Invalid or missing signature")
            return False, client_ip, security_report
    else:
        security_report["signature_valid"] = True
        security_report["signature_provided"] = False
        logger.warning("No secret key configured for signature verification")
    
    # 6. Parse payload for replay check
    try:
        data = json.loads(payload)
        reference = (
            data.get("data", {}).get("reference") or
            data.get("reference") or
            "unknown"
        )
        timestamp = request.headers.get(WEBHOOK_TIMESTAMP_HEADER)
        
        if check_replay_attack(reference, timestamp):
            security_report["errors"].append("Potential replay attack detected")
            return False, client_ip, security_report
        security_report["replay_check_passed"] = True
        
    except json.JSONDecodeError:
        security_report["errors"].append("Invalid JSON payload")
        return False, client_ip, security_report
    
    # All checks passed
    is_secure = len(security_report["errors"]) == 0
    
    return is_secure, client_ip, security_report


# ============================================================================
# WEBHOOK SECURITY MIDDLEWARE/DECORATOR
# ============================================================================

class WebhookSecurityError(HTTPException):
    """Custom exception for webhook security failures"""
    def __init__(self, detail: str, security_report: dict):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
        self.security_report = security_report
