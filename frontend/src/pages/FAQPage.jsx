import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';

const faqs = [
  {
    question: "What is Cashflow MFB?",
    answer: "Cashflow MFB is a licensed microfinance bank regulated by the Central Bank of Nigeria. We provide fast, collateral-free loans to Nigerians with steady income sources, including salary earners, business owners, and self-employed professionals."
  },
  {
    question: "How much can I borrow?",
    answer: "You can borrow between ₦1,000,000 (₦1M) and ₦100,000,000 (₦100M) depending on your income, employment status, and creditworthiness. First-time borrowers may start with lower amounts and increase with successful repayment history."
  },
  {
    question: "Do I need collateral to get a loan?",
    answer: "No! All our loans are 100% unsecured. You don't need to pledge any assets, property, or guarantors to access our loan facilities."
  },
  {
    question: "What are the eligibility requirements?",
    answer: "To be eligible, you must: (1) Be a Nigerian citizen or resident, (2) Be at least 18 years old, (3) Have a valid government-issued ID (NIN/BVN), (4) Have a steady source of income (salary, business, or self-employment), (5) Have an active bank account in your name."
  },
  {
    question: "How long does the approval process take?",
    answer: "Our approval process is fast. Once you submit your application and pay the ₦2,500 processing fee, your application is reviewed within 24 hours. Approved applicants receive their funds within 24 hours after paying the ₦3,000 fixed deposit."
  },
  {
    question: "What is the ₦2,500 processing fee?",
    answer: "The ₦2,500 is a non-refundable processing fee required to submit your loan application for review. This fee covers administrative and verification costs."
  },
  {
    question: "What is the ₦3,000 fixed deposit?",
    answer: "After your loan is approved, you'll need to pay a ₦3,000 fixed deposit before disbursement. This deposit demonstrates your commitment and is a standard practice in microfinance lending."
  },
  {
    question: "What are the repayment options?",
    answer: "We offer flexible repayment plans to match your income cycle: Weekly payments (ideal for weekly income earners), Bi-weekly payments (for those paid twice a month), and Monthly payments (for monthly salary earners). You can choose a repayment duration of 3, 6, 9, or 12 months."
  },
  {
    question: "What is the interest rate?",
    answer: "Our interest rate is 5% per month on the loan principal. The total interest is calculated based on your chosen repayment duration. All charges are transparently displayed before you accept the loan."
  },
  {
    question: "Can I repay my loan early?",
    answer: "Yes! Early repayment is encouraged and there are no penalties for paying off your loan before the due date. Contact us to arrange early settlement."
  },
  {
    question: "What happens if I miss a payment?",
    answer: "We understand that financial situations can change. If you anticipate difficulty making a payment, please contact us immediately. Late payments may attract additional charges and affect your credit score. We'll work with you to find a solution."
  },
  {
    question: "How do I make repayments?",
    answer: "Repayments can be made via bank transfer to our designated account, through our online payment portal, or via USSD banking. You'll receive payment reminders before each due date."
  },
  {
    question: "Is my personal information secure?",
    answer: "Absolutely. We use bank-grade encryption and security measures to protect your data. Your information is stored securely and will never be shared with third parties without your consent. We comply with Nigerian data protection regulations."
  },
  {
    question: "How can I check my loan status?",
    answer: "You can log into your account dashboard at any time to view your application status, repayment schedule, outstanding balance, and payment history."
  },
  {
    question: "What documents do I need to apply?",
    answer: "You'll need: (1) Valid government-issued ID card, (2) Passport photograph, (3) NIN (National Identification Number), (4) BVN (Bank Verification Number), (5) Bank account details for disbursement."
  },
  {
    question: "Can I apply for another loan after repaying my current one?",
    answer: "Yes! Once you've fully repaid your current loan, you become eligible for a new loan. Repeat customers with good repayment history may qualify for higher loan amounts and better terms."
  },
  {
    question: "How do I contact customer support?",
    answer: "You can reach us via email at payment@cashflowsmfb.com, call us at +234 800 CASHFLOW, or visit our office in Lagos. Our support team is available Monday to Friday, 8am to 6pm, and Saturday 9am to 2pm."
  }
];

const FAQItem = ({ faq, isOpen, onToggle }) => {
  return (
    <div className="border-b" style={{ borderColor: 'var(--border-light)' }}>
      <button
        className="w-full py-5 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors px-4 rounded-lg"
        onClick={onToggle}
      >
        <span className="heading-3 pr-4">{faq.question}</span>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--accent-text)' }} />
        ) : (
          <ChevronDown className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--text-muted)' }} />
        )}
      </button>
      {isOpen && (
        <div className="pb-5 px-4">
          <p className="body-medium" style={{ color: 'var(--text-secondary)' }}>
            {faq.answer}
          </p>
        </div>
      )}
    </div>
  );
};

const FAQPage = () => {
  const [openIndex, setOpenIndex] = useState(0);

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? -1 : index);
  };

  return (
    <div>
      <Header />
      
      {/* Hero Section */}
      <section className="py-20 px-4" style={{ background: 'var(--accent-wash)' }}>
        <div className="max-w-4xl mx-auto text-center">
          <HelpCircle className="w-16 h-16 mx-auto mb-6" style={{ color: 'var(--accent-text)' }} />
          <h1 className="heading-1 mb-4">Frequently Asked Questions</h1>
          <p className="body-large" style={{ color: 'var(--text-secondary)' }}>
            Everything you need to know about Cashflow MFB loans
          </p>
        </div>
      </section>

      {/* FAQ List */}
      <section className="py-16 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm">
            {faqs.map((faq, index) => (
              <FAQItem
                key={index}
                faq={faq}
                isOpen={openIndex === index}
                onToggle={() => toggleFAQ(index)}
              />
            ))}
          </div>

          {/* Still Have Questions */}
          <div className="mt-12 text-center p-8 rounded-lg" style={{ background: 'var(--bg-section)' }}>
            <h2 className="heading-2 mb-4">Still Have Questions?</h2>
            <p className="body-medium mb-6" style={{ color: 'var(--text-secondary)' }}>
              Can't find the answer you're looking for? Our support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="mailto:payment@cashflowsmfb.com">
                <button className="btn-primary">Email Support</button>
              </a>
              <a href="tel:+2348000000000">
                <button className="btn-secondary">Call Us</button>
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default FAQPage;
