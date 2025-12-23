# Cashflow MFB - Backend Integration Contracts

## Overview
This document outlines the API contracts, database schemas, and integration points between frontend and backend.

## Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Payment Gateway**: Nomba
- **Email Service**: SendGrid
- **File Storage**: Local server storage

## API Endpoints

### 1. Authentication APIs

#### POST /api/auth/register
Register a new user account
```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "phone": "+234 801 234 5678"
}

Response:
{
  "message": "Registration successful",
  "user_id": "user_123"
}
```

#### POST /api/auth/login
User login
```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

### 2. Loan Application APIs

#### POST /api/applications/submit
Submit loan application
```json
Request:
{
  "full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "email": "john@example.com",
  "phone": "+234 801 234 5678",
  "home_town": "Lagos",
  "residential_address": "123 Main St, Lagos",
  "place_of_work": "Company Name",
  "employment_status": "employed",
  "employment_details": "Senior Developer",
  "monthly_income": 250000,
  "loan_amount": 5000000,
  "loan_reason": "Business expansion",
  "nin": "12345678901",
  "bvn": "12345678901"
}

Response:
{
  "application_id": "LOAN-2025-001",
  "status": "pending_payment",
  "payment_url": "/payment/initiate/LOAN-2025-001"
}
```

#### GET /api/applications/{application_id}
Get application details
```json
Response:
{
  "id": "LOAN-2025-001",
  "status": "under_review",
  "loan_amount": 5000000,
  "customer_name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z",
  "payment_status": "paid"
}
```

#### GET /api/applications/user/{user_id}
Get all applications for a user

#### PUT /api/applications/{application_id}/status
Update application status (Admin only)
```json
Request:
{
  "status": "approved",
  "notes": "Application approved"
}
```

### 3. Payment APIs

#### POST /api/payments/initiate
Initiate Nomba payment
```json
Request:
{
  "application_id": "LOAN-2025-001",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "amount": 2500,
  "redirect_url": "http://localhost:3000/payment-callback"
}

Response:
{
  "checkout_link": "https://nomba.com/checkout/xyz",
  "order_reference": "LOAN-2025-001-1234567890"
}
```

#### POST /api/payments/verify
Verify payment status
```json
Request:
{
  "order_ref": "LOAN-2025-001-1234567890"
}

Response:
{
  "payment_status": "completed",
  "transaction_reference": "NOMBA-TXN-123456",
  "amount": 2500,
  "application_id": "LOAN-2025-001"
}
```

#### POST /api/webhooks/nomba
Nomba webhook endpoint for payment notifications

### 4. File Upload APIs

#### POST /api/uploads/documents
Upload ID card and passport photo
```
Content-Type: multipart/form-data

Fields:
- application_id: LOAN-2025-001
- id_card: file
- passport: file

Response:
{
  "id_card_url": "/uploads/LOAN-2025-001/id_card.jpg",
  "passport_url": "/uploads/LOAN-2025-001/passport.jpg"
}
```

### 5. Admin APIs

#### GET /api/admin/applications
Get all loan applications with filters
```
Query params:
- status: under_review|approved|rejected
- page: 1
- limit: 20
```

#### GET /api/admin/stats
Get dashboard statistics
```json
Response:
{
  "total_applications": 156,
  "pending_review": 23,
  "approved": 98,
  "rejected": 15,
  "total_disbursed": 450000000
}
```

## Database Schemas

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "full_name": "John Doe",
  "phone": "+234 801 234 5678",
  "role": "user|admin",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Applications Collection
```json
{
  "_id": "ObjectId",
  "application_id": "LOAN-2025-001",
  "user_id": "user_123",
  "full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "email": "john@example.com",
  "phone": "+234 801 234 5678",
  "home_town": "Lagos",
  "residential_address": "123 Main St",
  "place_of_work": "Company Name",
  "employment_status": "employed",
  "employment_details": "Senior Developer",
  "monthly_income": 250000,
  "loan_amount": 5000000,
  "loan_reason": "Business expansion",
  "nin": "12345678901",
  "bvn": "12345678901",
  "id_card_url": "/uploads/LOAN-2025-001/id_card.jpg",
  "passport_url": "/uploads/LOAN-2025-001/passport.jpg",
  "status": "pending_payment|under_review|approved|rejected|disbursed",
  "payment_status": "pending|paid|failed",
  "admin_notes": "",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Transactions Collection
```json
{
  "_id": "ObjectId",
  "application_id": "LOAN-2025-001",
  "order_reference": "LOAN-2025-001-1234567890",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "amount": 2500,
  "currency": "NGN",
  "nomba_checkout_id": "checkout_123",
  "status": "initiated|pending|completed|failed",
  "transaction_reference": "NOMBA-TXN-123456",
  "payment_method": "card",
  "webhook_received": false,
  "webhook_verified": false,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

## Frontend Integration Points

### Mock Data to Remove
- `/app/frontend/src/mock.js` - All mock functions
- `localStorage` usage in:
  - AuthContext (replace with JWT tokens)
  - LoanApplicationPage (replace with API calls)
  - PaymentCallbackPage (replace with API verification)

### Components to Update
1. **AuthContext.jsx** - Replace mock login with API call
2. **LoanApplicationPage.jsx** - Submit to backend API
3. **PaymentCallbackPage.jsx** - Verify payment via API
4. **UserDashboard.jsx** - Fetch data from API
5. **AdminDashboard.jsx** - Fetch applications from API

### Environment Variables
**Frontend (.env)**
```
REACT_APP_BACKEND_URL=<existing>
```

**Backend (.env)**
```
MONGO_URL=<existing>
DB_NAME=cashflow_mfb
JWT_SECRET=<generate_random_secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Nomba Payment Gateway
NOMBA_CLIENT_ID=microfin-portal
NOMBA_PRIVATE_KEY=BGLBxwTcgpQOjnMQ7eWbRUoIykYE+1Eqlcl6x7MXjDjutfbw7dmVWgLH7ULBX6rYa6i0tUi2B7FptHYBhV5sWQ==
NOMBA_ACCOUNT_ID=microfin-portal
NOMBA_BASE_URL=https://api.nomba.com
NOMBA_WEBHOOK_SECRET=<generate_webhook_secret>

# SendGrid Email
SENDGRID_API_KEY=2zuSvjMgaTx7wepeNgiHWMPuB6j2KRug
SENDGRID_FROM_EMAIL=kingsleydennis7500@gmail.com

# File Upload
UPLOAD_DIR=/app/backend/uploads
MAX_FILE_SIZE=5242880
```

## Email Templates

### Application Received
```
Subject: Application Received - Cashflow MFB

Dear [Customer Name],

Your loan application ([Application ID]) has been received successfully.

Amount Requested: ₦[Amount]
Status: Under Review

We will review your application and notify you within 24 hours.

Best regards,
Cashflow MFB Team
```

### Application Approved
```
Subject: Loan Approved - Cashflow MFB

Dear [Customer Name],

Congratulations! Your loan application ([Application ID]) has been approved.

Approved Amount: ₦[Amount]
Next Steps: Our team will contact you regarding disbursement.

Login to your dashboard: [Dashboard URL]

Best regards,
Cashflow MFB Team
```

### Application Rejected
```
Subject: Application Update - Cashflow MFB

Dear [Customer Name],

We regret to inform you that your loan application ([Application ID]) could not be approved at this time.

Reason: [Admin Notes]

You may reapply after 30 days.

Best regards,
Cashflow MFB Team
```

## Security Considerations
1. All passwords hashed with bcrypt
2. JWT tokens for authentication
3. File upload validation (type, size)
4. Webhook signature verification for Nomba
5. Input validation and sanitization
6. CORS configuration for frontend domain
7. Rate limiting on authentication endpoints
8. Sensitive data encryption in database

## Testing Checklist
- [ ] User registration and login
- [ ] JWT token generation and validation
- [ ] Loan application submission
- [ ] File upload (ID card, passport)
- [ ] Nomba payment initiation
- [ ] Payment webhook handling
- [ ] Email notifications
- [ ] Admin dashboard operations
- [ ] User dashboard data fetching
- [ ] Application status updates
