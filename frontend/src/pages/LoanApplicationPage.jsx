import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Progress } from '../components/ui/progress';
import { toast } from 'sonner';
import PersonalInfoStep from '../components/application/PersonalInfoStep';
import EmploymentStep from '../components/application/EmploymentStep';
import IdentityStep from '../components/application/IdentityStep';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoanApplicationPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Personal Info
    fullName: '',
    dateOfBirth: '',
    email: '',
    phone: '',
    homeTown: '',
    residentialAddress: '',
    
    // Employment
    placeOfWork: '',
    employmentStatus: '',
    employmentDetails: '',
    monthlyIncome: '',
    loanReason: '',
    loanAmount: '',
    
    // Identity
    nin: '',
    bvn: '',
    idCard: null,
    passport: null,
  });

  const totalSteps = 3;
  const progress = (currentStep / totalSteps) * 100;

  const handleNext = (data) => {
    setFormData({ ...formData, ...data });
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit({ ...formData, ...data });
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async (finalData) => {
    try {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Append all form fields
      formData.append('full_name', finalData.fullName);
      formData.append('date_of_birth', finalData.dateOfBirth);
      formData.append('email', finalData.email);
      formData.append('phone', finalData.phone);
      formData.append('home_town', finalData.homeTown);
      formData.append('residential_address', finalData.residentialAddress);
      formData.append('place_of_work', finalData.placeOfWork);
      formData.append('employment_status', finalData.employmentStatus);
      formData.append('employment_details', finalData.employmentDetails);
      formData.append('monthly_income', finalData.monthlyIncome);
      formData.append('loan_amount', finalData.loanAmount);
      formData.append('loan_reason', finalData.loanReason);
      formData.append('nin', finalData.nin);
      formData.append('bvn', finalData.bvn);
      
      // Append files
      if (finalData.idCard) {
        formData.append('id_card', finalData.idCard);
      }
      if (finalData.passport) {
        formData.append('passport', finalData.passport);
      }
      
      // Submit to backend
      const response = await axios.post(`${API}/applications/submit`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const { application_id } = response.data;
      
      toast.success('Application submitted successfully!');
      
      // Initiate payment
      const paymentResponse = await axios.post(`${API}/payments/initiate`, {
        application_id: application_id,
        customer_email: finalData.email,
        customer_name: finalData.fullName,
        amount: 2500,
        redirect_url: `${window.location.origin}/payment-callback`
      });
      
      const { checkout_link, order_reference } = paymentResponse.data;
      
      // Store order reference for verification
      localStorage.setItem('order_reference', order_reference);
      localStorage.setItem('application_id', application_id);
      
      // Redirect to Xixapay payment page
      window.location.href = checkout_link;
      
    } catch (error) {
      console.error('Application submission error:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit application');
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1:
        return 'Personal Information';
      case 2:
        return 'Employment & Income Details';
      case 3:
        return 'Identity & Verification';
      default:
        return '';
    }
  };

  return (
    <div>
      <Header />
      
      <div className="min-h-screen py-20 px-4" style={{ background: 'var(--bg-section)' }}>
        <div className="max-w-3xl mx-auto">
          {/* Progress Section */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h2 className="heading-3">{getStepTitle()}</h2>
                <span className="body-small" style={{ color: 'var(--text-muted)' }}>
                  Step {currentStep} of {totalSteps}
                </span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </div>

          {/* Step Content */}
          <div className="bg-white rounded-lg shadow-sm p-6 md:p-8">
            {currentStep === 1 && (
              <PersonalInfoStep
                initialData={formData}
                onNext={handleNext}
              />
            )}
            
            {currentStep === 2 && (
              <EmploymentStep
                initialData={formData}
                onNext={handleNext}
                onBack={handleBack}
              />
            )}
            
            {currentStep === 3 && (
              <IdentityStep
                initialData={formData}
                onNext={handleNext}
                onBack={handleBack}
              />
            )}
          </div>

          {/* Privacy Notice */}
          <div className="mt-6 p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
            <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
              <strong>Privacy & Data Protection:</strong> Your information is encrypted and
              stored securely. We comply with all Nigerian data protection regulations and
              will only use your data for loan processing purposes. Your information will
              never be shared with third parties without your consent.
            </p>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default LoanApplicationPage;
