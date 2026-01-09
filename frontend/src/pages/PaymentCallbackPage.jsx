import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2, Clock } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading');
  const [paymentData, setPaymentData] = useState(null);
  const [pollCount, setPollCount] = useState(0);
  const hasVerified = useRef(false);
  const isMounted = useRef(true);

  // Verify payment on mount
  useEffect(() => {
    isMounted.current = true;
    
    // Skip if already verified (handles StrictMode double-mount)
    if (hasVerified.current) return;
    hasVerified.current = true;
    
    const verifyPayment = async () => {
      try {
        // BudPay returns: ?reference=xxx&status=success/failed
        // Or we use our stored order_reference
        const budpayRef = searchParams.get('reference');
        const budpayStatus = searchParams.get('status');
        const orderRef = searchParams.get('orderRef') || budpayRef || localStorage.getItem('order_reference');
        const applicationId = localStorage.getItem('application_id');

        if (!orderRef) {
          if (isMounted.current) setStatus('failed');
          return;
        }

        // If BudPay returned a failed status directly
        if (budpayStatus === 'failed' || budpayStatus === 'cancelled') {
          if (isMounted.current) {
            setStatus('failed');
            setPaymentData({ orderRef, applicationId });
          }
          return;
        }

        // Verify with our backend
        const response = await axios.post(`${API}/payments/verify`, {
          order_ref: orderRef
        });

        if (!isMounted.current) return;

        const { payment_status, transaction_reference, amount: paidAmount } = response.data;

        setPaymentData({
          orderRef: orderRef,
          amount: paidAmount,
          transactionRef: transaction_reference,
          applicationId: applicationId
        });

        if (payment_status === 'completed') {
          setStatus('success');
          localStorage.removeItem('order_reference');
          localStorage.removeItem('application_id');
          localStorage.removeItem('payment_type');
        } else if (payment_status === 'failed') {
          setStatus('failed');
        } else {
          // Payment is pending - start polling
          setStatus('pending');
        }
      } catch (error) {
        console.error('Payment verification error:', error);
        if (isMounted.current) {
          setStatus('failed');
        }
      }
    };
    
    verifyPayment();
    
    return () => {
      isMounted.current = false;
    };
  }, [searchParams]);

  // Poll for payment status when pending
  useEffect(() => {
    if (status === 'pending' && pollCount < 30) {
      const interval = setInterval(async () => {
        setPollCount(prev => prev + 1);
        try {
          const orderRef = searchParams.get('reference') || searchParams.get('orderRef') || localStorage.getItem('order_reference');
          if (orderRef) {
            const response = await axios.post(`${API}/payments/verify`, {
              order_ref: orderRef
            });
            
            if (response.data.payment_status === 'completed') {
              setStatus('success');
              setPaymentData(prev => ({
                ...prev,
                transactionRef: response.data.transaction_reference,
                amount: response.data.amount
              }));
              localStorage.removeItem('order_reference');
              localStorage.removeItem('application_id');
              localStorage.removeItem('payment_type');
            } else if (response.data.payment_status === 'failed') {
              setStatus('failed');
            }
          }
        } catch (error) {
          console.error('Poll error:', error);
        }
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(interval);
    }
  }, [status, pollCount, searchParams]);

  const verifyPaymentManual = async () => {
    setStatus('verifying');
    try {
      const orderRef = searchParams.get('reference') || searchParams.get('orderRef') || localStorage.getItem('order_reference');
      const applicationId = localStorage.getItem('application_id');

      if (!orderRef) {
        setStatus('failed');
        return;
      }

      const response = await axios.post(`${API}/payments/verify`, {
        order_ref: orderRef
      });

      const { payment_status, transaction_reference, amount: paidAmount } = response.data;

      setPaymentData({
        orderRef: orderRef,
        amount: paidAmount,
        transactionRef: transaction_reference,
        applicationId: applicationId
      });

      if (payment_status === 'completed') {
        setStatus('success');
        localStorage.removeItem('order_reference');
        localStorage.removeItem('application_id');
        localStorage.removeItem('payment_type');
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

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8" style={{ background: 'var(--bg-section)' }}>
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'loading' && 'Loading...'}
            {status === 'verifying' && 'Verifying Payment...'}
            {status === 'pending' && 'Payment Processing...'}
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

          {status === 'pending' && (
            <div>
              <Clock className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
              
              <div className="p-4 rounded-lg mb-4" style={{ background: 'var(--accent-wash)' }}>
                <p className="body-small font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                  Your payment is being processed...
                </p>
                <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                  This page will automatically update once your payment is confirmed.
                </p>
              </div>

              {paymentData?.amount && (
                <div className="p-4 border rounded-lg mb-4">
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>Amount</p>
                  <p className="heading-3" style={{ color: 'var(--accent-text)' }}>
                    ₦{paymentData.amount?.toLocaleString()}
                  </p>
                </div>
              )}

              <div className="mt-6 space-y-3">
                <Button 
                  className="w-full btn-primary" 
                  onClick={verifyPaymentManual}
                  data-testid="verify-payment-btn"
                >
                  Check Payment Status
                </Button>
                <Link to="/" className="block">
                  <Button variant="outline" className="w-full rounded-full">
                    Go Home
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
                  <Button className="w-full btn-primary" data-testid="login-after-payment-btn">
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
                <Link to="/dashboard" className="block">
                  <Button className="w-full btn-primary" data-testid="retry-payment-btn">
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
