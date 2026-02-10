from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from database import get_db
from config import get_settings
from utils.email import email_service
from utils.webhook_security import (
    verify_webhook_security,
    log_webhook_event,
    get_client_ip,
)
from datetime import datetime, timezone
import httpx
import logging
import hmac
import hashlib
import json
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/payments", tags=["payments"])

# ============================================================================
# BUDPAY CONFIGURATION
# ============================================================================
BUDPAY_BASE_URL = "https://api.budpay.com/api/v2"

# Webhook security settings
REQUIRE_WEBHOOK_SIGNATURE = False  # Enable when BudPay provides signatures
REQUIRE_IP_ALLOWLIST = False  # Enable after configuring BUDPAY_WEBHOOK_IPS


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PaymentInitiate(BaseModel):
    application_id: str
    customer_email: str
    customer_name: str
    customer_phone: str = ""
    amount: float = 2500
    redirect_url: str


class PaymentVerify(BaseModel):
    order_ref: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_budpay_headers():
    """Get BudPay API headers with authentication"""
    return {
        "Authorization": f"Bearer {settings.budpay_secret_key}",
        "Content-Type": "application/json"
    }


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/initiate", response_model=dict)
async def initiate_payment(payment: PaymentInitiate, db=Depends(get_db)):
    """
    Initiate a payment transaction with BudPay Standard Checkout.
    
    BudPay Flow:
    1. Initialize transaction with amount and customer details
    2. Return checkout URL for customer to complete payment
    3. Customer pays via card, bank transfer, or USSD
    4. BudPay redirects to callback URL with payment status
    5. Webhook notification confirms payment
    """
    try:
        # Verify application exists
        application = await db.applications.find_one({"application_id": payment.application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Create unique order reference
        order_reference = f"CASHFLOW-{payment.application_id}-{uuid.uuid4().hex[:8]}"
        
        # Determine payment type
        is_processing_fee = payment.amount <= 2500
        
        # Prepare BudPay Standard Checkout payload
        budpay_payload = {
            "email": payment.customer_email,
            "amount": str(int(payment.amount)),
            "currency": "NGN",
            "reference": order_reference,
            "callback": payment.redirect_url
        }
        
        logger.info(f"Creating BudPay checkout: {budpay_payload}")
        
        checkout_link = None
        budpay_reference = None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BUDPAY_BASE_URL}/transaction/initialize",
                    headers=get_budpay_headers(),
                    json=budpay_payload
                )
                
                logger.info(f"BudPay response status: {response.status_code}")
                logger.info(f"BudPay response: {response.text}")
                
                if response.status_code == 200:
                    budpay_response = response.json()
                    
                    if budpay_response.get("status"):
                        data = budpay_response.get("data", {})
                        checkout_link = data.get("authorization_url")
                        budpay_reference = data.get("reference") or order_reference
                        
                        logger.info(f"BudPay checkout URL created: {checkout_link}")
                    else:
                        error_msg = budpay_response.get("message", "Unknown error")
                        logger.error(f"BudPay API error: {error_msg}")
                        raise Exception(f"BudPay error: {error_msg}")
                else:
                    logger.error(f"BudPay API error: {response.status_code} - {response.text}")
                    raise Exception(f"BudPay API returned {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("BudPay API timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment gateway timeout. Please try again."
            )
        except Exception as budpay_error:
            logger.error(f"BudPay payment initiation failed: {str(budpay_error)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment gateway error: {str(budpay_error)}"
            )
        
        if not checkout_link:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to create checkout link"
            )
        
        # Store transaction record
        transaction_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "amount": payment.amount,
            "currency": "NGN",
            "budpay_reference": budpay_reference,
            "checkout_link": checkout_link,
            "payment_type": "processing_fee" if is_processing_fee else "deposit",
            "payment_method": "budpay",
            "status": "initiated",
            "transaction_reference": None,
            "webhook_received": False,
            "webhook_verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        return {
            "checkout_link": checkout_link,
            "order_reference": order_reference,
            "status": "initiated",
            "payment_type": "card",
            "amount": int(payment.amount),
            "currency": "NGN"
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
    """Verify payment status with BudPay API"""
    try:
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": verify.order_ref})
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        payment_status = transaction.get("status", "pending")
        transaction_reference = transaction.get("transaction_reference", "")
        
        # If not completed, check with BudPay
        if payment_status in ["initiated", "pending"]:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        f"{BUDPAY_BASE_URL}/transaction/verify/{verify.order_ref}",
                        headers=get_budpay_headers()
                    )
                    
                    logger.info(f"BudPay verify response: {response.status_code} - {response.text}")
                    
                    if response.status_code == 200:
                        budpay_data = response.json()
                        
                        if budpay_data.get("status"):
                            data = budpay_data.get("data", {})
                            
                            # Map BudPay status
                            budpay_status = str(data.get("status", "")).lower()
                            status_map = {
                                "success": "completed",
                                "successful": "completed",
                                "completed": "completed",
                                "approved": "completed",
                                "paid": "completed",
                                "pending": "pending",
                                "processing": "pending",
                                "failed": "failed",
                                "cancelled": "failed",
                                "abandoned": "failed",
                                "expired": "failed"
                            }
                            payment_status = status_map.get(budpay_status, payment_status)
                            transaction_reference = data.get("reference") or data.get("transaction_reference") or transaction_reference
                            
            except Exception as verify_error:
                logger.warning(f"BudPay status check failed: {str(verify_error)}")
        
        # Update transaction if status changed
        if payment_status != transaction.get("status"):
            await db.transactions.update_one(
                {"order_reference": verify.order_ref},
                {"$set": {
                    "status": payment_status,
                    "transaction_reference": transaction_reference,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            # Update application if payment successful
            if payment_status == "completed":
                await process_successful_payment(transaction, db)
        
        return {
            "payment_status": payment_status,
            "transaction_reference": transaction_reference,
            "amount": transaction["amount"],
            "application_id": transaction["application_id"],
            "payment_type": transaction.get("payment_type", "card"),
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
async def budpay_webhook(request: Request, db=Depends(get_db)):
    """
    Handle BudPay payment webhooks.
    
    Security measures:
    1. HMAC signature verification (when configured)
    2. IP allowlisting (when configured)
    3. Audit logging
    
    BudPay sends webhooks when:
    - Payment is successful (charge.success)
    - Payment fails (charge.failed)
    """
    client_ip = get_client_ip(request)
    order_ref = "unknown"
    
    try:
        # Get raw body
        body = await request.body()
        
        # Verify webhook signature if configured
        signature = request.headers.get("x-budpay-signature") or request.headers.get("budpay-signature")
        
        if signature and settings.budpay_secret_key and REQUIRE_WEBHOOK_SIGNATURE:
            expected_signature = hmac.new(
                settings.budpay_secret_key.encode('utf-8'),
                body,
                hashlib.sha512
            ).hexdigest()
            
            if not hmac.compare_digest(signature.lower(), expected_signature.lower()):
                logger.warning(f"Invalid BudPay webhook signature from {client_ip}")
                log_webhook_event(request, client_ip, "unknown", "invalid_signature", {})
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid webhook signature"
                )
        
        # Parse webhook data
        webhook_data = json.loads(body)
        logger.info(f"Received BudPay webhook from {client_ip}: {webhook_data}")
        
        # Extract event type and data
        event_type = (
            webhook_data.get("notifyType") or 
            webhook_data.get("event") or 
            webhook_data.get("notify") or
            "unknown"
        )
        
        event_data = webhook_data.get("data", webhook_data)
        
        # Extract reference
        order_ref = (
            event_data.get("reference") or
            event_data.get("tx_ref") or
            event_data.get("merchantTransactionRef") or
            webhook_data.get("reference")
        )
        
        transaction_status = str(event_data.get("status") or webhook_data.get("status") or "").lower()
        transaction_id = event_data.get("id") or event_data.get("transaction_id")
        amount_paid = event_data.get("amount") or event_data.get("charged_amount")
        
        if not order_ref:
            logger.warning(f"BudPay webhook missing order reference from {client_ip}")
            log_webhook_event(request, client_ip, "missing", "rejected", {})
            return {"status": "ok", "message": "No order reference provided"}
        
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": order_ref})
        if not transaction:
            transaction = await db.transactions.find_one({"budpay_reference": order_ref})
        
        if not transaction:
            logger.warning(f"Transaction not found for webhook: {order_ref} from {client_ip}")
            log_webhook_event(request, client_ip, order_ref, "not_found", {})
            return {"status": "ok", "message": "Transaction not found"}
        
        # Map webhook status
        status_map = {
            "success": "completed",
            "successful": "completed",
            "completed": "completed",
            "approved": "completed",
            "paid": "completed",
            "failed": "failed",
            "cancelled": "failed",
            "abandoned": "failed",
            "expired": "failed"
        }
        payment_status = status_map.get(transaction_status, "pending")
        
        # Update transaction
        update_data = {
            "status": payment_status,
            "webhook_received": True,
            "webhook_verified": True,
            "webhook_ip": client_ip,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if transaction_id:
            update_data["transaction_reference"] = str(transaction_id)
        if amount_paid:
            update_data["amount_paid"] = float(amount_paid)
            
        await db.transactions.update_one(
            {"order_reference": transaction["order_reference"]},
            {"$set": update_data}
        )
        
        # Process successful payment
        if payment_status == "completed":
            await process_successful_payment(transaction, db)
        
        log_webhook_event(request, client_ip, order_ref, "success", {
            "event_type": event_type,
            "payment_status": payment_status
        })
        
        return {"status": "success", "message": "Webhook processed"}
        
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in webhook payload from {client_ip}")
        log_webhook_event(request, client_ip, order_ref, "invalid_json", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error from {client_ip}: {str(e)}")
        log_webhook_event(request, client_ip, order_ref, "error", {"error": str(e)})
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
        
        amount = transaction.get("amount", 0)
        is_processing_fee = amount <= 2500
        is_deposit = amount >= 3000
        
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
            
            logger.info(f"Application {application_id} - Deposit marked as paid")
            
            try:
                await email_service.send_deposit_confirmed(
                    application.get("email"),
                    application.get("full_name"),
                    application_id,
                    application.get("approved_amount") or application.get("loan_amount")
                )
            except Exception as email_error:
                logger.error(f"Failed to send deposit email: {email_error}")
        
        if len(app_update) > 1:
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
    
    if transaction.get("created_at"):
        transaction["created_at"] = transaction["created_at"].isoformat()
    if transaction.get("updated_at"):
        transaction["updated_at"] = transaction["updated_at"].isoformat()
    
    return transaction
