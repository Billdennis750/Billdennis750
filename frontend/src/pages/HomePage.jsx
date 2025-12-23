import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import {
  Zap,
  Shield,
  Calendar,
  CheckCircle,
  ArrowRight,
  Clock,
  BadgeCheck,
  Users,
} from 'lucide-react';
import { mockPartners } from '../mock';

const HomePage = () => {
  return (
    <div>
      <Header />

      {/* Hero Section */}
      <section className="hero-gradient min-h-screen flex items-center justify-center pt-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="heading-1 mb-6">
            Get ₦1.5M – ₦15M.
            <br />
            No Collateral. No Stress.
          </h1>
          <p className="body-large mb-8" style={{ color: 'var(--text-secondary)' }}>
            Money shouldn't slow you down. We give you fast loans with zero
            collateral. Straightforward. Quick. Reliable.
          </p>
          <div className="flex flex-col gap-6 items-center justify-center max-w-2xl mx-auto">
            <Link to="/apply" className="w-full">
              <button 
                className="w-full text-white text-xl font-bold py-6 px-12 rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3"
                style={{ 
                  background: 'linear-gradient(135deg, #8FEC78 0%, #81DD67 100%)',
                  boxShadow: '0 10px 40px rgba(143, 236, 120, 0.4), 0 0 20px rgba(143, 236, 120, 0.2)',
                  minHeight: '80px'
                }}
              >
                <span>Apply Now</span>
                <ArrowRight className="w-6 h-6" />
              </button>
            </Link>
            <a href="#why-choose-us" className="w-full">
              <button 
                className="w-full text-xl font-semibold py-6 px-12 rounded-full border-2 hover:bg-gray-50 transition-all duration-300 flex items-center justify-center space-x-3"
                style={{ 
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(10px)',
                  borderColor: 'rgba(0, 0, 0, 0.1)',
                  color: 'var(--text-primary)',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                  minHeight: '80px'
                }}
              >
                <span>Learn More</span>
              </button>
            </a>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-3"
                   style={{ background: 'var(--accent-wash)' }}>
                <Clock className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-2">Fast Approval</h3>
              <p className="body-small">Get approved in 24 hours</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-3"
                   style={{ background: 'var(--accent-wash)' }}>
                <Shield className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-2">No Collateral</h3>
              <p className="body-small">100% unsecured loans</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-3"
                   style={{ background: 'var(--accent-wash)' }}>
                <BadgeCheck className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-2">CBN Regulated</h3>
              <p className="body-small">Fully licensed & compliant</p>
            </div>
          </div>
        </div>
      </section>

      {/* Loan Overview Section */}
      <section id="about" className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Loan Overview</h2>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Simple, transparent lending with no hidden charges
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="product-card">
              <h3 className="heading-3 mb-2">₦50k – ₦15M</h3>
              <p className="body-small">Loan Amount Range</p>
            </div>
            <div className="product-card">
              <h3 className="heading-3 mb-2">No Collateral</h3>
              <p className="body-small">100% unsecured loans</p>
            </div>
            <div className="product-card">
              <h3 className="heading-3 mb-2">Transparent Rates</h3>
              <p className="body-small">No hidden charges</p>
            </div>
            <div className="product-card">
              <h3 className="heading-3 mb-2">Fast Disbursement</h3>
              <p className="body-small">Quick approval & transfer</p>
            </div>
          </div>
        </div>
      </section>

      {/* Who Can Apply Section */}
      <section style={{ background: 'var(--bg-section)' }} className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Who Can Apply</h2>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              We serve Nigerians with a steady source of income
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-4">
              <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
              <div>
                <h3 className="heading-3 mb-2">Salary Earners</h3>
                <p className="body-small">Employed professionals with regular income</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
              <div>
                <h3 className="heading-3 mb-2">Business Owners</h3>
                <p className="body-small">Entrepreneurs with steady cashflow</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
              <div>
                <h3 className="heading-3 mb-2">Self-Employed</h3>
                <p className="body-small">Professionals with consistent income</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
              <div>
                <h3 className="heading-3 mb-2">Simple Process</h3>
                <p className="body-small">Straightforward application with fast review</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Cashflow MFB Section */}
      <section id="why-choose-us" className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Why Choose Cashflow MFB</h2>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Your trusted partner for financial growth
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="product-card">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                   style={{ background: 'var(--accent-wash)' }}>
                <Zap className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-3">Fast Approval</h3>
              <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                Quick application and instant decisioning. Get your funds within 24 hours of approval.
              </p>
            </div>

            <div className="product-card">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                   style={{ background: 'var(--accent-wash)' }}>
                <Shield className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-3">No Collateral Required</h3>
              <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                All loans are completely unsecured. No need to pledge assets or property.
              </p>
            </div>

            <div className="product-card">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                   style={{ background: 'var(--accent-wash)' }}>
                <Calendar className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-3">Flexible Repayment Plans</h3>
              <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                Choose weekly, bi-weekly, or monthly repayment structured to match your income.
              </p>
            </div>

            <div className="product-card">
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                   style={{ background: 'var(--accent-wash)' }}>
                <BadgeCheck className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
              </div>
              <h3 className="heading-3 mb-3">Trusted & Regulated</h3>
              <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                Fully compliant with CBN regulatory standards and customer protection policies.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Repayment Options Section */}
      <section id="repayment" style={{ background: 'var(--bg-section)' }} className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Flexible Repayment Options</h2>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Choose a plan that works for your cashflow
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="product-card text-center">
              <Calendar className="w-10 h-10 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
              <h3 className="heading-3 mb-3">Weekly</h3>
              <p className="body-small mb-4">Perfect for weekly income earners</p>
              <Link to="/apply">
                <button className="btn-secondary">Learn More</button>
              </Link>
            </div>

            <div className="product-card text-center">
              <Calendar className="w-10 h-10 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
              <h3 className="heading-3 mb-3">Bi-Weekly</h3>
              <p className="body-small mb-4">Ideal for bi-monthly salary payments</p>
              <Link to="/apply">
                <button className="btn-secondary">Learn More</button>
              </Link>
            </div>

            <div className="product-card text-center">
              <Calendar className="w-10 h-10 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
              <h3 className="heading-3 mb-3">Monthly</h3>
              <p className="body-small mb-4">Best for monthly income cycles</p>
              <Link to="/apply">
                <button className="btn-secondary">Learn More</button>
              </Link>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link to="/apply">
              <button className="btn-primary">
                Apply Now <ArrowRight className="w-4 h-4 ml-2 inline" />
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Partners Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Trusted Partners</h2>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Working with leading institutions
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {mockPartners.map((partner, index) => (
              <div
                key={index}
                className="flex items-center justify-center p-6 rounded-lg"
                style={{ background: 'var(--bg-section)' }}
              >
                <img
                  src={partner.logo}
                  alt={partner.name}
                  className="max-w-full h-auto opacity-60 hover:opacity-100 transition-opacity"
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 px-4" style={{ background: 'var(--accent-wash)' }}>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="heading-2 mb-4">Apply Now and Get the Funding You Need</h2>
          <p className="body-large mb-8" style={{ color: 'var(--text-secondary)' }}>
            Your goals deserve the right support. Whether you're growing your business,
            handling urgent needs, or securing new opportunities, Cashflow MFB is ready
            to back you with fast, reliable, no-collateral financing.
          </p>
          <Link to="/apply">
            <button className="btn-primary">
              Start Your Application <ArrowRight className="w-5 h-5 ml-2 inline" />
            </button>
          </Link>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <Users className="w-16 h-16 mx-auto mb-6" style={{ color: 'var(--accent-text)' }} />
          <h2 className="heading-2 mb-4">We're Here to Help</h2>
          <p className="body-large mb-8" style={{ color: 'var(--text-secondary)' }}>
            We're here to support you every step of the way. Whether you have questions
            about our loan products, need assistance with your application, or want to
            speak with a representative, our team is always ready to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="mailto:support@cashflowmfb.ng">
              <button className="btn-primary">Contact Support</button>
            </a>
            <a href="tel:+2348000000000">
              <button className="btn-secondary">Call Us Now</button>
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default HomePage;
