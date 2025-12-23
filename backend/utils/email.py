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
    
    async def send_application_received(self, to_email: str, customer_name: str, application_id: str, amount: float):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Application Received - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0d7916;">Application Received</h2>
                    <p>Dear {customer_name},</p>
                    <p>Your loan application (<strong>{application_id}</strong>) has been received successfully.</p>
                    <p><strong>Amount Requested:</strong> ₦{amount:,.2f}</p>
                    <p><strong>Status:</strong> Under Review</p>
                    <p>We will review your application and notify you within 24 hours.</p>
                    <br>
                    <p>Best regards,<br>Cashflow MFB Team</p>
                </div>
                '''
            )
            response = self.client.send(message)
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def send_application_approved(self, to_email: str, customer_name: str, application_id: str, amount: float):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Loan Approved - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0d7916;">Loan Approved!</h2>
                    <p>Dear {customer_name},</p>
                    <p>Congratulations! Your loan application (<strong>{application_id}</strong>) has been approved.</p>
                    <p><strong>Approved Amount:</strong> ₦{amount:,.2f}</p>
                    <p><strong>Next Steps:</strong> Our team will contact you regarding disbursement.</p>
                    <br>
                    <p>Best regards,<br>Cashflow MFB Team</p>
                </div>
                '''
            )
            response = self.client.send(message)
            logger.info(f"Approval email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send approval email: {str(e)}")
            return False
    
    async def send_application_rejected(self, to_email: str, customer_name: str, application_id: str, reason: str):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=f'Application Update - Cashflow MFB',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0d7916;">Application Update</h2>
                    <p>Dear {customer_name},</p>
                    <p>We regret to inform you that your loan application (<strong>{application_id}</strong>) could not be approved at this time.</p>
                    <p><strong>Reason:</strong> {reason}</p>
                    <p>You may reapply after 30 days.</p>
                    <br>
                    <p>Best regards,<br>Cashflow MFB Team</p>
                </div>
                '''
            )
            response = self.client.send(message)
            logger.info(f"Rejection email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to send rejection email: {str(e)}")
            return False

email_service = EmailService()
