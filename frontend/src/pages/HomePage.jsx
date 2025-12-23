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
  Star,
  Calculator,
  TrendingUp,
  Target,
} from 'lucide-react';
import { mockPartners } from '../mock';

const HomePage = () => {
  return (
    <div>
      <Header />

      {/* Hero Section with Gradient */}
      <section 
        className="min-h-screen flex items-center justify-center pt-24 pb-16 px-4"
        style={{
          background: 'radial-gradient(at 53% 78%, hsla(60,100%,50%,0.2) 0px, transparent 50%), radial-gradient(at 71% 91%, hsla(108,100%,50%,0.2) 0px, transparent 50%), radial-gradient(at 31% 91%, hsla(30,100%,50%,0.15) 0px, transparent 50%), white'
        }}
      >
        <div className="max-w-4xl mx-auto text-center">
          {/* Trust Badge */}
          <div className="inline-flex items-center space-x-2 mb-8 px-6 py-3 rounded-full" style={{ background: 'var(--accent-wash)', border: '1px solid var(--accent-strong)' }}>
            <BadgeCheck className="w-5 h-5" style={{ color: 'var(--accent-text)' }} />
            <span className="body-small font-semibold" style={{ color: 'var(--accent-text)' }}>
              CBN Regulated & Licensed
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="heading-1 mb-6" style={{ fontSize: 'clamp(2.5rem, 6vw, 5rem)', lineHeight: '1.1' }}>
            Get ₦1.5M – ₦15M.
            <br />
            <span style={{ color: 'var(--text-primary)' }}>No Collateral.</span>{' '}
            <span style={{ color: 'var(--accent-text)' }}>No Stress.</span>
          </h1>

          {/* Subheadline */}
          <p className="body-large mb-8 max-w-2xl mx-auto" style={{ color: 'var(--text-secondary)', fontSize: 'clamp(1.125rem, 2.5vw, 1.375rem)' }}>
            Money shouldn't slow you down. We give you fast loans with zero
            collateral. <strong>Straightforward. Quick. Reliable.</strong>
          </p>

          {/* Key Benefits */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 max-w-3xl mx-auto">
            <div className="flex items-center justify-center md:justify-start space-x-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'var(--accent-primary)' }}>
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <p className="body-medium font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Approval in 24-48 hours
                </p>
              </div>
            </div>

            <div className="flex items-center justify-center md:justify-start space-x-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'var(--accent-primary)' }}>
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <p className="body-medium font-semibold" style={{ color: 'var(--text-primary)' }}>
                  100% Collateral-Free
                </p>
              </div>
            </div>

            <div className="flex items-center justify-center md:justify-start space-x-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'var(--accent-primary)' }}>
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <p className="body-medium font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Flexible Repayment
                </p>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link to="/apply">
              <button 
                className="btn-primary text-lg px-8 py-4 font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
                style={{ 
                  minWidth: '200px',
                  background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-strong))'
                }}
              >
                Apply Now <ArrowRight className="w-5 h-5 ml-2 inline" />
              </button>
            </Link>
            <Link to="/apply">
              <button 
                className="btn-secondary text-lg px-8 py-4 font-semibold hover:bg-gray-50 transition-all"
                style={{ minWidth: '200px' }}
              >
                <Calculator className="w-5 h-5 mr-2 inline" />
                Calculate Your Loan
              </button>
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-4">
            <div className="flex items-center space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star key={star} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
              ))}
            </div>
            <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
              Trusted by over <strong style={{ color: 'var(--text-primary)' }}>10,000+ Nigerians</strong>
            </p>
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
