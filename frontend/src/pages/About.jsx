// src/pages/About.jsx
import './LegalPages.css';

export const About = () => {
  return (
    <div className="legal-page">
      <div className="container">
        <h1>About Us</h1>
        <div className="legal-content">
          <p>
            ArtisanHub is Ghana's premier incident management and workforce dispatch platform. 
            We connect call centers, dispatchers, and skilled artisans to resolve field incidents 
            faster and more efficiently than ever before.
          </p>
          <h2>Our Mission</h2>
          <p>
            To empower Africa's workforce with technology that streamlines communication, 
            improves response times, and creates economic opportunities for skilled professionals.
          </p>
          <h2>Our Vision</h2>
          <p>
            To become the leading workforce management platform across Africa, bridging the gap 
            between service providers and those who need them most.
          </p>
          <h2>Why ArtisanHub?</h2>
          <ul>
            <li><strong>Real-time Dispatching</strong> – Instant job assignments with live tracking</li>
            <li><strong>Verified Artisans</strong> – KYC-verified professionals you can trust</li>
            <li><strong>24/7 Support</strong> – Dedicated support team always available</li>
            <li><strong>Data-Driven Insights</strong> – Analytics to optimize your workforce</li>
          </ul>
        </div>
      </div>
    </div>
  );
};