from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from database import get_db
from config import get_settings
from utils.email import email_service
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

class PaymentInitiate(BaseModel):
    application_id: str
    customer_email: str
    customer_name: str
    customer_phone: str = ""
    amount: float = 2500
    redirect_url: str

class PaymentVerify(BaseModel):
    order_ref: str


def get_xixapay_headers():
    """Get Xixapay API headers with authentication"""
    return {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }


@router.post("/initiate", response_model=dict)
async def initiate_payment(payment: PaymentInitiate, db=Depends(get_db)):
    """
    Initiate a payment transaction with Xixapay using Dynamic Virtual Account.
    
    Xixapay Flow:
    1. Create a dynamic virtual account with the exact payment amount
    2. Return the virtual account details for customer to make payment
    3. Customer pays to the virtual account via bank transfer
    4. Xixapay sends webhook notification when payment is received
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
        order_reference = f"CASHFLOW-{payment.application_id}-{int(datetime.now(timezone.utc).timestamp())}"
        
        # Get phone number - use provided or extract from application
        phone_number = payment.customer_phone
        if not phone_number and application:
            phone_number = application.get("phone", "")
        if not phone_number:
            phone_number = "08012345678"  # Default placeholder
        
        # Format phone number to be exactly 11 digits for Xixapay
        # Remove any non-digit characters
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))
        
        # Handle different phone formats
        if phone_number.startswith('234') and len(phone_number) == 13:
            # Nigerian format with country code: 2348012345678 -> 08012345678
            phone_number = '0' + phone_number[3:]
        elif phone_number.startswith('234') and len(phone_number) > 13:
            phone_number = '0' + phone_number[3:14]
        elif len(phone_number) == 10 and not phone_number.startswith('0'):
            # Missing leading 0: 8012345678 -> 08012345678
            phone_number = '0' + phone_number
        elif len(phone_number) > 11:
            # Truncate to 11 digits
            phone_number = phone_number[:11]
        elif len(phone_number) < 11:
            # Pad with zeros or use default
            phone_number = "08012345678"
        
        logger.info(f"Formatted phone number: {phone_number} (length: {len(phone_number)})")
        
        # Prepare Xixapay Dynamic Virtual Account payload
        # Using Xixapay's createVirtualAccount endpoint for dynamic account
        # IMPORTANT: callbackUrl must be publicly accessible for webhooks
        webhook_url = f"{settings.backend_url}/api/payments/webhook"
        
        va_payload = {
            "businessId": settings.xixapay_merchant_id,
            "accountType": "dynamic",
            "amount": int(payment.amount),  # Exact amount for dynamic account
            "bankCode": ["29007"],  # Safehaven Dynamic
            "name": payment.customer_name,
            "email": payment.customer_email,
            "phoneNumber": phone_number,
            "externalReference": order_reference,
            "callbackUrl": webhook_url  # Webhook URL for payment notifications
        }
        
        logger.info(f"Creating virtual account with webhook URL: {webhook_url}")
        
        checkout_link = None
        xixapay_reference = None
        virtual_account_number = None
        virtual_account_bank = None
        
        try:
            # Create dynamic virtual account with Xixapay
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.xixapay_base_url}/api/v1/createVirtualAccount",
                    headers=get_xixapay_headers(),
                    json=va_payload
                )
                
                logger.info(f"Xixapay VA response status: {response.status_code}")
                logger.info(f"Xixapay VA response: {response.text}")
                
                if response.status_code in [200, 201]:
                    xixapay_response = response.json()
                    
                    # Handle Xixapay's response structure
                    bank_accounts = xixapay_response.get("bankAccounts", [])
                    if bank_accounts:
                        account = bank_accounts[0]  # Get first bank account
                        virtual_account_number = account.get("accountNumber")
                        virtual_account_bank = account.get("bankName", "Partner Bank")
                        xixapay_reference = account.get("Reserved_Account_Id") or account.get("externalReference") or order_reference
                    else:
                        # Fallback to other possible response formats
                        data = xixapay_response.get("data", xixapay_response)
                        virtual_account_number = data.get("accountNumber") or data.get("account_number")
                        virtual_account_bank = data.get("bankName") or data.get("bank_name") or "Partner Bank"
                        xixapay_reference = data.get("reference") or data.get("accountReference") or order_reference
                    
                    # For virtual accounts, the checkout "link" is the bank transfer info
                    # We'll create a special URL that shows the bank transfer details
                    checkout_link = f"{payment.redirect_url}?orderRef={order_reference}&type=bank_transfer&account={virtual_account_number}&bank={virtual_account_bank}&amount={int(payment.amount)}"
                    
                else:
                    # Log the error
                    logger.error(f"Xixapay API error: {response.status_code} - {response.text}")
                    raise Exception(f"Xixapay API returned {response.status_code}: {response.text}")
                    
        except httpx.TimeoutException:
            logger.error("Xixapay API timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment gateway timeout. Please try again."
            )
        except Exception as xixapay_error:
            logger.error(f"Xixapay payment initiation failed: {str(xixapay_error)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment gateway error: {str(xixapay_error)}"
            )
        
        if not virtual_account_number:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to create virtual account for payment"
            )
        
        # Store transaction record
        transaction_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "amount": payment.amount,
            "currency": "NGN",
            "xixapay_reference": xixapay_reference,
            "virtual_account_number": virtual_account_number,
            "virtual_account_bank": virtual_account_bank,
            "payment_type": "bank_transfer",
            "status": "initiated",
            "transaction_reference": None,
            "payment_method": "bank_transfer",
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
            "payment_type": "bank_transfer",
            "virtual_account": {
                "account_number": virtual_account_number,
                "bank_name": virtual_account_bank,
                "amount": int(payment.amount),
                "currency": "NGN"
            }
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
    """Verify payment status - checks database for webhook updates"""
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
        
        # For Xixapay virtual accounts, the status is updated via webhook
        # We can optionally try to query Xixapay for status update
        if payment_status in ["initiated", "pending"]:
            try:
                # Check if webhook has updated the status
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        f"{settings.xixapay_base_url}/api/v1/transaction/{verify.order_ref}",
                        headers=get_xixapay_headers()
                    )
                    
                    if response.status_code == 200:
                        xixapay_data = response.json()
                        data = xixapay_data.get("data", xixapay_data)
                        
                        # Map Xixapay status
                        xixapay_status = str(data.get("status", "")).lower()
                        status_map = {
                            "success": "completed",
                            "successful": "completed",
                            "completed": "completed",
                            "paid": "completed",
                            "pending": "pending",
                            "processing": "pending",
                            "failed": "failed",
                            "cancelled": "failed",
                            "abandoned": "failed",
                            "expired": "failed"
                        }
                        payment_status = status_map.get(xixapay_status, payment_status)
                        transaction_reference = data.get("transactionReference") or data.get("reference") or transaction_reference
                        
            except Exception as verify_error:
                logger.warning(f"Xixapay status check failed: {str(verify_error)}")
                # Continue with database status
        
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
                application_id = transaction["application_id"]
                await db.applications.update_one(
                    {"application_id": application_id},
                    {"$set": {
                        "payment_status": "paid",
                        "status": "under_review",
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                
                # Get application details for email
                application = await db.applications.find_one({"application_id": application_id})
                
                if application:
                    try:
                        await email_service.send_application_received(
                            application.get("email"),
                            application.get("full_name"),
                            application_id,
                            application.get("loan_amount")
                        )
                    except Exception as email_error:
                        logger.error(f"Failed to send email notification: {email_error}")
        
        return {
            "payment_status": payment_status,
            "transaction_reference": transaction_reference,
            "amount": transaction["amount"],
            "application_id": transaction["application_id"],
            "payment_type": transaction.get("payment_type", "bank_transfer"),
            "virtual_account": {
                "account_number": transaction.get("virtual_account_number"),
                "bank_name": transaction.get("virtual_account_bank")
            } if transaction.get("virtual_account_number") else None,
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
async def xixapay_webhook(request: Request, db=Depends(get_db)):
    """
    Handle Xixapay payment webhooks for virtual account payments.
    
    Xixapay sends webhooks when:
    - Payment is received on a virtual account
    - Payment status changes
    
    Webhook payload includes:
    - notification_status: Status of the payment
    - transaction_id: Unique transaction identifier
    - amount_paid: Amount received
    - account_number: Virtual account that received payment
    - external_reference: Your order reference
    """
    try:
        # Get raw body
        body = await request.body()
        
        # Optional: Verify webhook signature if provided
        signature = request.headers.get("xixapay-signature") or request.headers.get("x-xixapay-signature")
        
        if signature and settings.xixapay_webhook_secret:
            expected_signature = hmac.new(
                settings.xixapay_webhook_secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid webhook signature received")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )
        
        # Parse webhook data
        webhook_data = json.loads(body)
        logger.info(f"Received Xixapay webhook: {webhook_data}")
        
        # Extract transaction details - handle various field name formats
        order_ref = (
            webhook_data.get("externalReference") or
            webhook_data.get("external_reference") or
            webhook_data.get("merchantTransactionId") or
            webhook_data.get("reference") or
            webhook_data.get("order_reference")
        )
        
        notification_status = str(webhook_data.get("notification_status") or webhook_data.get("status") or "").lower()
        transaction_id = webhook_data.get("transaction_id") or webhook_data.get("transactionId")
        amount_paid = webhook_data.get("amount_paid") or webhook_data.get("amount")
        settlement_amount = webhook_data.get("settlement_amount")
        
        if not order_ref:
            # Try to find by account number
            account_number = webhook_data.get("account_number") or webhook_data.get("accountNumber")
            if account_number:
                transaction = await db.transactions.find_one({"virtual_account_number": account_number})
                if transaction:
                    order_ref = transaction["order_reference"]
        
        if not order_ref:
            logger.warning("Webhook missing order reference")
            return {"status": "ok", "message": "No order reference provided"}
        
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": order_ref})
        if not transaction:
            # Try finding by xixapay reference
            transaction = await db.transactions.find_one({"xixapay_reference": order_ref})
        
        if not transaction:
            logger.warning(f"Transaction not found for webhook: {order_ref}")
            return {"status": "ok", "message": "Transaction not found"}
        
        # Map webhook status to internal status
        status_map = {
            "payment_successful": "completed",
            "successful": "completed",
            "success": "completed",
            "completed": "completed",
            "paid": "completed",
            "payment_failed": "failed",
            "failed": "failed",
            "cancelled": "failed",
            "abandoned": "failed",
            "expired": "failed"
        }
        payment_status = status_map.get(notification_status, "pending")
        
        # Update transaction
        update_data = {
            "status": payment_status,
            "webhook_received": True,
            "webhook_verified": True,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if transaction_id:
            update_data["transaction_reference"] = transaction_id
        if amount_paid:
            update_data["amount_paid"] = amount_paid
        if settlement_amount:
            update_data["settlement_amount"] = settlement_amount
            
        await db.transactions.update_one(
            {"order_reference": transaction["order_reference"]},
            {"$set": update_data}
        )
        
        # Update application if payment successful
        if payment_status == "completed":
            application_id = transaction["application_id"]
            await db.applications.update_one(
                {"application_id": application_id},
                {"$set": {
                    "payment_status": "paid",
                    "status": "under_review",
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            logger.info(f"Application {application_id} marked as paid via webhook")
            
            # Send email notification
            application = await db.applications.find_one({"application_id": application_id})
            if application:
                try:
                    await email_service.send_application_received(
                        application.get("email"),
                        application.get("full_name"),
                        application_id,
                        application.get("loan_amount")
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send email notification: {email_error}")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


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
    
    # Convert datetime objects to ISO strings for JSON serialization
    if transaction.get("created_at"):
        transaction["created_at"] = transaction["created_at"].isoformat()
    if transaction.get("updated_at"):
        transaction["updated_at"] = transaction["updated_at"].isoformat()
    
    return transaction
