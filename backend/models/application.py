from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

class LoanApplicationCreate(BaseModel):
    full_name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    home_town: str
    residential_address: str
    place_of_work: str
    employment_status: str
    employment_details: str
    monthly_income: float
    loan_amount: float
    loan_reason: str
    nin: str
    bvn: str

class LoanApplication(LoanApplicationCreate):
    application_id: str
    user_id: Optional[str] = None
    id_card_url: Optional[str] = None
    passport_url: Optional[str] = None
    status: str = "pending_payment"
    payment_status: str = "pending"
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
