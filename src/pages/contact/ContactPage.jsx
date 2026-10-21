import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import EnquiryForm from '../../storefront/EnquiryForm';
import { openAssistant } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

export default function ContactPage() {
  useEffect(() => { document.title = 'Contact us | AutoCart'; }, []);
  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 820 }}>
      <h1 className="ac-display">Contact us</h1>
      <p className="ac-sub">Ask us anything about products, orders or selling on AutoCart. You do not need an account.</p>
      <div style={{ marginTop: 28 }}><EnquiryForm placeholder="How can we help?" /></div>
      <div className="ac-box" style={{ marginTop: 20 }}>
        <h2>Need an answer right now?</h2>
        <p className="ac-muted">The assistant can find products, check stock near you and look up your orders at any time. Signed-in customers can also open a support ticket and get a reply from a person.</p>
        <div className="ac-row">
          <button className="ac-btn ac-btn-blue ac-btn-small" onClick={openAssistant}>Ask the assistant</button>
          <Link to="/support" className="ac-btn ac-btn-outline ac-btn-small">My support tickets</Link>
        </div>
      </div>
    </div></div>
  );
}
