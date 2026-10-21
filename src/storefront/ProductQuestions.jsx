import React, { useEffect, useState } from 'react';
import api from '../services/api';
import EnquiryForm from './EnquiryForm';
import './storefront.css';
import './forms.css';

/** Public questions and answers for one product, with a form to ask a new one. */
export default function ProductQuestions({ product }) {
  const [rows, setRows] = useState([]);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    if (!product?.id) return;
    api.get(`/product-questions/${product.id}`).then((r) => setRows(r.data)).catch(() => setRows([]));
  }, [product?.id]);

  if (!product) return null;
  return (
    <section className="ac ac-qa" aria-labelledby="qa-h" style={{ marginTop: 56 }}>
      <div className="ac-row-between" style={{ marginBottom: 18 }}>
        <div>
          <h2 id="qa-h" className="ac-display" style={{ fontSize: 30 }}>Questions and answers</h2>
          <p className="ac-muted" style={{ margin: '6px 0 0' }}>{rows.length ? `${rows.length} answered by the seller or our team.` : 'Be the first to ask. The seller or our team will answer.'}</p>
        </div>
        {!asking && <button className="ac-btn ac-btn-blue ac-btn-small" onClick={() => setAsking(true)}>Ask a question</button>}
      </div>

      {asking && <div style={{ marginBottom: 20 }}><EnquiryForm productId={product.id} productName={product.name} /></div>}

      <div className="ac-thread">
        {rows.map((q) => (
          <div className="ac-bubble" key={q.id}>
            <header><b>{q.asker} asked</b></header>
            <p style={{ fontWeight: 600 }}>{q.question}</p>
            <p className="ac-muted" style={{ marginTop: 8 }}><b style={{ color: 'var(--brand)' }}>Answer from {q.answeredBy || 'the seller'}:</b> {q.answer}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
