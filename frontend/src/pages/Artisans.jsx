import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaSlidersH, FaTimes, FaTools, FaSpinner, FaChevronRight } from 'react-icons/fa';
import { getArtisans } from '../api/artisansAPI';
import ArtisanCard from '../components/common/ArtisanCard';
import './Artisans.css';

export default function Artisans() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [artisans, setArtisans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });

  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    location: searchParams.get('location') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    rating: searchParams.get('rating') || '',
    available: searchParams.get('available') === 'true' ? true : '',
  });

  const [showFilters, setShowFilters] = useState(false);

  const activeFilterCount = Object.entries(filters).filter(
    ([key, value]) => key !== 'search' && value !== '' && value !== null && value !== undefined
  ).length;

  // ─── Fetch function (memoized with useCallback) ────────────
  const fetchArtisans = useCallback(async (pageUrl = null) => {
    setLoading(true);
    try {
      const params = { ...filters };
      Object.keys(params).forEach((key) => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      let data;
      if (pageUrl) {
        const response = await fetch(pageUrl);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        data = await response.json();
      } else {
        const response = await getArtisans(params);
        data = response;
      }

      const results = data.results || data || [];
      if (Array.isArray(results)) {
        setArtisans(prev => pageUrl ? [...prev, ...results] : results);
        setPagination({
          count: data.count ?? results.length,
          next: data.next ?? null,
          previous: data.previous ?? null,
        });
      } else {
        console.warn('Unexpected data format:', data);
        setArtisans([]);
      }
    } catch (error) {
      console.error('Failed to fetch artisans:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]); // ✅ fetchArtisans updates when filters change

  // ─── Auto‑fetch on mount and when filters change ────────────
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchArtisans();
  }, [fetchArtisans]); // ✅ correct dependency

  // ─── Update URL when filters change ─────────────────────────
  useEffect(() => {
    const params = {};
    Object.keys(filters).forEach((key) => {
      if (filters[key] !== '' && filters[key] !== null && filters[key] !== undefined) {
        params[key] = filters[key];
      }
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  // ─── Handlers ────────────────────────────────────────────────
  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      location: '',
      min_price: '',
      max_price: '',
      rating: '',
      available: '',
    });
  };

  const loadMore = () => {
    if (pagination.next) fetchArtisans(pagination.next);
  };

  return (
    <div className="art-page">
      <div className="art-topline" aria-hidden="true" />

      <div className="art-container">
        {/* Eyebrow / breadcrumb */}
        <div className="art-eyebrow">
          <span>Marketplace</span>
          <FaChevronRight className="art-eyebrow-sep" />
          <span className="art-eyebrow-current">Artisans</span>
        </div>

        {/* Header */}
        <div className="art-header">
          <div>
            <h1 className="art-title">Find a trusted artisan</h1>
            <p className="art-subtitle">
              Vetted plumbers, electricians and craftspeople, ready to work near you.
            </p>
          </div>
          {pagination.count > 0 && (
            <div className="art-count">
              <span className="art-count-number">{pagination.count}</span>
              <span className="art-count-label">{pagination.count === 1 ? 'artisan' : 'artisans'} listed</span>
            </div>
          )}
        </div>

        {/* Toolbar */}
        <div className="art-toolbar">
          <div className="art-search">
            <FaSearch className="art-search-icon" />
            <input
              type="text"
              name="search"
              placeholder="Search by name, trade, or skill…"
              value={filters.search}
              onChange={handleFilterChange}
              className="art-search-input"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`art-filter-toggle ${showFilters ? 'is-active' : ''}`}
            aria-expanded={showFilters}
          >
            <FaSlidersH className="text-[13px]" />
            Filters
            {activeFilterCount > 0 && <span className="art-filter-count">{activeFilterCount}</span>}
          </button>
        </div>

        {/* Filters drawer */}
        <motion.div
          initial={false}
          animate={{ height: showFilters ? 'auto' : 0, opacity: showFilters ? 1 : 0 }}
          transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
          className="overflow-hidden"
        >
          <div className="art-filter-panel">
            <div className="art-filter-grid">
              <div className="art-field">
                <label className="art-label">Category</label>
                <input
                  name="category"
                  placeholder="e.g. Plumbing"
                  value={filters.category}
                  onChange={handleFilterChange}
                  className="art-input"
                />
              </div>
              <div className="art-field">
                <label className="art-label">Location</label>
                <input
                  name="location"
                  placeholder="City, region"
                  value={filters.location}
                  onChange={handleFilterChange}
                  className="art-input"
                />
              </div>
              <div className="art-field">
                <label className="art-label">Min price</label>
                <div className="art-input-prefix">
                  <span>₵</span>
                  <input
                    name="min_price"
                    type="number"
                    placeholder="0"
                    value={filters.min_price}
                    onChange={handleFilterChange}
                    className="art-input art-input--prefixed"
                  />
                </div>
              </div>
              <div className="art-field">
                <label className="art-label">Max price</label>
                <div className="art-input-prefix">
                  <span>₵</span>
                  <input
                    name="max_price"
                    type="number"
                    placeholder="500"
                    value={filters.max_price}
                    onChange={handleFilterChange}
                    className="art-input art-input--prefixed"
                  />
                </div>
              </div>
              <div className="art-field">
                <label className="art-label">Rating</label>
                <select
                  name="rating"
                  value={filters.rating}
                  onChange={handleFilterChange}
                  className="art-input"
                >
                  <option value="">Any rating</option>
                  <option value="4">4+ stars</option>
                  <option value="3">3+ stars</option>
                  <option value="2">2+ stars</option>
                </select>
              </div>
            </div>

            <div className="art-filter-footer">
              <label className="art-checkbox-row">
                <input
                  type="checkbox"
                  name="available"
                  checked={filters.available === true}
                  onChange={() =>
                    setFilters((prev) => ({
                      ...prev,
                      available: prev.available === true ? '' : true,
                    }))
                  }
                  className="art-checkbox"
                />
                Only show artisans available now
              </label>
              <button onClick={clearFilters} className="art-clear-btn">
                <FaTimes className="text-[11px]" /> Clear all
              </button>
            </div>
          </div>
        </motion.div>

        {/* Active filter chips */}
        {activeFilterCount > 0 && !showFilters && (
          <div className="art-chip-row">
            {filters.category && <span className="art-chip">{filters.category}</span>}
            {filters.location && <span className="art-chip">{filters.location}</span>}
            {(filters.min_price || filters.max_price) && (
              <span className="art-chip">
                ₵{filters.min_price || '0'}–{filters.max_price || '∞'}
              </span>
            )}
            {filters.rating && <span className="art-chip">{filters.rating}+ stars</span>}
            {filters.available === true && <span className="art-chip">Available now</span>}
            <button onClick={clearFilters} className="art-chip art-chip--clear">
              <FaTimes className="text-[10px]" /> Clear
            </button>
          </div>
        )}

        {/* Results */}
        {loading && !artisans.length ? (
          <div className="art-grid">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="art-card-shell">
                <div className="art-skeleton-card">
                  <div className="art-skeleton-media" />
                  <div className="art-skeleton-line art-skeleton-line--title" />
                  <div className="art-skeleton-line art-skeleton-line--sub" />
                  <div className="art-skeleton-line art-skeleton-line--tag" />
                </div>
              </div>
            ))}
          </div>
        ) : artisans.length === 0 ? (
          <div className="art-empty">
            <div className="art-empty-badge">
              <FaTools className="text-[18px]" aria-hidden="true" />
            </div>
            <p className="art-empty-title">No artisans found</p>
            <p className="art-empty-sub">Try a different search term or loosen your filters.</p>
            {activeFilterCount > 0 && (
              <button onClick={clearFilters} className="art-empty-clear">
                Clear all filters
              </button>
            )}
          </div>
        ) : (
          <>
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="art-grid"
              >
                {artisans.map((artisan, i) => (
                  <motion.div
                    key={artisan.id}
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: Math.min(i, 8) * 0.035, ease: [0.16, 1, 0.3, 1] }}
                    className="art-card-shell"
                  >
                    <ArtisanCard artisan={artisan} />
                  </motion.div>
                ))}
              </motion.div>
            </AnimatePresence>
            {pagination.next && (
              <div className="art-load-more">
                <button onClick={loadMore} disabled={loading} className="art-load-btn">
                  {loading ? (
                    <>
                      <FaSpinner className="animate-spin" />
                      Loading…
                    </>
                  ) : (
                    'Load more artisans'
                  )}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}