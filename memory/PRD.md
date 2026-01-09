# Cashflow MFB - Product Requirements Document

## Original Problem Statement
Build a full-stack platform for Cashflow MFB, a microfinance bank, enabling:
- Multi-step loan applications with document uploads
- User dashboard for tracking application status and payments
- Admin dashboard for managing applications and approvals
- Payment integration for processing fees (₦2,500) and fixed deposits (₦3,000)
- Email notifications for application status changes

## Tech Stack
- **Frontend**: React, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **Database**: MongoDB
- **Email**: Resend (primary), SendGrid (fallback)
- **Payments**: BudPay (migrated from Xixapay)

## Core Features

### User Features
- Multi-step loan application form (5 steps)
- Document upload (ID card, passport photo)
- User dashboard with application status tracking
- Payment processing for fees and deposits
- Password reset functionality

### Admin Features
- View all applications with filtering
- Approve/reject loan applications
- Approve/decline loan disbursements
- View uploaded documents
- Email notifications to users

## Payment Flow
1. User submits loan application → Status: `pending_payment`
2. User pays ₦2,500 processing fee via BudPay → Status: `under_review`
3. Admin reviews and approves → Status: `approved`
4. User pays ₦3,000 fixed deposit → Status: `deposit_paid`, Disbursement: `pending`
5. Admin approves disbursement → Status: `disbursed`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Applications
- `POST /api/applications/` - Submit new application
- `GET /api/applications/` - List all applications
- `GET /api/applications/{id}` - Get single application
- `GET /api/applications/user/my-applications` - Get user's applications

### Payments (BudPay)
- `POST /api/payments/initiate` - Initialize BudPay checkout
- `POST /api/payments/verify` - Verify payment status
- `POST /api/payments/webhook` - BudPay webhook handler
- `GET /api/payments/transaction/{ref}` - Get transaction details

### Admin
- `POST /api/admin/applications/{id}/status` - Update application status
- `POST /api/admin/applications/{id}/disbursement` - Approve/decline disbursement

## Recent Changes (January 2025)

### Completed
- ✅ **BudPay Integration** - Migrated from Xixapay to BudPay payment gateway
- ✅ **Email Service Fix** - Fixed email service to use Resend as primary with SendGrid fallback
- ✅ **PaymentCallbackPage Fix** - Fixed React StrictMode issue with AbortController
- ✅ **Loan Disbursement Workflow** - Added admin approve/decline buttons with email notifications
- ✅ **Admin Dashboard Enhancements** - Added submission timestamps, document viewing
- ✅ **CBN Licensed Section** - Added to About Us page

### In Progress
- 🔄 **Application Submission Bug** - Production environment issue (needs deployment verification)
- 🔄 **Production Deployment Sync** - Ensure preview and production environments match

### Backlog
- Security Cleanup: Remove temporary debug endpoints
- Code refactoring: Simplify applications.py

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=cashflow_mfb
BUDPAY_SECRET_KEY=sk_live_xxx
BUDPAY_PUBLIC_KEY=pk_live_xxx
RESEND_API_KEY=re_xxx
EMAIL_PROVIDER=resend
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://cashflow-patch.preview.emergentagent.com
```

## Test Credentials
- **Admin**: kdride6@gmail.com / djscan30Z@
- **Test User**: test_payment_user@example.com / TestPass123!

## Key Files
- `/app/backend/routers/payments.py` - BudPay integration
- `/app/backend/utils/email.py` - Email service (Resend/SendGrid)
- `/app/frontend/src/pages/UserDashboard.jsx` - User payment flow
- `/app/frontend/src/pages/PaymentCallbackPage.jsx` - Payment callback handling
- `/app/frontend/src/pages/AdminDashboard.jsx` - Admin management
