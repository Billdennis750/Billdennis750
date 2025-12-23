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

  const handleSubmit = (finalData) => {
    // Mock submission
    console.log('Submitting application:', finalData);
    
    // Store application in localStorage (mock)
    const applicationId = `LOAN-2025-${Math.floor(Math.random() * 1000)}`;
    const application = {
      id: applicationId,
      ...finalData,
      status: 'Pending Payment',
      createdAt: new Date().toISOString(),
    };
    
    localStorage.setItem('currentApplication', JSON.stringify(application));
    
    toast.success('Application submitted successfully!');
    
    // Redirect to payment page (mock payment gateway)
    setTimeout(() => {
      navigate(`/payment-callback?orderRef=${applicationId}&status=success`);
    }, 1000);
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
