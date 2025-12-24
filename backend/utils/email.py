from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import get_settings
import logging
import os
from datetime import datetime

settings = get_settings()
logger = logging.getLogger(__name__)

# Logo URL for emails (can be overridden by environment variable)
LOGO_URL = os.environ.get("LOGO_URL", "https://customer-assets.emergentagent.com/job_microfin-portal/artifacts/yv8s58dq_1000315618-removebg-preview.png")
WEBSITE_URL = os.environ.get("BACKEND_URL", "https://cashflowsmfb.com")

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = settings.sendgrid_from_email
        self.base_url = WEBSITE_URL
    
    def _get_email_header(self):
        """Get branded email header with logo"""
        return f'''
        <div style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%);">
            <a href="{self.base_url}" target="_blank">
                <img src="{LOGO_URL}" alt="Cashflow MFB" style="max-width: 180px; height: auto;" />
            </a>
        </div>
        '''
    
    def _get_email_footer(self):
        """Get branded email footer"""
        return f'''
        <div style="background: #f8f9fa; padding: 30px 20px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px 0;">
                Need help? Contact our support team
            </p>
            <p style="margin: 0;">
                <a href="mailto:support@cashflowmfb.ng" style="color: #0d7916; text-decoration: none;">support@cashflowmfb.ng</a>
                &nbsp;|&nbsp;
                <a href="tel:+2348000000000" style="color: #0d7916; text-decoration: none;">+234 800 CASHFLOW</a>
            </p>
            <p style="color: #adb5bd; font-size: 12px; margin-top: 20px;">
                © {datetime.now().year} Cashflow MFB. Licensed by CBN.<br>
                Lagos, Nigeria
            </p>
        </div>
        '''
    
    def _get_email_template(self, content):
        """Wrap content in branded email template"""
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                {self._get_email_header()}
                <div style="padding: 40px 30px;">
                    {content}
                </div>
                {self._get_email_footer()}
            </div>
        </body>
        </html>
        '''
    
    def _get_duration_text(self, duration: str) -> str:
        """Convert duration code to readable text"""
        mapping = {
            "3_months": "3 Months",
            "6_months": "6 Months",
            "9_months": "9 Months",
            "12_months": "12 Months"
        }
        return mapping.get(duration, duration)
    
    def _get_frequency_text(self, frequency: str) -> str:
        """Convert frequency code to readable text"""
        mapping = {
            "weekly": "Weekly",
            "bi_weekly": "Bi-Weekly",
            "monthly": "Monthly"
        }
        return mapping.get(frequency, frequency)
    
    async def send_application_received_pending_payment(
        self, to_email: str, customer_name: str, application_id: str,
        amount: float, duration: str, frequency: str, estimated_payment: float
    ):
        """Send email when application is submitted but payment not yet made"""
        try:
            content = f'''
            <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px;">Application Received!</h2>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Thank you for submitting your loan application. We have received your application and created your account successfully.
            </p>
            
            <div style="background: #f8f9fa; border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="color: #0d7916; margin: 0 0 15px 0; font-size: 18px;">📋 Application Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px;">Application ID:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px; font-weight: 600;">{application_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px;">Loan Amount:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px; font-weight: 600;">₦{amount:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px;">Duration:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px; font-weight: 600;">{self._get_duration_text(duration)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px;">Frequency:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px; font-weight: 600;">{self._get_frequency_text(frequency)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px;">Est. Payment:</td>
                        <td style="padding: 8px 0; color: #0d7916; font-size: 14px; font-weight: 600;">₦{estimated_payment:,.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #856404; margin: 0 0 10px 0; font-size: 16px;">⚠️ Action Required</h3>
                <p style="color: #856404; margin: 0; font-size: 14px;">
                    To proceed with your application, please pay the <strong>₦2,500</strong> processing fee.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(13, 121, 22, 0.3);">
                    Login & Pay Now
                </a>
            </div>
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Processing fee is non-refundable and separate from your loan repayment.
            </p>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Application Received - Action Required | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Application received email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send application received email: {str(e)}")
            return False
    
    async def send_payment_confirmation(
        self, to_email: str, customer_name: str, amount: float,
        fee_type: str, transaction_ref: str, application_id: str
    ):
        """Send payment confirmation email with full details"""
        try:
            fee_label = "Processing Fee" if fee_type == "processing_fee" else "Fixed Deposit"
            now = datetime.now()
            
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">✓</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 28px;">Payment Successful!</h2>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Your payment has been confirmed. Thank you for your payment.
            </p>
            
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 25px; margin: 25px 0; border: 1px solid #dee2e6;">
                <h3 style="color: #333; margin: 0 0 20px 0; font-size: 18px; border-bottom: 2px solid #0d7916; padding-bottom: 10px;">Payment Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px; border-bottom: 1px solid #e9ecef;">Customer Name:</td>
                        <td style="padding: 12px 0; color: #333; font-size: 14px; font-weight: 600; text-align: right; border-bottom: 1px solid #e9ecef;">{customer_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px; border-bottom: 1px solid #e9ecef;">Fee Type:</td>
                        <td style="padding: 12px 0; color: #333; font-size: 14px; font-weight: 600; text-align: right; border-bottom: 1px solid #e9ecef;">{fee_label}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px; border-bottom: 1px solid #e9ecef;">Amount Paid:</td>
                        <td style="padding: 12px 0; color: #0d7916; font-size: 18px; font-weight: 700; text-align: right; border-bottom: 1px solid #e9ecef;">₦{amount:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px; border-bottom: 1px solid #e9ecef;">Date & Time:</td>
                        <td style="padding: 12px 0; color: #333; font-size: 14px; font-weight: 600; text-align: right; border-bottom: 1px solid #e9ecef;">{now.strftime('%B %d, %Y at %I:%M %p')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px; border-bottom: 1px solid #e9ecef;">Transaction Ref:</td>
                        <td style="padding: 12px 0; color: #333; font-size: 12px; font-family: monospace; text-align: right; border-bottom: 1px solid #e9ecef;">{transaction_ref}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-size: 14px;">Application ID:</td>
                        <td style="padding: 12px 0; color: #333; font-size: 14px; font-weight: 600; text-align: right;">{application_id}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #d4edda; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <p style="color: #155724; margin: 0; font-size: 14px;">
                    <strong>What's Next?</strong><br>
                    {"Your application is now under review. You will be notified within 24 hours." if fee_type == "processing_fee" else "Your loan is being processed. Funds will be credited within 24 hours."}
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                    View Dashboard
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Payment Confirmed - ₦{amount:,.0f} {fee_label} | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Payment confirmation email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {str(e)}")
            return False
    
    async def send_application_received(self, to_email: str, customer_name: str, application_id: str, amount: float):
        """Send email when ₦2,500 processing fee is paid - application under review"""
        try:
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">✓</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 28px;">Payment Confirmed!</h2>
                <p style="color: #666; font-size: 16px; margin-top: 10px;">Application Under Review</p>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Thank you! Your processing fee payment of ₦2,500 has been confirmed.
            </p>
            
            <div style="background: #d4edda; border-left: 4px solid #0d7916; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #155724; margin: 0 0 10px 0; font-size: 16px;">Application Status: Under Review</h3>
                <p style="color: #155724; margin: 0; font-size: 14px;">
                    <strong>Application ID:</strong> {application_id}<br>
                    <strong>Loan Amount:</strong> ₦{amount:,.2f}
                </p>
            </div>
            
            <h3 style="color: #333; font-size: 16px; margin-top: 30px;">What happens next?</h3>
            <ul style="color: #555; font-size: 14px; line-height: 2;">
                <li>Our team will review your application within 24 hours</li>
                <li>You will receive an email notification once a decision is made</li>
                <li>You can track your application status in your dashboard</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                    View Dashboard
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Payment Confirmed - Application Under Review | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Payment confirmed email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send payment confirmed email: {str(e)}")
            return False
    
    async def send_loan_approved(
        self, to_email: str, customer_name: str, application_id: str,
        amount: float, duration: str, frequency: str, bank_name: str, account_number: str
    ):
        """Send approval email with ₦3,000 deposit request"""
        try:
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">🎉</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 28px;">Congratulations!</h2>
                <p style="color: #666; font-size: 18px; margin-top: 10px;">Your Loan is Approved!</p>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                We are pleased to inform you that your loan application has been <strong style="color: #0d7916;">APPROVED</strong>!
            </p>
            
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="color: #155724; margin: 0 0 15px 0; font-size: 18px;">✓ Approved Loan Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Application ID:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{application_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Approved Amount:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 18px; font-weight: 700;">₦{amount:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Duration:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{self._get_duration_text(duration)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Frequency:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{self._get_frequency_text(frequency)}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #f8f9fa; border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="color: #333; margin: 0 0 15px 0; font-size: 16px;">Bank Account for Disbursement</h3>
                <p style="color: #555; font-size: 14px; margin: 0;">
                    <strong>Bank:</strong> {bank_name}<br>
                    <strong>Account Number:</strong> {account_number}
                </p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">
                    Your approved loan will be credited to this account.
                </p>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #856404; margin: 0 0 10px 0; font-size: 16px;">⚠️ Final Step Required</h3>
                <p style="color: #856404; margin: 0; font-size: 14px;">
                    To complete your loan disbursement, please pay the <strong>₦3,000</strong> fixed deposit.<br>
                    This deposit is a security requirement and will be returned upon full loan repayment.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(13, 121, 22, 0.3);">
                    Proceed to Pay ₦3,000
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='🎉 Loan Approved! - Complete Your Disbursement | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Approval email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send approval email: {str(e)}")
            return False
    
    async def send_deposit_confirmed(self, to_email: str, customer_name: str, application_id: str, amount: float):
        """Send email when ₦3,000 deposit is paid"""
        try:
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">✓</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 28px;">Deposit Confirmed!</h2>
                <p style="color: #666; font-size: 16px; margin-top: 10px;">Processing Your Loan</p>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Your ₦3,000 fixed deposit has been confirmed. We are now processing your loan disbursement.
            </p>
            
            <div style="background: #d4edda; border-left: 4px solid #0d7916; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #155724; margin: 0 0 10px 0; font-size: 16px;">Status: Processing</h3>
                <p style="color: #155724; margin: 0; font-size: 14px;">
                    <strong>Application ID:</strong> {application_id}<br>
                    <strong>Loan Amount:</strong> ₦{amount:,.2f}<br>
                    <strong>Expected Disbursement:</strong> Within 24 hours
                </p>
            </div>
            
            <p style="color: #555; font-size: 14px; line-height: 1.6;">
                Your loan will be credited to your registered bank account within 24 hours.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                    Track Status
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Deposit Confirmed - Processing Your Loan | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Deposit confirmed email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send deposit confirmed email: {str(e)}")
            return False
    
    async def send_loan_disbursed(
        self, to_email: str, customer_name: str, application_id: str,
        amount: float, bank_name: str, account_number: str, repayment_schedule: list
    ):
        """Send email when loan is disbursed"""
        try:
            # Build repayment schedule table
            schedule_html = ""
            if repayment_schedule and len(repayment_schedule) > 0:
                first_payments = repayment_schedule[:3]
                schedule_html = "<table style='width: 100%; border-collapse: collapse; margin-top: 15px;'>"
                schedule_html += "<tr style='background: #e9ecef;'><th style='padding: 10px; text-align: left; font-size: 12px;'>#</th><th style='padding: 10px; text-align: left; font-size: 12px;'>Due Date</th><th style='padding: 10px; text-align: right; font-size: 12px;'>Amount</th></tr>"
                for payment in first_payments:
                    schedule_html += f"<tr><td style='padding: 10px; border-bottom: 1px solid #e9ecef; font-size: 14px;'>{payment['payment_number']}</td><td style='padding: 10px; border-bottom: 1px solid #e9ecef; font-size: 14px;'>{payment['due_date']}</td><td style='padding: 10px; border-bottom: 1px solid #e9ecef; font-size: 14px; text-align: right; font-weight: 600;'>₦{payment['amount']:,.2f}</td></tr>"
                schedule_html += "</table>"
                if len(repayment_schedule) > 3:
                    schedule_html += f"<p style='color: #666; font-size: 12px; margin-top: 10px;'>... and {len(repayment_schedule) - 3} more payments</p>"
            
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">💰</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 28px;">Loan Disbursed!</h2>
                <p style="color: #666; font-size: 16px; margin-top: 10px;">Funds Credited to Your Account</p>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Great news! Your approved loan has been credited to your bank account.
            </p>
            
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="color: #155724; margin: 0 0 15px 0; font-size: 18px;">💵 Disbursement Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Application ID:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{application_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Amount Credited:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 20px; font-weight: 700;">₦{amount:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Bank:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{bank_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px;">Account:</td>
                        <td style="padding: 8px 0; color: #155724; font-size: 14px; font-weight: 600;">{account_number}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #f8f9fa; border-radius: 12px; padding: 25px; margin: 25px 0;">
                <h3 style="color: #333; margin: 0 0 5px 0; font-size: 16px;">📅 Upcoming Repayments</h3>
                {schedule_html}
            </div>
            
            <div style="background: #e7f3ff; border-left: 4px solid #0066cc; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #004085; margin: 0 0 10px 0; font-size: 16px;">📋 Important Reminders</h3>
                <ul style="color: #004085; margin: 0; padding-left: 20px; font-size: 14px;">
                    <li>Make payments on or before the due date</li>
                    <li>View your full schedule in your dashboard</li>
                    <li>Early repayment is allowed without penalties</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                    View Repayment Schedule
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='💰 Loan Disbursed! - Funds Credited | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Disbursement email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send disbursement email: {str(e)}")
            return False
    
    async def send_payment_reminder(
        self, to_email: str, customer_name: str, application_id: str,
        fee_type: str, amount: float
    ):
        """Send payment reminder email"""
        try:
            fee_label = "Processing Fee (₦2,500)" if fee_type == "processing_fee" else "Fixed Deposit (₦3,000)"
            
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #fff3cd; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">⏰</span>
                </div>
                <h2 style="color: #856404; margin: 0; font-size: 24px;">Payment Reminder</h2>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                This is a friendly reminder that your <strong>{fee_label}</strong> payment is still pending for application <strong>{application_id}</strong>.
            </p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <h3 style="color: #856404; margin: 0 0 10px 0; font-size: 16px;">Outstanding Payment</h3>
                <p style="color: #856404; margin: 0; font-size: 24px; font-weight: 700;">
                    ₦{amount:,.2f}
                </p>
            </div>
            
            <p style="color: #555; font-size: 14px; line-height: 1.6;">
                Please complete your payment to proceed with your loan application. Your application cannot be processed until payment is received.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(13, 121, 22, 0.3);">
                    Pay Now
                </a>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'⏰ Payment Reminder - {fee_label} | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Payment reminder email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send payment reminder email: {str(e)}")
            return False
    
    async def send_application_rejected(self, to_email: str, customer_name: str, application_id: str, reason: str):
        """Send rejection email"""
        try:
            content = f'''
            <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px;">Application Update</h2>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                We regret to inform you that your loan application (<strong>{application_id}</strong>) could not be approved at this time.
            </p>
            
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <p style="color: #721c24; margin: 0; font-size: 14px;">
                    <strong>Reason:</strong> {reason}
                </p>
            </div>
            
            <p style="color: #555; font-size: 14px; line-height: 1.6;">
                You may reapply after 30 days. If you have any questions, please contact our support team.
            </p>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Application Update | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Rejection email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send rejection email: {str(e)}")
            return False
    
    async def send_application_approved(self, to_email: str, customer_name: str, application_id: str, amount: float):
        """Legacy method - redirects to send_loan_approved"""
        return await self.send_loan_approved(
            to_email, customer_name, application_id, amount,
            "6_months", "monthly", "N/A", "N/A"
        )
    
    async def send_password_reset(self, to_email: str, customer_name: str, reset_token: str):
        """Send password reset email with reset link"""
        try:
            reset_link = f"{self.base_url}/reset-password?token={reset_token}"
            
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #e7f3ff; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">🔐</span>
                </div>
                <h2 style="color: #333; margin: 0; font-size: 24px;">Password Reset Request</h2>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                We received a request to reset your password for your Cashflow MFB account.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(13, 121, 22, 0.3);">
                    Reset My Password
                </a>
            </div>
            
            <p style="color: #999; font-size: 14px; text-align: center; margin: 20px 0;">
                Or copy and paste this link into your browser:
            </p>
            <p style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-size: 12px; word-break: break-all; color: #666; text-align: center;">
                {reset_link}
            </p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <p style="color: #856404; margin: 0; font-size: 14px;">
                    <strong>⚠️ Important:</strong><br>
                    • This link will expire in 1 hour<br>
                    • If you didn't request this reset, please ignore this email<br>
                    • Never share this link with anyone
                </p>
            </div>
            
            <p style="color: #555; font-size: 14px; line-height: 1.6;">
                If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.
            </p>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Password Reset Request | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Password reset email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    async def send_password_changed(self, to_email: str, customer_name: str):
        """Send confirmation email when password is successfully changed"""
        try:
            content = f'''
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: #d4edda; border-radius: 50%; padding: 20px; margin-bottom: 15px;">
                    <span style="font-size: 40px;">✓</span>
                </div>
                <h2 style="color: #0d7916; margin: 0; font-size: 24px;">Password Changed Successfully</h2>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6;">
                Your password has been successfully changed. You can now log in with your new password.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.base_url}/login" style="display: inline-block; background: linear-gradient(135deg, #0d7916 0%, #0a5c12 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                    Login to Your Account
                </a>
            </div>
            
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                <p style="color: #721c24; margin: 0; font-size: 14px;">
                    <strong>⚠️ Didn't change your password?</strong><br>
                    If you didn't make this change, please contact our support team immediately at payment@cashflowsmfb.com
                </p>
            </div>
            '''
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Password Changed Successfully | Cashflow MFB',
                html_content=self._get_email_template(content)
            )
            response = self.client.send(message)
            logger.info(f"Password changed confirmation email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password changed email: {str(e)}")
            return False

email_service = EmailService()
