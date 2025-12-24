import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  LogOut, Users, FileText, CreditCard, Activity, 
  Search, CheckCircle, Clock, XCircle, Eye, 
  DollarSign, TrendingUp, UserCheck, AlertCircle,
  Download, RefreshCw, ChevronDown, ChevronUp, Settings,
  Lock, Mail as MailIcon, Send, Image, FileImage, X, Trash2, AlertTriangle
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const LOGO_URL = "https://customer-assets.emergentagent.com/job_microfin-portal/artifacts/yv8s58dq_1000315618-removebg-preview.png";

const statusColors = {
  pending_payment: { bg: '#fff3cd', text: '#856404', label: 'Pending Payment' },
  under_review: { bg: '#cce5ff', text: '#004085', label: 'Under Review' },
  approved: { bg: '#d4edda', text: '#155724', label: 'Approved' },
  deposit_paid: { bg: '#e2d5f1', text: '#5a3d8a', label: 'Deposit Paid' },
  processing: { bg: '#d1ecf1', text: '#0c5460', label: 'Processing' },
  disbursed: { bg: '#c3e6cb', text: '#155724', label: 'Disbursed' },
  repayment_in_progress: { bg: '#d4edda', text: '#0d7916', label: 'Repayment' },
  fully_repaid: { bg: '#28a745', text: '#ffffff', label: 'Fully Repaid' },
  rejected: { bg: '#f8d7da', text: '#721c24', label: 'Rejected' },
};

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [applications, setApplications] = useState([]);
  const [users, setUsers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPaid: 0,
    totalPending: 0,
    totalCollected: 0
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedApp, setSelectedApp] = useState(null);
  const [expandedRows, setExpandedRows] = useState({});
  
  // Change Password State
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [changingPassword, setChangingPassword] = useState(false);
  
  // Email Reminders State
  const [selectedUsersForReminder, setSelectedUsersForReminder] = useState([]);
  const [reminderType, setReminderType] = useState('all');
  const [sendingReminders, setSendingReminders] = useState(false);
  
  // Document Preview State
  const [documentPreview, setDocumentPreview] = useState(null);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  
  // User Delete State
  const [userToDelete, setUserToDelete] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingUser, setDeletingUser] = useState(false);
  const [userDetails, setUserDetails] = useState(null);
  const [loadingUserDetails, setLoadingUserDetails] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      // Fetch applications
      const appsRes = await axios.get(`${API}/applications/`, { headers });
      const apps = appsRes.data.applications || [];
      setApplications(apps);
      
      // Fetch users
      try {
        const usersRes = await axios.get(`${API}/admin/users`, { headers });
        setUsers(usersRes.data.users || []);
      } catch (e) {
        console.log('Users endpoint not available');
      }
      
      // Fetch transactions
      try {
        const txnRes = await axios.get(`${API}/admin/transactions`, { headers });
        setTransactions(txnRes.data.transactions || []);
      } catch (e) {
        console.log('Transactions endpoint not available');
      }
      
      // Calculate stats
      const paidUsers = apps.filter(a => a.processing_fee_paid).length;
      const pendingUsers = apps.filter(a => !a.processing_fee_paid).length;
      const totalCollected = apps.reduce((sum, a) => {
        let amount = 0;
        if (a.processing_fee_paid) amount += 2500;
        if (a.deposit_paid) amount += 3000;
        return sum + amount;
      }, 0);
      
      setStats({
        totalUsers: apps.length,
        totalPaid: paidUsers,
        totalPending: pendingUsers,
        totalCollected: totalCollected
      });
      
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleStatusUpdate = async (appId, newStatus, notes = '') => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/applications/${appId}/status`, 
        { status: newStatus, notes },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      toast.success('Status updated successfully');
      fetchData();
      setSelectedApp(null);
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const toggleRow = (id) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (passwordData.newPassword.length < 8) {
      toast.error('New password must be at least 8 characters long');
      return;
    }
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    setChangingPassword(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/auth/change-password`, {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      }, { headers: { Authorization: `Bearer ${token}` }});
      
      toast.success('Password changed successfully');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  // Email Reminder Functions
  const handleSelectUserForReminder = (email) => {
    setSelectedUsersForReminder(prev => 
      prev.includes(email) 
        ? prev.filter(e => e !== email)
        : [...prev, email]
    );
  };

  const handleSelectAllForReminder = () => {
    const pendingUsers = applications
      .filter(app => !app.processing_fee_paid || (app.status === 'approved' && !app.deposit_paid))
      .map(app => app.email);
    
    if (selectedUsersForReminder.length === pendingUsers.length) {
      setSelectedUsersForReminder([]);
    } else {
      setSelectedUsersForReminder(pendingUsers);
    }
  };

  const handleSendReminders = async () => {
    if (selectedUsersForReminder.length === 0) {
      toast.error('Please select at least one user');
      return;
    }
    
    setSendingReminders(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/admin/send-reminders`, {
        user_emails: selectedUsersForReminder,
        reminder_type: reminderType
      }, { headers: { Authorization: `Bearer ${token}` }});
      
      toast.success(response.data.message);
      setSelectedUsersForReminder([]);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send reminders');
    } finally {
      setSendingReminders(false);
    }
  };

  const handleSendReminderToAll = async () => {
    setSendingReminders(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/admin/send-reminder-all`, {}, 
        { headers: { Authorization: `Bearer ${token}` }});
      
      toast.success(response.data.message);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send reminders');
    } finally {
      setSendingReminders(false);
    }
  };

  // Document Preview Functions
  const handleViewDocument = (docUrl, docType, applicantName) => {
    if (!docUrl) {
      toast.error(`No ${docType} document uploaded`);
      return;
    }
    setDocumentPreview({
      url: `${BACKEND_URL}${docUrl}`,
      type: docType,
      applicantName: applicantName
    });
    setShowDocumentModal(true);
  };

  const handleDownloadDocument = (docUrl, docType, applicantName) => {
    if (!docUrl) {
      toast.error(`No ${docType} document uploaded`);
      return;
    }
    const link = document.createElement('a');
    link.href = `${BACKEND_URL}${docUrl}`;
    link.download = `${applicantName}_${docType}`;
    link.click();
  };

  // User Delete Functions
  const handleViewUserDetails = async (userEmail) => {
    setLoadingUserDetails(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/users/${encodeURIComponent(userEmail)}/details`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserDetails(response.data);
      setUserToDelete(userEmail);
      setShowDeleteModal(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to get user details');
    } finally {
      setLoadingUserDetails(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;
    
    setDeletingUser(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete(`${API}/admin/users/${encodeURIComponent(userToDelete)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(response.data.message);
      setShowDeleteModal(false);
      setUserToDelete(null);
      setUserDetails(null);
      
      // Refresh data
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingUser(false);
    }
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setUserToDelete(null);
    setUserDetails(null);
  };

  const filteredApps = applications.filter(app => {
    const matchesSearch = 
      app.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.application_id?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || app.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    const config = statusColors[status] || statusColors.pending_payment;
    return (
      <span style={{ 
        background: config.bg, 
        color: config.text,
        padding: '4px 12px',
        borderRadius: '20px',
        fontSize: '12px',
        fontWeight: '600'
      }}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <img src={LOGO_URL} alt="Cashflow MFB" className="h-10" />
            <div>
              <h1 className="text-lg font-bold text-gray-800">Admin Dashboard</h1>
              <p className="text-xs text-gray-500">Manage applications & users</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {user?.full_name || 'Admin'}</span>
            <Button onClick={handleLogout} variant="outline" size="sm" className="rounded-full">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-blue-100 text-sm">Total Users</p>
                  <p className="text-3xl font-bold mt-1">{stats.totalUsers}</p>
                </div>
                <Users className="w-10 h-10 text-blue-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-green-100 text-sm">Paid Users</p>
                  <p className="text-3xl font-bold mt-1">{stats.totalPaid}</p>
                </div>
                <UserCheck className="w-10 h-10 text-green-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-yellow-100 text-sm">Pending Payment</p>
                  <p className="text-3xl font-bold mt-1">{stats.totalPending}</p>
                </div>
                <Clock className="w-10 h-10 text-yellow-200" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-purple-100 text-sm">Total Collected</p>
                  <p className="text-3xl font-bold mt-1">₦{stats.totalCollected.toLocaleString()}</p>
                </div>
                <DollarSign className="w-10 h-10 text-purple-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="applications" className="space-y-4">
          <TabsList className="bg-white p-1 rounded-lg shadow-sm">
            <TabsTrigger value="applications" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <FileText className="w-4 h-4 mr-2" />
              Applications
            </TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <Users className="w-4 h-4 mr-2" />
              Users
            </TabsTrigger>
            <TabsTrigger value="payments" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <CreditCard className="w-4 h-4 mr-2" />
              Payments
            </TabsTrigger>
            <TabsTrigger value="activity" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <Activity className="w-4 h-4 mr-2" />
              Activity
            </TabsTrigger>
            <TabsTrigger value="reminders" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <Send className="w-4 h-4 mr-2" />
              Reminders
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </TabsTrigger>
          </TabsList>

          {/* Applications Tab */}
          <TabsContent value="applications">
            <Card>
              <CardHeader className="pb-4">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <CardTitle>All Applications</CardTitle>
                  <div className="flex gap-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input 
                        placeholder="Search by name, email, ID..." 
                        className="pl-10 w-64"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Filter status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="pending_payment">Pending Payment</SelectItem>
                        <SelectItem value="under_review">Under Review</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="deposit_paid">Deposit Paid</SelectItem>
                        <SelectItem value="disbursed">Disbursed</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button onClick={fetchData} variant="outline" size="icon">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto text-green-600" />
                    <p className="mt-2 text-gray-500">Loading applications...</p>
                  </div>
                ) : filteredApps.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 mx-auto text-gray-300" />
                    <p className="mt-2 text-gray-500">No applications found</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b bg-gray-50">
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">ID</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Applicant</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Amount</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Status</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Date</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredApps.map((app) => (
                          <React.Fragment key={app.application_id}>
                            <tr className="border-b hover:bg-gray-50 cursor-pointer" onClick={() => toggleRow(app.application_id)}>
                              <td className="p-3">
                                <span className="font-mono text-sm">{app.application_id}</span>
                              </td>
                              <td className="p-3">
                                <div>
                                  <p className="font-medium text-gray-800">{app.full_name}</p>
                                  <p className="text-sm text-gray-500">{app.email}</p>
                                </div>
                              </td>
                              <td className="p-3">
                                <span className="font-semibold text-green-600">₦{Number(app.loan_amount).toLocaleString()}</span>
                              </td>
                              <td className="p-3">{getStatusBadge(app.status)}</td>
                              <td className="p-3 text-sm text-gray-500">
                                {new Date(app.created_at).toLocaleDateString()}
                              </td>
                              <td className="p-3">
                                <div className="flex gap-2">
                                  <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); toggleRow(app.application_id); }}>
                                    {expandedRows[app.application_id] ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                  </Button>
                                  <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); setSelectedApp(app); }}>
                                    <Eye className="w-4 h-4" />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                            {expandedRows[app.application_id] && (
                              <tr className="bg-gray-50">
                                <td colSpan="6" className="p-4">
                                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div>
                                      <h4 className="font-semibold text-sm mb-2">Personal Info</h4>
                                      <p className="text-sm"><span className="text-gray-500">Phone:</span> {app.phone}</p>
                                      <p className="text-sm"><span className="text-gray-500">Home Town:</span> {app.home_town}</p>
                                      <p className="text-sm"><span className="text-gray-500">Address:</span> {app.residential_address}</p>
                                    </div>
                                    <div>
                                      <h4 className="font-semibold text-sm mb-2">Bank Details</h4>
                                      <p className="text-sm"><span className="text-gray-500">Bank:</span> {app.bank_name}</p>
                                      <p className="text-sm"><span className="text-gray-500">Account:</span> {app.account_number}</p>
                                      <p className="text-sm"><span className="text-gray-500">Name:</span> {app.account_name}</p>
                                    </div>
                                    <div>
                                      <h4 className="font-semibold text-sm mb-2">Payment Status</h4>
                                      <p className="text-sm flex items-center gap-2">
                                        {app.processing_fee_paid ? <CheckCircle className="w-4 h-4 text-green-500" /> : <Clock className="w-4 h-4 text-yellow-500" />}
                                        Processing Fee: {app.processing_fee_paid ? 'Paid' : 'Pending'}
                                      </p>
                                      <p className="text-sm flex items-center gap-2">
                                        {app.deposit_paid ? <CheckCircle className="w-4 h-4 text-green-500" /> : <Clock className="w-4 h-4 text-gray-400" />}
                                        Deposit: {app.deposit_paid ? 'Paid' : 'Not Paid'}
                                      </p>
                                    </div>
                                    <div>
                                      <h4 className="font-semibold text-sm mb-2">Documents</h4>
                                      <div className="flex flex-col gap-2">
                                        <Button 
                                          size="sm" 
                                          variant="outline"
                                          className="justify-start"
                                          onClick={() => handleViewDocument(app.id_card_url, 'ID Card', app.full_name)}
                                        >
                                          <FileImage className="w-4 h-4 mr-2" /> View ID Card
                                        </Button>
                                        <Button 
                                          size="sm" 
                                          variant="outline"
                                          className="justify-start"
                                          onClick={() => handleViewDocument(app.passport_url, 'Passport', app.full_name)}
                                        >
                                          <Image className="w-4 h-4 mr-2" /> View Passport
                                        </Button>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="mt-4 flex gap-2">
                                    {app.status === 'under_review' && (
                                      <>
                                        <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleStatusUpdate(app.application_id, 'approved')}>
                                          <CheckCircle className="w-4 h-4 mr-1" /> Approve
                                        </Button>
                                        <Button size="sm" variant="destructive" onClick={() => handleStatusUpdate(app.application_id, 'rejected', 'Application did not meet requirements')}>
                                          <XCircle className="w-4 h-4 mr-1" /> Reject
                                        </Button>
                                      </>
                                    )}
                                    {app.status === 'deposit_paid' && (
                                      <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleStatusUpdate(app.application_id, 'disbursed')}>
                                        <DollarSign className="w-4 h-4 mr-1" /> Mark as Disbursed
                                      </Button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>Registered Users</CardTitle>
              </CardHeader>
              <CardContent>
                {users.length === 0 ? (
                  <div className="text-center py-12">
                    <Users className="w-12 h-12 mx-auto text-gray-300" />
                    <p className="mt-2 text-gray-500">No registered users yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b bg-gray-50">
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Name</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Email</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Phone</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Role</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Registered</th>
                          <th className="text-left p-3 text-sm font-semibold text-gray-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((user, index) => (
                          <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="p-3 font-medium">{user.full_name}</td>
                            <td className="p-3 text-gray-600">{user.email}</td>
                            <td className="p-3 text-gray-600">{user.phone || 'N/A'}</td>
                            <td className="p-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                user.role === 'admin' 
                                  ? 'bg-purple-100 text-purple-700' 
                                  : 'bg-green-100 text-green-700'
                              }`}>
                                {user.role || 'user'}
                              </span>
                            </td>
                            <td className="p-3 text-sm text-gray-500">
                              {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                            </td>
                            <td className="p-3">
                              {user.role !== 'admin' ? (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
                                  onClick={() => handleViewUserDetails(user.email)}
                                  disabled={loadingUserDetails}
                                >
                                  <Trash2 className="w-4 h-4 mr-1" />
                                  Delete
                                </Button>
                              ) : (
                                <span className="text-xs text-gray-400">Protected</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments">
            <Card>
              <CardHeader>
                <CardTitle>Payment Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-left p-3 text-sm font-semibold text-gray-600">User</th>
                        <th className="text-left p-3 text-sm font-semibold text-gray-600">Type</th>
                        <th className="text-left p-3 text-sm font-semibold text-gray-600">Amount</th>
                        <th className="text-left p-3 text-sm font-semibold text-gray-600">Status</th>
                        <th className="text-left p-3 text-sm font-semibold text-gray-600">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {applications.filter(a => a.processing_fee_paid || a.deposit_paid).map((app) => (
                        <React.Fragment key={app.application_id}>
                          {app.processing_fee_paid && (
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">{app.full_name}</td>
                              <td className="p-3">Processing Fee</td>
                              <td className="p-3 font-semibold text-green-600">₦2,500</td>
                              <td className="p-3">
                                <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                  Paid
                                </span>
                              </td>
                              <td className="p-3 text-sm text-gray-500">
                                {app.processing_fee_paid_at ? new Date(app.processing_fee_paid_at).toLocaleString() : '-'}
                              </td>
                            </tr>
                          )}
                          {app.deposit_paid && (
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">{app.full_name}</td>
                              <td className="p-3">Fixed Deposit</td>
                              <td className="p-3 font-semibold text-green-600">₦3,000</td>
                              <td className="p-3">
                                <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                  Paid
                                </span>
                              </td>
                              <td className="p-3 text-sm text-gray-500">
                                {app.deposit_paid_at ? new Date(app.deposit_paid_at).toLocaleString() : '-'}
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {applications.slice(0, 10).map((app) => (
                    <div key={app.application_id} className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                        <FileText className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-800">{app.full_name}</p>
                        <p className="text-sm text-gray-500">
                          Application {app.application_id} - Status: {statusColors[app.status]?.label || app.status}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(app.updated_at || app.created_at).toLocaleString()}
                        </p>
                      </div>
                      {getStatusBadge(app.status)}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reminders Tab */}
          <TabsContent value="reminders">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Send to Selected Users */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Send className="w-5 h-5" />
                    Send Reminders to Selected Users
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Reminder Type</label>
                      <Select value={reminderType} onValueChange={setReminderType}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select reminder type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Pending Payments</SelectItem>
                          <SelectItem value="processing_fee">Processing Fee Only (₦2,500)</SelectItem>
                          <SelectItem value="deposit">Deposit Only (₦3,000)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium">Select Users</label>
                        <Button variant="link" size="sm" onClick={handleSelectAllForReminder}>
                          {selectedUsersForReminder.length === applications.filter(a => !a.processing_fee_paid || (a.status === 'approved' && !a.deposit_paid)).length ? 'Deselect All' : 'Select All Pending'}
                        </Button>
                      </div>
                      <div className="max-h-64 overflow-y-auto border rounded-lg">
                        {applications.filter(app => !app.processing_fee_paid || (app.status === 'approved' && !app.deposit_paid)).length === 0 ? (
                          <div className="p-4 text-center text-gray-500">
                            No users with pending payments
                          </div>
                        ) : (
                          applications
                            .filter(app => !app.processing_fee_paid || (app.status === 'approved' && !app.deposit_paid))
                            .map((app) => (
                              <div 
                                key={app.application_id} 
                                className={`flex items-center gap-3 p-3 border-b hover:bg-gray-50 cursor-pointer ${selectedUsersForReminder.includes(app.email) ? 'bg-green-50' : ''}`}
                                onClick={() => handleSelectUserForReminder(app.email)}
                              >
                                <input 
                                  type="checkbox" 
                                  checked={selectedUsersForReminder.includes(app.email)}
                                  onChange={() => {}}
                                  className="w-4 h-4 text-green-600"
                                />
                                <div className="flex-1">
                                  <p className="font-medium text-sm">{app.full_name}</p>
                                  <p className="text-xs text-gray-500">{app.email}</p>
                                </div>
                                <div className="text-right">
                                  {!app.processing_fee_paid && (
                                    <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">₦2,500 pending</span>
                                  )}
                                  {app.processing_fee_paid && !app.deposit_paid && app.status === 'approved' && (
                                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">₦3,000 deposit</span>
                                  )}
                                </div>
                              </div>
                            ))
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-500">
                        {selectedUsersForReminder.length} user(s) selected
                      </p>
                      <Button 
                        className="bg-green-600 hover:bg-green-700"
                        onClick={handleSendReminders}
                        disabled={sendingReminders || selectedUsersForReminder.length === 0}
                      >
                        {sendingReminders ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Sending...
                          </>
                        ) : (
                          <>
                            <Send className="w-4 h-4 mr-2" />
                            Send Reminders
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MailIcon className="w-5 h-5" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <h4 className="font-semibold text-yellow-800 mb-2">Send to All Pending Users</h4>
                      <p className="text-sm text-yellow-700 mb-4">
                        This will send payment reminder emails to ALL users with pending payments (both processing fee and deposit).
                      </p>
                      <Button 
                        className="w-full bg-yellow-600 hover:bg-yellow-700"
                        onClick={handleSendReminderToAll}
                        disabled={sendingReminders}
                      >
                        {sendingReminders ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Sending...
                          </>
                        ) : (
                          <>
                            <Send className="w-4 h-4 mr-2" />
                            Send to All Pending Users
                          </>
                        )}
                      </Button>
                    </div>
                    
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-semibold text-gray-800 mb-2">Reminder Statistics</h4>
                      <div className="grid grid-cols-2 gap-4 mt-3">
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <p className="text-2xl font-bold text-yellow-600">
                            {applications.filter(a => !a.processing_fee_paid).length}
                          </p>
                          <p className="text-xs text-gray-500">Pending Processing Fee</p>
                        </div>
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <p className="text-2xl font-bold text-purple-600">
                            {applications.filter(a => a.processing_fee_paid && !a.deposit_paid && a.status === 'approved').length}
                          </p>
                          <p className="text-xs text-gray-500">Pending Deposit</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <h4 className="font-semibold text-green-800 mb-2">Auto Reminders</h4>
                      <p className="text-sm text-green-700">
                        Automatic reminders are sent every 24 hours to users with pending payments older than 24 hours.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Change Password Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lock className="w-5 h-5" />
                    Change Password
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Current Password</label>
                      <Input
                        type="password"
                        placeholder="Enter current password"
                        value={passwordData.currentPassword}
                        onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">New Password</label>
                      <Input
                        type="password"
                        placeholder="Enter new password"
                        value={passwordData.newPassword}
                        onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                        required
                        minLength={8}
                      />
                      <p className="text-xs text-gray-500 mt-1">Must be at least 8 characters</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Confirm New Password</label>
                      <Input
                        type="password"
                        placeholder="Confirm new password"
                        value={passwordData.confirmPassword}
                        onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                        required
                      />
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full bg-green-600 hover:bg-green-700"
                      disabled={changingPassword}
                    >
                      {changingPassword ? 'Changing...' : 'Change Password'}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Account Info Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Account Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500">Full Name</p>
                      <p className="font-medium">{user?.full_name || 'Admin'}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500">Email Address</p>
                      <p className="font-medium">{user?.email || 'admin@cashflowmfb.com'}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500">Role</p>
                      <p className="font-medium capitalize">{user?.role || 'Admin'}</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-sm text-green-700">
                        <strong>Security Tip:</strong> Change your password regularly and never share your login credentials.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Application Detail Modal */}
      {selectedApp && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedApp(null)}>
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold">{selectedApp.full_name}</h2>
                  <p className="text-gray-500">{selectedApp.application_id}</p>
                </div>
                {getStatusBadge(selectedApp.status)}
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-3">Personal Information</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Email:</span> {selectedApp.email}</p>
                    <p><span className="text-gray-500">Phone:</span> {selectedApp.phone}</p>
                    <p><span className="text-gray-500">DOB:</span> {selectedApp.date_of_birth}</p>
                    <p><span className="text-gray-500">Home Town:</span> {selectedApp.home_town}</p>
                    <p><span className="text-gray-500">Address:</span> {selectedApp.residential_address}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Employment Details</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Workplace:</span> {selectedApp.place_of_work}</p>
                    <p><span className="text-gray-500">Status:</span> {selectedApp.employment_status}</p>
                    <p><span className="text-gray-500">Income:</span> ₦{Number(selectedApp.monthly_income).toLocaleString()}</p>
                    <p><span className="text-gray-500">Reason:</span> {selectedApp.loan_reason}</p>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-3">Bank Details</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Bank:</span> {selectedApp.bank_name}</p>
                    <p><span className="text-gray-500">Account Name:</span> {selectedApp.account_name}</p>
                    <p><span className="text-gray-500">Account Number:</span> {selectedApp.account_number}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Loan Details</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Amount:</span> <span className="font-semibold text-green-600">₦{Number(selectedApp.loan_amount).toLocaleString()}</span></p>
                    <p><span className="text-gray-500">Duration:</span> {selectedApp.repayment_duration?.replace('_', ' ')}</p>
                    <p><span className="text-gray-500">Frequency:</span> {selectedApp.repayment_frequency?.replace('_', '-')}</p>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Identity Verification</h3>
                <div className="space-y-2 text-sm">
                  <p><span className="text-gray-500">NIN:</span> {selectedApp.nin}</p>
                  <p><span className="text-gray-500">BVN:</span> {selectedApp.bvn}</p>
                </div>
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setSelectedApp(null)}>Close</Button>
              {selectedApp.status === 'under_review' && (
                <>
                  <Button variant="destructive" onClick={() => handleStatusUpdate(selectedApp.application_id, 'rejected', 'Application did not meet requirements')}>
                    Reject
                  </Button>
                  <Button className="bg-green-600 hover:bg-green-700" onClick={() => handleStatusUpdate(selectedApp.application_id, 'approved')}>
                    Approve
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* User Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={closeDeleteModal}>
          <div className="bg-white rounded-xl max-w-lg w-full overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b bg-red-50 flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-red-800">Delete User Account</h3>
                <p className="text-sm text-red-600">This action cannot be undone</p>
              </div>
            </div>
            
            <div className="p-6">
              {loadingUserDetails ? (
                <div className="text-center py-8">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400" />
                  <p className="mt-2 text-gray-500">Loading user details...</p>
                </div>
              ) : userDetails ? (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold mb-2">User Information</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <p><span className="text-gray-500">Name:</span> {userDetails.user?.full_name}</p>
                      <p><span className="text-gray-500">Email:</span> {userDetails.user?.email}</p>
                      <p><span className="text-gray-500">Phone:</span> {userDetails.user?.phone || 'N/A'}</p>
                      <p><span className="text-gray-500">Registered:</span> {userDetails.user?.created_at ? new Date(userDetails.user.created_at).toLocaleDateString() : 'N/A'}</p>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="font-semibold text-yellow-800 mb-2">Data to be Deleted:</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      <li>• User account and profile</li>
                      <li>• {userDetails.summary?.total_applications || 0} loan application(s)</li>
                      <li>• {userDetails.summary?.total_transactions || 0} transaction record(s)</li>
                      <li>• All uploaded documents</li>
                      <li>• Password reset tokens</li>
                    </ul>
                  </div>
                  
                  <p className="text-sm text-gray-600">
                    Are you sure you want to permanently delete <strong>{userDetails.user?.full_name}</strong> ({userDetails.user?.email}) and all associated data?
                  </p>
                </div>
              ) : (
                <p className="text-center text-gray-500">No user data available</p>
              )}
            </div>
            
            <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
              <Button variant="outline" onClick={closeDeleteModal} disabled={deletingUser}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={handleDeleteUser}
                disabled={deletingUser || !userDetails}
                className="bg-red-600 hover:bg-red-700"
              >
                {deletingUser ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Permanently
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {showDocumentModal && documentPreview && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowDocumentModal(false)}>
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b flex justify-between items-center">
              <div>
                <h3 className="font-semibold">{documentPreview.type}</h3>
                <p className="text-sm text-gray-500">{documentPreview.applicantName}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownloadDocument(documentPreview.url.replace(BACKEND_URL, ''), documentPreview.type, documentPreview.applicantName)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setShowDocumentModal(false)}>
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </div>
            <div className="p-4 flex items-center justify-center bg-gray-100" style={{ minHeight: '60vh' }}>
              <img 
                src={documentPreview.url} 
                alt={documentPreview.type}
                className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" x="50" text-anchor="middle" font-size="12">Image not found</text></svg>';
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
