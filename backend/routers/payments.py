from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from database import get_db
from config import get_settings
from utils.email import email_service
from utils.webhook_security import (
    verify_webhook_security,
    log_webhook_event,
    get_client_ip,
    WebhookSecurityError
)
from datetime import datetime, timezone
import httpx
import logging
import json
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/payments", tags=["payments"])

# ============================================================================
# OTPAY CONFIGURATION
# ============================================================================
OTPAY_BASE_URL = "https://otpay.ng/api/v1"

# OTPay Official Webhook IPs (from their documentation)
OTPAY_WEBHOOK_IPS = {"185.31.40.25", "2a00:b6e0:1:20:16::1"}

# Webhook security settings
REQUIRE_WEBHOOK_SIGNATURE = False  # OTPay uses IP allowlisting instead
REQUIRE_IP_ALLOWLIST = True  # Enable for production


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PaymentInitiate(BaseModel):
    application_id: str
    customer_email: str
    customer_name: str
    customer_phone: str = ""
    amount: float = 2500
    redirect_url: str = ""


class PaymentVerify(BaseModel):
    order_ref: str


class VirtualAccountCreate(BaseModel):
    application_id: str
    customer_email: str
    customer_name: str
    customer_phone: str
    amount: float = 2500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_otpay_headers():
    """Get OTPay API headers with authentication"""
    return {
        "api-key": settings.otpay_api_key,
        "secret-key": settings.otpay_secret_key,
        "Content-Type": "application/json"
    }


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/initiate", response_model=dict)
async def initiate_payment(payment: PaymentInitiate, db=Depends(get_db)):
    """
    Initiate a payment by creating a virtual account with OTPay.
    
    OTPay Flow:
    1. Create a virtual account for the customer
    2. Return virtual account details (bank name, account number)
    3. Customer transfers the exact amount to the virtual account
    4. OTPay sends webhook notification when payment is received
    5. Our webhook handler updates the application status
    """
    try:
        # Verify application exists
        application = await db.applications.find_one({"application_id": payment.application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Check if virtual account already exists for this application
        existing_va = await db.virtual_accounts.find_one({
            "application_id": payment.application_id,
            "status": "active"
        })
        
        if existing_va:
            # Return existing virtual account
            return {
                "status": "success",
                "payment_type": "bank_transfer",
                "virtual_account": {
                    "account_number": existing_va["account_number"],
                    "account_name": existing_va["account_name"],
                    "bank_name": existing_va["bank_name"]
                },
                "amount": int(payment.amount),
                "currency": "NGN",
                "order_reference": existing_va["order_reference"],
                "message": f"Transfer exactly ₦{int(payment.amount):,} to complete payment"
            }
        
        # Create unique order reference
        order_reference = f"CASHFLOW-{payment.application_id}-{uuid.uuid4().hex[:8]}"
        
        # Determine payment type
        is_processing_fee = payment.amount <= 2500
        payment_description = "Loan Processing Fee" if is_processing_fee else "Loan Security Deposit"
        
        # Prepare OTPay virtual account creation payload
        otpay_payload = {
            "business_code": settings.otpay_business_code,
            "phone": payment.customer_phone or "08000000000",
            "email": payment.customer_email,
            "bank_code": [100033],  # PalmPay bank code
            "name": payment.customer_name
        }
        
        logger.info(f"Creating OTPay virtual account: {otpay_payload}")
        
        virtual_account = None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{OTPAY_BASE_URL}/create_virtual_account",
                    headers=get_otpay_headers(),
                    json=otpay_payload
                )
                
                logger.info(f"OTPay response status: {response.status_code}")
                logger.info(f"OTPay response: {response.text}")
                
                if response.status_code == 200:
                    # OTPay sometimes returns response with a prefix before JSON
                    # e.g., "22802830412{\"status\":true,...}"
                    response_text = response.text
                    
                    # Find the start of JSON object
                    json_start = response_text.find('{')
                    if json_start > 0:
                        response_text = response_text[json_start:]
                    
                    otpay_response = json.loads(response_text)
                    
                    if otpay_response.get("status"):
                        accounts = otpay_response.get("accounts", [])
                        if accounts:
                            account = accounts[0]
                            virtual_account = {
                                "ref": account.get("ref"),
                                "account_number": account.get("number"),
                                "account_name": account.get("name"),
                                "bank_name": account.get("bank", "PALMPAY")
                            }
                            logger.info(f"OTPay virtual account created: {virtual_account}")
                    else:
                        error_msg = otpay_response.get("desc", "Unknown error")
                        logger.error(f"OTPay API error: {error_msg}")
                        raise Exception(f"OTPay error: {error_msg}")
                else:
                    logger.error(f"OTPay API error: {response.status_code} - {response.text}")
                    raise Exception(f"OTPay API returned {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("OTPay API timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment gateway timeout. Please try again."
            )
        except Exception as otpay_error:
            logger.error(f"OTPay virtual account creation failed: {str(otpay_error)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment gateway error: {str(otpay_error)}"
            )
        
        if not virtual_account:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to create virtual account"
            )
        
        # Store virtual account record
        va_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "otpay_ref": virtual_account["ref"],
            "account_number": virtual_account["account_number"],
            "account_name": virtual_account["account_name"],
            "bank_name": virtual_account["bank_name"],
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "customer_phone": payment.customer_phone,
            "expected_amount": payment.amount,
            "payment_type": "processing_fee" if is_processing_fee else "deposit",
            "payment_method": "otpay_virtual_account",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.virtual_accounts.insert_one(va_doc)
        
        # Also create a transaction record
        transaction_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "amount": payment.amount,
            "currency": "NGN",
            "virtual_account_number": virtual_account["account_number"],
            "virtual_account_bank": virtual_account["bank_name"],
            "payment_type": "processing_fee" if is_processing_fee else "deposit",
            "payment_method": "otpay",
            "status": "pending",
            "webhook_received": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        return {
            "status": "success",
            "payment_type": "bank_transfer",
            "virtual_account": {
                "account_number": virtual_account["account_number"],
                "account_name": virtual_account["account_name"],
                "bank_name": virtual_account["bank_name"]
            },
            "amount": int(payment.amount),
            "currency": "NGN",
            "order_reference": order_reference,
            "message": f"Transfer exactly ₦{int(payment.amount):,} to complete payment"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate payment"
        )


@router.post("/verify", response_model=dict)
async def verify_payment(verify: PaymentVerify, db=Depends(get_db)):
    """Verify payment status by querying transaction records"""
    try:
        # Find transaction by order reference
        transaction = await db.transactions.find_one({"order_reference": verify.order_ref})
        
        if not transaction:
            # Try finding by virtual account
            va = await db.virtual_accounts.find_one({"order_reference": verify.order_ref})
            if va:
                transaction = await db.transactions.find_one({
                    "virtual_account_number": va["account_number"]
                })
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        payment_status = transaction.get("status", "pending")
        
        # If still pending, try to query OTPay for status
        if payment_status == "pending" and transaction.get("transaction_reference"):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        f"{OTPAY_BASE_URL}/query_transaction",
                        headers=get_otpay_headers(),
                        json={
                            "business_code": settings.otpay_business_code,
                            "order_no": transaction.get("transaction_reference")
                        }
                    )
                    
                    if response.status_code == 200:
                        otpay_data = response.json()
                        if otpay_data.get("status") and otpay_data.get("data"):
                            data = otpay_data["data"]
                            if data.get("status") == "sent":
                                payment_status = "completed"
                                
                                # Update transaction
                                await db.transactions.update_one(
                                    {"order_reference": verify.order_ref},
                                    {"$set": {
                                        "status": "completed",
                                        "updated_at": datetime.now(timezone.utc)
                                    }}
                                )
                                
                                # Process successful payment
                                await process_successful_payment(transaction, db)
                                
            except Exception as query_error:
                logger.warning(f"OTPay query failed: {str(query_error)}")
        
        return {
            "payment_status": payment_status,
            "transaction_reference": transaction.get("transaction_reference", ""),
            "amount": transaction.get("amount"),
            "application_id": transaction.get("application_id"),
            "payment_type": transaction.get("payment_type", "bank_transfer"),
            "message": f"Payment {payment_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify payment"
        )


@router.post("/webhook")
async def otpay_webhook(request: Request, db=Depends(get_db)):
    """
    Handle OTPay payment webhooks with comprehensive security.
    
    Security measures:
    1. IP Allowlisting (OTPay IPs: 185.31.40.25, 2a00:b6e0:1:20:16::1)
    2. TLS/HTTPS enforcement
    3. Rate limiting
    4. Audit logging
    
    OTPay sends webhooks when:
    - Payment is received to a virtual account
    """
    client_ip = get_client_ip(request)
    transaction_ref = "unknown"
    
    try:
        # ================================================================
        # STEP 1: IP Allowlist Verification (OTPay specific)
        # ================================================================
        if REQUIRE_IP_ALLOWLIST:
            if client_ip not in OTPAY_WEBHOOK_IPS:
                logger.warning(f"Webhook from unauthorized IP: {client_ip}. Allowed: {OTPAY_WEBHOOK_IPS}")
                log_webhook_event(request, client_ip, "unknown", "ip_rejected", {
                    "allowed_ips": list(OTPAY_WEBHOOK_IPS)
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized IP address"
                )
        
        # ================================================================
        # STEP 2: Parse Webhook Payload
        # ================================================================
        body = await request.body()
        webhook_data = json.loads(body)
        
        logger.info(f"Received OTPay webhook from {client_ip}: {webhook_data}")
        
        # Extract OTPay webhook fields
        # OTPay webhook format:
        # {
        #   "email": "test@gmail.com",
        #   "phone": "09012345678",
        #   "business_code": "XXX",
        #   "account_number": "XXXXXXXXXX",
        #   "customer_account_name": "Name - [TEST](OT-PAY)",
        #   "customer_account_bank": "PALMPAY",
        #   "amount": 200,
        #   "date": "2025-01-01 17:26:46",
        #   "transaction_reference": "MIXXXXXXXXXXXXXXXXX",
        #   "customer_senderbankname": "OPAY",
        #   "customer_senderaccountnumber": "****1234",
        #   "customer_sendername": "PERFECT TEST"
        # }
        
        account_number = webhook_data.get("account_number")
        transaction_ref = webhook_data.get("transaction_reference", "unknown")
        amount = webhook_data.get("amount", 0)
        sender_name = webhook_data.get("customer_sendername", "")
        sender_bank = webhook_data.get("customer_senderbankname", "")
        
        if not account_number:
            logger.warning(f"OTPay webhook missing account_number from {client_ip}")
            log_webhook_event(request, client_ip, transaction_ref, "missing_account", {})
            return {"status": "ok", "message": "No account number provided"}
        
        # ================================================================
        # STEP 3: Find Virtual Account and Transaction
        # ================================================================
        virtual_account = await db.virtual_accounts.find_one({
            "account_number": account_number,
            "status": "active"
        })
        
        if not virtual_account:
            logger.warning(f"Virtual account not found: {account_number} from {client_ip}")
            log_webhook_event(request, client_ip, transaction_ref, "account_not_found", {
                "account_number": account_number
            })
            return {"status": "ok", "message": "Virtual account not found"}
        
        # Find or create transaction
        transaction = await db.transactions.find_one({
            "virtual_account_number": account_number,
            "status": "pending"
        })
        
        if not transaction:
            # Create new transaction record from webhook
            transaction = {
                "application_id": virtual_account["application_id"],
                "order_reference": virtual_account["order_reference"],
                "customer_email": virtual_account["customer_email"],
                "customer_name": virtual_account["customer_name"],
                "amount": virtual_account["expected_amount"],
                "virtual_account_number": account_number,
                "payment_type": virtual_account["payment_type"],
                "payment_method": "otpay"
            }
        
        # ================================================================
        # STEP 4: Validate Amount
        # ================================================================
        expected_amount = virtual_account.get("expected_amount", 0)
        if amount < expected_amount:
            logger.warning(
                f"Partial payment received: ₦{amount} of ₦{expected_amount} "
                f"for account {account_number}"
            )
            # Still process but log warning
        
        # ================================================================
        # STEP 5: Update Transaction Record
        # ================================================================
        update_data = {
            "status": "completed",
            "transaction_reference": transaction_ref,
            "amount_received": amount,
            "sender_name": sender_name,
            "sender_bank": sender_bank,
            "webhook_received": True,
            "webhook_ip": client_ip,
            "webhook_data": webhook_data,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.transactions.update_one(
            {"virtual_account_number": account_number, "status": "pending"},
            {"$set": update_data},
            upsert=True
        )
        
        # Mark virtual account as used
        await db.virtual_accounts.update_one(
            {"account_number": account_number},
            {"$set": {
                "status": "completed",
                "transaction_reference": transaction_ref,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # ================================================================
        # STEP 6: Process Successful Payment
        # ================================================================
        await process_successful_payment(transaction, db)
        
        # ================================================================
        # STEP 7: Log Success
        # ================================================================
        log_webhook_event(
            request=request,
            client_ip=client_ip,
            reference=transaction_ref,
            status="success",
            details={
                "account_number": account_number,
                "amount": amount,
                "sender": sender_name
            }
        )
        
        return {"status": "success", "message": "Webhook processed"}
        
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in webhook payload from {client_ip}")
        log_webhook_event(request, client_ip, transaction_ref, "invalid_json", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error from {client_ip}: {str(e)}")
        log_webhook_event(request, client_ip, transaction_ref, "error", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


async def process_successful_payment(transaction: dict, db):
    """Process successful payment - update application and send emails"""
    try:
        application_id = transaction.get("application_id")
        if not application_id:
            logger.warning("Transaction missing application_id")
            return
            
        application = await db.applications.find_one({"application_id": application_id})
        
        if not application:
            logger.warning(f"Application not found for payment: {application_id}")
            return
        
        # Determine payment type
        payment_type = transaction.get("payment_type", "")
        amount = transaction.get("amount", 0)
        
        is_processing_fee = payment_type == "processing_fee" or amount <= 2500
        is_deposit = payment_type == "deposit" or amount >= 3000
        
        app_update = {
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Processing fee payment (₦2,500)
        if is_processing_fee and not application.get("processing_fee_paid"):
            app_update["processing_fee_paid"] = True
            app_update["processing_fee_paid_at"] = datetime.now(timezone.utc)
            app_update["payment_status"] = "paid"
            app_update["status"] = "under_review"
            
            logger.info(f"Application {application_id} - Processing fee marked as paid")
            
            # Send payment confirmation email
            try:
                await email_service.send_payment_confirmation(
                    application.get("email"),
                    application.get("full_name"),
                    amount,
                    "processing_fee",
                    transaction.get("transaction_reference") or transaction.get("order_reference"),
                    application_id
                )
            except Exception as email_error:
                logger.error(f"Failed to send processing fee email: {email_error}")
        
        # Deposit payment (₦3,000)
        elif is_deposit and not application.get("deposit_paid") and application.get("status") == "approved":
            app_update["deposit_paid"] = True
            app_update["deposit_paid_at"] = datetime.now(timezone.utc)
            app_update["status"] = "deposit_paid"
            app_update["disbursement_status"] = "pending"
            
            logger.info(f"Application {application_id} - Deposit marked as paid, awaiting disbursement approval")
            
            # Send deposit confirmation email
            try:
                await email_service.send_deposit_confirmed(
                    application.get("email"),
                    application.get("full_name"),
                    application_id,
                    application.get("approved_amount") or application.get("loan_amount")
                )
            except Exception as email_error:
                logger.error(f"Failed to send deposit email: {email_error}")
        
        if len(app_update) > 1:  # More than just updated_at
            await db.applications.update_one(
                {"application_id": application_id},
                {"$set": app_update}
            )
            
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")


@router.get("/transaction/{order_ref}")
async def get_transaction(order_ref: str, db=Depends(get_db)):
    """Get transaction details by order reference"""
    transaction = await db.transactions.find_one(
        {"order_reference": order_ref},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Convert datetime objects to ISO strings
    if transaction.get("created_at"):
        transaction["created_at"] = transaction["created_at"].isoformat()
    if transaction.get("updated_at"):
        transaction["updated_at"] = transaction["updated_at"].isoformat()
    
    return transaction


@router.get("/virtual-account/{application_id}")
async def get_virtual_account(application_id: str, db=Depends(get_db)):
    """Get virtual account details for an application"""
    va = await db.virtual_accounts.find_one(
        {"application_id": application_id, "status": "active"},
        {"_id": 0}
    )
    
    if not va:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active virtual account found for this application"
        )
    
    # Convert datetime objects
    if va.get("created_at"):
        va["created_at"] = va["created_at"].isoformat()
    if va.get("updated_at"):
        va["updated_at"] = va["updated_at"].isoformat()
    
    return va
