import { useState, useEffect, useRef, useId } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  FaUser,
  FaLock,
  FaSignInAlt,
  FaEye,
  FaEyeSlash,
  FaExclamationCircle,
} from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

// ─── Role‑based landing pages ──────────────────────────────
const DASHBOARD_ROUTES = {
  AGENT:      "/incidents/new",
  ARTISAN:    "/artisan/dashboard",
  ADMIN:      "/dashboard",
  COMPANY:    "/dashboard",
  DISPATCHER: "/dispatch",
  SUPERVISOR: "/dashboard",
  MANAGER:    "/dashboard",
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Login() {
  const navigate = useNavigate();
  const mountedRef = useRef(true);
  const { login } = useAuth();
  const idPrefix = useId();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  // Check existing session
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const savedType = localStorage.getItem("user_type");
    if (token && savedType && DASHBOARD_ROUTES[savedType]) {
      navigate(DASHBOARD_ROUTES[savedType], { replace: true });
    } else {
      setTimeout(() => {
        if (mountedRef.current) setCheckingAuth(false);
      }, 0);
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !EMAIL_PATTERN.test(trimmedEmail)) {
      setErrorMessage("Enter a valid email address.");
      return;
    }
    if (!password) {
      setErrorMessage("Password is required.");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await login(trimmedEmail, password);
      if (!mountedRef.current) return;

      const userData = response?.user || response;
      const actualType = userData?.user_type || response?.user_type;

      if (!actualType || !DASHBOARD_ROUTES[actualType]) {
        // Fallback: if no valid role, go to /dashboard
        navigate("/dashboard", { replace: true });
        return;
      }

      localStorage.setItem("user_type", actualType);
      navigate(DASHBOARD_ROUTES[actualType], { replace: true });

    } catch (err) {
      if (!mountedRef.current) return;
      const msg = err?.detail || err?.message || "Invalid email or password.";
      setErrorMessage(msg);
    } finally {
      if (mountedRef.current) setIsLoading(false);
    }
  };

  if (checkingAuth) {
    return (
      <div className="session-check" role="status" aria-label="Checking session">
        <div className="session-spinner">
          <div className="session-spinner-ring" />
        </div>
      </div>
    );
  }

  const emailId = `${idPrefix}-email`;
  const passwordId = `${idPrefix}-password`;

  return (
    <div className="login-page">
      <div className="glow-field" aria-hidden="true">
        <div className="glow glow-blue" />
        <div className="glow glow-purple" />
        <div className="glow glow-indigo" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 28, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        className="login-card-wrap"
      >
        <div className="login-card">
          <div className="brand">
            <div className="brand-badge">
              <FaSignInAlt aria-hidden="true" />
            </div>
            <h1>
              Artisan <span className="brand-gradient-text">Marketplace</span>
            </h1>
            <p>Connect with trusted professionals</p>
          </div>

          <h2 className="form-heading">Welcome back</h2>

          <AnimatePresence>
            {errorMessage && (
              <motion.div
                role="alert"
                aria-live="assertive"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="error-banner"
              >
                <FaExclamationCircle aria-hidden="true" />
                <span>{errorMessage}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="login-form" noValidate>
            <div className="field-group">
              <label htmlFor={emailId} className="field-label">Email Address</label>
              <div className="input-wrap">
                <FaUser className="input-icon" aria-hidden="true" />
                <input
                  id={emailId}
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="text-input"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div className="field-group">
              <div className="field-row">
                <label htmlFor={passwordId} className="field-label">Password</label>
                <Link to="/forgot-password" className="forgot-link">
                  Forgot password?
                </Link>
              </div>
              <div className="input-wrap">
                <FaLock className="input-icon" aria-hidden="true" />
                <input
                  id={passwordId}
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  minLength={1}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="text-input has-toggle"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  className="password-toggle"
                >
                  <AnimatePresence mode="wait" initial={false}>
                    {showPassword ? (
                      <motion.span
                        key="hide"
                        initial={{ opacity: 0, rotate: -45, scale: 0.7 }}
                        animate={{ opacity: 1, rotate: 0, scale: 1 }}
                        exit={{ opacity: 0, rotate: 45, scale: 0.7 }}
                        transition={{ duration: 0.15 }}
                        style={{ display: "flex" }}
                      >
                        <FaEyeSlash aria-hidden="true" />
                      </motion.span>
                    ) : (
                      <motion.span
                        key="show"
                        initial={{ opacity: 0, rotate: 45, scale: 0.7 }}
                        animate={{ opacity: 1, rotate: 0, scale: 1 }}
                        exit={{ opacity: 0, rotate: -45, scale: 0.7 }}
                        transition={{ duration: 0.15 }}
                        style={{ display: "flex" }}
                      >
                        <FaEye aria-hidden="true" />
                      </motion.span>
                    )}
                  </AnimatePresence>
                </button>
              </div>
            </div>

            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              aria-busy={isLoading}
              className="submit-btn"
            >
              {isLoading ? (
                <>
                  <span className="spinner" aria-hidden="true" />
                  <span className="sr-only">Signing in…</span>
                </>
              ) : (
                <>
                  <FaSignInAlt aria-hidden="true" />
                  Sign In
                </>
              )}
            </motion.button>
          </form>

          <div className="login-footer">
            <p>
              Don't have an account?{" "}
              <Link to="/register" className="signup-link">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}