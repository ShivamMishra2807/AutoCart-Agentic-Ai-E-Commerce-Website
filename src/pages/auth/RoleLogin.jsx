import RoleTabs from './RoleTabs';
import React, { useEffect, useState } from 'react';
import { Link, Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { ShieldCheck, Store, ClipboardCheck, LifeBuoy, PackageCheck, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import api from '../../services/api';
import { BrandLink } from '../../storefront/Brand';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

const CONFIG = {
  admin: {
    title: 'Admin sign in', kicker: 'AutoCart console', landing: '/admin', allowed: ['ADMIN', 'STAFF'], Icon: ShieldCheck,
    pitch: 'Run the marketplace',
    points: [[ClipboardCheck, 'Review seller applications and documents'], [LifeBuoy, 'Answer support tickets and customer questions'], [PackageCheck, 'Watch orders, stock and payments']],
    wrong: 'This account is not an administrator. Customers sign in on the main sign-in page.',
    demo: ['admin@auracart.com', 'admin123'],
  },
  seller: {
    title: 'Seller sign in', kicker: 'AutoCart seller centre', landing: '/seller/dashboard', allowed: ['SELLER', 'ADMIN'], Icon: Store,
    pitch: 'Sell to shoppers near you',
    points: [[Store, 'See your store on the nearby-store map'], [LifeBuoy, 'Answer customer questions about your products'], [PackageCheck, 'Track your stock and orders']],
    wrong: 'This account is not an approved seller yet.',
    demo: null,
  },
};

export default function RoleLogin({ role }) {
  const cfg = CONFIG[role];
  const { login, logout, register: signUp, user } = useAuth();
  const [params] = useSearchParams();
  // The seller page has two modes: sign in, or create a seller account (then upload documents to apply).
  const [mode, setMode] = useState(role === 'seller' && params.get('mode') === 'create' ? 'create' : 'signin');
  const effectiveMode = role === 'seller' ? mode : 'signin';
  const [form, setForm] = useState({ name: '', phone: '', confirm: '' });
  const navigate = useNavigate();
  const { state } = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(state?.denied ? cfg.wrong : '');

  useEffect(() => {
    document.title = `${cfg.title} | AutoCart`;
    if (role !== 'seller') {
      setMode('signin');
    } else if (params.get('mode') === 'create') {
      setMode('create');
    }
    setError('');
  }, [role, params, cfg.title]);

  if (user && cfg.allowed.includes(user.role) && !busy) return <Navigate to={state?.from?.pathname || cfg.landing} replace />;

  const createAccount = async (e) => {
    e.preventDefault();
    const bad = !form.name.trim() ? 'Enter your full name.' : !/^[6-9]\d{9}$/.test(form.phone.replace(/\D/g, '').slice(-10)) ? 'Enter a 10-digit mobile number.' : password.length < 6 ? 'Choose a password of at least 6 characters.' : password !== form.confirm ? 'The two passwords do not match.' : '';
    if (bad) { setError(bad); return; }
    setBusy(true); setError('');
    try {
      try {
        await signUp({ name: form.name.trim(), email: email.trim(), phone: form.phone.replace(/\D/g, '').slice(-10), password });
      } catch (signErr) {
        const msg = String(signErr?.response?.data?.detail || signErr?.message || '');
        if (msg.toLowerCase().includes('already exists')) {
          // Existing customer account: authenticate with password to proceed to seller onboarding
          try {
            await login(email.trim(), password);
          } catch (loginErr) {
            setError('An account with this email already exists. Please verify your password to continue, or click Sign In.');
            setBusy(false);
            return;
          }
        } else {
          throw signErr;
        }
      }
      await api.post('/seller/applications/start');  // the admin can now see this sign-up
      navigate('/seller/apply', { replace: true });  // next: store details and documents (Aadhaar, PAN)
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'We could not create your account. This email may already be registered. Try signing in.');
      setBusy(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError('');
    try {
      const data = await login(email.trim(), password);
      if (!cfg.allowed.includes(data.user.role)) { logout(); setError(cfg.wrong); setBusy(false); return; }
      navigate(state?.from?.pathname || cfg.landing, { replace: true });
    } catch (err) {
      setError(err?.response?.status === 429 ? 'Too many tries. Please wait a minute and try again.' : err?.response?.data?.detail || 'We could not sign you in. Check your email and password.');
      setBusy(false);
    }
  };

  return (
    <div className="ac ac-rolelogin">
      <aside className="ac-rl-side">
        <BrandLink />
        <div>
          <p className="ac-rl-kicker">{cfg.kicker}</p>
          <h1 className="ac-display">{cfg.pitch}.</h1>
          <ul>{cfg.points.map(([Icon, text]) => <li key={text}><Icon size={20} /> {text}</li>)}</ul>
        </div>
        <small>{role === 'admin' ? 'Staff only. Every action is recorded.' : 'Free to join. You only pay a small commission when you sell.'}</small>
      </aside>

      <main className="ac-rl-main">
        <RoleTabs current={role} />
        {role === 'seller' && (
          <div role="tablist" aria-label="Seller account" className="ac-rl-modes">
            <button role="tab" type="button" aria-selected={mode === 'signin'} onClick={() => { setMode('signin'); setError(''); }}>Sign in</button>
            <button role="tab" type="button" aria-selected={mode === 'create'} onClick={() => { setMode('create'); setError(''); }}>Create seller account</button>
          </div>
        )}
        {effectiveMode === 'create' ? (
          <form className="ac-rl-card" onSubmit={createAccount} noValidate>
            <cfg.Icon size={34} color="var(--brand)" />
            <h2 className="ac-display">Create your seller account</h2>
            <p className="ac-muted" style={{ margin: '6px 0 18px' }}>Step 1 of 2. Next you add your store details and upload your Aadhaar (masked) and PAN. Our team reviews them before your store goes live.</p>
            {error && <div className="ac-box" role="alert" style={{ borderColor: 'var(--coral)', color: 'var(--coral)', marginBottom: 16, padding: 14, fontWeight: 600 }}>{error}</div>}
            <div className="ac-field"><label htmlFor="sr-name">Full name</label>
              <input id="sr-name" className="ac-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} autoComplete="name" required /></div>
            <div className="ac-field" style={{ marginTop: 12 }}><label htmlFor="sr-email">Email</label>
              <input id="sr-email" type="email" className="ac-input" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required /></div>
            <div className="ac-field" style={{ marginTop: 12 }}><label htmlFor="sr-phone">Mobile number</label>
              <input id="sr-phone" className="ac-input" inputMode="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} autoComplete="tel" required /></div>
            <div className="ac-field" style={{ marginTop: 12 }}><label htmlFor="sr-pw">Password</label>
              <input id="sr-pw" type={show ? 'text' : 'password'} className="ac-input" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" required /></div>
            <div className="ac-field" style={{ marginTop: 12 }}><label htmlFor="sr-pw2">Confirm password</label>
              <input id="sr-pw2" type={show ? 'text' : 'password'} className="ac-input" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} autoComplete="new-password" required /></div>
            <label className="ac-check" style={{ marginTop: 10 }}><input type="checkbox" checked={show} onChange={(e) => setShow(e.target.checked)} /><span>Show passwords</span></label>
            <button className="ac-btn ac-btn-blue" style={{ width: '100%', marginTop: 18 }} disabled={busy}>{busy ? 'Creating…' : 'Create account and continue'}</button>
            <div className="ac-rl-links">
              <button type="button" className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={() => { setMode('signin'); setError(''); }}>Already have a seller account? Sign in</button>
              <Link to="/">Back to the store</Link>
            </div>
          </form>
        ) : (
        <form className="ac-rl-card" onSubmit={submit} noValidate>
          <cfg.Icon size={34} color="var(--brand)" />
          <h2 className="ac-display">{cfg.title}</h2>
          <p className="ac-muted" style={{ margin: '6px 0 22px' }}>{role === 'admin' ? 'Use your administrator account.' : 'Use the account you applied with.'}</p>
          {error && <div className="ac-box" role="alert" style={{ borderColor: 'var(--coral)', color: 'var(--coral)', marginBottom: 16, padding: 14, fontWeight: 600 }}>{error}</div>}
          <div className="ac-field"><label htmlFor="rl-email">Email</label>
            <input id="rl-email" type="email" className="ac-input" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" required /></div>
          <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="rl-pw">Password</label>
            <div style={{ position: 'relative' }}>
              <input id="rl-pw" type={show ? 'text' : 'password'} className="ac-input" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required style={{ paddingRight: 48 }} />
              <button type="button" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'} className="ac-eye">{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
            </div></div>
          <button className="ac-btn ac-btn-blue" style={{ width: '100%', marginTop: 22 }} disabled={busy || !email || !password}>{busy ? 'Signing in…' : 'Sign in'}</button>
          {import.meta.env.DEV && cfg.demo && (
            <button type="button" className="ac-textlink" style={{ border: 0, background: 'none', marginTop: 14, display: 'block' }} onClick={() => { setEmail(cfg.demo[0]); setPassword(cfg.demo[1]); }}>Fill the demo account (development only)</button>
          )}
          <div className="ac-rl-links">
            {role === 'seller' && <button type="button" className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={() => { setMode('create'); setError(''); }}>New seller? Create an account</button>}
            <Link to="/login">Customer sign in</Link>
            <Link to="/">Back to the store</Link>
          </div>
        </form>
        )}
      </main>
    </div>
  );
}
