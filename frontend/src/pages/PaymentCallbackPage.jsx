import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2, Copy, Building2, Clock } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentCallbackPage = () => {
  const [searchParams] = useSearchParams();
  
  // Check if this is a bank transfer payment
  const paymentType = searchParams.get('type');
  const accountNumber = searchParams.get('account');
  const bankName = searchParams.get('bank');
  const amount = searchParams.get('amount');
  
  // Determine if this is a bank transfer from URL params
  const isBankTransfer = paymentType === 'bank_transfer' && accountNumber;
  
  // Calculate initial state based on URL params
  const initialState = useMemo(() => {
    if (isBankTransfer) {
      return {
        status: 'bank_transfer',
        paymentData: {
          orderRef: searchParams.get('orderRef'),
          amount: parseInt(amount) || 2500,
          virtualAccount: {
            account_number: accountNumber,
            bank_name: decodeURIComponent(bankName || 'Partner Bank')
          }
        }
      };
    }
    return { status: 'loading', paymentData: null };
  }, [isBankTransfer, accountNumber, bankName, amount, searchParams]);

  const [status, setStatus] = useState(initialState.status);
  const [paymentData, setPaymentData] = useState(initialState.paymentData);
  const [pollCount, setPollCount] = useState(0);
  const hasVerified = useRef(false);

  // Verify payment on mount (only for non-bank transfer)
  useEffect(() => {
    if (isBankTransfer || hasVerified.current) return;
    hasVerified.current = true;
    
    const controller = new AbortController();
    
    const verifyPayment = async () => {
      try {
        const orderRef = searchParams.get('orderRef') || localStorage.getItem('order_reference');
        const applicationId = localStorage.getItem('application_id');

        if (!orderRef) {
          setStatus('failed');
          return;
        }

        const response = await axios.post(`${API}/payments/verify`, {
          order_ref: orderRef
        }, { signal: controller.signal });

        const { payment_status, transaction_reference, amount: paidAmount, virtual_account } = response.data;

        setPaymentData({
          orderRef: orderRef,
          amount: paidAmount,
          transactionRef: transaction_reference,
          applicationId: applicationId,
          virtualAccount: virtual_account
        });

        if (payment_status === 'completed') {
          setStatus('success');
          localStorage.removeItem('order_reference');
          localStorage.removeItem('application_id');
        } else if (payment_status === 'failed') {
          setStatus('failed');
        } else {
          setStatus('pending');
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          console.error('Payment verification error:', error);
          setStatus('failed');
        }
      }
    };
    
    verifyPayment();
    
    return () => controller.abort();
  }, [isBankTransfer, searchParams]);

  // Poll for payment status when showing bank transfer instructions
  useEffect(() => {
    if (status === 'bank_transfer' && pollCount < 60) {
      const interval = setInterval(async () => {
        setPollCount(prev => prev + 1);
        try {
          const orderRef = searchParams.get('orderRef') || localStorage.getItem('order_reference');
          if (orderRef) {
            const response = await axios.post(`${API}/payments/verify`, {
              order_ref: orderRef
            });
            
            if (response.data.payment_status === 'completed') {
              setStatus('success');
              setPaymentData(prev => ({
                ...prev,
                transactionRef: response.data.transaction_reference
              }));
              localStorage.removeItem('order_reference');
              localStorage.removeItem('application_id');
            }
          }
        } catch (error) {
          console.error('Poll error:', error);
        }
      }, 10000); // Poll every 10 seconds

      return () => clearInterval(interval);
    }
  }, [status, pollCount, searchParams]);

  const verifyPaymentManual = async () => {
    setStatus('verifying');
    try {
      const orderRef = searchParams.get('orderRef') || localStorage.getItem('order_reference');
      const applicationId = localStorage.getItem('application_id');

      if (!orderRef) {
        setStatus('failed');
        return;
      }

      const response = await axios.post(`${API}/payments/verify`, {
        order_ref: orderRef
      });

      const { payment_status, transaction_reference, amount: paidAmount, virtual_account } = response.data;

      setPaymentData({
        orderRef: orderRef,
        amount: paidAmount,
        transactionRef: transaction_reference,
        applicationId: applicationId,
        virtualAccount: virtual_account
      });

      if (payment_status === 'completed') {
        setStatus('success');
        localStorage.removeItem('order_reference');
        localStorage.removeItem('application_id');
      } else if (payment_status === 'failed') {
        setStatus('failed');
      } else {
        setStatus('pending');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('failed');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const handleVerifyClick = () => {
    verifyPaymentManual();
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8" style={{ background: 'var(--bg-section)' }}>
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'loading' && 'Loading...'}
            {status === 'verifying' && 'Verifying Payment...'}
            {status === 'bank_transfer' && 'Complete Your Payment'}
            {status === 'pending' && 'Awaiting Payment'}
            {status === 'success' && 'Payment Successful!'}
            {status === 'failed' && 'Payment Failed'}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          {(status === 'loading' || status === 'verifying') && (
            <div className="flex flex-col items-center">
              <Loader2 className="w-16 h-16 animate-spin" style={{ color: 'var(--accent-text)' }} />
              <p className="body-medium mt-4" style={{ color: 'var(--text-secondary)' }}>
                {status === 'loading' ? 'Loading payment details...' : 'Verifying your payment...'}
              </p>
            </div>
          )}

          {(status === 'bank_transfer' || status === 'pending') && paymentData?.virtualAccount && (
            <div>
              <Building2 className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
              
              <div className="p-4 rounded-lg mb-4" style={{ background: 'var(--accent-wash)' }}>
                <p className="body-small font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                  Transfer exactly ₦{paymentData.amount?.toLocaleString()} to:
                </p>
              </div>

              <div className="space-y-4 text-left">
                <div className="p-4 border rounded-lg">
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>Bank Name</p>
                  <p className="body-medium font-semibold">{paymentData.virtualAccount.bank_name}</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="body-small" style={{ color: 'var(--text-muted)' }}>Account Number</p>
                      <p className="body-medium font-mono font-semibold text-lg">
                        {paymentData.virtualAccount.account_number}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(paymentData.virtualAccount.account_number)}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>Amount</p>
                  <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                    ₦{paymentData.amount?.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-lg border border-yellow-300 bg-yellow-50">
                <div className="flex items-start gap-2">
                  <Clock className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div className="text-left">
                    <p className="body-small font-medium text-yellow-800">Important:</p>
                    <ul className="body-small text-yellow-700 list-disc list-inside mt-1">
                      <li>Transfer the exact amount shown</li>
                      <li>Use any Nigerian bank app or USSD</li>
                      <li>Payment confirms automatically</li>
                      <li>This page will update when payment is received</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <Button 
                  className="w-full btn-primary" 
                  onClick={handleVerifyClick}
                >
                  I&apos;ve Made the Transfer
                </Button>
                <Link to="/" className="block">
                  <Button variant="outline" className="w-full rounded-full">
                    Cancel & Go Home
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div>
              <CheckCircle className="w-16 h-16 mx-auto" style={{ color: 'var(--accent-text)' }} />
              <div className="mt-6 space-y-4">
                {paymentData?.transactionRef && (
                  <div>
                    <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                      Transaction Reference
                    </p>
                    <p className="body-medium font-mono">{paymentData.transactionRef}</p>
                  </div>
                )}
                <div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Amount Paid
                  </p>
                  <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                    ₦{paymentData?.amount?.toLocaleString()}
                  </p>
                </div>
                <div className="p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
                  <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                    Your loan application is now under review. We&apos;ll notify you via email
                    within 24 hours. Please login to track your application status.
                  </p>
                </div>
              </div>
              <div className="mt-6 space-y-3">
                <Link to="/login" className="block">
                  <Button className="w-full btn-primary">
                    Login to Dashboard
                  </Button>
                </Link>
                <Link to="/" className="block">
                  <Button variant="outline" className="w-full rounded-full">
                    Back to Home
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {status === 'failed' && (
            <div>
              <XCircle className="w-16 h-16 mx-auto text-red-500" />
              <p className="body-medium mt-4" style={{ color: 'var(--text-secondary)' }}>
                Your payment could not be processed. Please try again or contact support.
              </p>
              <div className="mt-6 space-y-3">
                <Link to="/apply" className="block">
                  <Button className="w-full btn-primary">
                    Try Again
                  </Button>
                </Link>
                <Link to="/" className="block">
                  <Button variant="outline" className="w-full rounded-full">
                    Back to Home
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentCallbackPage;
