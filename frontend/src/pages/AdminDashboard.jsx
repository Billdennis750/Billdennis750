import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  LogOut, 
  Users, 
  TrendingUp, 
  CheckCircle, 
  XCircle, 
  Clock,
  DollarSign,
  FileText,
  Mail,
  Phone,
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedApp, setSelectedApp] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch applications
      const appsResponse = await axios.get(`${API}/applications/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApplications(appsResponse.data.applications);
      
      // Fetch stats
      const statsResponse = await axios.get(`${API}/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API}/applications/${appId}/status`,
        { status: newStatus, notes: `Status updated to ${newStatus}` },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Update local state
      setApplications(apps => 
        apps.map(app => 
          app.application_id === appId ? { ...app, status: newStatus } : app
        )
      );
      
      toast.success(`Application ${appId} status updated to ${newStatus}`);
      
      // Refresh data
      fetchData();
    } catch (error) {
      console.error('Status update failed:', error);
      toast.error('Failed to update status');
    }
  };

  const statsData = [
    {
      title: 'Total Applications',
      value: stats?.total_applications || 0,
      icon: FileText,
      color: 'var(--accent-text)',
    },
    {
      title: 'Pending Review',
      value: stats?.pending_review || 0,
      icon: Clock,
      color: '#f59e0b',
    },
    {
      title: 'Approved',
      value: stats?.approved || 0,
      icon: CheckCircle,
      color: 'var(--accent-text)',
    },
    {
      title: 'Total Disbursed',
      value: stats ? `₦${(stats.total_disbursed / 1000000).toFixed(1)}M` : '₦0',
      icon: DollarSign,
      color: 'var(--accent-text)',
    },
  ];

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-section)' }}>
      {/* Header */}
      <header className="bg-white border-b" style={{ borderColor: 'var(--border-light)' }}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="heading-3">Admin Dashboard</h1>
            <p className="body-small" style={{ color: 'var(--text-muted)' }}>
              Cashflow MFB Management Portal
            </p>
          </div>
          <Button onClick={handleLogout} variant="ghost" className="rounded-full">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {loading ? (
            <div className="col-span-4 text-center py-8">Loading...</div>
          ) : (
            statsData.map((stat, index) => (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                        {stat.title}
                      </p>
                      <p className="heading-2 mt-1">{stat.value}</p>
                    </div>
                    <div className="w-12 h-12 rounded-full flex items-center justify-center"
                         style={{ background: 'var(--accent-wash)' }}>
                      <stat.icon className="w-6 h-6" style={{ color: stat.color }} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Applications Table */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Application ID
                    </th>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Customer
                    </th>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Amount
                    </th>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Status
                    </th>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Applied Date
                    </th>
                    <th className="text-left py-3 px-4 body-small font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="text-center py-8">Loading applications...</td>
                    </tr>
                  ) : applications.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="text-center py-8">No applications found</td>
                    </tr>
                  ) : (
                    applications.map((app) => (
                      <tr key={app.application_id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td className="py-4 px-4">
                          <span className="body-medium font-mono">{app.application_id}</span>
                        </td>
                        <td className="py-4 px-4">
                          <div>
                            <p className="body-medium">{app.full_name}</p>
                            <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                              {app.email}
                            </p>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <span className="body-medium font-semibold">
                            ₦{app.loan_amount.toLocaleString()}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="px-3 py-1 rounded-full text-sm"
                                style={{ 
                                  background: app.status === 'approved' ? 'var(--accent-wash)' : 
                                             app.status === 'under_review' ? '#fef3c7' : 
                                             'var(--bg-section)',
                                  color: app.status === 'approved' ? 'var(--accent-text)' : 
                                        'var(--text-body)'
                                }}>
                            {app.status}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="body-small">{new Date(app.created_at).toLocaleDateString()}</span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              className="rounded-full"
                              onClick={() => setSelectedApp(app)}
                            >
                              View
                            </Button>
                            <Select
                              onValueChange={(value) => handleStatusChange(app.application_id, value)}
                              defaultValue={app.status}
                            >
                              <SelectTrigger className="w-32 rounded-full">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="under_review">Under Review</SelectItem>
                                <SelectItem value="approved">Approved</SelectItem>
                                <SelectItem value="rejected">Rejected</SelectItem>
                                <SelectItem value="disbursed">Disbursed</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Application Details Modal/Panel */}
        {selectedApp && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
               onClick={() => setSelectedApp(null)}>
            <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}>
              <CardHeader>
                <CardTitle>Application Details - {selectedApp.id}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Customer Information */}
                <div>
                  <h3 className="heading-3 mb-4">Customer Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Full Name</p>
                      <p className="body-medium">{selectedApp.full_name}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Email</p>
                      <p className="body-medium">{selectedApp.email}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Phone</p>
                      <p className="body-medium">{selectedApp.phone}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Employment Status</p>
                      <p className="body-medium">{selectedApp.employment_status}</p>
                    </div>
                  </div>
                </div>

                {/* Loan Details */}
                <div>
                  <h3 className="heading-3 mb-4">Loan Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Loan Amount</p>
                      <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                        ₦{selectedApp.loan_amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Monthly Income</p>
                      <p className="body-medium">₦{selectedApp.monthly_income.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* Application Status */}
                <div>
                  <h3 className="heading-3 mb-4">Status Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Current Status</p>
                      <p className="body-medium font-semibold">{selectedApp.status}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Payment Status</p>
                      <p className="body-medium font-semibold">{selectedApp.payment_status}</p>
                    </div>
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Applied Date</p>
                      <p className="body-medium">{new Date(selectedApp.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end space-x-3 pt-4">
                  <Button variant="outline" onClick={() => setSelectedApp(null)} className="rounded-full">
                    Close
                  </Button>
                  <Button 
                    className="btn-primary"
                    onClick={() => {
                      toast.success('Notification sent to customer');
                      setSelectedApp(null);
                    }}
                  >
                    Contact Customer
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
