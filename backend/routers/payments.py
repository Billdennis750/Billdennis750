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
    """Initiate a payment transaction with Xixapay"""
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
        
        # Prepare Xixapay payment payload
        payment_payload = {
            "merchantId": settings.xixapay_merchant_id,
            "merchantTransactionId": order_reference,
            "amount": int(payment.amount),  # Xixapay expects integer amount in Naira
            "currency": "NGN",
            "description": "Loan Processing Fee - Cashflow MFB",
            "customer": {
                "name": payment.customer_name,
                "email": payment.customer_email,
            },
            "callbackUrl": f"{settings.backend_url}/api/payments/webhook",
            "redirectUrl": payment.redirect_url,
            "metadata": {
                "application_id": payment.application_id,
                "fee_type": "processing_fee"
            }
        }
        
        checkout_link = None
        xixapay_reference = None
        
        try:
            # Create payment with Xixapay
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.xixapay_base_url}/api/v1/payment/initiate",
                    headers=get_xixapay_headers(),
                    json=payment_payload
                )
                
                logger.info(f"Xixapay response status: {response.status_code}")
                logger.info(f"Xixapay response: {response.text}")
                
                if response.status_code == 200:
                    xixapay_response = response.json()
                    checkout_link = xixapay_response.get("data", {}).get("authorizationUrl") or xixapay_response.get("authorizationUrl")
                    xixapay_reference = xixapay_response.get("data", {}).get("reference") or xixapay_response.get("reference")
                else:
                    # Log the error but continue with fallback
                    logger.error(f"Xixapay API error: {response.status_code} - {response.text}")
                    raise Exception(f"Xixapay API returned {response.status_code}")
                    
        except Exception as xixapay_error:
            logger.error(f"Xixapay payment initiation failed: {str(xixapay_error)}")
            # Return error - no mock fallback as per user's requirement for real payment
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment gateway error: {str(xixapay_error)}"
            )
        
        if not checkout_link:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to get payment URL from Xixapay"
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
            "status": "initiated",
            "transaction_reference": None,
            "payment_method": None,
            "webhook_received": False,
            "webhook_verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        return {
            "checkout_link": checkout_link,
            "order_reference": order_reference,
            "status": "initiated"
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
    """Verify payment status with Xixapay"""
    try:
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": verify.order_ref})
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        payment_status = "pending"
        transaction_reference = ""
        
        try:
            # Verify payment with Xixapay
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{settings.xixapay_base_url}/api/v1/payment/verify/{verify.order_ref}",
                    headers=get_xixapay_headers()
                )
                
                logger.info(f"Xixapay verify response: {response.status_code} - {response.text}")
                
                if response.status_code == 200:
                    xixapay_data = response.json()
                    data = xixapay_data.get("data", xixapay_data)
                    
                    # Map Xixapay status to our status
                    xixapay_status = data.get("status", "").lower()
                    status_map = {
                        "success": "completed",
                        "successful": "completed",
                        "completed": "completed",
                        "paid": "completed",
                        "pending": "pending",
                        "processing": "pending",
                        "failed": "failed",
                        "cancelled": "failed",
                        "abandoned": "failed"
                    }
                    payment_status = status_map.get(xixapay_status, "pending")
                    transaction_reference = data.get("transactionReference") or data.get("reference") or ""
                else:
                    logger.warning(f"Xixapay verification returned {response.status_code}")
                    
        except Exception as verify_error:
            logger.error(f"Xixapay verification error: {str(verify_error)}")
            # Return current known status from database
            payment_status = transaction.get("status", "pending")
        
        # Update transaction
        await db.transactions.update_one(
            {"order_reference": verify.order_ref},
            {"$set": {
                "status": payment_status,
                "transaction_reference": transaction_reference,
                "payment_method": "card",
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
                # Send email notification
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
    """Handle Xixapay payment webhooks"""
    try:
        # Get raw body
        body = await request.body()
        
        # Optional: Verify webhook signature if Xixapay provides one
        signature = request.headers.get("xixapay-signature") or request.headers.get("x-xixapay-signature")
        
        if signature and settings.xixapay_webhook_secret:
            # Verify signature using HMAC-SHA256
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
        
        # Extract transaction details
        order_ref = webhook_data.get("merchantTransactionId") or webhook_data.get("reference") or webhook_data.get("order_reference")
        notification_status = webhook_data.get("status", "").lower()
        transaction_id = webhook_data.get("transactionId") or webhook_data.get("transaction_id")
        
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
        
        # Map status
        status_map = {
            "success": "completed",
            "successful": "completed",
            "completed": "completed",
            "paid": "completed",
            "failed": "failed",
            "cancelled": "failed",
            "abandoned": "failed"
        }
        payment_status = status_map.get(notification_status, "pending")
        
        # Update transaction
        await db.transactions.update_one(
            {"order_reference": transaction["order_reference"]},
            {"$set": {
                "status": payment_status,
                "transaction_reference": transaction_id,
                "webhook_received": True,
                "webhook_verified": True,
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
            
            logger.info(f"Application {application_id} marked as paid via webhook")
        
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
