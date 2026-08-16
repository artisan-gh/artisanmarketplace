// src/pages/Contact.jsx
import { useState } from 'react';
import { FaEnvelope, FaPhone, FaMapMarkerAlt } from 'react-icons/fa';
import './LegalPages.css';

export const Contact = () => {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission (connect to backend)
    setSubmitted(true);
  };

  return (
    <div className="legal-page">
      <div className="container">
        <h1>Contact Us</h1>
        <div className="contact-grid">
          <div className="contact-info">
            <h2>Get in Touch</h2>
            <p>
              Have questions, feedback, or want to learn more about ArtisanHub? 
              We'd love to hear from you.
            </p>
            <div className="contact-details">
              <div className="contact-item">
                <FaEnvelope />
                <span>hello@artisanhub.com</span>
              </div>
              <div className="contact-item">
                <FaPhone />
                <span>+233 50 123 4567</span>
              </div>
              <div className="contact-item">
                <FaMapMarkerAlt />
                <span>Accra, Ghana</span>
              </div>
            </div>
          </div>
          <div className="contact-form-wrapper">
            {submitted ? (
              <div className="success-message">
                <h3>Thank you!</h3>
                <p>Your message has been sent. We'll get back to you soon.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="contact-form">
                <input
                  type="text"
                  name="name"
                  placeholder="Your Name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
                <input
                  type="email"
                  name="email"
                  placeholder="Your Email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
                <textarea
                  name="message"
                  placeholder="Your Message"
                  rows="5"
                  value={formData.message}
                  onChange={handleChange}
                  required
                />
                <button type="submit" className="btn btn--primary">
                  Send Message
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};