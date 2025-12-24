import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { ArrowLeft, Shield, Lock, Eye, FileText } from 'lucide-react';

const PrivacyPolicyPage = () => {
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
            <Shield className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--accent-text)' }} />
            <h1 className="heading-1 mb-4">Privacy Policy</h1>
            <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
              Cashflow Microfinance Bank
            </p>
            <p className="body-small mt-2" style={{ color: 'var(--text-muted)' }}>
              Effective Date: January 1, 2025
            </p>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg shadow-sm p-8 space-y-8">
            {/* Introduction */}
            <section>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                Cashflow Microfinance Bank (&quot;Cashflow MFB&quot;, &quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, store, share, and protect your information when you use our website, loan application platform, and related services.
              </p>
              <p className="body-medium mt-4" style={{ color: 'var(--text-body)' }}>
                By accessing or using our services, you agree to the collection and use of your information as described in this Privacy Policy.
              </p>
            </section>

            {/* Section 1 */}
            <section>
              <h2 className="heading-2 mb-4">1. Information We Collect</h2>
              <p className="body-medium mb-4" style={{ color: 'var(--text-body)' }}>
                We collect personal and sensitive information necessary to process loan applications, verify identity, comply with regulatory requirements, and provide our services.
              </p>
              
              <div className="space-y-4">
                <div>
                  <h3 className="heading-3 mb-2">a. Personal Information</h3>
                  <ul className="list-disc list-inside space-y-1 body-medium" style={{ color: 'var(--text-body)' }}>
                    <li>Full name</li>
                    <li>Date of birth</li>
                    <li>Email address</li>
                    <li>Phone number</li>
                    <li>Home town</li>
                    <li>Residential address</li>
                  </ul>
                </div>

                <div>
                  <h3 className="heading-3 mb-2">b. Employment & Financial Information</h3>
                  <ul className="list-disc list-inside space-y-1 body-medium" style={{ color: 'var(--text-body)' }}>
                    <li>Place of work</li>
                    <li>Employment status and details</li>
                    <li>Monthly income</li>
                    <li>Reason for loan application</li>
                  </ul>
                </div>

                <div>
                  <h3 className="heading-3 mb-2">c. Identity & Verification Information</h3>
                  <ul className="list-disc list-inside space-y-1 body-medium" style={{ color: 'var(--text-body)' }}>
                    <li>National Identification Number (NIN)</li>
                    <li>Bank Verification Number (BVN)</li>
                    <li>Government-issued ID card</li>
                    <li>Passport photograph</li>
                  </ul>
                </div>

                <div>
                  <h3 className="heading-3 mb-2">d. Payment Information</h3>
                  <ul className="list-disc list-inside space-y-1 body-medium" style={{ color: 'var(--text-body)' }}>
                    <li>Proof of payment of the ₦2,500 processing fee</li>
                    <li>Transaction references from our payment gateway</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Section 2 */}
            <section>
              <h2 className="heading-2 mb-4">2. How We Use Your Information</h2>
              <p className="body-medium mb-3" style={{ color: 'var(--text-body)' }}>
                We use your information for the following purposes:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>To process and evaluate loan applications</li>
                <li>To verify your identity and prevent fraud</li>
                <li>To comply with CBN and other regulatory requirements</li>
                <li>To create and manage your user account and dashboard</li>
                <li>To communicate with you regarding your application status</li>
                <li>To provide customer support and respond to inquiries</li>
                <li>To improve our website, services, and user experience</li>
              </ul>
            </section>

            {/* Section 3 */}
            <section className="p-6 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
              <h2 className="heading-2 mb-4">3. Processing Fee Disclosure</h2>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                As part of the loan application process, applicants are required to pay a fixed <strong>₦2,500 processing fee</strong>.
              </p>
              <p className="body-medium mt-2" style={{ color: 'var(--text-body)' }}>
                This fee covers application processing, verification, and account setup. <strong>Payment of this fee does not guarantee loan approval.</strong>
              </p>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="heading-2 mb-4">4. Data Sharing & Disclosure</h2>
              <p className="body-medium mb-3" style={{ color: 'var(--text-body)' }}>
                We do not sell or rent your personal information.
              </p>
              <p className="body-medium mb-2" style={{ color: 'var(--text-body)' }}>
                We may share your information only when necessary with:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>Licensed payment gateway providers</li>
                <li>Identity verification and compliance partners</li>
                <li>Regulatory authorities, where required by law</li>
                <li>Service providers assisting us in operating our platform under strict confidentiality agreements</li>
              </ul>
            </section>

            {/* Section 5 */}
            <section>
              <div className="flex items-start space-x-3 mb-4">
                <Lock className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <h2 className="heading-2">5. Data Security</h2>
              </div>
              <p className="body-medium mb-3" style={{ color: 'var(--text-body)' }}>
                We implement appropriate technical and organizational security measures to protect your information, including:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>Secure servers and encrypted data storage</li>
                <li>Restricted access to personal data</li>
                <li>Secure document upload systems</li>
              </ul>
              <p className="body-medium mt-3" style={{ color: 'var(--text-body)' }}>
                Despite our efforts, no method of transmission over the internet is 100% secure. We encourage users to protect their login credentials.
              </p>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="heading-2 mb-4">6. Data Retention</h2>
              <p className="body-medium mb-2" style={{ color: 'var(--text-body)' }}>
                We retain your personal information only for as long as necessary to:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>Fulfill the purposes outlined in this Privacy Policy</li>
                <li>Comply with legal, regulatory, and reporting obligations</li>
              </ul>
              <p className="body-medium mt-3" style={{ color: 'var(--text-body)' }}>
                When data is no longer required, it is securely deleted or anonymized.
              </p>
            </section>

            {/* Section 7 */}
            <section>
              <div className="flex items-start space-x-3 mb-4">
                <Eye className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <h2 className="heading-2">7. Your Rights</h2>
              </div>
              <p className="body-medium mb-2" style={{ color: 'var(--text-body)' }}>
                You have the right to:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>Request access to your personal information</li>
                <li>Request correction of inaccurate data</li>
                <li>Request deletion of your data, subject to legal obligations</li>
                <li>Withdraw consent where applicable</li>
              </ul>
              <p className="body-medium mt-3" style={{ color: 'var(--text-body)' }}>
                Requests can be made through our official support channels.
              </p>
            </section>

            {/* Section 8 */}
            <section>
              <h2 className="heading-2 mb-4">8. Cookies & Tracking</h2>
              <p className="body-medium mb-2" style={{ color: 'var(--text-body)' }}>
                Our website may use cookies and similar technologies to:
              </p>
              <ul className="list-disc list-inside space-y-2 body-medium" style={{ color: 'var(--text-body)' }}>
                <li>Improve functionality and performance</li>
                <li>Enhance user experience</li>
                <li>Analyze traffic and usage patterns</li>
              </ul>
              <p className="body-medium mt-3" style={{ color: 'var(--text-body)' }}>
                You may disable cookies in your browser settings, but this may affect site functionality.
              </p>
            </section>

            {/* Section 9 */}
            <section>
              <h2 className="heading-2 mb-4">9. Third-Party Links</h2>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                Our website may contain links to third-party websites. Cashflow MFB is not responsible for the privacy practices or content of those external sites.
              </p>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="heading-2 mb-4">10. Changes to This Privacy Policy</h2>
              <p className="body-medium" style={{ color: 'var(--text-body)' }}>
                We may update this Privacy Policy from time to time. Any changes will be posted on this page, and continued use of our services constitutes acceptance of the updated policy.
              </p>
            </section>

            {/* Section 11 */}
            <section className="p-6 rounded-lg" style={{ background: 'var(--bg-section)' }}>
              <div className="flex items-start space-x-3 mb-4">
                <FileText className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: 'var(--accent-text)' }} />
                <h2 className="heading-2">11. Contact Us</h2>
              </div>
              <p className="body-medium mb-4" style={{ color: 'var(--text-body)' }}>
                If you have questions, concerns, or requests regarding this Privacy Policy or how your data is handled, please contact us through our official support channels.
              </p>
              <div className="space-y-2">
                <p className="body-medium font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Cashflow Microfinance Bank (Cashflow MFB)
                </p>
                <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                  Fast. Reliable. No-Collateral Financing.
                </p>
                <div className="flex flex-col space-y-1 mt-3">
                  <a href="mailto:support@cashflowmfb.ng" className="body-small hover:text-green-600">
                    Email: support@cashflowmfb.ng
                  </a>
                  <a href="tel:+2348000000000" className="body-small hover:text-green-600">
                    Phone: +234 800 CASHFLOW
                  </a>
                </div>
              </div>
            </section>
          </div>

          {/* Bottom CTA */}
          <div className="mt-12 text-center">
            <p className="body-medium mb-4" style={{ color: 'var(--text-secondary)' }}>
              Ready to apply for a loan?
            </p>
            <Link to="/apply">
              <button className="btn-primary">
                Start Your Application
              </button>
            </Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default PrivacyPolicyPage;
