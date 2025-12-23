import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { 
  ArrowLeft, 
  Target, 
  Eye, 
  Zap, 
  Shield, 
  Calendar, 
  CheckCircle,
  Heart,
  Users,
  TrendingUp,
} from 'lucide-react';

const AboutUsPage = () => {
  return (
    <div>
      <Header />

      <div className="min-h-screen py-20 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Back Link */}
          <Link to="/" className="inline-flex items-center body-medium mb-8" style={{ color: 'var(--accent-text)' }}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>

          {/* Header */}
          <div className="text-center mb-12">
            <Users className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
            <h1 className="heading-1 mb-4">About Us</h1>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Empowering Nigerians with Fast, Reliable, No-Collateral Loans
            </p>
          </div>

          {/* Who We Are */}
          <section className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="heading-2 mb-6">Who We Are</h2>
            <div className="space-y-4">
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                <strong>Cashflow Microfinance Bank (Cashflow MFB)</strong> is a customer-focused financial institution committed to providing fast, reliable, and accessible loan solutions to Nigerians. We exist to remove financial barriers and help individuals and businesses move forward with confidence—without the burden of collateral or unnecessary delays.
              </p>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                We understand that access to timely funding can make all the difference. That's why we have built a simple, transparent, and technology-driven lending platform designed to support growth, stability, and opportunity.
              </p>
            </div>
          </section>

          {/* What We Do */}
          <section className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="heading-2 mb-6">What We Do</h2>
            <p className="body-medium mb-6" style={{ color: 'var(--text-body)' }}>
              At Cashflow MFB, we offer <strong>collateral-free loans ranging from ₦1.5 million to ₦15 million</strong> to eligible Nigerians with a steady source of income. Our loan products are designed to support:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="p-6 rounded-lg text-center" style={{ background: 'var(--accent-wash)' }}>
                <TrendingUp className="w-10 h-10 mx-auto mb-3" style={{ color: 'var(--accent-text)' }} />
                <h3 className="heading-3 mb-2">Business Growth</h3>
                <p className="body-small">Expansion and working capital</p>
              </div>
              <div className="p-6 rounded-lg text-center" style={{ background: 'var(--accent-wash)' }}>
                <Target className="w-10 h-10 mx-auto mb-3" style={{ color: 'var(--accent-text)' }} />
                <h3 className="heading-3 mb-2">Personal Projects</h3>
                <p className="body-small">Life goals and aspirations</p>
              </div>
              <div className="p-6 rounded-lg text-center" style={{ background: 'var(--accent-wash)' }}>
                <Zap className="w-10 h-10 mx-auto mb-3" style={{ color: 'var(--accent-text)' }} />
                <h3 className="heading-3 mb-2">Urgent Needs</h3>
                <p className="body-small">Financial emergencies</p>
              </div>
            </div>
            <p className="body-medium" style={{ color: 'var(--text-body)' }}>
              Our process is straightforward, secure, and efficient—allowing customers to apply online, complete verification, and track their loan status from a personalized dashboard.
            </p>
          </section>

          {/* Mission & Vision */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-center space-x-3 mb-4">
                <Target className="w-8 h-8" style={{ color: 'var(--accent-text)' }} />
                <h2 className="heading-2">Our Mission</h2>
              </div>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                To empower Nigerians with quick and responsible access to finance through transparent, secure, and customer-centric loan solutions.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-center space-x-3 mb-4">
                <Eye className="w-8 h-8" style={{ color: 'var(--accent-text)' }} />
                <h2 className="heading-2">Our Vision</h2>
              </div>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                To become a trusted microfinance bank that drives financial inclusion and economic growth by making credit accessible, fair, and stress-free.
              </p>
            </div>
          </div>

          {/* Why Choose Cashflow MFB */}
          <section className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="heading-2 mb-6">Why Choose Cashflow MFB</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-4">
                <Zap className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <div>
                  <h3 className="heading-3 mb-1">Fast Approval</h3>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    Quick application and efficient decisioning
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Shield className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <div>
                  <h3 className="heading-3 mb-1">No Collateral Required</h3>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    All loans are unsecured
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <CheckCircle className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <div>
                  <h3 className="heading-3 mb-1">Transparent Process</h3>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    Clear terms with no hidden charges
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Calendar className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <div>
                  <h3 className="heading-3 mb-1">Flexible Repayment</h3>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    Options designed to suit different income structures
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Shield className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <div>
                  <h3 className="heading-3 mb-1">Secure & Regulated</h3>
                  <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
                    We operate in line with applicable CBN guidelines and prioritize customer data protection
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Trust & Transparency */}
          <section className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <Heart className="w-8 h-8" style={{ color: 'var(--accent-text)' }} />
              <h2 className="heading-2">Our Commitment to Trust & Transparency</h2>
            </div>
            <div className="space-y-4">
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                We believe trust is the foundation of every financial relationship. From clear communication to secure handling of personal information, we are committed to protecting our customers and maintaining the highest standards of integrity and professionalism.
              </p>
              <div className="p-6 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
                <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                  <strong>Processing Fee Disclosure:</strong> A fixed <strong>₦2,500 processing fee</strong> is required to complete the loan application. This fee covers verification and processing and does not guarantee loan approval. All terms are clearly communicated before payment is made.
                </p>
              </div>
            </div>
          </section>

          {/* Supporting You */}
          <section className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="heading-2 mb-6">Supporting You Every Step of the Way</h2>
            <p className="body-medium mb-4" style={{ color: 'var(--text-body)' }}>
              From application to repayment, our team is here to support you. Whether you are growing your business, managing personal goals, or navigating urgent needs, Cashflow MFB is ready to stand with you—every step of the journey.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <Link to="/apply">
                <button className="btn-primary">
                  Start Your Application
                </button>
              </Link>
              <Link to="/contact">
                <button className="btn-secondary">
                  Contact Us
                </button>
              </Link>
            </div>
          </section>

          {/* Bottom CTA */}
          <div className="text-center p-8 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
            <h3 className="heading-3 mb-4">Ready to Move Forward?</h3>
            <p className="body-medium mb-6" style={{ color: 'var(--text-secondary)' }}>
              Join thousands of Nigerians who trust Cashflow MFB for fast, reliable, no-collateral loans.
            </p>
            <Link to="/apply">
              <button className="btn-primary">
                Apply for a Loan Today
              </button>
            </Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default AboutUsPage;
