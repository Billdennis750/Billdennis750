import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  LogOut, FileText, CreditCard, Calendar, Mail, Phone, 
  Clock, CheckCircle, AlertCircle, Building2, Wallet,
  ArrowRight, RefreshCw
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const statusConfig = {
  pending_payment: { label: 'Pending Payment', color: '#f59e0b', icon: Clock, description: 'Pay ₦2,500 processing fee to proceed' },
  under_review: { label: 'Under Review', color: '#3b82f6', icon: Clock, description: 'Your application is being reviewed' },
  approved: { label: 'Approved', color: '#10b981', icon: CheckCircle, description: 'Pay ₦3,000 deposit to receive your loan' },
  deposit_paid: { label: 'Deposit Paid', color: '#8b5cf6', icon: CheckCircle, description: 'Processing your loan disbursement' },
  processing: { label: 'Processing', color: '#6366f1', icon: RefreshCw, description: 'Loan will be credited within 24 hours' },
  disbursed: { label: 'Loan Disbursed', color: '#10b981', icon: Wallet, description: 'Loan credited to your account' },
  repayment_in_progress: { label: 'Repayment In Progress', color: '#0d7916', icon: CreditCard, description: 'Make payments on schedule' },
  fully_repaid: { label: 'Fully Repaid', color: '#059669', icon: CheckCircle, description: 'Congratulations! Loan fully repaid' },
  rejected: { label: 'Rejected', color: '#ef4444', icon: AlertCircle, description: 'Application was not approved' },
};

const UserDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [paymentLoading, setPaymentLoading] = useState(false);
  
  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/applications/user/my-applications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApplications(response.data.applications || []);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
      // Try fetching all and filter
      try {
        const response = await axios.get(`${API}/applications/`);
        const userApps = response.data.applications.filter(app => app.email === user?.email);
        setApplications(userApps);
      } catch (err) {
        console.error('Fallback fetch failed:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (app, paymentType) => {
    setPaymentLoading(true);
    try {
      const amount = paymentType === 'processing_fee' ? 2500 : 3000;
      
      const response = await axios.post(`${API}/payments/initiate`, {
        application_id: app.application_id,
        customer_email: app.email,
        customer_name: app.full_name,
        customer_phone: app.phone,
        amount: amount,
        redirect_url: `${window.location.origin}/payment-callback`
      });
      
      localStorage.setItem('order_reference', response.data.order_reference);
      localStorage.setItem('application_id', app.application_id);
      localStorage.setItem('payment_type', paymentType);
      
      window.location.href = response.data.checkout_link;
    } catch (error) {
      toast.error('Failed to initiate payment');
      setPaymentLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getFrequencyLabel = (freq) => ({
    'weekly': 'Weekly',
    'bi_weekly': 'Bi-Weekly',
    'monthly': 'Monthly'
  }[freq] || freq);

  const getDurationLabel = (dur) => ({
    '3_months': '3 Months',
    '6_months': '6 Months',
    '9_months': '9 Months',
    '12_months': '12 Months'
  }[dur] || dur);

  const recentApp = applications.length > 0 ? applications[0] : null;
  const status = recentApp ? statusConfig[recentApp.status] || statusConfig.pending_payment : null;

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-section)' }}>
      {/* Header */}
      <header className="bg-white border-b" style={{ borderColor: 'var(--border-light)' }}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="heading-3" style={{ color: 'var(--accent-text)' }}>Cashflow MFB</h1>
          <Button onClick={handleLogout} variant="ghost" className="rounded-full">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="heading-2 mb-2">Welcome back, {user?.full_name || user?.name || 'User'}!</h2>
          <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
            Manage your loan application and track your repayment schedule
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
            <p>Loading your applications...</p>
          </div>
        ) : !recentApp ? (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
              <h3 className="heading-3 mb-2">No Applications Yet</h3>
              <p className="body-medium mb-6" style={{ color: 'var(--text-secondary)' }}>
                Start your loan application to get access to collateral-free loans.
              </p>
              <Button onClick={() => navigate('/apply')} className="btn-primary">
                Apply for a Loan
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Status Banner */}
            <Card className="mb-6" style={{ borderLeft: `4px solid ${status?.color}` }}>
              <CardContent className="py-6">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-4">
                    {status?.icon && <status.icon className="w-10 h-10" style={{ color: status.color }} />}
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Application Status</p>
                      <p className="heading-3" style={{ color: status?.color }}>{status?.label}</p>
                      <p className="body-small mt-1" style={{ color: 'var(--text-secondary)' }}>{status?.description}</p>
                    </div>
                  </div>
                  
                  {/* Action Buttons Based on Status */}
                  {recentApp.status === 'pending_payment' && (
                    <Button 
                      onClick={() => handlePayment(recentApp, 'processing_fee')} 
                      className="btn-primary"
                      disabled={paymentLoading}
                    >
                      {paymentLoading ? 'Processing...' : 'Pay ₦2,500 Processing Fee'}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                  
                  {recentApp.status === 'approved' && (
                    <Button 
                      onClick={() => handlePayment(recentApp, 'deposit')} 
                      className="btn-primary"
                      disabled={paymentLoading}
                    >
                      {paymentLoading ? 'Processing...' : 'Pay ₦3,000 Deposit'}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Application Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Application Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Application ID</p>
                      <p className="body-medium font-mono">{recentApp.application_id}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Applied On</p>
                      <p className="body-medium">{new Date(recentApp.created_at).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Loan Amount</p>
                      <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                        ₦{Number(recentApp.loan_amount).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Approved Amount</p>
                      <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                        {recentApp.approved_amount ? `₦${Number(recentApp.approved_amount).toLocaleString()}` : 'Pending'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Repayment Plan */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Repayment Plan
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Duration</p>
                      <p className="body-medium font-semibold">{getDurationLabel(recentApp.repayment_duration)}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Frequency</p>
                      <p className="body-medium font-semibold">{getFrequencyLabel(recentApp.repayment_frequency)}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Est. Payment</p>
                      <p className="body-medium font-semibold">
                        ₦{Number(recentApp.estimated_repayment || 0).toLocaleString()}/{recentApp.repayment_frequency === 'monthly' ? 'month' : recentApp.repayment_frequency === 'weekly' ? 'week' : '2 weeks'}
                      </p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Total Repayment</p>
                      <p className="body-medium font-semibold">₦{Number(recentApp.total_repayment || 0).toLocaleString()}</p>
                    </div>
                  </div>
                  
                  {/* Repayment Progress (if disbursed) */}
                  {['disbursed', 'repayment_in_progress', 'fully_repaid'].includes(recentApp.status) && (
                    <div className="pt-4 border-t">
                      <div className="flex justify-between mb-2">
                        <span className="body-small">Repayment Progress</span>
                        <span className="body-small font-semibold">
                          ₦{Number(recentApp.total_repaid || 0).toLocaleString()} / ₦{Number(recentApp.total_repayment || 0).toLocaleString()}
                        </span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all"
                          style={{ 
                            width: `${Math.min(100, ((recentApp.total_repaid || 0) / (recentApp.total_repayment || 1)) * 100)}%`,
                            background: 'var(--accent-text)'
                          }}
                        />
                      </div>
                      {recentApp.next_repayment_date && (
                        <p className="body-small mt-2" style={{ color: 'var(--text-muted)' }}>
                          Next payment: ₦{Number(recentApp.next_repayment_amount || 0).toLocaleString()} due on {new Date(recentApp.next_repayment_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Bank Account Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="w-5 h-5" />
                    Bank Account (Read-only)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 rounded-lg" style={{ background: 'var(--bg-section)' }}>
                    <div className="grid grid-cols-1 gap-3">
                      <div>
                        <p className="body-small" style={{ color: 'var(--text-muted)' }}>Bank Name</p>
                        <p className="body-medium font-semibold">{recentApp.bank_name}</p>
                      </div>
                      <div>
                        <p className="body-small" style={{ color: 'var(--text-muted)' }}>Account Name</p>
                        <p className="body-medium font-semibold">{recentApp.account_name}</p>
                      </div>
                      <div>
                        <p className="body-small" style={{ color: 'var(--text-muted)' }}>Account Number</p>
                        <p className="body-medium font-mono font-semibold">{recentApp.account_number}</p>
                      </div>
                    </div>
                  </div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Your approved loan will be credited to this account only.
                  </p>
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="w-5 h-5" />
                    Payment Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--bg-section)' }}>
                      <div className="flex items-center gap-3">
                        {recentApp.processing_fee_paid ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                          <Clock className="w-5 h-5 text-yellow-500" />
                        )}
                        <div>
                          <p className="body-medium">Processing Fee</p>
                          <p className="body-small" style={{ color: 'var(--text-muted)' }}>₦2,500</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${recentApp.processing_fee_paid ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {recentApp.processing_fee_paid ? 'Paid' : 'Pending'}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--bg-section)' }}>
                      <div className="flex items-center gap-3">
                        {recentApp.deposit_paid ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                          <Clock className="w-5 h-5 text-gray-400" />
                        )}
                        <div>
                          <p className="body-medium">Fixed Deposit</p>
                          <p className="body-small" style={{ color: 'var(--text-muted)' }}>₦3,000</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${recentApp.deposit_paid ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {recentApp.deposit_paid ? 'Paid' : recentApp.status === 'approved' ? 'Required' : 'Not Yet'}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--bg-section)' }}>
                      <div className="flex items-center gap-3">
                        {recentApp.disbursed ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                          <Clock className="w-5 h-5 text-gray-400" />
                        )}
                        <div>
                          <p className="body-medium">Loan Disbursement</p>
                          <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                            ₦{Number(recentApp.approved_amount || recentApp.loan_amount).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${recentApp.disbursed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {recentApp.disbursed ? 'Credited' : 'Pending'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Support Section */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Need Help?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <a href="mailto:support@cashflowmfb.ng" className="flex items-center gap-3 p-4 rounded-lg hover:bg-gray-50 transition-colors border">
                    <Mail className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
                    <div>
                      <p className="body-medium font-semibold">Email Support</p>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>support@cashflowmfb.ng</p>
                    </div>
                  </a>
                  <a href="tel:+2348000000000" className="flex items-center gap-3 p-4 rounded-lg hover:bg-gray-50 transition-colors border">
                    <Phone className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
                    <div>
                      <p className="body-medium font-semibold">Phone Support</p>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>+234 800 CASHFLOW</p>
                    </div>
                  </a>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;
