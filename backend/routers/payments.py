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
# BUDPAY CONFIGURATION - DEDICATED VIRTUAL ACCOUNT (DVA)
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


async def create_budpay_customer(email: str, first_name: str, last_name: str, phone: str):
    """Create a customer in BudPay to get customer_code for DVA"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BUDPAY_BASE_URL}/customer",
                headers=get_budpay_headers(),
                json={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name or "Customer",
                    "phone": phone
                }
            )
            
            logger.info(f"BudPay create customer response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    return data.get("data", {}).get("customer_code")
                # Customer might already exist
                elif "already exist" in data.get("message", "").lower():
                    # Try to fetch existing customer
                    return await get_existing_customer_code(email)
            elif response.status_code == 401:
                # 401 might indicate customer exists
                response_data = response.json()
                if "already exist" in response_data.get("message", "").lower():
                    return await get_existing_customer_code(email)
            return None
    except Exception as e:
        logger.error(f"Failed to create BudPay customer: {e}")
        return None


async def get_existing_customer_code(email: str):
    """Fetch existing customer code from BudPay by email"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to fetch customer list and find by email
            response = await client.get(
                f"{BUDPAY_BASE_URL}/customer",
                headers=get_budpay_headers()
            )
            
            logger.info(f"BudPay fetch customers response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    customers = data.get("data", [])
                    for customer in customers:
                        if customer.get("email", "").lower() == email.lower():
                            return customer.get("customer_code")
            return None
    except Exception as e:
        logger.error(f"Failed to fetch BudPay customer: {e}")
        return None


async def create_dedicated_virtual_account(customer_code: str):
    """Create a dedicated virtual account for bank transfers"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BUDPAY_BASE_URL}/dedicated_virtual_account",
                headers=get_budpay_headers(),
                json={
                    "customer": customer_code
                }
            )
            
            logger.info(f"BudPay DVA response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    return data.get("data", {})
            return None
    except Exception as e:
        logger.error(f"Failed to create BudPay DVA: {e}")
        return None


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/initiate", response_model=dict)
async def initiate_payment(payment: PaymentInitiate, db=Depends(get_db)):
    """
    Initiate a payment transaction with BudPay Dedicated Virtual Account.
    
    DVA Flow (Bank Transfer Only - No Checkout Redirect):
    1. Create/get customer in BudPay
    2. Create dedicated virtual account for the customer
    3. Return bank account details for direct transfer
    4. Customer transfers exact amount to the virtual account
    5. BudPay webhook confirms payment automatically
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
        
        # Parse customer name
        name_parts = payment.customer_name.strip().split(" ", 1)
        first_name = name_parts[0] if name_parts else "Customer"
        last_name = name_parts[1] if len(name_parts) > 1 else "User"
        
        # Check if customer already has a virtual account stored
        existing_dva = await db.virtual_accounts.find_one({
            "customer_email": payment.customer_email,
            "is_active": True
        })
        
        virtual_account = None
        customer_code = None
        
        if existing_dva:
            # Use existing virtual account
            virtual_account = {
                "bank_name": existing_dva.get("bank_name"),
                "account_number": existing_dva.get("account_number"),
                "account_name": existing_dva.get("account_name")
            }
            customer_code = existing_dva.get("customer_code")
            logger.info(f"Using existing DVA for {payment.customer_email}")
        else:
            # Create new customer and DVA
            logger.info(f"Creating new BudPay customer for {payment.customer_email}")
            
            customer_code = await create_budpay_customer(
                email=payment.customer_email,
                first_name=first_name,
                last_name=last_name,
                phone=payment.customer_phone or "08000000000"
            )
            
            if customer_code:
                logger.info(f"Created BudPay customer: {customer_code}")
                
                # Create dedicated virtual account
                dva_data = await create_dedicated_virtual_account(customer_code)
                
                if dva_data:
                    virtual_account = {
                        "bank_name": dva_data.get("bank", {}).get("name") or dva_data.get("bank_name") or "BudPay Bank",
                        "account_number": dva_data.get("account_number") or dva_data.get("virtual_account_number"),
                        "account_name": dva_data.get("account_name") or f"Cashflow MFB - {payment.customer_name}"
                    }
                    
                    # Store the virtual account for future use
                    await db.virtual_accounts.update_one(
                        {"customer_email": payment.customer_email},
                        {"$set": {
                            "customer_email": payment.customer_email,
                            "customer_name": payment.customer_name,
                            "customer_code": customer_code,
                            "bank_name": virtual_account["bank_name"],
                            "account_number": virtual_account["account_number"],
                            "account_name": virtual_account["account_name"],
                            "is_active": True,
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        }},
                        upsert=True
                    )
                    logger.info(f"Created and stored DVA: {virtual_account}")
        
        # If DVA creation failed, use fallback static account
        if not virtual_account:
            logger.warning("DVA creation failed, using fallback account")
            virtual_account = {
                "bank_name": "Wema Bank",
                "account_number": "7366628986",
                "account_name": "CASHFLOW MFB"
            }
        
        # Store transaction record
        transaction_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "customer_code": customer_code,
            "amount": payment.amount,
            "currency": "NGN",
            "virtual_account": virtual_account,
            "payment_type": "processing_fee" if is_processing_fee else "deposit",
            "payment_method": "bank_transfer",
            "status": "pending",
            "transaction_reference": None,
            "webhook_received": False,
            "webhook_verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        # Return virtual account details for bank transfer
        return {
            "virtual_account": virtual_account,
            "order_reference": order_reference,
            "status": "pending",
            "payment_type": "bank_transfer",
            "amount": int(payment.amount),
            "currency": "NGN",
            "message": f"Transfer exactly ₦{int(payment.amount):,} to the account above"
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
    Handle BudPay payment webhooks including DVA (Dedicated Virtual Account) payments.
    
    BudPay webhook events:
    - transaction: Successful payment via DVA or card
    - transaction.recurrent: Recurring payment
    - charge.success / charge.failed: Checkout payments
    - dedicatedaccount.assign.success: DVA assigned
    - dedicatedaccount.assign.failed: DVA assignment failed
    
    DVA Flow:
    1. Customer transfers to virtual account
    2. BudPay sends webhook with eventType: "transaction"
    3. We update transaction status and application
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
        
        # Extract event type - BudPay uses eventType or event field
        event_type = (
            webhook_data.get("eventType") or  # Primary DVA format
            webhook_data.get("notifyType") or 
            webhook_data.get("event") or 
            webhook_data.get("notify") or
            "unknown"
        )
        
        # Get event data - can be nested in 'data' or at root
        event_data = webhook_data.get("data", webhook_data)
        
        # Extract reference - DVA uses orderId, checkout uses reference
        order_ref = (
            event_data.get("orderId") or  # DVA format
            event_data.get("reference") or
            event_data.get("tx_ref") or
            event_data.get("merchantTransactionRef") or
            webhook_data.get("orderId") or
            webhook_data.get("reference")
        )
        
        # Extract customer email for DVA lookup
        customer_email = (
            event_data.get("customerEmail") or
            event_data.get("customer", {}).get("email") or
            event_data.get("email")
        )
        
        # Extract transaction details
        transaction_status = str(event_data.get("status") or webhook_data.get("status") or "").lower()
        transaction_id = event_data.get("id") or event_data.get("transaction_id") or event_data.get("transactionId")
        amount_paid = event_data.get("amount") or event_data.get("charged_amount") or event_data.get("amountPaid")
        
        # Handle DVA-specific events
        if event_type in ["transaction", "transaction.recurrent"]:
            # DVA payment - find by email and amount match if no direct reference
            if not order_ref and customer_email and amount_paid:
                # Find pending transaction for this customer with matching amount
                transaction = await db.transactions.find_one({
                    "customer_email": customer_email,
                    "status": "pending",
                    "amount": float(amount_paid)
                }, sort=[("created_at", -1)])
                
                if transaction:
                    order_ref = transaction.get("order_reference")
                    logger.info(f"Found DVA transaction by email match: {order_ref}")
        
        if not order_ref:
            logger.warning(f"BudPay webhook missing order reference from {client_ip}")
            log_webhook_event(request, client_ip, "missing", "rejected", webhook_data)
            return {"status": "ok", "message": "No order reference provided"}
        
        # Find transaction by order_reference
        transaction = await db.transactions.find_one({"order_reference": order_ref})
        
        # Fallback: try budpay_reference
        if not transaction:
            transaction = await db.transactions.find_one({"budpay_reference": order_ref})
        
        # Fallback for DVA: match by customer email + pending status
        if not transaction and customer_email:
            transaction = await db.transactions.find_one({
                "customer_email": customer_email,
                "status": "pending"
            }, sort=[("created_at", -1)])
        
        if not transaction:
            logger.warning(f"Transaction not found for webhook: {order_ref} from {client_ip}")
            log_webhook_event(request, client_ip, order_ref, "not_found", webhook_data)
            return {"status": "ok", "message": "Transaction not found"}
        
        # Map webhook status to our status
        status_map = {
            "success": "completed",
            "successful": "completed",
            "completed": "completed",
            "approved": "completed",
            "paid": "completed",
            "delivered": "completed",  # DVA might use this
            "failed": "failed",
            "cancelled": "failed",
            "abandoned": "failed",
            "expired": "failed"
        }
        
        # For "transaction" event type, assume success if status is not explicitly failed
        if event_type == "transaction" and transaction_status not in ["failed", "cancelled", "abandoned", "expired"]:
            payment_status = "completed"
        else:
            payment_status = status_map.get(transaction_status, "pending")
        
        # Update transaction record
        update_data = {
            "status": payment_status,
            "webhook_received": True,
            "webhook_verified": True,
            "webhook_ip": client_ip,
            "webhook_event_type": event_type,
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
        
        # Process successful payment - update application status
        if payment_status == "completed":
            await process_successful_payment(transaction, db)
            logger.info(f"Successfully processed DVA payment for {order_ref}")
        
        log_webhook_event(request, client_ip, order_ref, "success", {
            "event_type": event_type,
            "payment_status": payment_status,
            "amount": amount_paid
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



class ManualConfirmPayment(BaseModel):
    order_reference: str
    transaction_reference: str = ""
    admin_note: str = ""


@router.post("/admin/confirm-payment")
async def admin_confirm_payment(confirm: ManualConfirmPayment, db=Depends(get_db)):
    """
    Admin endpoint to manually confirm a payment.
    Use when BudPay webhook doesn't arrive or for testing purposes.
    """
    try:
        # Find the transaction
        transaction = await db.transactions.find_one({"order_reference": confirm.order_reference})
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.get("status") == "completed":
            return {
                "success": True,
                "message": "Payment was already confirmed",
                "application_id": transaction.get("application_id")
            }
        
        # Update transaction to completed
        update_data = {
            "status": "completed",
            "manual_confirmation": True,
            "admin_confirmed_at": datetime.now(timezone.utc),
            "admin_note": confirm.admin_note or "Manual confirmation by admin",
            "updated_at": datetime.now(timezone.utc)
        }
        
        if confirm.transaction_reference:
            update_data["transaction_reference"] = confirm.transaction_reference
        
        await db.transactions.update_one(
            {"order_reference": confirm.order_reference},
            {"$set": update_data}
        )
        
        # Process the successful payment (update application status)
        await process_successful_payment(transaction, db)
        
        logger.info(f"Admin manually confirmed payment: {confirm.order_reference}")
        
        return {
            "success": True,
            "message": "Payment confirmed successfully",
            "application_id": transaction.get("application_id"),
            "amount": transaction.get("amount"),
            "payment_type": transaction.get("payment_type")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin confirm payment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment"
        )


@router.get("/pending-payments")
async def get_pending_payments(db=Depends(get_db)):
    """Get all pending payment transactions for admin review"""
    try:
        pending = await db.transactions.find(
            {"status": "pending"},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        # Convert datetime objects to ISO strings
        for txn in pending:
            if txn.get("created_at"):
                txn["created_at"] = txn["created_at"].isoformat()
            if txn.get("updated_at"):
                txn["updated_at"] = txn["updated_at"].isoformat()
        
        return {
            "success": True,
            "count": len(pending),
            "transactions": pending
        }
    except Exception as e:
        logger.error(f"Error fetching pending payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending payments"
        )
