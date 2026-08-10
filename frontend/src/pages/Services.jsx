import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaSpinner, FaSearch, FaPlus, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getServices, deleteService } from '../api/servicesAPI';
import toast from 'react-hot-toast';
import './Services.css';

export default function Services() {
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deleting, setDeleting] = useState(null);

  // ─── Fetch services ──────────────────────────────────────────
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await getServices();
        setServices(response.data.results || response.data || []);
      } catch (error) {
        console.error('Failed to fetch services:', error);
        toast.error('Could not load services.');
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, []);

  // ─── Handle delete ──────────────────────────────────────────
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this service?')) return;
    setDeleting(id);
    try {
      await deleteService(id);
      setServices(services.filter(s => s.id !== id));
      toast.success('Service deleted.');
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete service.');
    } finally {
      setDeleting(null);
    }
  };

  // ─── Filter by search ───────────────────────────────────────
  const filtered = services.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    (s.category && s.category.toLowerCase().includes(search.toLowerCase()))
  );

  // ─── Loading ─────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="services-page">
        <div className="services-loading">
          <FaSpinner className="animate-spin" />
          <p>Loading services…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="services-page">
      <div className="services-container">
        {/* Header */}
        <div className="services-header">
          <div>
            <h1>Services</h1>
            <p>Browse all available services</p>
          </div>
          {user?.is_staff && (
            <Link to="/services/create" className="services-add-btn">
              <FaPlus /> Add Service
            </Link>
          )}
        </div>

        {/* Search */}
        <div className="services-search">
          <FaSearch className="services-search-icon" />
          <input
            type="text"
            placeholder="Search by name or category…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="services-search-input"
          />
        </div>

        {/* Grid */}
        {filtered.length === 0 ? (
          <div className="services-empty">
            <p>No services found.</p>
          </div>
        ) : (
          <div className="services-grid">
            {filtered.map((service) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="service-card"
              >
                {service.image && (
                  <img
                    src={service.image}
                    alt={service.name}
                    className="service-card-image"
                  />
                )}
                <div className="service-card-body">
                  <h3>{service.name}</h3>
                  <p className="service-card-category">
                    {service.category}
                    {service.subcategory && ` › ${service.subcategory}`}
                  </p>
                  <p className="service-card-price">
                    GHS {Number(service.minimum_price).toFixed(2)}
                    {service.maximum_price > service.minimum_price &&
                      ` – GHS ${Number(service.maximum_price).toFixed(2)}`}
                  </p>
                  <p className="service-card-duration">
                    ⏱ {service.estimated_duration}h
                  </p>
                  {service.is_featured && (
                    <span className="service-card-badge">Featured</span>
                  )}
                </div>
                <div className="service-card-actions">
                  <Link to={`/services/${service.id}`} className="service-action-btn">
                    <FaEye />
                  </Link>
                  {user?.is_staff && (
                    <>
                      <Link to={`/services/${service.id}/edit`} className="service-action-btn">
                        <FaEdit />
                      </Link>
                      <button
                        onClick={() => handleDelete(service.id)}
                        disabled={deleting === service.id}
                        className="service-action-btn service-action-btn--delete"
                      >
                        {deleting === service.id ? <FaSpinner className="animate-spin" /> : <FaTrash />}
                      </button>
                    </>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}