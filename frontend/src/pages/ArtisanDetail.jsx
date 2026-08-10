import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FaMapMarkerAlt,
  FaPhone,
  FaEnvelope,
  FaShare,
  FaHeart,
  FaCalendarAlt,
  FaCheckCircle,
  FaChevronRight,
} from 'react-icons/fa';
import { getArtisan } from '../api/artisansAPI';
import { useAuth } from '../context/AuthContext';
import './ArtisanDetail.css';

export default function ArtisanDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [artisan, setArtisan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArtisan = async () => {
      try {
        const data = await getArtisan(id);
        setArtisan(data);
      } catch (err) {
        console.error('Error loading artisan:', err);
        setError('Failed to load artisan profile.');
      } finally {
        setLoading(false);
      }
    };
    fetchArtisan();
  }, [id]);

  const handleBook = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    navigate(`/book?artisan=${id}`);
  };

  if (loading) {
    return (
      <div className="art-detail-page art-detail-status">
        <div className="art-detail-spinner" aria-hidden="true" />
        <p>Loading profile…</p>
      </div>
    );
  }

  if (error || !artisan) {
    return (
      <div className="art-detail-page art-detail-status">
        <p className="art-detail-error">{error || 'Artisan not found'}</p>
        <button onClick={() => navigate('/artisans')} className="art-detail-status-link">
          ← Back to artisans
        </button>
      </div>
    );
  }

  const {
    full_name,
    business_name,
    bio,
    verified,
    categories_detail,
    service_offerings = [],
    created_at,
    user_detail,
  } = artisan;

  const email = user_detail?.email || '';
  const phone = user_detail?.phone_number || '';
  const location = user_detail?.location || '';
  const initial = business_name?.[0] || full_name?.[0] || 'A';
  const joined = created_at
    ? new Date(created_at).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
    : null;

  return (
    <div className="art-detail-page">
      <div className="art-topline" aria-hidden="true" />

      <div className="art-detail-container">
        <div className="art-eyebrow">
          <button onClick={() => navigate('/artisans')} className="art-detail-back">
            Artisans
          </button>
          <FaChevronRight className="art-eyebrow-sep" />
          <span className="art-eyebrow-current">{business_name || full_name}</span>
        </div>

        <div className="art-detail-card">
          {/* ─── Profile header ─── */}
          <div className="art-detail-header">
            <div className="art-detail-avatar">
              {user_detail?.profile_picture ? (
                <img
                  src={user_detail.profile_picture}
                  alt={full_name}
                  width="112"
                  height="112"
                  className="art-detail-avatar-img"
                />
              ) : (
                <span className="art-detail-avatar-fallback">{initial}</span>
              )}
            </div>

            <div className="art-detail-identity">
              <div className="art-detail-identity-top">
                <div>
                  <h1 className="art-detail-name">{business_name || full_name}</h1>
                  <p className="art-detail-subname">{full_name}</p>
                </div>
                <div className="art-detail-icon-actions">
                  <button className="art-detail-icon-btn" aria-label="Save">
                    <FaHeart />
                  </button>
                  <button className="art-detail-icon-btn" aria-label="Share">
                    <FaShare />
                  </button>
                </div>
              </div>

              <div className="art-detail-meta-row">
                {verified && (
                  <span className="art-verified-badge">
                    <FaCheckCircle /> Verified
                  </span>
                )}
                {location && (
                  <span className="art-detail-meta-item">
                    <FaMapMarkerAlt /> {location}
                  </span>
                )}
                {joined && <span className="art-detail-meta-item">Joined {joined}</span>}
              </div>

              {bio && <p className="art-detail-bio">{bio}</p>}

              {categories_detail && categories_detail.length > 0 && (
                <div className="art-category-row art-detail-categories">
                  {categories_detail.map((cat) => (
                    <span key={cat.id} className="art-category-pill">
                      {cat.name}
                    </span>
                  ))}
                </div>
              )}

              <div className="art-detail-actions">
                {email && (
                  <a href={`mailto:${email}`} className="art-detail-btn art-detail-btn--ghost">
                    <FaEnvelope /> Contact
                  </a>
                )}
                {phone && (
                  <a href={`tel:${phone}`} className="art-detail-btn art-detail-btn--ghost">
                    <FaPhone /> Call
                  </a>
                )}
                <button onClick={handleBook} className="art-detail-btn art-detail-btn--primary">
                  <FaCalendarAlt /> Book now
                </button>
              </div>
            </div>
          </div>

          {/* ─── Services ─── */}
          {service_offerings.length > 0 && (
            <div className="art-detail-section">
              <h2 className="art-detail-section-title">Services offered</h2>
              <div className="art-service-grid">
                {service_offerings.map((offering) => (
                  <div key={offering.id} className="art-service-card">
                    <div className="art-service-top">
                      <div>
                        <h4 className="art-service-name">
                          {offering.service_detail?.name || 'Service'}
                        </h4>
                        <p className="art-service-exp">
                          {offering.experience_years || 0}{' '}
                          {offering.experience_years === 1 ? 'year' : 'years'} experience
                        </p>
                      </div>
                      <span className="art-service-price">
                        ₵{Number(offering.price).toFixed(2)}
                      </span>
                    </div>
                    <span
                      className={`art-service-status ${
                        offering.is_available
                          ? 'art-service-status--available'
                          : 'art-service-status--unavailable'
                      }`}
                    >
                      {offering.is_available ? 'Available' : 'Unavailable'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ─── Reviews ─── */}
          <div className="art-detail-section">
            <h2 className="art-detail-section-title">Reviews</h2>
            <div className="art-detail-reviews-empty">
              Reviews will appear here once customers start leaving feedback.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}