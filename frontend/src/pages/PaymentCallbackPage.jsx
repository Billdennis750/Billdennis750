import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const PaymentCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying');
  const [paymentData, setPaymentData] = useState(null);

  useEffect(() => {
    // Mock payment verification
    const orderRef = searchParams.get('orderRef');
    const paymentStatus = searchParams.get('status');

    setTimeout(() => {
      if (paymentStatus === 'success') {
        setStatus('success');
        setPaymentData({
          orderRef: orderRef,
          amount: 2500,
          transactionRef: `NOMBA-${Date.now()}`,
        });
        
        // Store payment success
        const application = JSON.parse(localStorage.getItem('currentApplication') || '{}');
        application.paymentStatus = 'Paid';
        application.status = 'Under Review';
        localStorage.setItem('currentApplication', JSON.stringify(application));
      } else {
        setStatus('failed');
      }
    }, 2000);
  }, [searchParams]);

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
