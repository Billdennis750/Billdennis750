import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Progress } from '../components/ui/progress';
import { toast } from 'sonner';
import PersonalInfoStep from '../components/application/PersonalInfoStep';
import EmploymentStep from '../components/application/EmploymentStep';
import BankDetailsStep from '../components/application/BankDetailsStep';
import LoanPreferencesStep from '../components/application/LoanPreferencesStep';
import IdentityStep from '../components/application/IdentityStep';
import axios from 'axios';
import { CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoanApplicationPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    // Personal Info
    fullName: '',
    dateOfBirth: '',
    email: '',
    phone: '',
    secondaryPhone: '',
    relativePhone: '',
    homeTown: '',
    flatHouseNumber: '',
    residentialAddress: '',
    
    // Employment
    placeOfWork: '',
    employmentStatus: '',
    employmentDetails: '',
    monthlyIncome: '',
    loanReason: '',
    
    // Bank Details
    bankName: '',
    accountName: '',
    accountNumber: '',
    
    // Loan Preferences
    loanAmount: '',
    repaymentDuration: '',
    repaymentFrequency: '',
    repaymentEstimate: null,
    
    // Identity & Account
    nin: '',
    bvn: '',
    password: '',
    idCard: null,
    passport: null,
  });

  const totalSteps = 5;
  const progress = (currentStep / totalSteps) * 100;

  const handleNext = (data) => {
    setFormData({ ...formData, ...data });
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
      window.scrollTo(0, 0);
    } else {
      handleSubmit({ ...formData, ...data });
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo(0, 0);
    }
  };

  const handleSubmit = async (finalData) => {
    setIsSubmitting(true);
    try {
      // Create FormData for file upload
      const formDataObj = new FormData();
      
      // Personal Information
      formDataObj.append('full_name', finalData.fullName);
      formDataObj.append('date_of_birth', finalData.dateOfBirth);
      formDataObj.append('email', finalData.email);
      formDataObj.append('phone', finalData.phone);
      formDataObj.append('home_town', finalData.homeTown);
      formDataObj.append('residential_address', finalData.residentialAddress);
      
      // Employment & Income
      formDataObj.append('place_of_work', finalData.placeOfWork);
      formDataObj.append('employment_status', finalData.employmentStatus);
      formDataObj.append('employment_details', finalData.employmentDetails);
      formDataObj.append('monthly_income', finalData.monthlyIncome);
      formDataObj.append('loan_reason', finalData.loanReason);
      
      // Bank Details
      formDataObj.append('bank_name', finalData.bankName);
      formDataObj.append('account_name', finalData.accountName);
      formDataObj.append('account_number', finalData.accountNumber);
      
      // Loan Preferences
      formDataObj.append('loan_amount', finalData.loanAmount);
      formDataObj.append('repayment_duration', finalData.repaymentDuration);
      formDataObj.append('repayment_frequency', finalData.repaymentFrequency);
      
      // Identity
      formDataObj.append('nin', finalData.nin);
      formDataObj.append('bvn', finalData.bvn);
      
      // Password for account creation
      formDataObj.append('password', finalData.password);
      
      // Files
      if (finalData.idCard) {
        formDataObj.append('id_card', finalData.idCard);
      }
      if (finalData.passport) {
        formDataObj.append('passport', finalData.passport);
      }
      
      // Submit application
      const response = await axios.post(`${API}/applications/submit`, formDataObj, {
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
        customer_phone: finalData.phone,
        amount: 2500,
        redirect_url: `${window.location.origin}/payment-callback`
      });
      
      const { checkout_link, order_reference } = paymentResponse.data;
      
      // Store references for verification
      localStorage.setItem('order_reference', order_reference);
      localStorage.setItem('application_id', application_id);
      
      // Redirect to payment page
      window.location.href = checkout_link;
      
    } catch (error) {
      console.error('Application submission error:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit application');
      setIsSubmitting(false);
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1:
        return 'Personal Information';
      case 2:
        return 'Employment & Income Details';
      case 3:
        return 'Bank Account Details';
      case 4:
        return 'Loan & Repayment Preferences';
      case 5:
        return 'Identity & Account Creation';
      default:
        return '';
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 1:
        return 'Tell us about yourself';
      case 2:
        return 'Your employment and income information';
      case 3:
        return 'Where should we send your loan?';
      case 4:
        return 'Choose your loan amount and repayment plan';
      case 5:
        return 'Verify your identity and create your account';
      default:
        return '';
    }
  };

  const steps = [
    { num: 1, label: 'Personal' },
    { num: 2, label: 'Employment' },
    { num: 3, label: 'Bank' },
    { num: 4, label: 'Loan' },
    { num: 5, label: 'Identity' },
  ];

  return (
    <div>
      <Header />
      
      <div className="min-h-screen py-20 px-4" style={{ background: 'var(--bg-section)' }}>
        <div className="max-w-3xl mx-auto">
          {/* Progress Section */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            {/* Step Indicators */}
            <div className="flex justify-between mb-6">
              {steps.map((step) => (
                <div key={step.num} className="flex flex-col items-center">
                  <div 
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                      currentStep > step.num 
                        ? 'bg-green-500 text-white' 
                        : currentStep === step.num 
                          ? 'bg-green-600 text-white' 
                          : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {currentStep > step.num ? <CheckCircle className="w-5 h-5" /> : step.num}
                  </div>
                  <span className={`text-xs mt-1 hidden sm:block ${currentStep >= step.num ? 'text-green-600 font-medium' : 'text-gray-400'}`}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
            
            <Progress value={progress} className="h-2 mb-4" />
            
            <div className="text-center">
              <h2 className="heading-3">{getStepTitle()}</h2>
              <p className="body-small mt-1" style={{ color: 'var(--text-muted)' }}>
                {getStepDescription()} • Step {currentStep} of {totalSteps}
              </p>
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
              <BankDetailsStep
                initialData={formData}
                onNext={handleNext}
                onBack={handleBack}
              />
            )}
            
            {currentStep === 4 && (
              <LoanPreferencesStep
                initialData={formData}
                onNext={handleNext}
                onBack={handleBack}
              />
            )}
            
            {currentStep === 5 && (
              <IdentityStep
                initialData={formData}
                onNext={handleNext}
                onBack={handleBack}
              />
            )}
            
            {isSubmitting && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-8 text-center">
                  <div className="animate-spin w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p className="font-medium">Submitting your application...</p>
                  <p className="text-sm text-gray-500 mt-1">Please wait, do not close this page.</p>
                </div>
              </div>
            )}
          </div>

          {/* Fee Notice */}
          <div className="mt-6 p-4 rounded-lg border border-yellow-300 bg-yellow-50">
            <p className="body-small text-yellow-800">
              <strong>Processing Fee:</strong> A non-refundable ₦2,500 processing fee is required after form submission. 
              This fee is separate from your loan repayment.
            </p>
          </div>

          {/* Privacy Notice */}
          <div className="mt-4 p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
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
