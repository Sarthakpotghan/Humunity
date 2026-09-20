import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Logo, MaterialIcon } from '../components/ui';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const homeByRole = (role) => {
    switch (role) {
      case 'ngo': return '/ngo/dashboard';
      case 'admin': return '/admin/dashboard';
      default: return '/donor/dashboard';
    }
  };

  useEffect(() => {
    if (loggedIn && user) {
      const from = location.state?.from?.pathname;
      navigate(from || homeByRole(user.role), { replace: true });
    }
  }, [loggedIn, user, navigate, location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      setLoggedIn(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-10">
      <div className="w-full max-w-md flex flex-col gap-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <Logo size="xl" />
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface">Welcome back</h1>
            <p className="font-body-md text-on-surface-variant mt-1">Sign in to continue donating with Humunity</p>
          </div>
        </div>

        <form className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-6 flex flex-col gap-5" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-error-container text-on-error-container rounded-lg p-3.5 font-body-sm flex items-center gap-2">
              <MaterialIcon name="error" size={18} />
              {error}
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="font-label-md text-on-surface">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="field"
              placeholder="you@example.com"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="font-label-md text-on-surface">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="field"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="text-center font-body-md text-on-surface-variant">
          Don't have an account?{' '}
          <Link to="/register" className="font-label-md text-primary hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}