# BudPay Webhook Security Implementation

## Overview

This document describes the comprehensive webhook security implementation for the Cashflow MFB BudPay integration.

## Security Measures Implemented

### 1. HMAC Signature Verification ✅

```python
# Location: /app/backend/utils/webhook_security.py

def verify_webhook_signature(request, payload, secret_key):
    """
    Verifies HMAC-SHA512 signature using constant-time comparison
    to prevent timing attacks.
    """
    signature = request.headers.get("x-budpay-signature")
    expected = hmac.new(secret_key.encode(), payload, hashlib.sha512).hexdigest()
    return hmac.compare_digest(signature.lower(), expected.lower())
```

**Configuration:**
- `BUDPAY_WEBHOOK_SECRET` in `.env` for separate webhook signing key
- Falls back to `BUDPAY_SECRET_KEY` if not set

### 2. TLS/HTTPS Enforcement ✅

```python
def verify_tls(request):
    """
    Checks X-Forwarded-Proto header (for proxied requests)
    and direct URL scheme for HTTPS.
    """
    # Checks: X-Forwarded-Proto, request.url.scheme
    # Allows HTTP only for localhost development
```

### 3. IP Allowlisting ✅

```python
# Configuration in .env:
BUDPAY_WEBHOOK_IPS="52.31.139.75,52.49.173.169,52.214.14.220"

# Supports:
# - Individual IPs: "52.31.139.75"
# - CIDR blocks: "52.31.139.0/24"
# - Multiple values: comma-separated
```

**Important:** Contact BudPay support to get their official webhook IPs.

### 4. Replay Attack Prevention ✅

```python
def check_replay_attack(reference, timestamp):
    """
    - Stores processed webhook references in memory
    - Rejects webhooks older than 5 minutes (MAX_WEBHOOK_AGE_SECONDS)
    - Rejects duplicate references within 1 hour
    """
```

### 5. Rate Limiting ✅

```python
MAX_WEBHOOKS_PER_MINUTE = 100

def check_rate_limit(client_ip):
    """
    Limits webhooks to 100 per IP per minute.
    Prevents DDoS and brute-force attacks.
    """
```

### 6. Audit Logging ✅

Every webhook event is logged with:
- Timestamp
- Client IP
- Reference
- Status (success/failed/rejected)
- User-Agent
- Security report

```json
{
  "timestamp": "2026-01-10T16:58:36.701695+00:00",
  "event_type": "webhook_received",
  "client_ip": "52.31.139.75",
  "reference": "CASHFLOW-LOAN-2025-002-abc123",
  "status": "success",
  "user_agent": "BudPay-Webhook/1.0",
  "details": {
    "tls_verified": true,
    "ip_allowed": true,
    "signature_valid": true
  }
}
```

## Configuration

### Environment Variables (.env)

```bash
# BudPay Webhook Security
BUDPAY_WEBHOOK_IPS=""        # Comma-separated IPs/CIDRs
BUDPAY_WEBHOOK_SECRET=""     # Optional signing secret
```

### Strict Mode (Production)

In `/app/backend/routers/payments.py`:

```python
# Set these to True for production
REQUIRE_WEBHOOK_SIGNATURE = True   # Reject without valid signature
REQUIRE_IP_ALLOWLIST = True        # Reject from non-allowed IPs
```

## Webhook URL Configuration

### For Production (Dedicated Subdomain)

Configure in BudPay Dashboard:
```
https://webhooks.cashflowsmfb.com/api/payments/webhook
```

**DNS Configuration Required:**
1. Create A record: `webhooks.cashflowsmfb.com` → Your server IP
2. Configure SSL certificate for the subdomain
3. Set up nginx/reverse proxy to route to your backend

### For Current Setup

```
https://cashflowsmfb.com/api/payments/webhook
```

## Security Flow

```
BudPay Server
     │
     ▼
┌─────────────────────────────────────────────────┐
│  1. TLS Verification                            │
│     - Check HTTPS connection                    │
│     - Verify X-Forwarded-Proto header           │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  2. IP Allowlist Check                          │
│     - Extract client IP (X-Forwarded-For)       │
│     - Verify against BUDPAY_WEBHOOK_IPS         │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  3. Rate Limiting                               │
│     - Check requests per minute per IP          │
│     - Reject if > 100/minute                    │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  4. Signature Verification                      │
│     - Compute HMAC-SHA512 of payload            │
│     - Compare with x-budpay-signature header    │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  5. Replay Attack Check                         │
│     - Check if reference already processed      │
│     - Verify timestamp is within 5 minutes      │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  6. Process Webhook                             │
│     - Parse payload                             │
│     - Update transaction status                 │
│     - Send confirmation emails                  │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  7. Audit Log                                   │
│     - Log all details for compliance            │
└─────────────────────────────────────────────────┘
```

## Testing Webhook Security

```bash
# Test with mock webhook (should be rejected without proper setup)
curl -X POST https://cashflowsmfb.com/api/payments/webhook \
  -H "Content-Type: application/json" \
  -H "x-budpay-signature: invalid_signature" \
  -d '{"notify":"transaction","notifyType":"successful","data":{"reference":"TEST-001","status":"success"}}'

# Expected: 403 Forbidden (when REQUIRE_WEBHOOK_SIGNATURE=True)
```

## Compliance Notes

1. **PCI-DSS**: No card data is stored; BudPay handles all sensitive payment info
2. **Data Retention**: Webhook audit logs should be retained per regulatory requirements
3. **Encryption**: All data transmitted over TLS 1.2+
4. **Access Control**: Webhook endpoint only accepts POST from verified sources

## Next Steps for Production

1. **Contact BudPay Support** to get official webhook IP addresses
2. **Configure `BUDPAY_WEBHOOK_IPS`** with the provided IPs
3. **Enable strict mode** by setting:
   - `REQUIRE_WEBHOOK_SIGNATURE = True`
   - `REQUIRE_IP_ALLOWLIST = True`
4. **Set up dedicated webhook subdomain** (`webhooks.cashflowsmfb.com`)
5. **Configure Redis** for rate limiting and replay prevention (currently in-memory)
6. **Set up log aggregation** for webhook audit logs (CloudWatch, ELK, etc.)
