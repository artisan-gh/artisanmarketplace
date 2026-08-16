// src/pages/TermsOfService.jsx
import './LegalPages.css';

export const TermsOfService = () => {
  return (
    <div className="legal-page">
      <div className="container">
        <h1>Terms of Service</h1>
        <div className="legal-content">
          <p><em>Last updated: January 1, 2025</em></p>

          <h2>1. Acceptance of Terms</h2>
          <p>
            By using ArtisanHub, you agree to these Terms of Service. If you do not agree, 
            please do not use the platform.
          </p>

          <h2>2. User Accounts</h2>
          <p>
            You must create an account to use our services. You are responsible for maintaining 
            the security of your account and for all activities that occur under your account.
          </p>

          <h2>3. Services</h2>
          <p>
            ArtisanHub connects customers with independent service providers. We facilitate 
            bookings, payments, and communication but are not responsible for the quality of 
            work performed by artisans.
          </p>

          <h2>4. Payments</h2>
          <p>
            Payments are processed securely through our platform. Refunds and cancellations 
            follow our published refund policy.
          </p>

          <h2>5. User Conduct</h2>
          <p>
            Users must treat others respectfully, provide accurate information, and comply with 
            all applicable laws. Prohibited conduct includes fraud, harassment, and misuse of 
            the platform.
          </p>

          <h2>6. Termination</h2>
          <p>
            We may suspend or terminate accounts for violation of these terms or for any other 
            reason at our discretion.
          </p>

          <h2>7. Limitation of Liability</h2>
          <p>
            ArtisanHub is provided "as is" without warranties. We are not liable for any damages 
            arising from your use of the platform.
          </p>

          <h2>8. Changes to Terms</h2>
          <p>
            We may update these terms from time to time. Continued use of the platform constitutes 
            acceptance of the updated terms.
          </p>

          <h2>9. Contact</h2>
          <p>
            For questions about these terms, contact us at legal@artisanhub.com.
          </p>
        </div>
      </div>
    </div>
  );
};