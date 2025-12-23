import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { LogOut, FileText, CreditCard, Calendar, Mail, Phone } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/applications/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setApplications(response.data.applications);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Get the most recent application
  const recentApplication = applications.length > 0 ? applications[0] : null;

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-section)' }}>
      {/* Header */}
      <header className="bg-white border-b" style={{ borderColor: 'var(--border-light)' }}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="heading-3">My Dashboard</h1>
          <Button onClick={handleLogout} variant="ghost" className="rounded-full">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="heading-2 mb-2">Welcome back, {user?.name}!</h2>
          <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
            Manage your loan applications and track your repayment schedule
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Application Status
                  </p>
                  <p className="heading-3 mt-1">
                    {application ? application.status : 'No Active Application'}
                  </p>
                </div>
                <FileText className="w-10 h-10" style={{ color: 'var(--accent-text)' }} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Loan Amount
                  </p>
                  <p className="heading-3 mt-1">
                    {application ? `₦${Number(application.loanAmount).toLocaleString()}` : '₦0'}
                  </p>
                </div>
                <CreditCard className="w-10 h-10" style={{ color: 'var(--accent-text)' }} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Payment Status
                  </p>
                  <p className="heading-3 mt-1">
                    {application ? application.paymentStatus : 'N/A'}
                  </p>
                </div>
                <Calendar className="w-10 h-10" style={{ color: 'var(--accent-text)' }} />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Application Details */}
          <Card>
            <CardHeader>
              <CardTitle>Application Details</CardTitle>
            </CardHeader>
            <CardContent>
              {application ? (
                <div className="space-y-4">
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>Application ID</p>
                    <p className="body-medium font-mono">{application.id}</p>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>Loan Amount</p>
                    <p className="body-medium">₦{Number(application.loanAmount).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>Purpose</p>
                    <p className="body-medium">{application.loanReason}</p>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>Status</p>
                    <span className="px-3 py-1 rounded-full text-sm font-medium"
                          style={{ 
                            background: application.status === 'Under Review' ? 'var(--accent-wash)' : 'var(--bg-section)',
                            color: 'var(--accent-text)'
                          }}>
                      {application.status}
                    </span>
                  </div>
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>Applied On</p>
                    <p className="body-medium">{new Date(application.createdAt).toLocaleDateString()}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                  <p className="body-medium mb-4" style={{ color: 'var(--text-secondary)' }}>
                    You haven't submitted any loan applications yet.
                  </p>
                  <Button onClick={() => navigate('/apply')} className="btn-primary">
                    Apply for a Loan
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Repayment Schedule */}
          <Card>
            <CardHeader>
              <CardTitle>Repayment Schedule</CardTitle>
            </CardHeader>
            <CardContent>
              {application && application.status === 'Approved' ? (
                <div className="space-y-4">
                  {mockRepaymentSchedule.map((payment) => (
                    <div key={payment.id} className="flex justify-between items-center p-4 rounded-lg"
                         style={{ background: 'var(--bg-section)' }}>
                      <div>
                        <p className="body-medium">₦{payment.amount.toLocaleString()}</p>
                        <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                          Due: {payment.dueDate}
                        </p>
                      </div>
                      <span className="px-3 py-1 rounded-full text-sm"
                            style={{ 
                              background: payment.status === 'Upcoming' ? 'var(--accent-wash)' : 'var(--bg-section)',
                              color: 'var(--text-body)'
                            }}>
                        {payment.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                  <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                    Your repayment schedule will appear here once your loan is approved.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Transaction History */}
          <Card>
            <CardHeader>
              <CardTitle>Transaction History</CardTitle>
            </CardHeader>
            <CardContent>
              {application && application.paymentStatus === 'Paid' ? (
                <div className="space-y-4">
                  {mockTransactions.map((txn) => (
                    <div key={txn.id} className="flex justify-between items-center p-4 rounded-lg"
                         style={{ background: 'var(--bg-section)' }}>
                      <div>
                        <p className="body-medium">{txn.type}</p>
                        <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                          {txn.date}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="body-medium font-semibold">₦{txn.amount.toLocaleString()}</p>
                        <p className="body-small" style={{ color: 'var(--accent-text)' }}>
                          {txn.status}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CreditCard className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                  <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                    No transactions yet.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Support */}
          <Card>
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                Our support team is here to assist you with any questions.
              </p>
              <div className="space-y-3">
                <a href="mailto:support@cashflowmfb.ng" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <Mail className="w-5 h-5" style={{ color: 'var(--accent-text)' }} />
                  <div>
                    <p className="body-medium">Email Support</p>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>support@cashflowmfb.ng</p>
                  </div>
                </a>
                <a href="tel:+2348000000000" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <Phone className="w-5 h-5" style={{ color: 'var(--accent-text)' }} />
                  <div>
                    <p className="body-medium">Phone Support</p>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>+234 800 CASHFLOW</p>
                  </div>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
