import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";

/*
  Note: the illustration on the left is not available as a real asset from
  the design file. It has been recreated as a lightweight SVG scene (a
  farmer silhouette carrying a tool over green fields) with the same soft
  blur treatment as the original mockup. Replace `FarmerIllustration` with
  the real artwork when available.
*/
export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [resetSent, setResetSent] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    if (!userId.trim() || !password.trim()) {
      setError("Enter both your User ID and Password to continue.");
      return;
    }
    setError("");
    onLogin({ userId, rememberMe });
    navigate("/dashboard");
  }

  return (
    <div className="login-page">
      <div className="login-illustration">
        <img src="/farmer-field.jpeg" alt="Farmer working in a field" className="login-illustration-image" />
      </div>

      <div className="login-card-wrap">
        <div className="login-card">
          <div className="login-card-spacer" />

          <h1 className="login-title">Login</h1>
          <p className="login-subtitle">
            Enter your credentials to continue. Your access level is set by your account.
          </p>

          <form onSubmit={handleSubmit} noValidate>
            <label className="login-field">
              <span className="sr-only">User ID</span>
              <input
                type="text"
                placeholder="User ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                autoComplete="username"
              />
            </label>

            <label className="login-field">
              <span className="sr-only">Password</span>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </label>

            {error && <p className="login-error">{error}</p>}

            <label className="login-remember">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              Remember me
            </label>

            <button
              type="button"
              className="login-forgot"
              onClick={() => setResetSent(true)}
            >
              Forgot Password ? Sign in here
            </button>
            {resetSent && (
              <p className="login-reset-note">
                If an account matches this User ID, password reset instructions have been sent.
              </p>
            )}

            <button type="submit" className="login-submit">
              Login
            </button>
          </form>

          <p className="login-footer">Ministry of Agriculture (INDIA) &bull; All rights reserved</p>
        </div>
      </div>
    </div>
  );
}
