import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaSpinner, FaArrowLeft, FaEdit, FaTrash} from 'react-icons/fa';
import { getService, deleteService } from '../api/servicesAPI';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './ServiceDetail.css';

export default function ServiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchService = async () => {
      try {
        const response = await getService(id);
        setService(response.data);
      } catch (error) {
        console.error('Failed to fetch service:', error);
        toast.error('Service not found.');
        navigate('/services');
      } finally {
        setLoading(false);
      }
    };
    fetchService();
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this service?')) return;
    setDeleting(true);
    try {
      await deleteService(id);
      toast.success('Service deleted.');
      navigate('/services');
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete service.');
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="service-detail-page">
        <div className="service-detail-loading">
          <FaSpinner className="animate-spin" />
          <p>Loading service details…</p>
        </div>
      </div>
    );
  }

  if (!service) return null;

  const isAdmin = user?.is_staff;

  return (
    <div className="service-detail-page">
      <div className="service-detail-container">
        {/* Back button */}
        <Link to="/services" className="service-detail-back">
          <FaArrowLeft /> Back to services
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="service-detail-card"
        >
          <div className="service-detail-header">
            <h1>{service.name}</h1>
            <div className="service-detail-badges">
              {service.is_featured && (
                <span className="badge badge-featured">Featured</span>
              )}
              <span className={`badge badge-${service.is_active ? 'active' : 'inactive'}`}>
                {service.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          <div className="service-detail-body">
            {service.image && (
              <div className="service-detail-image">
                <img src={service.image} alt={service.name} />
              </div>
            )}

            <div className="service-detail-info">
              <p className="service-detail-description">{service.description}</p>

              <div className="service-detail-meta">
                <div className="meta-item">
                  <span className="meta-label">Category</span>
                  <span className="meta-value">{service.category}</span>
                </div>
                {service.subcategory && (
                  <div className="meta-item">
                    <span className="meta-label">Subcategory</span>
                    <span className="meta-value">{service.subcategory}</span>
                  </div>
                )}
                <div className="meta-item">
                  <span className="meta-label">Price Range</span>
                  <span className="meta-value">
                    GHS {Number(service.minimum_price).toFixed(2)}
                    {service.maximum_price > service.minimum_price &&
                      ` – GHS ${Number(service.maximum_price).toFixed(2)}`}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Estimated Duration</span>
                  <span className="meta-value">{service.estimated_duration} hours</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Created</span>
                  <span className="meta-value">
                    {new Date(service.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Last Updated</span>
                  <span className="meta-value">
                    {new Date(service.updated_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {isAdmin && (
            <div className="service-detail-actions">
              <Link to={`/services/${service.id}/edit`} className="btn btn-primary">
                <FaEdit /> Edit Service
              </Link>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="btn btn-danger"
              >
                {deleting ? <FaSpinner className="animate-spin" /> : <FaTrash />}
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}