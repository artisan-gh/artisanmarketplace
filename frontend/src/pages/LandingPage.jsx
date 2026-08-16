// src/pages/LandingPage.jsx
import { useState, useEffect, useRef, useCallback } from 'react';
import {
  FaShieldAlt,
  FaHeadset,
  FaUsers,
  FaRocket,
  FaArrowRight,
  FaStar,
  FaQuoteLeft,
  FaBars,
  FaTimes,
  FaGithub,
  FaTwitter,
  FaLinkedin,
  FaYoutube,
} from 'react-icons/fa';
import { Link } from 'react-router-dom';
import './LandingPage.css';

export const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const statsRef = useRef(null);
  const [counts, setCounts] = useState({ artisans: 0, incidents: 0, satisfaction: 0 });

  // ─── Scroll effects ──────────────────────────────────────────────
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // ─── Stats counter animation ────────────────────────────────────
  const animateCounts = useCallback(() => {
    const targets = [8500, 12450, 98];
    const durations = [2000, 2000, 1500];

    targets.forEach((target, idx) => {
      const key = ['artisans', 'incidents', 'satisfaction'][idx];
      let start = 0;
      const step = Math.max(1, Math.floor(target / 60));
      const interval = setInterval(() => {
        start += step;
        if (start >= target) {
          start = target;
          clearInterval(interval);
        }
        setCounts((prev) => ({ ...prev, [key]: start }));
      }, durations[idx] / 60);
    });
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          animateCounts();
        }
      },
      { threshold: 0.3 }
    );

    if (statsRef.current) {
      observer.observe(statsRef.current);
    }

    return () => observer.disconnect();
  }, [animateCounts]);

  // ─── Testimonials ──────────────────────────────────────────────────
  const testimonials = [
    {
      id: 1,
      name: 'Sarah Kwame',
      role: 'Call Center Manager',
      content:
        'This platform transformed how we handle field incidents. Response times dropped by 60% and our artisans love the mobile experience.',
      avatar: 'S',
      rating: 5,
    },
    {
      id: 2,
      name: 'James Osei',
      role: 'Master Artisan',
      content:
        'I receive real-time job alerts, track my earnings, and communicate directly with dispatchers. It’s a game-changer for my business.',
      avatar: 'J',
      rating: 5,
    },
    {
      id: 3,
      name: 'Najahatu Asam Moro',
      role: 'Operations Director',
      content:
        'The analytics dashboard gives us complete visibility into our workforce. We’ve scaled from 50 to 200 artisans in just 6 months.',
      avatar: 'N',
      rating: 5,
    },
  ];

  // ─── Features ──────────────────────────────────────────────────────
  const features = [
    {
      icon: <FaRocket />,
      title: 'Real-time Dispatching',
      desc: 'Instant job assignments with live tracking and automated routing to the nearest available artisan.',
    },
    {
      icon: <FaShieldAlt />,
      title: 'Secure & Verified',
      desc: 'KYC-verified artisans, encrypted communications, and full audit trails for every incident.',
    },
    {
      icon: <FaHeadset />,
      title: '24/7 Support',
      desc: 'Dedicated support team, AI-powered chatbots, and comprehensive knowledge base for all users.',
    },
    {
      icon: <FaUsers />,
      title: 'Collaborative Platform',
      desc: 'Seamless coordination between call centers, dispatchers, supervisors, and field teams.',
    },
  ];

  return (
    <div className="landing-page landing-page--dark">
      {/* ─── Navbar ────────────────────────────────────────────────── */}
      <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
        <div className="container">
          <div className="navbar__brand">
            <span className="brand-icon">⚡</span>
            <span className="brand-name">Artisan<span className="brand-highlight">Hub</span></span>
          </div>

          <ul className={`navbar__links ${mobileMenuOpen ? 'open' : ''}`}>
            <li><a href="#features">Features</a></li>
            <li><a href="#testimonials">Testimonials</a></li>
            <li><a href="#stats">Stats</a></li>
            <li><Link to="/login" className="btn btn--outline">Sign In</Link></li>
            <li><Link to="/register" className="btn btn--primary">Get Started</Link></li>
          </ul>

          <button
            className="navbar__toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </nav>

      {/* ─── Hero Section ────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero__bg-gradient" />
        <div className="hero__floating-shapes">
          <div className="shape shape--1" />
          <div className="shape shape--2" />
          <div className="shape shape--3" />
          <div className="shape shape--4" />
          <div className="shape shape--5" />
        </div>

        <div className="container hero__content">
          <div className="hero__text">
            <span className="hero__badge">🚀 Next-Gen Workforce Management</span>
            <h1>
              Connect, Dispatch &amp; <br />
              <span className="gradient-text">Resolve Incidents</span> in Real-Time
            </h1>
            <p>
              The all-in-one platform for call centers, dispatchers, and artisans.
              Streamline incident reporting, dispatch the right talent, and close
              jobs faster than ever before.
            </p>
            <div className="hero__actions">
              <Link to="/register" className="btn btn--primary btn--large">
                Start Free Trial <FaArrowRight />
              </Link>
              <Link to="/demo" className="btn btn--outline btn--large">
                Watch Demo
              </Link>
            </div>
            <div className="hero__trust">
              <div className="trust-avatars">
                <img src="https://i.pravatar.cc/40?img=1" alt="User" />
                <img src="https://i.pravatar.cc/40?img=2" alt="User" />
                <img src="https://i.pravatar.cc/40?img=3" alt="User" />
                <img src="https://i.pravatar.cc/40?img=4" alt="User" />
                <span className="trust-count">+2,500</span>
              </div>
              <span className="trust-text">
                Trusted by <strong>500+</strong> companies across Ghana
              </span>
            </div>
          </div>

          <div className="hero__visual">
            <div className="dashboard-preview">
              <div className="dashboard-preview__header">
                <span className="dot dot--red" />
                <span className="dot dot--yellow" />
                <span className="dot dot--green" />
              </div>
              <div className="dashboard-preview__content">
                <div className="stat-card">
                  <span className="stat-label">Active Incidents</span>
                  <span className="stat-value">247</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Online Artisans</span>
                  <span className="stat-value">1,283</span>
                </div>
                <div className="stat-card stat-card--highlight">
                  <span className="stat-label">Resolution Rate</span>
                  <span className="stat-value">94%</span>
                </div>
                <div className="activity-feed">
                  <div className="activity-item">
                    <span className="activity-dot" />
                    <span className="activity-text">New incident #1042 assigned</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-dot activity-dot--success" />
                    <span className="activity-text">Artisan Kwame completed job</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-dot activity-dot--warning" />
                    <span className="activity-text">Priority escalation: #1018</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Features Section ────────────────────────────────────── */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Features</span>
            <h2>Everything You Need to <span className="gradient-text">Excel</span></h2>
            <p>
              Built for speed, reliability, and scale – our platform empowers
              every role in your workforce ecosystem.
            </p>
          </div>

          <div className="features__grid">
            {features.map((feature, idx) => (
              <div key={idx} className="feature-card" style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className="feature-card__icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Stats Section ────────────────────────────────────────── */}
      <section id="stats" className="stats" ref={statsRef}>
        <div className="container">
          <div className="stats__grid">
            <div className="stat-item">
              <span className="stat-number">{counts.artisans.toLocaleString()}+</span>
              <span className="stat-label">Verified Artisans</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{counts.incidents.toLocaleString()}+</span>
              <span className="stat-label">Incidents Resolved</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{counts.satisfaction}%</span>
              <span className="stat-label">Customer Satisfaction</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">4.9★</span>
              <span className="stat-label">Average Rating</span>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Testimonials ────────────────────────────────────────── */}
      <section id="testimonials" className="testimonials">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Testimonials</span>
            <h2>Loved by Teams <span className="gradient-text">Everywhere</span></h2>
            <p>Hear from real users who transformed their operations with our platform.</p>
          </div>

          <div className="testimonials__grid">
            {testimonials.map((t) => (
              <div key={t.id} className="testimonial-card">
                <FaQuoteLeft className="testimonial-card__quote" />
                <p className="testimonial-card__content">"{t.content}"</p>
                <div className="testimonial-card__footer">
                  <div className="testimonial-card__avatar">{t.avatar}</div>
                  <div>
                    <div className="testimonial-card__name">{t.name}</div>
                    <div className="testimonial-card__role">{t.role}</div>
                  </div>
                  <div className="testimonial-card__stars">
                    {[...Array(t.rating)].map((_, i) => (
                      <FaStar key={i} />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA Section ──────────────────────────────────────────── */}
      <section className="cta">
        <div className="container">
          <div className="cta__wrapper">
            <div className="cta__content">
              <span className="section-tag section-tag--light">Get Started</span>
              <h2>Ready to Transform Your <span className="gradient-text">Workforce</span>?</h2>
              <p>
                Join thousands of businesses already using ArtisanHub to dispatch,
                track, and resolve incidents faster than ever.
              </p>
              <div className="cta__actions">
                <Link to="/register" className="btn btn--primary btn--large">
                  Start Free Trial <FaArrowRight />
                </Link>
                <Link to="/contact" className="btn btn--outline btn--large">
                  Contact Sales
                </Link>
              </div>
            </div>
            <div className="cta__visual">
              <div className="cta-illustration">
                <span className="emoji-big">🚀</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Footer ────────────────────────────────────────────────── */}
      <footer className="footer">
        <div className="container">
          <div className="footer__grid">
            <div className="footer__brand">
              <span className="brand-icon">⚡</span>
              <span className="brand-name">Artisan<span className="brand-highlight">Hub</span></span>
              <p className="footer__desc">
                The premier incident management and workforce dispatch platform
                for Africa’s growing economy.
              </p>
              <div className="footer__social">
                <a href="#" aria-label="Twitter"><FaTwitter /></a>
                <a href="#" aria-label="LinkedIn"><FaLinkedin /></a>
                <a href="#" aria-label="GitHub"><FaGithub /></a>
                <a href="#" aria-label="YouTube"><FaYoutube /></a>
              </div>
            </div>

            <div className="footer__links">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#testimonials">Testimonials</a>
              <Link to="/pricing">Pricing</Link>
              <Link to="/demo">Demo</Link>
            </div>

            <div className="footer__links">
              <h4>Company</h4>
              <Link to="/about">About</Link>
              <Link to="/careers">Careers</Link>
              <Link to="/blog">Blog</Link>
              <Link to="/contact">Contact</Link>
            </div>

            <div className="footer__links">
              <h4>Support</h4>
              <Link to="/help">Help Center</Link>
              <Link to="/privacy">Privacy Policy</Link>
              <Link to="/terms">Terms of Service</Link>
              <Link to="/terms/artisan-agreement">Artisan Agreement</Link>
            </div>
          </div>

          <div className="footer__bottom">
            <span>&copy; 2026 ArtisanHub. All rights reserved.</span>
            <span>Made with ❤️ in Ghana</span>
          </div>
        </div>
      </footer>
    </div>
  );
};