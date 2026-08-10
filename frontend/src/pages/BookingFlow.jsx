import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaArrowLeft,
  FaArrowRight,
  FaCheckCircle,
  FaCalendarAlt,
  FaToolbox,
  FaCreditCard,
  FaSpinner,
} from 'react-icons/fa';
import { getArtisan } from '../api/artisansAPI';
import { createBooking } from '../api/bookingsAPI';
import { initiatePayment } from '../api/paymentsAPI';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './BookingFlow.css';

// ─── Steps ────────────────────────────────────────────────────
const STEPS = [
  { id: 'service', label: 'Service', icon: FaToolbox },
  { id: 'datetime', label: 'Date & time', icon: FaCalendarAlt },
  { id: 'confirm', label: 'Confirm', icon: FaCheckCircle },
  { id: 'payment', label: 'Payment', icon: FaCreditCard },
];

export default function BookingFlow() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const artisanId = searchParams.get('artisan');
  const [artisan, setArtisan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState(0);
  const [selectedService, setSelectedService] = useState(null);
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [address, setAddress] = useState('');
  const [bookingId, setBookingId] = useState(null);
  const [bookingAmount, setBookingAmount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPaying, setIsPaying] = useState(false);

  // ─── Fetch artisan details ─────────────────────────────────
  useEffect(() => {
    if (!artisanId) {
      toast.error('No artisan selected. Please go back and choose an artisan.');
      navigate('/artisans');
      return;
    }
    const fetchArtisan = async () => {
      try {
        const data = await getArtisan(artisanId);
        setArtisan(data);
        setAddress(data.location || '');
      } catch (err) {
        console.error(err);
        toast.error('Failed to load artisan details.');
        navigate('/artisans');
      } finally {
        setLoading(false);
      }
    };
    fetchArtisan();
  }, [artisanId, navigate]);

  // ─── Redirect if not logged in ─────────────────────────────
  useEffect(() => {
    if (!user) {
      toast.error('Please log in to book a service.');
      navigate('/login');
    }
  }, [user, navigate]);

  // ─── Check client profile ─────────────────────────────────
  useEffect(() => {
    if (user && !user.client_profile) {
      toast.error('You need a client profile to book. Please update your profile.');
      navigate('/profile');
    }
  }, [user, navigate]);

  // ─── Handlers ──────────────────────────────────────────────
  const nextStep = () => {
    if (step === 0 && !selectedService) {
      toast.error('Please select a service.');
      return;
    }
    if (step === 1 && (!scheduledDate || !scheduledTime)) {
      toast.error('Please select a date and time.');
      return;
    }
    if (step === 2) {
      handleSubmit();
      return;
    }
    setStep((prev) => Math.min(prev + 1, STEPS.length - 1));
  };

  const prevStep = () => setStep((prev) => Math.max(prev - 1, 0));

  const handleSubmit = async () => {
    console.log('🔵 handleSubmit called');
    if (!user) {
      toast.error('Please log in.');
      navigate('/login');
      return;
    }
    if (!user.client_profile) {
      toast.error('You need a client profile to book. Please update your profile.');
      navigate('/profile');
      return;
    }

    if (!selectedService) {
      toast.error('Please select a service.');
      return;
    }

    const serviceId = selectedService.service_detail?.id || selectedService.service;
    if (!serviceId) {
      toast.error('Invalid service selected.');
      return;
    }

    // ✅ Log the selectedService price
    console.log('💰 selectedService.price:', selectedService.price);

    setIsSubmitting(true);
    try {
      const bookingData = {
        client: user.client_profile.id,
        artisan: artisan.id,
        service: serviceId,
        scheduled_date: scheduledDate,
        scheduled_time: scheduledTime,
        title: `${selectedService.service_detail?.name || 'Service'} with ${artisan.business_name}`,
        description: `Booking for ${selectedService.service_detail?.name || 'service'}`,
        address: address || artisan.location || 'To be confirmed',
        estimated_cost: selectedService.price,
      };

      console.log('📦 Sending booking data:', bookingData);
      const response = await createBooking(bookingData);
      const result = response.data;
      console.log('✅ Booking created:', result);
      console.log('🔑 result.id:', result.id);

      // ✅ Set booking ID and amount – use selectedService.price directly
      const bookingIdValue = result.id || result.pk || result.booking_id;
      if (!bookingIdValue) {
        console.error('❌ No booking ID in response:', result);
        toast.error('Booking created but no ID returned. Please contact support.');
        setIsSubmitting(false);
        return;
      }
      setBookingId(bookingIdValue);
      // ✅ Use the selected service price, not the response's estimated_cost
      const amount = Number(selectedService.price) || 0;
      setBookingAmount(amount);
      console.log('📌 bookingId set to:', bookingIdValue);
      console.log('💰 bookingAmount set to:', amount);

      setStep(3);
      toast.success('Booking created! Please complete payment.');
    } catch (err) {
      console.error('❌ Booking creation failed.', err);
      const errorData = err.response?.data;
      let errorMsg = 'Failed to create booking.';

      if (errorData) {
        if (errorData.__all__) {
          errorMsg = errorData.__all__.join(', ');
        } else if (errorData.non_field_errors) {
          errorMsg = errorData.non_field_errors.join(', ');
        } else if (errorData.detail) {
          errorMsg = errorData.detail;
        } else {
          const messages = Object.entries(errorData)
            .map(([key, value]) => {
              if (Array.isArray(value)) return `${key}: ${value.join(', ')}`;
              return `${key}: ${value}`;
            })
            .join(' | ');
          if (messages) errorMsg = messages;
        }
      }

      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // ─── Payment ──────────────────────────────────────────────
  const handlePaystackRedirect = async () => {
    console.log('🟢 Pay button clicked');
    console.log('📌 bookingId:', bookingId);
    console.log('💰 bookingAmount:', bookingAmount);
    console.log('👤 user:', user);

    // Alert to confirm the function is called
    alert('Pay button clicked! Check console for logs.');

    if (!bookingId) {
      toast.error('No booking to pay for.');
      return;
    }

    if (bookingAmount <= 0) {
      toast.error('Invalid booking amount. Please try again.');
      return;
    }

    setIsPaying(true);

    try {
      console.log('⏳ Calling initiatePayment...');
      const response = await initiatePayment({
        booking_id: bookingId,
        amount: bookingAmount,
        currency: 'GHS',
        description: `Payment for booking #${bookingId}`,
      });

      console.log('📡 Full response:', response);
      console.log('📡 response.data:', response.data);

      // Extract data – sometimes response is already the data
      const data = response.data || response;
      console.log('📡 Extracted data:', data);

      if (!data.authorization_url) {
        console.error('❌ No authorization_url in response:', data);
        toast.error('Payment initiation failed: No redirect URL.');
        setIsPaying(false);
        return;
      }

      console.log('🔗 Redirecting to:', data.authorization_url);
      window.location.href = data.authorization_url;

    } catch (err) {
      console.error('❌ Payment initiation failed:', err);
      console.error('err.response:', err.response);
      console.error('err.response?.data:', err.response?.data);
      const errorMsg = err.response?.data?.error || err.message || 'Could not start payment.';
      toast.error(errorMsg);
      setIsPaying(false);
    }
  };

  if (loading) {
    return (
      <div className="art-book-page art-book-status">
        <div className="art-detail-spinner" aria-hidden="true" />
        <p>Loading artisan details…</p>
      </div>
    );
  }

  if (!artisan) return null;

  // ─── Render ──────────────────────────────────────────────────
  return (
    <div className="art-book-page">
      <div className="art-topline" aria-hidden="true" />

      <div className="art-book-container">
        {/* Header */}
        <div className="art-book-head">
          <button onClick={() => navigate('/artisans')} className="art-book-back">
            <FaArrowLeft /> Back to artisans
          </button>
          <h1 className="art-book-title">
            Book a service<span className="art-book-dot">.</span>
          </h1>
          <p className="art-book-subtitle">
            {artisan.business_name || artisan.full_name} · {artisan.location || 'Location not set'}
          </p>
        </div>

        {/* Step indicator */}
        <div className="art-steps">
          {STEPS.map((s, i) => (
            <div key={s.id} className="art-step-item">
              <div
                className={`art-step-pill ${
                  i === step ? 'art-step-pill--active' : i < step ? 'art-step-pill--done' : ''
                }`}
              >
                <s.icon aria-hidden="true" />
                {s.label}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`art-step-line ${i < step ? 'art-step-line--done' : ''}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="art-book-panel"
          >
            {step === 0 && (
              <div>
                <h2 className="art-book-panel-title">Choose a service</h2>
                <div className="art-service-select-grid">
                  {artisan.service_offerings?.map((offering) => (
                    <button
                      key={offering.id}
                      onClick={() => setSelectedService(offering)}
                      className={`art-service-select-card ${
                        selectedService?.id === offering.id ? 'art-service-select-card--active' : ''
                      }`}
                    >
                      <div className="art-service-select-name">
                        {offering.service_detail?.name || 'Service'}
                      </div>
                      {offering.experience_years > 0 && (
                        <div className="art-service-select-exp">
                          {offering.experience_years}{' '}
                          {offering.experience_years === 1 ? 'year' : 'years'} experience
                        </div>
                      )}
                      <div className="art-service-select-price">
                        ₵{Number(offering.price).toFixed(2)}
                      </div>
                      {!offering.is_available && (
                        <span className="art-service-select-unavailable">Not available</span>
                      )}
                    </button>
                  ))}
                </div>
                {(!artisan.service_offerings || artisan.service_offerings.length === 0) && (
                  <p className="art-book-empty-note">This artisan has no services listed.</p>
                )}
              </div>
            )}

            {step === 1 && (
              <div>
                <h2 className="art-book-panel-title">When do you need it?</h2>
                <div className="art-book-field-grid">
                  <div className="art-book-field">
                    <label className="art-book-label">Date</label>
                    <input
                      type="date"
                      value={scheduledDate}
                      onChange={(e) => setScheduledDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className="art-book-input"
                    />
                  </div>
                  <div className="art-book-field">
                    <label className="art-book-label">Time</label>
                    <input
                      type="time"
                      value={scheduledTime}
                      onChange={(e) => setScheduledTime(e.target.value)}
                      className="art-book-input"
                    />
                  </div>
                </div>
                <div className="art-book-field art-book-field--full">
                  <label className="art-book-label">Address (optional)</label>
                  <input
                    type="text"
                    placeholder="Where should the artisan come?"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    className="art-book-input"
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div>
                <h2 className="art-book-panel-title">Confirm your booking</h2>
                <div className="art-summary">
                  <div className="art-summary-row">
                    <span>Artisan</span>
                    <span className="art-summary-value">
                      {artisan.business_name || artisan.full_name}
                    </span>
                  </div>
                  <div className="art-summary-row">
                    <span>Service</span>
                    <span className="art-summary-value">
                      {selectedService?.service_detail?.name || 'Service'}
                    </span>
                  </div>
                  <div className="art-summary-row">
                    <span>Date & time</span>
                    <span className="art-summary-value">
                      {new Date(scheduledDate).toLocaleDateString()} at {scheduledTime}
                    </span>
                  </div>
                  <div className="art-summary-row">
                    <span>Location</span>
                    <span className="art-summary-value">
                      {address || artisan.location || 'To be confirmed'}
                    </span>
                  </div>
                  <div className="art-summary-row art-summary-row--total">
                    <span>Total</span>
                    <span className="art-summary-total">
                      ₵{Number(selectedService?.price || 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div>
                <h2 className="art-book-panel-title">Complete payment</h2>
                <div className="art-payment-summary">
                  <div className="art-payment-row">
                    <span>Booking ID</span>
                    <span className="art-payment-id">#{bookingId}</span>
                  </div>
                  <div className="art-payment-row">
                    <span>Amount</span>
                    <span className="art-payment-amount">₵{bookingAmount.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  onClick={handlePaystackRedirect}
                  disabled={isPaying || !bookingId}
                  className="art-pay-btn"
                >
                  {isPaying ? (
                    <span className="art-pay-btn-loading">
                      <FaSpinner className="art-spin" />
                      Initializing…
                    </span>
                  ) : (
                    'Pay with Paystack'
                  )}
                </button>

                <button onClick={() => navigate('/dashboard')} className="art-pay-later-btn">
                  Pay later
                </button>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation buttons (only before payment) */}
        {step < 3 && (
          <div className="art-book-nav">
            <button
              onClick={prevStep}
              className={`art-book-nav-back ${step === 0 ? 'art-book-nav-back--hidden' : ''}`}
            >
              Back
            </button>
            <button onClick={nextStep} disabled={isSubmitting} className="art-book-nav-next">
              {step === 2 ? (isSubmitting ? 'Creating…' : 'Confirm booking') : 'Continue'}
              {!isSubmitting && step !== 2 && <FaArrowRight className="text-xs" />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}