// src/pages/Careers.jsx
import './LegalPages.css';

export const Careers = () => {
  const openings = [
    { title: 'Senior Full Stack Developer', type: 'Full-time', location: 'Accra, Ghana' },
    { title: 'Product Manager', type: 'Full-time', location: 'Accra, Ghana' },
    { title: 'Customer Success Manager', type: 'Full-time', location: 'Remote' },
    { title: 'UI/UX Designer', type: 'Contract', location: 'Accra, Ghana' },
    { title: 'Sales Executive', type: 'Full-time', location: 'Accra, Ghana' },
  ];

  return (
    <div className="legal-page">
      <div className="container">
        <h1>Careers at ArtisanHub</h1>
        <div className="legal-content">
          <p>
            Join us in building the future of workforce management in Africa. We're looking for 
            passionate, talented individuals who want to make a difference.
          </p>
          <h2>Why Work With Us?</h2>
          <ul>
            <li>🚀 Work on impactful projects that transform industries</li>
            <li>🌍 Remote-first culture with offices in Accra</li>
            <li>💡 Innovative environment with cutting-edge technology</li>
            <li>📈 Growth opportunities and professional development</li>
            <li>🤝 Collaborative and inclusive team culture</li>
          </ul>
          <h2>Open Positions</h2>
          <div className="job-listings">
            {openings.map((job, index) => (
              <div key={index} className="job-card">
                <h3>{job.title}</h3>
                <p>{job.type} · {job.location}</p>
                <button className="btn btn--primary">Apply Now</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};