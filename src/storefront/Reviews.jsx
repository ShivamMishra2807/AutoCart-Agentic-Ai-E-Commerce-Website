import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BadgeCheck, Star } from 'lucide-react';
import api from '../services/api';
import { count } from './parts';
import './storefront.css';
import './forms.css';

export const Stars = ({ value, size = 16 }) => (
  <span className="ac-starrow" role="img" aria-label={`${value} out of 5 stars`}>
    {[1, 2, 3, 4, 5].map((n) => <Star key={n} size={size} fill={n <= Math.round(value) ? 'currentColor' : 'none'} />)}
  </span>
);

const day = (d) => new Date(d).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });

/** Customer reviews for one product: summary, list, and a form to write one. */
export default function Reviews({ productId, signedIn }) {
  const [data, setData] = useState(null);
  const [writing, setWriting] = useState(false);
  const [form, setForm] = useState({ rating: 0, title: '', body: '' });
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(() => api.get(`/reviews/${productId}`).then((r) => {
    setData(r.data);
    if (r.data.mine) setForm({ rating: r.data.mine.rating, title: r.data.mine.title, body: r.data.mine.body });
  }).catch(() => setData({ count: 0, average: null, distribution: {}, reviews: [], error: true })), [productId]);
  useEffect(() => { setData(null); setWriting(false); load(); }, [load]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setErrors({}); setError('');
    try { await api.post(`/reviews/${productId}`, form); setWriting(false); await load(); }
    catch (err) { setErrors(err?.response?.data?.errors || {}); setError(err?.response?.data?.detail || 'We could not save your review.'); }
    setBusy(false);
  };

  if (!data) return <div className="ac-skel" style={{ height: 200, marginTop: 56 }} />;
  const total = data.count || 0;

  return (
    <section className="ac-reviews" id="reviews" aria-labelledby="rev-h">
      <div className="ac-row-between" style={{ marginBottom: 24 }}>
        <h2 id="rev-h" className="ac-display" style={{ fontSize: 32 }}>Customer reviews</h2>
        {!writing && (signedIn
          ? <button className="ac-btn ac-btn-outline ac-btn-small" onClick={() => setWriting(true)}>{data.mine ? 'Edit your review' : 'Write a review'}</button>
          : <Link to="/login" className="ac-btn ac-btn-outline ac-btn-small">Sign in to review</Link>)}
      </div>

      {total > 0 ? (
        <div className="ac-rev-top">
          <div className="ac-rev-score"><b>{data.average}</b><Stars value={data.average} size={20} /><span className="ac-muted">{count.format(total)} review{total > 1 ? 's' : ''} on AutoCart</span></div>
          <div className="ac-rev-bars">
            {[5, 4, 3, 2, 1].map((n) => {
              const c = data.distribution[String(n)] || 0;
              return <div key={n}><span>{n}</span><Star size={13} fill="currentColor" /><i><u style={{ width: `${(c / total) * 100}%` }} /></i><em>{c}</em></div>;
            })}
          </div>
        </div>
      ) : (
        <div className="ac-box" style={{ textAlign: 'center', padding: 36 }}>
          <Star size={36} color="var(--gold)" />
          <h3 style={{ margin: '10px 0 4px', fontSize: 20 }}>No reviews yet</h3>
          <p className="ac-muted" style={{ margin: 0 }}>Bought this? Help the next shopper by sharing what you think.</p>
        </div>
      )}

      {writing && (
        <form className="ac-box" onSubmit={submit} noValidate style={{ marginTop: 20 }}>
          <h3 style={{ margin: 0, fontSize: 20 }}>{data.mine ? 'Edit your review' : 'Write your review'}</h3>
          <p className="ac-muted" style={{ margin: '6px 0 16px', fontSize: 14 }}>{data.verifiedBuyer ? 'You bought this on AutoCart, so your review gets a Verified buyer badge.' : 'Your review will show without a Verified buyer badge, because we cannot find this product in your orders.'}</p>
          {error && <div className="ac-warn" role="alert" style={{ marginBottom: 10 }}>{error}</div>}
          <div className="ac-field"><label id="rv-r">Your rating</label>
            <div className="ac-starpick" role="radiogroup" aria-labelledby="rv-r">
              {[1, 2, 3, 4, 5].map((n) => (
                <button type="button" key={n} role="radio" aria-checked={form.rating === n} aria-label={`${n} star${n > 1 ? 's' : ''}`} data-on={n <= form.rating} onClick={() => setForm({ ...form, rating: n })}><Star size={30} fill={n <= form.rating ? 'currentColor' : 'none'} /></button>))}
            </div>
            {errors.rating && <span className="ac-err" role="alert">{errors.rating}</span>}</div>
          <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="rv-t">Headline (optional)</label>
            <input id="rv-t" className="ac-input" maxLength={120} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="The short version" /></div>
          <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="rv-b">Your review</label>
            <textarea id="rv-b" className="ac-textarea" aria-invalid={!!errors.body} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} placeholder="What did you like or not like? How are you using it?" />
            {errors.body && <span className="ac-err" role="alert">{errors.body}</span>}</div>
          <div className="ac-row" style={{ marginTop: 16 }}>
            <button className="ac-btn ac-btn-blue ac-btn-small" disabled={busy}>{busy ? 'Saving…' : 'Post review'}</button>
            <button type="button" className="ac-btn ac-btn-outline ac-btn-small" onClick={() => setWriting(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="ac-revlist">
        {data.reviews.map((r) => (
          <article key={r.id} className="ac-rev">
            <div className="ac-row-between"><div className="ac-row" style={{ gap: 10 }}><span className="ac-avatar-sm" aria-hidden="true">{r.name[0]}</span><b>{r.name}</b>
              {r.verified && <span className="ac-chip-status" data-tone="ok"><BadgeCheck size={13} />&nbsp;Verified buyer</span>}</div><span className="ac-muted" style={{ fontSize: 14 }}>{day(r.createdAt)}</span></div>
            <div style={{ margin: '10px 0 4px' }}><Stars value={r.rating} /></div>
            {r.title && <b style={{ display: 'block', marginBottom: 4 }}>{r.title}</b>}
            <p style={{ margin: 0, lineHeight: 1.65, whiteSpace: 'pre-wrap' }}>{r.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
