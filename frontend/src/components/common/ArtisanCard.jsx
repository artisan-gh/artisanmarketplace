import { Link } from 'react-router-dom';
import { FaStar, FaMapMarkerAlt } from 'react-icons/fa';

export default function ArtisanCard({ artisan }) {
  const {
    id,
    full_name,
    business_name,
    category_names,
    min_price,
    average_rating,
    is_available,
    location,
    profile_picture,
  } = artisan;

  const initial = business_name?.[0] || full_name?.[0] || 'A';
  const extraCategories = category_names && category_names.length > 2 ? category_names.length - 2 : 0;

  return (
    <Link to={`/artisans/${id}`} className="block group art-card-shell">
      <div className="card-inner h-full flex flex-col">
        {/* Media */}
        <div className="art-card-media">
          {profile_picture ? (
            <img
              src={profile_picture}
              alt={full_name}
              className="art-card-media-img transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="art-card-media-fallback">
              <span className="art-card-monogram">{initial}</span>
            </div>
          )}
          <div className="art-card-media-fade" aria-hidden="true" />

          {is_available && (
            <div className="art-badge-available">
              <span className="art-badge-dot" />
              Available now
            </div>
          )}
        </div>

        {/* Body */}
        <div className="art-card-body">
          <div className="art-card-top-row">
            <div className="art-avatar-ring">
              {profile_picture ? (
                <img src={profile_picture} alt="" className="w-full h-full object-cover" />
              ) : (
                <span className="art-avatar-fallback">{initial}</span>
              )}
            </div>

            {average_rating ? (
              <div className="art-rating-badge">
                <FaStar aria-hidden="true" />
                {Number(average_rating).toFixed(1)}
              </div>
            ) : (
              <div className="art-rating-badge art-rating-badge--new">New</div>
            )}
          </div>

          <h3 className="art-card-name truncate">{business_name || full_name}</h3>
          <p className="art-card-trade truncate">{full_name}</p>

          {category_names && category_names.length > 0 && (
            <div className="art-category-row">
              {category_names.slice(0, 2).map((c) => (
                <span key={c} className="art-category-pill">
                  {c}
                </span>
              ))}
              {extraCategories > 0 && (
                <span className="art-category-pill art-category-pill--muted">+{extraCategories}</span>
              )}
            </div>
          )}

          <div className="art-card-footer">
            <span className="art-card-location">
              <FaMapMarkerAlt aria-hidden="true" />
              {location || 'Ghana'}
            </span>
            {min_price && (
              <span className="art-card-price">
                From <strong>₵{Number(min_price).toFixed(2)}</strong>
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}