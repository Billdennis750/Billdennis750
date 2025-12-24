import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await axios.post(`${BACKEND_URL}/api/auth/forgot-password`, { email });
      setIsSubmitted(true);
      toast.success('Password reset instructions sent!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <Header />
      
      <div className="min-h-screen flex items-center justify-center py-20 px-4" style={{ background: 'var(--bg-section)' }}>
        <div className="w-full max-w-md">
          <Link to="/login" className="inline-flex items-center mb-6 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
          
          <div className="bg-white rounded-lg shadow-sm p-8">
            {!isSubmitted ? (
              <>
                <div className="text-center mb-8">
                  <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ background: 'var(--accent-wash)' }}>
                    <Mail className="w-8 h-8" style={{ color: 'var(--accent-text)' }} />
                  </div>
                  <h1 className="heading-2 mb-2">Forgot Password?</h1>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    Enter your email and we&apos;ll send you a link to reset your password.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Email Address</label>
                    <Input
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full btn-primary"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Sending...' : 'Send Reset Link'}
                  </Button>
                </form>
              </>
            ) : (
              <div className="text-center">
                <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center bg-green-100">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="heading-2 mb-2">Check Your Email</h2>
                <p className="body-medium mb-6" style={{ color: 'var(--text-secondary)' }}>
                  We&apos;ve sent a password reset link to <strong>{email}</strong>. 
                  The link will expire in 1 hour.
                </p>
                <p className="body-small mb-6" style={{ color: 'var(--text-muted)' }}>
                  Didn&apos;t receive the email? Check your spam folder or
                </p>
                <Button
                  onClick={() => setIsSubmitted(false)}
                  variant="outline"
                  className="w-full"
                >
                  Try Again
                </Button>
              </div>
            )}

            <div className="mt-6 text-center">
              <p className="body-small" style={{ color: 'var(--text-muted)' }}>
                Remember your password?{' '}
                <Link to="/login" className="text-green-600 hover:text-green-700 font-medium">
                  Sign In
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default ForgotPasswordPage;
