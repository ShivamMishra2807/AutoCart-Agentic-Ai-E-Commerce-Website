import React, { useState } from 'react';
import { Check } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import './storefront.css';
import './forms.css';

/** Ask a question about one product (pass productId) or send a general enquiry (leave it out). Guests give a name and email. */
export default function EnquiryForm({ productId = '', productName = '', onSent, placeholder }) {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' });
  const [errors, setErrors] = useState({});
  const [state, setState] = useState('idle'); // idle | sending | sent
  const [error, setError] = useState('');
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setState('sending'); setErrors({}); setError('');
    try {
      await api.post('/enquiries', { ...form, productId });
      setState('sent'); setForm({ name: '', email: '', phone: '', message: '' });
      onSent?.();
    } catch (err) {
      setErrors(err?.response?.data?.errors || {});
      setError(err?.response?.status === 429 ? 'You have sent a lot of questions. Please try again in a while.' : err?.response?.data?.detail || 'We could not send that. Please try again.');
      setState('idle');
    }
  };

  if (state === 'sent') {
    return (
      <div className="ac-box" role="status" style={{ borderColor: 'var(--brand)' }}>
        <b style={{ display: 'flex', gap: 8, alignItems: 'center' }}><Check size={20} color="var(--brand)" /> Question sent</b>
        <p className="ac-muted" style={{ margin: '8px 0 0' }}>
          {user ? 'You will get an email when it is answered.' : 'We will email you the answer as soon as we can.'}
          {productId ? ' If the answer is useful to others, it will appear on this page.' : ''}
        </p>
        <button className="ac-btn ac-btn-outline ac-btn-small" style={{ marginTop: 12 }} onClick={() => setState('idle')}>Ask another question</button>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="ac-box" noValidate>
      <h2>{productId ? `Ask about ${productName || 'this product'}` : 'Send us a question'}</h2>
      <p className="ac-muted" style={{ margin: '0 0 16px' }}>{productId ? 'The seller or our team will answer.' : 'Our team will reply by email.'}</p>
      {error && <div className="ac-warn" role="alert" style={{ marginBottom: 12 }}>{error}</div>}
      {!user && (
        <div className="ac-grid-2" style={{ marginBottom: 16 }}>
          <div className="ac-field"><label htmlFor="enq-name">Your name</label>
            <input id="enq-name" className="ac-input" aria-invalid={!!errors.name} value={form.name} onChange={(e) => set('name', e.target.value)} autoComplete="name" />
            {errors.name && <span className="ac-err" role="alert">{errors.name}</span>}</div>
          <div className="ac-field"><label htmlFor="enq-email">Email</label>
            <input id="enq-email" type="email" className="ac-input" aria-invalid={!!errors.email} value={form.email} onChange={(e) => set('email', e.target.value)} autoComplete="email" />
            {errors.email && <span className="ac-err" role="alert">{errors.email}</span>}</div>
        </div>
      )}
      <div className="ac-field"><label htmlFor="enq-msg">Your question</label>
        <textarea id="enq-msg" className="ac-textarea" aria-invalid={!!errors.message} placeholder={placeholder || (productId ? 'For example: does it come with a warranty?' : 'How can we help?')}
          value={form.message} onChange={(e) => set('message', e.target.value)} />
        {errors.message && <span className="ac-err" role="alert">{errors.message}</span>}</div>
      <div className="ac-field" style={{ marginTop: 16, maxWidth: 320 }}><label htmlFor="enq-phone">Phone (optional)</label>
        <input id="enq-phone" className="ac-input" inputMode="tel" value={form.phone} onChange={(e) => set('phone', e.target.value)} />
        <small>Only the seller or our team will see this.</small></div>
      <button className="ac-btn ac-btn-blue ac-btn-small" style={{ marginTop: 18 }} disabled={state === 'sending'}>{state === 'sending' ? 'Sending…' : 'Send question'}</button>
    </form>
  );
}
