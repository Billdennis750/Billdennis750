// Mock data for Cashflow MFB application

export const mockUser = {
  id: 'user_001',
  name: 'John Doe',
  email: 'john.doe@example.com',
  phone: '+234 801 234 5678',
  hasActiveLoan: false,
};

export const mockLoanApplications = [
  {
    id: 'LOAN-2025-001',
    customerName: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+234 801 234 5678',
    loanAmount: 5000000,
    status: 'Under Review',
    appliedDate: '2025-01-15',
    employmentStatus: 'Employed',
    monthlyIncome: 250000,
    reason: 'Business Expansion',
    paymentStatus: 'Paid',
  },
  {
    id: 'LOAN-2025-002',
    customerName: 'Jane Smith',
    email: 'jane.smith@example.com',
    phone: '+234 802 345 6789',
    loanAmount: 2000000,
    status: 'Approved',
    appliedDate: '2025-01-14',
    employmentStatus: 'Self-Employed',
    monthlyIncome: 180000,
    reason: 'Personal Need',
    paymentStatus: 'Paid',
  },
];

export const mockTransactions = [
  {
    id: 'TXN-001',
    type: 'Processing Fee',
    amount: 2500,
    date: '2025-01-15',
    status: 'Completed',
    reference: 'NOMBA-TXN-123456',
  },
];

export const mockAdminStats = {
  totalApplications: 156,
  pendingReview: 23,
  approved: 98,
  rejected: 15,
  totalDisbursed: 450000000,
  thisMonthApplications: 45,
};

export const mockPartners = [
  { 
    name: 'Zenith Bank', 
    logo: 'https://customer-assets.emergentagent.com/job_easy-loan-access/artifacts/nux1a2f0_download%20%284%29.png' 
  },
  { 
    name: 'First Bank', 
    logo: 'https://customer-assets.emergentagent.com/job_easy-loan-access/artifacts/njxhxlzd_download%20%283%29.png' 
  },
  { 
    name: 'Access Bank', 
    logo: 'https://customer-assets.emergentagent.com/job_easy-loan-access/artifacts/wpx21s8t_download%20%282%29.png' 
  },
  { 
    name: 'GTBank', 
    logo: 'https://customer-assets.emergentagent.com/job_easy-loan-access/artifacts/rty3liiw_download%20%281%29.png' 
  },
];

export const mockRepaymentSchedule = [
  {
    id: 1,
    dueDate: '2025-02-15',
    amount: 550000,
    status: 'Upcoming',
  },
  {
    id: 2,
    dueDate: '2025-03-15',
    amount: 550000,
    status: 'Pending',
  },
];
