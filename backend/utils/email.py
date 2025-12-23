from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = settings.sendgrid_from_email
        self.base_url = settings.backend_url.replace('/api', '')
    
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
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Application Received - Action Required - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #333;">Application Received!</h2>
                    <p>Dear {customer_name},</p>
                    <p>Thank you for submitting your loan application. We have received your application and created your account successfully.</p>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0d7916;">Application Details</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Loan Amount Requested:</strong> ₦{amount:,.2f}</p>
                        <p><strong>Repayment Duration:</strong> {self._get_duration_text(duration)}</p>
                        <p><strong>Repayment Frequency:</strong> {self._get_frequency_text(frequency)}</p>
                        <p><strong>Estimated Payment:</strong> ₦{estimated_payment:,.2f} per {frequency.replace('_', '-')}</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3 style="margin-top: 0; color: #856404;">⚠️ Action Required</h3>
                        <p>To proceed with your application, please pay the <strong>₦2,500</strong> processing fee.</p>
                        <p>Your application will remain pending until payment is received.</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}/login" style="background: #0d7916; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            Login & Pay Now
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>Note:</strong> Processing fee is non-refundable and separate from your loan repayment.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong><br>
                        This email was sent to {to_email}
                    </p>
                </div>
                '''
            )
            response = self.client.send(message)
            logger.info(f"Application received email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send application received email: {str(e)}")
            return False
    
    async def send_application_received(self, to_email: str, customer_name: str, application_id: str, amount: float):
        """Send email when ₦2,500 processing fee is paid - application under review"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Payment Confirmed - Application Under Review - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #0d7916;">✓ Payment Confirmed!</h2>
                    <p>Dear {customer_name},</p>
                    <p>Thank you! Your processing fee payment of ₦2,500 has been confirmed.</p>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0d7916;">
                        <h3 style="margin-top: 0; color: #155724;">Application Status: Under Review</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Loan Amount Requested:</strong> ₦{amount:,.2f}</p>
                    </div>
                    
                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>Our team will review your application within 24 hours</li>
                        <li>You will receive an email notification once a decision is made</li>
                        <li>You can track your application status in your dashboard</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}/login" style="background: #0d7916; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            View Dashboard
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong>
                    </p>
                </div>
                '''
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
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'🎉 Loan Approved! - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #0d7916;">🎉 Congratulations! Your Loan is Approved!</h2>
                    <p>Dear {customer_name},</p>
                    <p>We are pleased to inform you that your loan application has been <strong>APPROVED</strong>!</p>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0d7916;">
                        <h3 style="margin-top: 0; color: #155724;">Approved Loan Details</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Approved Amount:</strong> ₦{amount:,.2f}</p>
                        <p><strong>Repayment Duration:</strong> {self._get_duration_text(duration)}</p>
                        <p><strong>Repayment Frequency:</strong> {self._get_frequency_text(frequency)}</p>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Bank Account for Disbursement</h3>
                        <p><strong>Bank:</strong> {bank_name}</p>
                        <p><strong>Account Number:</strong> {account_number}</p>
                        <p style="color: #666; font-size: 14px;">Your approved loan will be credited to this account.</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3 style="margin-top: 0; color: #856404;">⚠️ Final Step Required</h3>
                        <p>To complete your loan disbursement, please pay the <strong>₦3,000</strong> fixed deposit.</p>
                        <p>This deposit is a security requirement and will be returned upon full loan repayment.</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}/login" style="background: #0d7916; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            Proceed to Pay ₦3,000
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong>
                    </p>
                </div>
                '''
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
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Deposit Confirmed - Processing Your Loan - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #0d7916;">✓ Deposit Confirmed!</h2>
                    <p>Dear {customer_name},</p>
                    <p>Your ₦3,000 fixed deposit has been confirmed. We are now processing your loan disbursement.</p>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0d7916;">
                        <h3 style="margin-top: 0; color: #155724;">Status: Processing</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Loan Amount:</strong> ₦{amount:,.2f}</p>
                        <p><strong>Expected Disbursement:</strong> Within 24 hours</p>
                    </div>
                    
                    <p>Your loan will be credited to your registered bank account within 24 hours.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}/login" style="background: #0d7916; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            Track Status
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong>
                    </p>
                </div>
                '''
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
                first_payments = repayment_schedule[:3]  # Show first 3 payments
                schedule_html = "<table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>"
                schedule_html += "<tr style='background: #f5f5f5;'><th style='padding: 10px; text-align: left;'>Payment #</th><th style='padding: 10px; text-align: left;'>Due Date</th><th style='padding: 10px; text-align: right;'>Amount</th></tr>"
                for payment in first_payments:
                    schedule_html += f"<tr><td style='padding: 10px; border-bottom: 1px solid #eee;'>{payment['payment_number']}</td><td style='padding: 10px; border-bottom: 1px solid #eee;'>{payment['due_date']}</td><td style='padding: 10px; border-bottom: 1px solid #eee; text-align: right;'>₦{payment['amount']:,.2f}</td></tr>"
                schedule_html += "</table>"
                if len(repayment_schedule) > 3:
                    schedule_html += f"<p style='color: #666; font-size: 14px;'>... and {len(repayment_schedule) - 3} more payments. View full schedule in your dashboard.</p>"
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'💰 Loan Disbursed! - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #0d7916;">💰 Your Loan Has Been Disbursed!</h2>
                    <p>Dear {customer_name},</p>
                    <p>Great news! Your approved loan has been credited to your bank account.</p>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0d7916;">
                        <h3 style="margin-top: 0; color: #155724;">Disbursement Details</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Amount Credited:</strong> ₦{amount:,.2f}</p>
                        <p><strong>Bank:</strong> {bank_name}</p>
                        <p><strong>Account:</strong> {account_number}</p>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Upcoming Repayments</h3>
                        {schedule_html}
                    </div>
                    
                    <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0066cc;">
                        <h3 style="margin-top: 0; color: #004085;">📋 Important Reminders</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Make payments on or before the due date to avoid late fees</li>
                            <li>You can view your full repayment schedule in your dashboard</li>
                            <li>Early repayment is allowed without penalties</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{self.base_url}/login" style="background: #0d7916; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            View Repayment Schedule
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong>
                    </p>
                </div>
                '''
            )
            response = self.client.send(message)
            logger.info(f"Disbursement email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send disbursement email: {str(e)}")
            return False
    
    async def send_application_rejected(self, to_email: str, customer_name: str, application_id: str, reason: str):
        """Send rejection email"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Application Update - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0d7916; margin: 0;">Cashflow MFB</h1>
                    </div>
                    
                    <h2 style="color: #333;">Application Update</h2>
                    <p>Dear {customer_name},</p>
                    <p>We regret to inform you that your loan application (<strong>{application_id}</strong>) could not be approved at this time.</p>
                    
                    <div style="background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <p><strong>Reason:</strong> {reason}</p>
                    </div>
                    
                    <p>You may reapply after 30 days. If you have any questions, please contact our support team.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Best regards,<br>
                        <strong>Cashflow MFB Team</strong>
                    </p>
                </div>
                '''
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

email_service = EmailService()
