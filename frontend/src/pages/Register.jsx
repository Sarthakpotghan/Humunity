import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Logo, MaterialIcon } from '../components/ui';

export default function Register() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'donor',
    phone: '',
    address: '',
  });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setNotice('');
    setLoading(true);
    try {
      await register(formData);
      setNotice('Account created — you can now sign in.');
      setTimeout(() => navigate('/login', { replace: true }), 1200);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-10">
      <div className="w-full max-w-md flex flex-col gap-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <Logo size="xl" />
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface">Create your account</h1>
            <p className="font-body-md text-on-surface-variant mt-1">Join the community matching surplus to needs</p>
          </div>
        </div>

        <form className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-6 flex flex-col gap-4" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-error-container text-on-error-container rounded-lg p-3.5 font-body-sm flex items-center gap-2">
              <MaterialIcon name="error" size={18} />
              {error}
            </div>
          )}
          {notice && (
            <div className="bg-tertiary-container text-on-tertiary-container rounded-lg p-3.5 font-body-sm flex items-center gap-2">
              <MaterialIcon name="check_circle" size={18} />
              {notice}
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label htmlFor="role" className="font-label-md text-on-surface">I am a...</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { value: 'donor', label: 'Donor', icon: 'volunteer_activism', desc: 'Giving items' },
                { value: 'ngo', label: 'NGO', icon: 'groups', desc: 'Receiving supplies' },
              ].map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, role: r.value })}
                  className={`flex flex-col items-center gap-1 rounded-lg p-4 transition-colors border-2 ${
                    formData.role === r.value
                      ? 'bg-tertiary-container/40 border-tertiary text-on-surface'
                      : 'bg-surface-container-low border-transparent text-on-surface-variant'
                  }`}
                >
                  <MaterialIcon name={r.icon} size={24} />
                  <span className="font-label-md">{r.label}</span>
                  <span className="font-label-sm">{r.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="name" className="font-label-md text-on-surface">Full Name</label>
            <input id="name" name="name" type="text" autoComplete="name" required value={formData.name} onChange={handleChange} className="field" placeholder="Full name" />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="font-label-md text-on-surface">Email address</label>
            <input id="email" name="email" type="email" autoComplete="email" required value={formData.email} onChange={handleChange} className="field" placeholder="you@example.com" />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="font-label-md text-on-surface">Password</label>
            <input id="password" name="password" type="password" autoComplete="new-password" required minLength={8} value={formData.password} onChange={handleChange} className="field" placeholder="At least 8 characters" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="phone" className="font-label-md text-on-surface">Phone (optional)</label>
              <input id="phone" name="phone" type="tel" autoComplete="tel" value={formData.phone} onChange={handleChange} className="field" placeholder="+91 ..." />
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="address" className="font-label-md text-on-surface">Address (optional)</label>
              <input id="address" name="address" type="text" autoComplete="street-address" value={formData.address} onChange={handleChange} className="field" placeholder="City, area" />
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3">
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p className="text-center font-body-md text-on-surface-variant">
          Already have an account?{' '}
          <Link to="/login" className="font-label-md text-primary hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}