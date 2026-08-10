import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  FaUser,
  FaTag,
  FaList,
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaClock,
  FaUserCheck,
  FaEdit,
  FaArrowLeft,
  FaCommentDots,
  FaPaperclip,
  FaHistory,
  FaUserPlus,
  FaExclamationTriangle,
  FaCheckCircle,
  FaHourglassHalf,
} from 'react-icons/fa';
import { getIncident } from '../../api/incidentsAPI';
import { getIncidentSLA } from '../../api/slaAPI';
import { StatusBadge } from '../common/StatusBadge';
import { CommentList } from '../comments/CommentList';
import { CommentForm } from '../comments/CommentForm';
import { AttachmentList } from '../attachments/AttachmentList';
import { AttachmentUpload } from '../attachments/AttachmentUpload';
import { useAuth } from '../../context/AuthContext';
import './IncidentDetail.css';

export const IncidentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');

  // ─── Fetch incident data ──────────────────────────────────
  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getIncident(id);
        // ✅ FIX: getIncident already returns the parsed JSON
        setIncident(res);
      } catch (err) {
        console.error('Failed to fetch incident:', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [id]);

  // ─── Fetch SLA data ──────────────────────────────────────
  const {
    data: slaData,
    isLoading: slaLoading,
    error: slaError,
  } = useQuery({
    queryKey: ['incidentSLA', id],
    queryFn: () => getIncidentSLA(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    retry: false, // don't retry on 404
  });

  // ─── Determine SLA status color ──────────────────────────
  const getSlaStatusColor = (status) => {
    if (status === 'BREACHED') return 'error';
    if (status === 'AT_RISK') return 'warning';
    return 'success';
  };

  const getSlaIcon = (status) => {
    if (status === 'BREACHED') return <FaExclamationTriangle className="text-red-500" />;
    if (status === 'AT_RISK') return <FaHourglassHalf className="text-yellow-500" />;
    return <FaCheckCircle className="text-green-500" />;
  };

  if (loading) {
    return (
      <div className="incident-detail-loading">
        <div className="loading-spinner" />
        <span>Loading incident details...</span>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="incident-detail-not-found">
        <h2>Incident not found</h2>
        <button onClick={() => navigate('/incidents')} className="btn btn-primary">
          Back to Incidents
        </button>
      </div>
    );
  }

  const customerName = incident.customer_detail?.name || incident.customer_name || '—';
  const categoryName = incident.category_detail?.name || incident.category_name || '—';
  const subcategoryName = incident.subcategory_detail?.name || incident.subcategory_name || '—';
  const assignedToName = incident.assigned_to_detail?.full_name || incident.assigned_to_name || 'Unassigned';

  const tabs = [
    { key: 'details', label: 'Details', icon: FaList },
    { key: 'comments', label: 'Comments', icon: FaCommentDots },
    { key: 'attachments', label: 'Attachments', icon: FaPaperclip },
    { key: 'timeline', label: 'Timeline', icon: FaHistory },
  ];

  const formatDate = (date) => {
    if (!date) return '—';
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // ─── Check if user can assign ──────────────────────────────
  const canAssign = user?.user_type === 'DISPATCHER' || user?.user_type === 'ADMIN';

  return (
    <div className="incident-detail-container">
      {/* ─── Header ────────────────────────────────────────────── */}
      <div className="incident-detail-header">
        <div className="header-left">
          <button
            onClick={() => navigate('/incidents')}
            className="back-button"
            aria-label="Back to incidents"
          >
            <FaArrowLeft />
          </button>
          <div>
            <h1 className="incident-title">{incident.incident_number}</h1>
            <p className="incident-subtitle">{incident.title}</p>
          </div>
        </div>
        <div className="header-actions">
          <div className="badge-group">
            <StatusBadge status={incident.status?.toLowerCase()}>
              {incident.status || 'New'}
            </StatusBadge>
            <StatusBadge status={incident.priority?.toLowerCase()}>
              {incident.priority || 'Medium'}
            </StatusBadge>
          </div>
          {canAssign && (
            <button
              onClick={() => navigate(`/assignments/new/${id}`)}
              className="btn btn-success btn-sm"
              style={{ background: '#22c55e', color: '#fff' }}
            >
              <FaUserPlus /> Assign
            </button>
          )}
          <button
            onClick={() => navigate(`/incidents/${id}/edit`)}
            className="btn btn-primary btn-sm"
          >
            <FaEdit /> Edit
          </button>
        </div>
      </div>

      {/* ─── Tabs ────────────────────────────────────────────────── */}
      <div className="incident-detail-tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`tab-btn ${isActive ? 'active' : ''}`}
            >
              <Icon />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ─── Tab Content ────────────────────────────────────────── */}
      <div className="incident-detail-content">
        {activeTab === 'details' && (
          <div className="details-grid">
            {/* ─── Left Column ──────────────────────────────────── */}
            <div className="details-card">
              <h3 className="card-title">
                <FaList className="card-icon" /> Details
              </h3>
              <div className="detail-item">
                <FaUser className="detail-icon" />
                <div>
                  <span className="detail-label">Customer</span>
                  <span className="detail-value">{customerName}</span>
                </div>
              </div>
              <div className="detail-item">
                <FaTag className="detail-icon" />
                <div>
                  <span className="detail-label">Category</span>
                  <span className="detail-value">{categoryName}</span>
                </div>
              </div>
              {subcategoryName !== '—' && (
                <div className="detail-item">
                  <FaList className="detail-icon" />
                  <div>
                    <span className="detail-label">Subcategory</span>
                    <span className="detail-value">{subcategoryName}</span>
                  </div>
                </div>
              )}
              <div className="detail-item">
                <FaMapMarkerAlt className="detail-icon" />
                <div>
                  <span className="detail-label">Location</span>
                  <span className="detail-value">{incident.address || '—'}</span>
                </div>
              </div>
              <div className="detail-item description-item">
                <div>
                  <span className="detail-label">Description</span>
                  <p className="detail-description">{incident.description || 'No description provided'}</p>
                </div>
              </div>
            </div>

            {/* ─── Right Column ─────────────────────────────────── */}
            <div className="details-card">
              <h3 className="card-title">
                <FaUserCheck className="card-icon" /> Assignment & SLA
              </h3>
              <div className="detail-item">
                <FaUser className="detail-icon" />
                <div>
                  <span className="detail-label">Assigned To</span>
                  <span className="detail-value">{assignedToName}</span>
                </div>
              </div>
              <div className="detail-item">
                <FaCalendarAlt className="detail-icon" />
                <div>
                  <span className="detail-label">Target Resolution</span>
                  <span className="detail-value">{formatDate(incident.target_resolution)}</span>
                </div>
              </div>
              <div className="detail-item">
                <FaClock className="detail-icon" />
                <div>
                  <span className="detail-label">Resolved At</span>
                  <span className="detail-value">{formatDate(incident.resolved_at)}</span>
                </div>
              </div>
              <div className="detail-item">
                <FaCalendarAlt className="detail-icon" />
                <div>
                  <span className="detail-label">Created</span>
                  <span className="detail-value">{formatDate(incident.created_at)}</span>
                </div>
              </div>

              {/* ─── SLA Section ───────────────────────────────── */}
              <hr className="my-4 border-gray-200" />
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <FaClock className="text-blue-500" /> SLA Status
              </h4>

              {slaLoading ? (
                <div className="text-sm text-gray-500">Loading SLA data...</div>
              ) : slaError ? (
                // ✅ Handle 404 gracefully – show "No SLA tracking"
                slaError.response?.status === 404 ? (
                  <div className="text-sm text-gray-500">No SLA tracking for this incident.</div>
                ) : (
                  <div className="text-sm text-red-500">Failed to load SLA data.</div>
                )
              ) : slaData ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    {getSlaIcon(slaData.sla_status)}
                    <StatusBadge status={getSlaStatusColor(slaData.sla_status)}>
                      {slaData.sla_status?.replace('_', ' ') || 'On Track'}
                    </StatusBadge>
                  </div>
                  {slaData.target_resolution && (
                    <div className="text-sm">
                      <span className="text-gray-500">Target:</span>
                      <span className="ml-1 font-medium">
                        {formatDate(slaData.target_resolution)}
                      </span>
                    </div>
                  )}
                  {slaData.remaining_time && (
                    <div className="text-sm">
                      <span className="text-gray-500">Remaining:</span>
                      <span className="ml-1 font-medium">{slaData.remaining_time}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">No SLA tracking for this incident.</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'comments' && (
          <div className="tab-panel comments-panel">
            <CommentForm incidentId={id} onCommentAdded={() => {}} />
            <CommentList incidentId={id} />
          </div>
        )}

        {activeTab === 'attachments' && (
          <div className="tab-panel attachments-panel">
            <AttachmentUpload incidentId={id} onUploadComplete={() => {}} />
            <AttachmentList incidentId={id} />
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="tab-panel timeline-panel">
            <div className="timeline-placeholder">
              <FaHistory className="placeholder-icon" />
              <p>Timeline is being built. Activity history will appear here soon.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};