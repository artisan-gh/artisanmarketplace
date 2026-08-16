// src/pages/HelpCenter.jsx
import './LegalPages.css';

export const HelpCenter = () => {
  const faqs = [
    {
      q: 'How do I sign up as an artisan?',
      a: 'Go to the registration page, select "Artisan", and complete your profile with your skills, experience, and verification documents.',
    },
    {
      q: 'How are payments processed?',
      a: 'Payments are processed securely through our platform. Customers pay online, and artisans receive their earnings after job completion.',
    },
    {
      q: 'What if I have a dispute with a customer?',
      a: 'Our support team will mediate disputes. You can submit a complaint through your dashboard, and we\'ll investigate and resolve it.',
    },
    {
      q: 'How do I update my service area?',
      a: 'Go to your profile settings and update your service area preferences. You can add multiple locations.',
    },
    {
      q: 'Is there a mobile app?',
      a: 'Yes, we have mobile apps for both iOS and Android. Download them from the App Store or Google Play Store.',
    },
  ];

  return (
    <div className="legal-page">
      <div className="container">
        <h1>Help Center</h1>
        <div className="legal-content">
          <p>Find answers to common questions about using ArtisanHub.</p>
          <div className="faq-section">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <h3>{faq.q}</h3>
                <p>{faq.a}</p>
              </div>
            ))}
          </div>
          <div className="help-actions">
            <p>Still need help? <a href="/contact">Contact our support team</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};