from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class RepaymentDuration(str, Enum):
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    NINE_MONTHS = "9_months"
    TWELVE_MONTHS = "12_months"

class RepaymentFrequency(str, Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"

class ApplicationStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"  # Application submitted, ₦2,500 not paid
    UNDER_REVIEW = "under_review"  # ₦2,500 paid, awaiting approval
    APPROVED = "approved"  # Approved, awaiting ₦3,000 deposit
    DEPOSIT_PAID = "deposit_paid"  # ₦3,000 paid, processing
    PROCESSING = "processing"  # 24hr processing period
    DISBURSED = "disbursed"  # Loan credited to account
    REPAYMENT_IN_PROGRESS = "repayment_in_progress"  # Active repayment
    FULLY_REPAID = "fully_repaid"  # Loan fully repaid
    REJECTED = "rejected"  # Application rejected

class LoanApplicationCreate(BaseModel):
    # Personal Information
    full_name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    home_town: str
    residential_address: str
    
    # Employment & Income
    place_of_work: str
    employment_status: str
    employment_details: str
    monthly_income: float
    loan_reason: str
    
    # Bank Account Details
    bank_name: str
    account_name: str
    account_number: str
    
    # Loan & Repayment Preferences
    loan_amount: float
    repayment_duration: RepaymentDuration
    repayment_frequency: RepaymentFrequency
    
    # Identity
    nin: str
    bvn: str
    
    # Account Creation
    password: str

class LoanApplication(BaseModel):
    application_id: str
    user_id: Optional[str] = None
    
    # Personal Information
    full_name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    home_town: str
    residential_address: str
    
    # Employment & Income
    place_of_work: str
    employment_status: str
    employment_details: str
    monthly_income: float
    loan_reason: str
    
    # Bank Account Details
    bank_name: str
    account_name: str
    account_number: str
    
    # Loan & Repayment Preferences
    loan_amount: float
    approved_amount: Optional[float] = None
    repayment_duration: str
    repayment_frequency: str
    estimated_repayment: Optional[float] = None
    
    # Identity
    nin: str
    bvn: str
    id_card_url: Optional[str] = None
    passport_url: Optional[str] = None
    
    # Status & Payments
    status: str = ApplicationStatus.PENDING_PAYMENT.value
    payment_status: str = "pending"  # pending, processing_fee_paid, deposit_paid
    processing_fee_paid: bool = False
    processing_fee_paid_at: Optional[datetime] = None
    deposit_paid: bool = False
    deposit_paid_at: Optional[datetime] = None
    
    # Disbursement
    disbursed: bool = False
    disbursed_at: Optional[datetime] = None
    disbursement_reference: Optional[str] = None
    
    # Repayment
    repayment_schedule: Optional[List[dict]] = None
    total_repaid: float = 0.0
    outstanding_balance: Optional[float] = None
    next_repayment_date: Optional[date] = None
    next_repayment_amount: Optional[float] = None
    
    # Admin
    admin_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    approved_amount: Optional[float] = None

class RepaymentScheduleItem(BaseModel):
    payment_number: int
    due_date: date
    amount: float
    principal: float
    interest: float
    status: str = "pending"  # pending, paid, overdue
    paid_at: Optional[datetime] = None

def calculate_repayment(loan_amount: float, duration: str, frequency: str) -> dict:
    """Calculate estimated repayment details"""
    # Interest rate: 5% per month (simple calculation for display)
    monthly_rate = 0.05
    
    # Duration in months
    duration_months = {
        "3_months": 3,
        "6_months": 6,
        "9_months": 9,
        "12_months": 12
    }.get(duration, 6)
    
    # Total interest
    total_interest = loan_amount * monthly_rate * duration_months
    total_amount = loan_amount + total_interest
    
    # Payments per month based on frequency
    payments_per_month = {
        "weekly": 4,
        "bi_weekly": 2,
        "monthly": 1
    }.get(frequency, 1)
    
    total_payments = duration_months * payments_per_month
    payment_amount = total_amount / total_payments
    
    return {
        "loan_amount": loan_amount,
        "total_interest": round(total_interest, 2),
        "total_amount": round(total_amount, 2),
        "duration_months": duration_months,
        "frequency": frequency,
        "total_payments": total_payments,
        "payment_amount": round(payment_amount, 2),
        "monthly_rate": monthly_rate * 100
    }
