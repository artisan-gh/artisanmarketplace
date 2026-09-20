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
  FaShieldAlt,
  FaBolt,
  FaUsers,
  FaCheckCircle,
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

const HIGHLIGHTS = [
  {
    icon: FaShieldAlt,
    title: "Verified artisans",
    text: "Every professional is vetted and identity-checked.",
  },
  {
    icon: FaBolt,
    title: "Instant matching",
    text: "Get connected with the right pro in seconds.",
  },
  {
    icon: FaUsers,
    title: "Trusted community",
    text: "Thousands of jobs completed across Ghana.",
  },
];

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
      <div className="am-session-check" role="status" aria-label="Checking session">
        <span className="am-spinner am-spinner--lg" />
      </div>
    );
  }

  const emailId = `${idPrefix}-email`;
  const passwordId = `${idPrefix}-password`;

  return (
    <div className="am-login">
      <div className="am-login__glow am-login__glow--a" aria-hidden="true" />
      <div className="am-login__glow am-login__glow--b" aria-hidden="true" />

      <motion.div
        className="am-shell"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* SIDEBAR */}
        <aside className="am-sidebar">
          <Link to="/" className="am-brand">
            <div className="am-brand__mark">
              <FaSignInAlt />
            </div>
            <div className="am-brand__text">
              <strong>Artisan</strong>
              <span>Marketplace</span>
            </div>
          </Link>

          <div className="am-sidebar__intro">
            <h2>Welcome back</h2>
            <p>
              Sign in to manage your jobs, track earnings, and connect with
              clients across Ghana.
            </p>
          </div>

          <ul className="am-highlights">
            {HIGHLIGHTS.map(({ icon: Icon, title, text }) => (
              <li key={title} className="am-highlight">
                <span className="am-highlight__icon">
                  <Icon />
                </span>
                <div>
                  <strong>{title}</strong>
                  <span>{text}</span>
                </div>
              </li>
            ))}
          </ul>

          <div className="am-sidebar__footer">
            <FaShieldAlt />
            <span>256-bit encrypted · Secure sign in</span>
          </div>
        </aside>

        {/* MAIN */}
        <main className="am-main am-main--login">
          <header className="am-main__header">
            <div className="am-main__heading">
              <span className="am-eyebrow">Sign in</span>
              <h1>Access your account</h1>
              <p>Enter your credentials to continue.</p>
            </div>

            <Link to="/register" className="am-signin-link">
              Create account
            </Link>
          </header>

          <AnimatePresence>
            {errorMessage && (
              <motion.div
                role="alert"
                aria-live="assertive"
                className="am-alert"
                initial={{ opacity: 0, y: -8, height: 0 }}
                animate={{ opacity: 1, y: 0, height: "auto" }}
                exit={{ opacity: 0, y: -8, height: 0 }}
              >
                <FaExclamationCircle aria-hidden="true" />
                <span>{errorMessage}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="am-form" noValidate>
            <div className="am-field">
              <label htmlFor={emailId}>Email address</label>
              <div className="am-input has-icon">
                <span className="am-input__icon">
                  <FaUser aria-hidden="true" />
                </span>
                <input
                  id={emailId}
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div className="am-field">
              <div className="am-field__row">
                <label htmlFor={passwordId}>Password</label>
                <Link to="/forgot-password" className="am-link">
                  Forgot password?
                </Link>
              </div>
              <div className="am-input has-icon has-trailing">
                <span className="am-input__icon">
                  <FaLock aria-hidden="true" />
                </span>
                <input
                  id={passwordId}
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  minLength={1}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  className="am-input__action"
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
              whileHover={{ scale: isLoading ? 1 : 1.01 }}
              whileTap={{ scale: 0.98 }}
              aria-busy={isLoading}
              className="am-btn am-btn--primary am-btn--cta am-btn--block"
            >
              {isLoading ? (
                <>
                  <span className="am-spinner am-spinner--sm" aria-hidden="true" />
                  <span>Signing in…</span>
                </>
              ) : (
                <>
                  Sign in
                  <FaSignInAlt aria-hidden="true" />
                </>
              )}
            </motion.button>
          </form>

          <div className="am-footnote am-footnote--center">
            <FaCheckCircle />
            <span>Your credentials are encrypted end-to-end.</span>
          </div>

          <div className="am-login__signup">
            <p>
              Don&apos;t have an account?{" "}
              <Link to="/register" className="am-link am-link--strong">
                Sign up
              </Link>
            </p>
          </div>
        </main>
      </motion.div>

      <footer className="am-page-footer">
        <span>© {new Date().getFullYear()} Artisan Marketplace</span>
        <span>Professional services made simple.</span>
      </footer>
    </div>
  );
}