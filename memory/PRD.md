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
- **Email**: SendGrid (legacy), Resend (in progress migration)
- **Payments**: BudPay Dedicated Virtual Account (DVA) - Bank Transfer

## Core Features

### User Features
- Multi-step loan application form (5 steps)
- Document upload (ID card, passport photo)
- User dashboard with application status tracking
- Bank transfer payment (DVA) - no external redirects
- Password reset functionality

### Admin Features
- View all applications with filtering and **pagination (50 per page)**
- Approve/reject loan applications
- Approve/decline loan disbursements
- View uploaded documents
- Email notifications to users
- **Manual payment confirmation** for pending bank transfers
- Total users count display

## Payment Flow (Updated Feb 13, 2026)
1. User submits loan application → Status: `pending_payment`
2. User clicks "Pay" → Modal shows bank transfer details (Wema Bank DVA)
3. User transfers ₦2,500 to the virtual account
4. **Option A**: BudPay webhook auto-confirms payment → Status: `under_review`
5. **Option B**: Admin manually confirms via Payments tab → Status: `under_review`
6. Admin reviews and approves → Status: `approved`
7. User pays ₦3,000 fixed deposit (same DVA flow)
8. Admin approves disbursement → Status: `disbursed`

## Recent Changes (Feb 13, 2026)
- **Enhanced BudPay DVA Webhook**: Updated webhook handler to support DVA-specific events (`eventType: "transaction"`)
- **Admin Manual Payment Confirmation**: Added Payments tab with "Pending Bank Transfers" section
  - Shows all pending transactions with Customer, Application ID, Amount, Type, Bank Details, Date
  - Admin can click "Confirm" button to manually confirm payments after verifying bank transfer
- **New API Endpoints**:
  - `GET /api/payments/pending-payments` - List all pending bank transfers
  - `POST /api/payments/admin/confirm-payment` - Manually confirm a payment

## Recent Changes (Feb 12, 2026)
- **Payment Flow Changed**: Removed BudPay checkout redirect, now uses **direct bank transfer** with in-app modal
- **Virtual Account**: Payment details shown directly in the app (Bank, Account Name, Account Number)
- **Admin Dashboard Pagination**: Added pagination to Applications and Users tabs (50 items per page)
- **Payment UI Redesign**: New prominent payment card with gradient styling, modern modal

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

### Payments (BudPay DVA)
- `POST /api/payments/initiate` - Get virtual account details for bank transfer
- `POST /api/payments/verify` - Verify payment status
- `POST /api/payments/webhook` - BudPay webhook handler (DVA events)
- `GET /api/payments/transaction/{ref}` - Get transaction details
- `GET /api/payments/pending-payments` - Get all pending bank transfers (Admin)
- `POST /api/payments/admin/confirm-payment` - Manually confirm payment (Admin)

### Admin
- `POST /api/admin/applications/{id}/status` - Update application status
- `POST /api/admin/applications/{id}/disbursement` - Approve/decline disbursement
- `GET /api/admin/users` - List all users
- `GET /api/admin/transactions` - List all transactions

## Pending/In Progress Issues

### P0 - Critical
- **Production Deployment**: Application fails to deploy to `cashflowsmfb.com` with health check 520 errors
  - Needs user to trigger new deployment and share logs
  - Previous fixes: Made MongoDB connection more resilient

### P1 - High Priority
- **BudPay Webhook Configuration**: Need to configure webhook URL in BudPay dashboard
  - Webhook URL: `https://loan-app-staging.preview.emergentagent.com/api/payments/webhook`

### P2 - Medium Priority
- **Email Service Migration**: SendGrid → Resend incomplete (both failing with 401)
- **Security Cleanup**: Remove temporary debug endpoints
- **Code Refactoring**: Remove dead OTPay/Xixapay code from payments.py

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=cashflow_mfb
BUDPAY_SECRET_KEY=sk_live_xxx
BUDPAY_PUBLIC_KEY=pk_live_xxx
RESEND_API_KEY=re_xxx
EMAIL_PROVIDER=resend
FRONTEND_URL=https://loan-app-staging.preview.emergentagent.com
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://loan-app-staging.preview.emergentagent.com
```

## Test Credentials
- **Admin**: kdride6@gmail.com / djscan30
- **Test User**: kingverbtv@gmail.com (password needs reset)

## Key Files
- `/app/backend/routers/payments.py` - BudPay DVA integration, webhook handler, admin confirm
- `/app/backend/utils/email.py` - Email service (Resend/SendGrid)
- `/app/frontend/src/pages/UserDashboard.jsx` - User payment flow with bank transfer modal
- `/app/frontend/src/pages/AdminDashboard.jsx` - Admin management with pending payments
- `/app/frontend/src/pages/PaymentCallbackPage.jsx` - Payment verification polling

## Testing
- Test Report: `/app/test_reports/iteration_4.json`
- Backend Tests: `/app/backend/tests/test_pending_payments.py`
- All tests passing: 100% success rate
