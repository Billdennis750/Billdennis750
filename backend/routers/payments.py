from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from database import get_db
from config import get_settings
from utils.email import email_service
from datetime import datetime
import httpx
import logging
import hmac
import hashlib
import base64
import json

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

async def get_nomba_headers():
    """Get Nomba API headers with authentication"""
    try:
        # Nomba uses accountId and privateKey for authentication
        auth_string = f"{settings.nomba_account_id}:{settings.nomba_private_key}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        return {
            "Authorization": f"Bearer {auth_b64}",
            "Content-Type": "application/json"
        }
    except Exception as e:
        logger.error(f"Failed to create Nomba headers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment gateway configuration error"
        )

@router.post("/initiate", response_model=dict)
async def initiate_payment(payment: PaymentInitiate, db=Depends(get_db)):
    try:
        # Verify application exists
        application = await db.applications.find_one({"application_id": payment.application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Get Nomba headers
        headers = await get_nomba_headers()
        
        # Create order reference
        order_reference = f"{payment.application_id}-{int(datetime.now().timestamp())}"
        
        # Prepare checkout payload
        checkout_payload = {
            "amount": int(payment.amount * 100),  # Convert to kobo
            "currency": "NGN",
            "customerEmail": payment.customer_email,
            "customerName": payment.customer_name,
            "orderReference": order_reference,
            "redirectUrl": payment.redirect_url,
            "callbackUrl": f"{settings.backend_url}/api/webhooks/nomba",
            "description": "Loan Processing Fee",
            "metadata": {
                "application_id": payment.application_id,
                "fee_type": "processing_fee"
            }
        }
        
        # Create checkout order with Nomba
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.nomba_base_url}/v1/checkout/order",
                headers=headers,
                json=checkout_payload,
                timeout=15.0
            )
            response.raise_for_status()
            checkout_response = response.json()
        
        # Store transaction record
        transaction_doc = {
            "application_id": payment.application_id,
            "order_reference": order_reference,
            "customer_email": payment.customer_email,
            "customer_name": payment.customer_name,
            "amount": payment.amount,
            "currency": "NGN",
            "nomba_checkout_id": checkout_response.get("checkoutId"),
            "status": "initiated",
            "transaction_reference": None,
            "payment_method": None,
            "webhook_received": False,
            "webhook_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.transactions.insert_one(transaction_doc)
        
        return {
            "checkout_link": checkout_response.get("checkoutLink"),
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
    try:
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": verify.order_ref})
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Get Nomba access token
        access_token = await get_nomba_access_token()
        
        # Query Nomba for transaction status
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.nomba_base_url}/checkout/order/{verify.order_ref}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15.0
            )
            response.raise_for_status()
            nomba_transaction = response.json()
        
        # Determine payment status
        nomba_status = nomba_transaction.get("status", "").lower()
        status_map = {
            "completed": "completed",
            "successful": "completed",
            "pending": "pending",
            "failed": "failed",
            "cancelled": "failed"
        }
        payment_status = status_map.get(nomba_status, "pending")
        
        # Update transaction
        await db.transactions.update_one(
            {"order_reference": verify.order_ref},
            {"$set": {
                "status": payment_status,
                "transaction_reference": nomba_transaction.get("transactionReference"),
                "payment_method": nomba_transaction.get("paymentMethod"),
                "updated_at": datetime.utcnow()
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
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Get application details
            application = await db.applications.find_one({"application_id": application_id})
            
            # Send email notification
            await email_service.send_application_received(
                application["email"],
                application["full_name"],
                application_id,
                application["loan_amount"]
            )
        
        return {
            "payment_status": payment_status,
            "transaction_reference": nomba_transaction.get("transactionReference", ""),
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

@router.post("/webhooks/nomba")
async def nomba_webhook(request: Request, db=Depends(get_db)):
    """Handle Nomba payment webhooks"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("X-Nomba-Signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Verify signature
        if not verify_webhook_signature(body, signature, settings.nomba_webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Parse webhook data
        webhook_data = json.loads(body)
        order_ref = webhook_data.get("reference")
        
        # Find transaction
        transaction = await db.transactions.find_one({"order_reference": order_ref})
        if not transaction:
            logger.warning(f"Transaction not found for webhook: {order_ref}")
            return {"status": "ok"}
        
        # Update transaction status
        nomba_status = webhook_data.get("status", "").lower()
        status_map = {
            "success": "completed",
            "successful": "completed",
            "completed": "completed",
            "failed": "failed",
            "cancelled": "failed"
        }
        payment_status = status_map.get(nomba_status, "pending")
        
        await db.transactions.update_one(
            {"order_reference": order_ref},
            {"$set": {
                "status": payment_status,
                "transaction_reference": webhook_data.get("transactionId"),
                "webhook_received": True,
                "webhook_verified": True,
                "updated_at": datetime.utcnow()
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
                    "updated_at": datetime.utcnow()
                }}
            )
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Nomba webhook signature"""
    try:
        if not signature.startswith("v1,"):
            return False
        
        provided_signature = signature.split(",")[1]
        provided_signature_bytes = base64.b64decode(provided_signature)
        
        secret_bytes = secret.encode() if isinstance(secret, str) else secret
        expected_signature = hmac.new(secret_bytes, payload, hashlib.sha256).digest()
        
        return hmac.compare_digest(expected_signature, provided_signature_bytes)
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        return False
