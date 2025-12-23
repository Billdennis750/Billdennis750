import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer style={{ background: 'var(--bg-section)', borderTop: '1px solid var(--border-light)' }}>
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h3 className="heading-3 mb-4">Cashflow MFB</h3>
            <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
              Fast, reliable, no-collateral loans for Nigerians with steady income.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Quick Links
            </h4>
            <ul className="space-y-2">
              <li>
                <a href="#about" className="body-small hover:text-green-600">
                  About Us
                </a>
              </li>
              <li>
                <a href="#why-choose-us" className="body-small hover:text-green-600">
                  Why Choose Us
                </a>
              </li>
              <li>
                <a href="#repayment" className="body-small hover:text-green-600">
                  Repayment Plans
                </a>
              </li>
              <li>
                <a href="#contact" className="body-small hover:text-green-600">
                  Contact
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Legal
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy-policy" className="body-small hover:text-green-600">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <a href="#" className="body-small hover:text-green-600">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="body-small hover:text-green-600">
                  Data Protection
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Contact Us
            </h4>
            <ul className="space-y-3">
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4" style={{ color: 'var(--accent-text)' }} />
                <span className="body-small">support@cashflowmfb.ng</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" style={{ color: 'var(--accent-text)' }} />
                <span className="body-small">+234 800 CASHFLOW</span>
              </li>
              <li className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" style={{ color: 'var(--accent-text)' }} />
                <span className="body-small">Lagos, Nigeria</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-8 pt-8 border-t" style={{ borderColor: 'var(--border-light)' }}>
          <p className="body-small text-center" style={{ color: 'var(--text-muted)' }}>
            © 2025 Cashflow MFB. Licensed and regulated by the Central Bank of Nigeria.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
