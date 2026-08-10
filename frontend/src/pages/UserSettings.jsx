// src/pages/UserSettings.jsx
import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUser } from '../api/authAPI';
import { updateUser, changePassword } from '../api/userAPI';
import {
  FaUser,
  FaWhatsapp,
  FaFacebook,
  FaInstagram,
  FaTwitter,
  FaCamera,
  FaUserCog,
  FaInfoCircle,
  FaSave,
  FaEdit,
  FaLock,
  FaKey,
} from 'react-icons/fa';
import './UserSettings.css';

const GENDER_OPTIONS = ['Male', 'Female', 'Other', 'Prefer not to say'];
const NATIONALITY_OPTIONS = ['Ghanaian', 'Nigerian', 'Kenyan', 'South African', 'British', 'American', 'Other'];

export const UserSettings = () => {
  const queryClient = useQueryClient();
  const fileInputRef = useRef(null);

  // ─── Fetch current user ──────────────────────────────────────
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Local state for form fields ────────────────────────────
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    introduction: '',
    job_title: '',
    gender: '',
    date_of_birth: '',          // ✅ changed from 'birthday'
    nationality: '',
    education: '',
    interests: '',
    languages: '',
    employer: '',               // ✅ added
    whatsapp: '',
    facebook: '',
    instagram: '',
    twitter: '',
    profile_picture: null,
  });

  const [account, setAccount] = useState({
    username: '',
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);

  // ─── Populate form when user data loads ────────────────────
  useEffect(() => {
    if (user) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
      setProfile({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        introduction: user.introduction || '',
        job_title: user.job_title || '',
        gender: user.gender || '',
        date_of_birth: user.date_of_birth || '',    // ✅ changed
        nationality: user.nationality || '',
        education: user.education || '',
        interests: user.interests || '',
        languages: user.languages || '',
        employer: user.employer || '',              // ✅ added
        whatsapp: user.whatsapp || '',
        facebook: user.facebook || '',
        instagram: user.instagram || '',
        twitter: user.twitter || '',
        profile_picture: user.profile_picture || null,
      });
      setAccount((prev) => ({
        ...prev,
        username: user.email || '',
      }));
    }
  }, [user]);

  // ─── Mutations ───────────────────────────────────────────────
  const updateProfileMutation = useMutation({
    mutationFn: (data) => updateUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setIsEditing(false);
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: (data) => changePassword(data),
    onSuccess: () => {
      setAccount({ ...account, old_password: '', new_password: '', confirm_password: '' });
      alert('Password changed successfully!');
    },
  });

  // ─── Handlers ─────────────────────────────────────────────────
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleAccountChange = (e) => {
    const { name, value } = e.target;
    setAccount((prev) => ({ ...prev, [name]: value }));
  };

  const handleProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfile((prev) => ({ ...prev, profile_picture: file }));
    }
  };

  const handleRemoveProfilePicture = () => {
    setProfile((prev) => ({ ...prev, profile_picture: null }));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    // Send only the fields that are editable (match your backend's UserUpdateSerializer)
    const editableFields = [
      'first_name', 'last_name', 'phone_number', 'profile_picture',
      'date_of_birth', 'gender', 'job_title', 'introduction',
      'nationality', 'education', 'interests', 'languages', 'employer',
      'whatsapp', 'facebook', 'instagram', 'twitter'
    ];
    editableFields.forEach((key) => {
      if (key === 'profile_picture') {
        if (profile.profile_picture instanceof File) {
          formData.append('profile_picture', profile.profile_picture);
        }
      } else {
        formData.append(key, profile[key] || '');
      }
    });
    updateProfileMutation.mutate(formData);
  };

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (account.new_password !== account.confirm_password) {
      alert('New passwords do not match.');
      return;
    }
    changePasswordMutation.mutate({
      old_password: account.old_password,
      new_password: account.new_password,
    });
  };

  // ─── Loading & error states ──────────────────────────────────
  if (isLoading) {
    return (
      <div className="user-settings">
        <div className="settings-skeleton">
          <div className="skeleton-header" />
          <div className="skeleton-body" />
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="user-settings__error">Failed to load user settings.</div>;
  }

  // ─── Tabs ─────────────────────────────────────────────────────
  const tabs = [
    { key: 'profile', label: 'User Profile', icon: FaUser },
    { key: 'account', label: 'Account Settings', icon: FaLock },
    { key: 'full-profile', label: 'Full Profile', icon: FaUserCog },
    { key: 'about', label: 'About the app', icon: FaInfoCircle },
  ];

  // ─── Render ──────────────────────────────────────────────────
  return (
    <div className="user-settings">
      <h1 className="settings-title">Settings</h1>

      {/* ─── Tabs ──────────────────────────────────────────────── */}
      <div className="settings-tabs">
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

      {/* ─── Tab Content ───────────────────────────────────────── */}
      <div className="settings-content">
        {/* ======================================================
            1. USER PROFILE
            ====================================================== */}
        {activeTab === 'profile' && (
          <div className="settings-panel">
            <div className="panel-header">
              <h2>Edit Profile</h2>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="btn btn-outline"
              >
                {isEditing ? 'Cancel' : <><FaEdit /> Edit</>}
              </button>
            </div>

            <form onSubmit={handleProfileSubmit} className="profile-form">
              {/* ─── Profile Picture ───────────────────────────── */}
              <div className="form-section">
                <label>Profile Picture</label>
                <div className="profile-picture-section">
                  <div className="avatar-wrapper">
                    {profile.profile_picture instanceof File ? (
                      <img
                        src={URL.createObjectURL(profile.profile_picture)}
                        alt="Profile"
                        className="avatar-preview"
                      />
                    ) : profile.profile_picture ? (
                      <img
                        src={profile.profile_picture}
                        alt="Profile"
                        className="avatar-preview"
                      />
                    ) : (
                      <div className="avatar-placeholder">
                        {profile.first_name?.charAt(0) || 'U'}
                      </div>
                    )}
                  </div>
                  <div className="avatar-actions">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="btn btn-sm btn-secondary"
                    >
                      <FaCamera /> Upload
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleProfilePictureChange}
                      style={{ display: 'none' }}
                    />
                    <button
                      type="button"
                      onClick={handleRemoveProfilePicture}
                      className="btn btn-sm btn-danger"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              {/* ─── Fields ────────────────────────────────────── */}
              <div className="form-grid-2">
                <div className="field-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={profile.first_name}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={profile.last_name}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={profile.email}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Mobile Phone</label>
                  <input
                    type="tel"
                    name="phone_number"
                    value={profile.phone_number}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Introduction</label>
                  <textarea
                    name="introduction"
                    value={profile.introduction}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    rows="3"
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Job Title</label>
                  <input
                    type="text"
                    name="job_title"
                    value={profile.job_title}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Employer</label>         {/* ✅ added */}
                  <input
                    type="text"
                    name="employer"
                    value={profile.employer}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Gender</label>
                  <select
                    name="gender"
                    value={profile.gender}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  >
                    <option value="">Select gender</option>
                    {GENDER_OPTIONS.map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
                <div className="field-group">
                  <label>Date of Birth</label>    
                  <input
                    type="date"
                    name="date_of_birth"          
                    value={profile.date_of_birth}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Nationality</label>
                  <select
                    name="nationality"
                    value={profile.nationality}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  >
                    <option value="">Select nationality</option>
                    {NATIONALITY_OPTIONS.map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
                <div className="field-group">
                  <label>Education</label>
                  <input
                    type="text"
                    name="education"
                    value={profile.education}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Interests</label>
                  <input
                    type="text"
                    name="interests"
                    value={profile.interests}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
                <div className="field-group">
                  <label>Languages</label>
                  <input
                    type="text"
                    name="languages"
                    value={profile.languages}
                    onChange={handleProfileChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>
              </div>

              {/* ─── Social Media ────────────────────────────── */}
              <div className="form-section">
                <h3>Social Media</h3>
                <div className="form-grid-2">
                  <div className="field-group">
                    <label><FaWhatsapp /> WhatsApp</label>
                    <input
                      type="text"
                      name="whatsapp"
                      value={profile.whatsapp}
                      onChange={handleProfileChange}
                      disabled={!isEditing}
                      className={!isEditing ? 'readonly' : ''}
                      placeholder="+233 XX XXX XXXX"
                    />
                  </div>
                  <div className="field-group">
                    <label><FaFacebook /> Facebook</label>
                    <input
                      type="text"
                      name="facebook"
                      value={profile.facebook}
                      onChange={handleProfileChange}
                      disabled={!isEditing}
                      className={!isEditing ? 'readonly' : ''}
                      placeholder="username"
                    />
                  </div>
                  <div className="field-group">
                    <label><FaInstagram /> Instagram</label>
                    <input
                      type="text"
                      name="instagram"
                      value={profile.instagram}
                      onChange={handleProfileChange}
                      disabled={!isEditing}
                      className={!isEditing ? 'readonly' : ''}
                      placeholder="@username"
                    />
                  </div>
                  <div className="field-group">
                    <label><FaTwitter /> Twitter</label>
                    <input
                      type="text"
                      name="twitter"
                      value={profile.twitter}
                      onChange={handleProfileChange}
                      disabled={!isEditing}
                      className={!isEditing ? 'readonly' : ''}
                      placeholder="@username"
                    />
                  </div>
                </div>
              </div>

              {isEditing && (
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={updateProfileMutation.isPending}>
                    {updateProfileMutation.isPending ? 'Saving...' : <><FaSave /> Save Profile</>}
                  </button>
                </div>
              )}
            </form>
          </div>
        )}

        {/* ======================================================
            2. ACCOUNT SETTINGS
            ====================================================== */}
        {activeTab === 'account' && (
          <div className="settings-panel">
            <h2>Account Settings</h2>
            <form onSubmit={handlePasswordSubmit} className="account-form">
              <div className="field-group">
                <label>Username (Email)</label>
                <input
                  type="email"
                  value={account.username}
                  disabled
                  className="readonly"
                />
                <small className="helper-text">Your email address is your username and cannot be changed.</small>
              </div>

              <div className="form-section">
                <h3>Change Password</h3>
                <div className="field-group">
                  <label>Old Password</label>
                  <input
                    type="password"
                    name="old_password"
                    value={account.old_password}
                    onChange={handleAccountChange}
                    placeholder="Enter current password"
                    required
                  />
                </div>
                <div className="field-group">
                  <label>New Password</label>
                  <input
                    type="password"
                    name="new_password"
                    value={account.new_password}
                    onChange={handleAccountChange}
                    placeholder="Min 8 characters"
                    required
                  />
                </div>
                <div className="field-group">
                  <label>Repeat New Password</label>
                  <input
                    type="password"
                    name="confirm_password"
                    value={account.confirm_password}
                    onChange={handleAccountChange}
                    placeholder="Re-enter new password"
                    required
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={changePasswordMutation.isPending}>
                  {changePasswordMutation.isPending ? 'Changing...' : <><FaKey /> Change Password</>}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* ======================================================
            3. FULL PROFILE
            ====================================================== */}
        {activeTab === 'full-profile' && (
          <div className="settings-panel">
            <h2>Full Profile</h2>
            <div className="full-profile-grid">
              <div className="profile-item">
                <span className="label">First name</span>
                <span className="value">{profile.first_name || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Surname</span>
                <span className="value">{profile.last_name || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Gender</span>
                <span className="value">{profile.gender || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">E-mail</span>
                <span className="value">{profile.email || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Mobile phone number</span>
                <span className="value">{profile.phone_number || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Introduction</span>
                <span className="value">{profile.introduction || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Date of Birth</span>      {/* ✅ changed */}
                <span className="value">{profile.date_of_birth || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Nationality</span>
                <span className="value">{profile.nationality || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Employer</span>
                <span className="value">{profile.employer || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Job title</span>
                <span className="value">{profile.job_title || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">User type</span>         {/* ✅ replaced roles */}
                <span className="value">{user?.user_type || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">User groups</span>       {/* ✅ replaced org_units */}
                <span className="value">{user?.groups?.map(g => g.name).join(', ') || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Education</span>
                <span className="value">{profile.education || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Interests</span>
                <span className="value">{profile.interests || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Languages</span>
                <span className="value">{profile.languages || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Employee Number</span>
                <span className="value">{user?.employee_number || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Department</span>
                <span className="value">{user?.department || '—'}</span>
              </div>
              <div className="profile-item">
                <span className="label">Hire Date</span>
                <span className="value">{user?.hire_date || '—'}</span>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================
            4. ABOUT THE APP
            ====================================================== */}
        {activeTab === 'about' && (
          <div className="settings-panel">
            <h2>About the app</h2>
            <div className="about-content">
              <div className="about-icon">
                <FaInfoCircle />
              </div>
              <h3>Artisan Marketplace</h3>
              <p className="version">Version 2.1.0</p>
              <p className="description">
                A comprehensive incident management and workforce dispatch platform designed for
                call centers, dispatchers, and artisans.
              </p>
              <div className="about-features">
                <div className="feature-item">
                  <span className="feature-label">📦 Built with:</span>
                  <span>React, Django, Celery, Redis</span>
                </div>
                <div className="feature-item">
                  <span className="feature-label">📅 Released:</span>
                  <span>July 2026</span>
                </div>
                <div className="feature-item">
                  <span className="feature-label">📧 Support:</span>
                  <span>support@artisanmarketplace.com</span>
                </div>
                <div className="feature-item">
                  <span className="feature-label">🔒 Security:</span>
                  <span>JWT authentication, RBAC</span>
                </div>
              </div>
              <div className="about-footer">
                <p>&copy; 2026 Artisan Marketplace. All rights reserved.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};