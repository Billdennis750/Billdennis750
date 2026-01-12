# Payment Gateway Webhook Security Implementation

## Overview

This document describes the comprehensive webhook security implementation for the Cashflow MFB payment integrations.

## Current Provider: OTPay (otpay.ng)

OTPay is a Nigerian virtual account payment gateway that enables bank transfer payments.

### Payment Flow
1. **Create Virtual Account** → Customer receives unique bank account details
2. **Customer Transfers** → Customer sends exact amount to the virtual account
3. **Webhook Notification** → OTPay sends webhook when payment is received
4. **Auto-Confirmation** → System updates application status automatically

### OTPay Webhook IPs (Official)
```
IPv4: 185.31.40.25
IPv6: 2a00:b6e0:1:20:16::1
```

## Security Measures Implemented

### 1. IP Allowlisting ✅

```python
# OTPay Official Webhook IPs (from documentation)
OTPAY_WEBHOOK_IPS = {"185.31.40.25", "2a00:b6e0:1:20:16::1"}

# Verification in webhook handler
if client_ip not in OTPAY_WEBHOOK_IPS:
    raise HTTPException(status_code=403, detail="Unauthorized IP")
```

### 2. TLS/HTTPS Enforcement ✅

```python
def verify_tls(request):
    # Checks X-Forwarded-Proto header (for proxied requests)
    # and direct URL scheme for HTTPS
```

### 3. Rate Limiting ✅

```python
MAX_WEBHOOKS_PER_MINUTE = 100

# Limits webhooks to 100 per IP per minute
# Prevents DDoS and brute-force attacks
```

### 4. Replay Attack Prevention ✅

```python
# Stores processed webhook references in memory
# Rejects webhooks older than 5 minutes
# Rejects duplicate references within 1 hour
```

### 5. Comprehensive Audit Logging ✅

Every webhook event is logged with:
- Timestamp
- Client IP
- Transaction reference
- Status (success/failed/rejected)
- User-Agent
- Full payload for debugging

## Configuration

### Environment Variables (.env)

```bash
# OTPay Payment Gateway (Primary)
OTPAY_API_KEY="APIKEY-xxx"
OTPAY_SECRET_KEY="SECKEY-xxx"
OTPAY_BUSINESS_CODE="xxx"
OTPAY_BASE_URL="https://otpay.ng/api/v1"

# OTPay Official Webhook IPs
OTPAY_WEBHOOK_IPS="185.31.40.25,2a00:b6e0:1:20:16::1"
```

### Webhook URL Configuration

Set this URL in your OTPay merchant dashboard (Developer > Webhook URL):
```
https://cashflowsmfb.com/api/payments/webhook
```

## OTPay Webhook Payload Format

```json
{
  "email": "customer@example.com",
  "phone": "09012345678",
  "business_code": "XXXXXXXXXX",
  "account_number": "6680269830",
  "customer_account_name": "John Doe - [BLM DATA SOLUTIONS LTD](OT-PAY)",
  "customer_account_bank": "PALMPAY",
  "amount": 2500,
  "date": "2025-01-12 14:05:00",
  "transaction_reference": "MIXXXXXXXXXXXXXXXXX",
  "customer_senderbankname": "OPAY",
  "customer_senderaccountnumber": "****1234",
  "customer_sendername": "JOHN DOE"
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payments/initiate` | POST | Create virtual account for payment |
| `/api/payments/verify` | POST | Check payment status |
| `/api/payments/webhook` | POST | Receive OTPay notifications |
| `/api/payments/virtual-account/{app_id}` | GET | Get virtual account details |
| `/api/payments/transaction/{ref}` | GET | Get transaction details |

## Legacy Providers (Deprecated)

### BudPay
- Status: Deprecated
- Reason: Replaced by OTPay per user request

### Xixapay
- Status: Deprecated
- Reason: Replaced by BudPay, then OTPay

## Compliance Notes

1. **PCI-DSS**: No card data is stored; OTPay handles all sensitive payment info
2. **Data Retention**: Webhook audit logs should be retained per regulatory requirements
3. **Encryption**: All data transmitted over TLS 1.2+
4. **Access Control**: Webhook endpoint only accepts POST from verified OTPay IPs
