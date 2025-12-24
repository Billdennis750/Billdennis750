import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  LogOut, FileText, CreditCard, Calendar, Mail, Phone, 
  Clock, CheckCircle, AlertCircle, Building2, Wallet,
  ArrowRight, RefreshCw, Sun, Moon, TrendingUp
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const LOGO_URL = "https://customer-assets.emergentagent.com/job_microfin-portal/artifacts/yv8s58dq_1000315618-removebg-preview.png";

const statusConfig = {
  pending_payment: { label: 'Pending Payment', color: '#f59e0b', bgColor: '#fef3c7', icon: Clock, description: 'Pay ₦2,500 processing fee to proceed' },
  under_review: { label: 'Under Review', color: '#3b82f6', bgColor: '#dbeafe', icon: Clock, description: 'Your application is being reviewed (24 hours)' },
  approved: { label: 'Approved', color: '#10b981', bgColor: '#d1fae5', icon: CheckCircle, description: 'Pay ₦3,000 deposit to receive your loan' },
  deposit_paid: { label: 'Deposit Paid', color: '#8b5cf6', bgColor: '#ede9fe', icon: CheckCircle, description: 'Processing your loan disbursement' },
  processing: { label: 'Processing', color: '#6366f1', bgColor: '#e0e7ff', icon: RefreshCw, description: 'Loan will be credited within 24 hours' },
  disbursed: { label: 'Loan Disbursed', color: '#10b981', bgColor: '#d1fae5', icon: Wallet, description: 'Loan credited to your account' },
  repayment_in_progress: { label: 'Repayment Active', color: '#0d7916', bgColor: '#dcfce7', icon: TrendingUp, description: 'Make payments on schedule' },
  fully_repaid: { label: 'Fully Repaid', color: '#059669', bgColor: '#d1fae5', icon: CheckCircle, description: 'Congratulations! Loan fully repaid' },
  rejected: { label: 'Rejected', color: '#ef4444', bgColor: '#fee2e2', icon: AlertCircle, description: 'Application was not approved' },
};

const UserDashboard = () => {
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
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

  const cardBg = isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100';
  const textPrimary = isDarkMode ? 'text-white' : 'text-gray-800';
  const textSecondary = isDarkMode ? 'text-slate-400' : 'text-gray-500';
  const textMuted = isDarkMode ? 'text-slate-500' : 'text-gray-400';

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'} border-b sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <img src={LOGO_URL} alt="Cashflow MFB" className="h-10" />
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="rounded-full"
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
            <Button onClick={handleLogout} variant="ghost" className="rounded-full">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className={`text-2xl font-bold mb-2 ${textPrimary}`}>
            Welcome back, {user?.full_name || user?.name || 'User'}! 👋
          </h2>
          <p className={textSecondary}>
            Track your loan application and manage your repayments
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-green-600" />
            <p className={`mt-2 ${textSecondary}`}>Loading your applications...</p>
          </div>
        ) : !recentApp ? (
          <Card className={`text-center py-12 ${cardBg}`}>
            <CardContent>
              <FileText className={`w-16 h-16 mx-auto mb-4 ${textMuted}`} />
              <h3 className={`text-xl font-bold mb-2 ${textPrimary}`}>No Applications Yet</h3>
              <p className={`mb-6 ${textSecondary}`}>
                Start your loan application to get access to collateral-free loans.
              </p>
              <Button onClick={() => navigate('/apply')} className="bg-green-600 hover:bg-green-700">
                Apply for a Loan
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Status Banner */}
            <Card className={`mb-6 border-l-4 ${cardBg}`} style={{ borderLeftColor: status?.color }}>
              <CardContent className="py-6">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-full flex items-center justify-center" style={{ backgroundColor: status?.bgColor }}>
                      {status?.icon && <status.icon className="w-7 h-7" style={{ color: status.color }} />}
                    </div>
                    <div>
                      <p className={`text-sm ${textMuted}`}>Application Status</p>
                      <p className="text-xl font-bold" style={{ color: status?.color }}>{status?.label}</p>
                      <p className={`text-sm mt-1 ${textSecondary}`}>{status?.description}</p>
                    </div>
                  </div>
                  
                  {recentApp.status === 'pending_payment' && (
                    <Button 
                      onClick={() => handlePayment(recentApp, 'processing_fee')} 
                      className="bg-green-600 hover:bg-green-700 shadow-lg shadow-green-600/30"
                      disabled={paymentLoading}
                    >
                      {paymentLoading ? 'Processing...' : 'Pay ₦2,500 Processing Fee'}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                  
                  {recentApp.status === 'approved' && (
                    <Button 
                      onClick={() => handlePayment(recentApp, 'deposit')} 
                      className="bg-green-600 hover:bg-green-700 shadow-lg shadow-green-600/30"
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
              <Card className={`${cardBg} shadow-sm hover:shadow-md transition-shadow`}>
                <CardHeader className="pb-2">
                  <CardTitle className={`flex items-center gap-2 text-lg ${textPrimary}`}>
                    <FileText className="w-5 h-5 text-green-600" />
                    Application Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <p className={`text-xs ${textMuted}`}>Application ID</p>
                      <p className={`font-mono font-semibold ${textPrimary}`}>{recentApp.application_id}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <p className={`text-xs ${textMuted}`}>Applied On</p>
                      <p className={`font-semibold ${textPrimary}`}>{new Date(recentApp.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-green-900/20' : 'bg-green-50'} border ${isDarkMode ? 'border-green-800' : 'border-green-100'}`}>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className={`text-xs ${textMuted}`}>Loan Amount Requested</p>
                        <p className="text-2xl font-bold text-green-600">₦{Number(recentApp.loan_amount).toLocaleString()}</p>
                      </div>
                      {recentApp.approved_amount && (
                        <div className="text-right">
                          <p className={`text-xs ${textMuted}`}>Approved</p>
                          <p className="text-xl font-bold text-green-600">₦{Number(recentApp.approved_amount).toLocaleString()}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Repayment Plan */}
              <Card className={`${cardBg} shadow-sm hover:shadow-md transition-shadow`}>
                <CardHeader className="pb-2">
                  <CardTitle className={`flex items-center gap-2 text-lg ${textPrimary}`}>
                    <Calendar className="w-5 h-5 text-blue-600" />
                    Repayment Plan
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <p className={`text-xs ${textMuted}`}>Duration</p>
                      <p className={`font-semibold ${textPrimary}`}>{getDurationLabel(recentApp.repayment_duration)}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <p className={`text-xs ${textMuted}`}>Frequency</p>
                      <p className={`font-semibold ${textPrimary}`}>{getFrequencyLabel(recentApp.repayment_frequency)}</p>
                    </div>
                  </div>
                  <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-blue-900/20' : 'bg-blue-50'} border ${isDarkMode ? 'border-blue-800' : 'border-blue-100'}`}>
                    <p className={`text-xs ${textMuted}`}>Estimated Payment</p>
                    <p className="text-2xl font-bold text-blue-600">
                      ₦{Number(recentApp.estimated_repayment || 0).toLocaleString()}
                      <span className="text-sm font-normal text-blue-400">
                        /{recentApp.repayment_frequency === 'monthly' ? 'month' : recentApp.repayment_frequency === 'weekly' ? 'week' : '2 weeks'}
                      </span>
                    </p>
                  </div>
                  
                  {['disbursed', 'repayment_in_progress', 'fully_repaid'].includes(recentApp.status) && (
                    <div className="pt-4 border-t border-dashed">
                      <div className="flex justify-between mb-2">
                        <span className={`text-sm ${textSecondary}`}>Progress</span>
                        <span className={`text-sm font-semibold ${textPrimary}`}>
                          {Math.round(((recentApp.total_repaid || 0) / (recentApp.total_repayment || 1)) * 100)}%
                        </span>
                      </div>
                      <div className={`h-3 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-700' : 'bg-gray-200'}`}>
                        <div 
                          className="h-full rounded-full bg-gradient-to-r from-green-500 to-green-400 transition-all"
                          style={{ width: `${Math.min(100, ((recentApp.total_repaid || 0) / (recentApp.total_repayment || 1)) * 100)}%` }}
                        />
                      </div>
                      <p className={`text-xs mt-2 ${textMuted}`}>
                        ₦{Number(recentApp.total_repaid || 0).toLocaleString()} of ₦{Number(recentApp.total_repayment || 0).toLocaleString()} repaid
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Bank Account Details */}
              <Card className={`${cardBg} shadow-sm hover:shadow-md transition-shadow`}>
                <CardHeader className="pb-2">
                  <CardTitle className={`flex items-center gap-2 text-lg ${textPrimary}`}>
                    <Building2 className="w-5 h-5 text-purple-600" />
                    Bank Account for Disbursement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-purple-900/20' : 'bg-purple-50'} border ${isDarkMode ? 'border-purple-800' : 'border-purple-100'}`}>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className={`text-sm ${textMuted}`}>Bank</span>
                        <span className={`font-semibold ${textPrimary}`}>{recentApp.bank_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className={`text-sm ${textMuted}`}>Account Name</span>
                        <span className={`font-semibold ${textPrimary}`}>{recentApp.account_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className={`text-sm ${textMuted}`}>Account Number</span>
                        <span className={`font-mono font-semibold ${textPrimary}`}>{recentApp.account_number}</span>
                      </div>
                    </div>
                  </div>
                  <p className={`text-xs mt-3 ${textMuted}`}>
                    ✓ Your approved loan will be credited to this account only
                  </p>
                </CardContent>
              </Card>

              {/* Payment Status */}
              <Card className={`${cardBg} shadow-sm hover:shadow-md transition-shadow`}>
                <CardHeader className="pb-2">
                  <CardTitle className={`flex items-center gap-2 text-lg ${textPrimary}`}>
                    <CreditCard className="w-5 h-5 text-orange-600" />
                    Payment Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className={`flex items-center justify-between p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${recentApp.processing_fee_paid ? 'bg-green-100' : 'bg-yellow-100'}`}>
                          {recentApp.processing_fee_paid ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <Clock className="w-5 h-5 text-yellow-600" />
                          )}
                        </div>
                        <div>
                          <p className={`font-medium ${textPrimary}`}>Processing Fee</p>
                          <p className={`text-sm ${textMuted}`}>₦2,500</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${recentApp.processing_fee_paid ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {recentApp.processing_fee_paid ? 'Paid' : 'Pending'}
                      </span>
                    </div>
                    
                    <div className={`flex items-center justify-between p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${recentApp.deposit_paid ? 'bg-green-100' : 'bg-gray-100'}`}>
                          {recentApp.deposit_paid ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <Clock className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <p className={`font-medium ${textPrimary}`}>Fixed Deposit</p>
                          <p className={`text-sm ${textMuted}`}>₦3,000</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        recentApp.deposit_paid ? 'bg-green-100 text-green-700' : 
                        recentApp.status === 'approved' ? 'bg-orange-100 text-orange-700' : 
                        'bg-gray-100 text-gray-500'
                      }`}>
                        {recentApp.deposit_paid ? 'Paid' : recentApp.status === 'approved' ? 'Required' : 'Not Yet'}
                      </span>
                    </div>
                    
                    <div className={`flex items-center justify-between p-3 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-gray-50'}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${recentApp.disbursed ? 'bg-green-100' : 'bg-gray-100'}`}>
                          {recentApp.disbursed ? (
                            <Wallet className="w-5 h-5 text-green-600" />
                          ) : (
                            <Clock className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <p className={`font-medium ${textPrimary}`}>Loan Disbursement</p>
                          <p className={`text-sm ${textMuted}`}>₦{Number(recentApp.approved_amount || recentApp.loan_amount).toLocaleString()}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${recentApp.disbursed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {recentApp.disbursed ? 'Credited' : 'Pending'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Support Section */}
            <Card className={`mt-6 ${cardBg} shadow-sm`}>
              <CardHeader className="pb-2">
                <CardTitle className={`text-lg ${textPrimary}`}>Need Help?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <a href="mailto:payment@cashflowsmfb.com" className={`flex items-center gap-3 p-4 rounded-xl ${isDarkMode ? 'bg-slate-700/50 hover:bg-slate-700' : 'bg-gray-50 hover:bg-gray-100'} transition-colors`}>
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      <Mail className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className={`font-semibold ${textPrimary}`}>Email Support</p>
                      <p className={`text-sm ${textMuted}`}>payment@cashflowsmfb.com</p>
                    </div>
                  </a>
                  <a href="tel:+2348000000000" className={`flex items-center gap-3 p-4 rounded-xl ${isDarkMode ? 'bg-slate-700/50 hover:bg-slate-700' : 'bg-gray-50 hover:bg-gray-100'} transition-colors`}>
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <Phone className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className={`font-semibold ${textPrimary}`}>Phone Support</p>
                      <p className={`text-sm ${textMuted}`}>+234 800 CASHFLOW</p>
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
