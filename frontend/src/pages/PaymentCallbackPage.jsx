import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying');
  const [paymentData, setPaymentData] = useState(null);

  useEffect(() => {
    verifyPayment();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const verifyPayment = async () => {
    try {
      // Get order reference from URL or localStorage
      const orderRef = searchParams.get('orderRef') || localStorage.getItem('order_reference');
      const applicationId = localStorage.getItem('application_id');

      if (!orderRef) {
        setStatus('failed');
        return;
      }

      // Verify payment with backend
      const response = await axios.post(`${API}/payments/verify`, {
        order_ref: orderRef
      });

      const { payment_status, transaction_reference, amount } = response.data;

      if (payment_status === 'completed') {
        setStatus('success');
        setPaymentData({
          orderRef: orderRef,
          amount: amount,
          transactionRef: transaction_reference,
          applicationId: applicationId
        });
        
        // Clear localStorage
        localStorage.removeItem('order_reference');
        localStorage.removeItem('application_id');
      } else {
        setStatus('failed');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'var(--bg-section)' }}>
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'verifying' && 'Verifying Payment...'}
            {status === 'success' && 'Payment Successful!'}
            {status === 'failed' && 'Payment Failed'}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          {status === 'verifying' && (
            <div className="flex flex-col items-center">
              <Loader2 className="w-16 h-16 animate-spin" style={{ color: 'var(--accent-text)' }} />
              <p className="body-medium mt-4" style={{ color: 'var(--text-secondary)' }}>
                Please wait while we verify your payment...
              </p>
            </div>
          )}

          {status === 'success' && (
            <div>
              <CheckCircle className="w-16 h-16 mx-auto" style={{ color: 'var(--accent-text)' }} />
              <div className="mt-6 space-y-4">
                <div>
                  <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                    Transaction Reference
                  </p>
                  <p className="body-medium font-mono">{paymentData?.transactionRef}</p>
                </div>
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
                    Your loan application is now under review. We'll notify you via email
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
