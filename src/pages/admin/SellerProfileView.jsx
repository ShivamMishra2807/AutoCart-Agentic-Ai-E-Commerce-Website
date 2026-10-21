import React, { useState } from 'react';
import { CheckCircle2, XCircle, AlertTriangle, FileText, X, MapPin } from 'lucide-react';
import api from '../../services/api';
import LocationPinMap from '../../storefront/LocationPinMap';

const GSTIN = /^\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d]Z[A-Z\d]$/;
export const DOC_LABEL = { AADHAAR: 'Aadhaar (masked)', PAN: 'PAN card', GST_CERTIFICATE: 'GST certificate', ADDRESS_PROOF: 'Address proof', BANK_PROOF: 'Bank proof', STORE_PHOTO: 'Store photo' };
const label = (s) => String(s || '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
const RISK = {
  Low: { ring: 'border-green-500 text-green-700 bg-green-50', word: 'Low risk', hint: 'Documents agree with the form.' },
  Medium: { ring: 'border-amber-500 text-amber-700 bg-amber-50', word: 'Medium risk', hint: 'Some details need a closer look.' },
  Incomplete: { ring: 'border-gray-400 text-gray-700 bg-gray-50', word: 'Incomplete', hint: 'Documents are missing, so risk cannot be judged yet.' },
  High: { ring: 'border-red-500 text-red-700 bg-red-50', word: 'High risk', hint: 'Several details do not match or are missing.' },
};

/** What an admin must confirm before approving, worked out from the real application. Used for the checklist and to guard the Approve button. */
export function readiness(p) {
  const docs = Object.fromEntries((p.documents || []).map((d) => [d.docType, d]));
  const doc = (type, name) => {
    const d = docs[type];
    if (!d) return { name, state: 'bad', note: 'Not uploaded' };
    if (d.ocrStatus && !['DONE', 'NOT_REQUIRED'].includes(d.ocrStatus)) return { name, state: 'warn', note: 'Uploaded, but the text could not be read. Open it and check by eye.' };
    return { name, state: 'ok', note: 'Uploaded and read' };
  };
  const loc = p.store?.latitude != null && p.store?.longitude != null;
  const mism = (p.comparison?.checks || []).filter((c) => c.status === 'mismatch');
  const items = [
    doc('AADHAAR', 'Aadhaar card (masked)'),
    doc('PAN', 'PAN card'),
    ...(docs.GST_CERTIFICATE ? [doc('GST_CERTIFICATE', 'Business licence / GST certificate')] : []),
    ...(docs.STORE_PHOTO ? [doc('STORE_PHOTO', 'Store photo (optional)')] : []),
    { name: 'Store location pinned on the map', state: loc ? 'ok' : 'bad', note: loc ? `${p.store.latitude.toFixed(4)}, ${p.store.longitude.toFixed(4)}` : 'Seller has not set a location' },
    ...(p.gstin ? [{ name: 'GSTIN looks valid', state: GSTIN.test(String(p.gstin || '').toUpperCase()) ? 'ok' : 'warn', note: p.gstin }] : []),
    { name: 'Form agrees with the documents', state: mism.length ? 'bad' : (p.comparison?.checks || []).length ? 'ok' : 'warn', note: mism.length ? `${mism.length} mismatch${mism.length > 1 ? 'es' : ''}: ${mism.map((m) => m.label).join('; ')}` : (p.comparison?.checks || []).length ? 'No mismatches found' : 'Nothing to compare yet' },
  ];
  const blockers = [];
  if (!docs.AADHAAR) blockers.push('Aadhaar');
  if (!docs.PAN) blockers.push('PAN card');
  if (!loc) blockers.push('store location');
  return { items, blockers, passed: items.filter((i) => i.state === 'ok').length, total: items.length };
}

const Card = ({ title, children, className = '' }) => (
  <section className={`bg-white rounded-2xl border border-gray-200 p-5 ${className}`}><h3 className="font-bold text-gray-900 mb-3">{title}</h3>{children}</section>
);
const Row = ({ k, v }) => (v ? <div className="flex gap-3 py-1.5 text-sm"><dt className="w-32 shrink-0 text-gray-500">{k}</dt><dd className="font-medium text-gray-900 break-words min-w-0">{v}</dd></div> : null);
const ICON = { ok: <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0" />, warn: <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />, bad: <XCircle className="w-5 h-5 text-red-600 shrink-0" /> };

export function RiskBadge({ score, category, size = 'lg' }) {
  const r = RISK[category] || RISK.Medium;
  const big = size === 'lg';
  return (
    <div className={`rounded-2xl border-2 ${r.ring} text-center ${big ? 'px-6 py-4 min-w-[150px]' : 'px-3 py-1.5'}`} aria-label={`Risk score ${score} out of 100, ${r.word}`}>
      <div className={`font-extrabold tabular-nums leading-none ${big ? 'text-5xl' : 'text-base'}`}>{score}<span className={big ? 'text-xl font-bold' : 'text-xs font-bold'}>/100</span></div>
      <div className={`font-bold ${big ? 'text-base mt-1' : 'text-xs'}`}>{r.word}</div>
    </div>
  );
}

export default function SellerProfileView({ p }) {
  const [preview, setPreview] = useState(null);
  const [fileErr, setFileErr] = useState('');
  const ready = readiness(p);
  const docs = Object.fromEntries((p.documents || []).map((d) => [d.docType, d]));
  const id = p.identity || {};

  const view = async (doc) => {
    setFileErr('');
    try {
      const fileUrl = doc.fileUrl ? doc.fileUrl.replace(/^\/api/, '') : `/seller/applications/${p.id}/documents/${doc.id}/file`;
      const { data } = await api.get(fileUrl, { responseType: 'blob' });
      setPreview({ url: URL.createObjectURL(data), type: doc.mimeType || data.type, name: DOC_LABEL[doc.docType] || doc.fileName });
    } catch (e) {
      setFileErr(e?.response?.data?.detail || 'This file could not be opened from server storage.');
    }
  };
  const OpenBtn = ({ d }) => (d
    ? <button onClick={() => view(d)} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-semibold whitespace-nowrap hover:bg-gray-50"><FileText className="w-4 h-4" /> Open document</button>
    : <span className="text-sm font-semibold text-red-600">Not uploaded</span>);

  return (
    <div className="space-y-4">
      {/* 1. Who, and how risky */}
      <section className="bg-white rounded-2xl border border-gray-200 p-5 flex flex-wrap items-center gap-5 justify-between">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-wide text-gray-400">Application {p.id}</div>
          <h2 className="text-2xl font-extrabold text-gray-900 truncate">{p.companyName}</h2>
          <p className="text-sm text-gray-600">{p.applicantName} · {p.city}{p.createdAt ? ` · sent ${new Date(p.createdAt).toLocaleDateString()}` : ''}</p>
          <p className="text-sm mt-2"><b>{ready.passed} of {ready.total}</b> checks passed. {ready.blockers.length ? <span className="text-red-700 font-semibold">Missing: {ready.blockers.join(', ')}.</span> : <span className="text-green-700 font-semibold">Ready for a decision.</span>}</p>
          {p.aiAssessment && <p className="text-xs text-gray-500 mt-1 max-w-xl">{p.aiAssessment}</p>}
        </div>
        <RiskBadge score={p.riskScore} category={ready.blockers.length ? 'Incomplete' : p.riskCategory} />
      </section>

      {/* 2. The checklist an admin walks through */}
      <Card title="Before you approve, check each of these">
        <ul className="grid sm:grid-cols-2 gap-x-6">
          {ready.items.map((i) => (
            <li key={i.name} className="flex items-start gap-3 py-2 border-t border-gray-100">
              {ICON[i.state]}<div><div className="font-semibold text-sm text-gray-900">{i.name}</div><div className={`text-xs ${i.state === 'bad' ? 'text-red-600' : i.state === 'warn' ? 'text-amber-700' : 'text-gray-500'}`}>{i.note}</div></div>
            </li>
          ))}
        </ul>
      </Card>
      {fileErr && <div role="alert" className="px-4 py-3 rounded-xl bg-red-50 text-red-800 text-sm">{fileErr}</div>}

      {/* 3. Aadhaar and PAN, side by side */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card title="Aadhaar card">
          <dl>
            <Row k="Number" v={id.aadhaarMasked ? `XXXX XXXX ${String(id.aadhaarMasked).slice(-4)}` : null} />
            <Row k="Name" v={id.name} /><Row k="Date of birth" v={id.dob} /><Row k="Gender" v={id.gender} /><Row k="Address" v={id.address} />
          </dl>
          {!id.aadhaarMasked && !id.name && <p className="text-sm text-gray-500 mb-2">{docs.AADHAAR ? 'Nothing could be read. Open the document and check it by eye.' : 'No Aadhaar was uploaded.'}</p>}
          <div className="mt-2"><OpenBtn d={docs.AADHAAR} /></div>
          <p className="text-xs text-gray-400 mt-3">Only the last 4 digits are stored. A full number is rejected on upload.</p>
        </Card>
        <Card title="PAN card">
          <dl><Row k="PAN number" v={id.pan} /><Row k="Name" v={id.panName} /><Row k="Father's name" v={id.fatherName} /><Row k="Date of birth" v={id.dob} /><Row k="PAN on the form" v={p.pan} /></dl>
          {!id.pan && <p className="text-sm text-gray-500 mb-2">{docs.PAN ? 'Nothing could be read. Open the document and check it by eye.' : 'No PAN card was uploaded.'}</p>}
          <div className="mt-2"><OpenBtn d={docs.PAN} /></div>
        </Card>
      </div>

      {/* 4. Business and where the store is */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card title="Business and contact">
          <dl>
            <Row k="Seller name" v={p.applicantName} /><Row k="Store name" v={p.store?.name} /><Row k="Phone" v={p.phone} /><Row k="Email" v={p.email} />
            <Row k="Business type" v={p.businessType} /><Row k="GSTIN" v={p.gstin} /><Row k="Categories" v={(p.productCategories || []).join(', ')} />
          </dl>
        </Card>
        <Card title="Store location">
          <p className="text-sm text-gray-700 mb-3 flex gap-2"><MapPin className="w-4 h-4 mt-0.5 shrink-0 text-gray-400" />{[p.store?.address, p.store?.city, p.store?.state, p.store?.pincode].filter(Boolean).join(', ') || 'No address'}</p>
          {p.store?.latitude != null ? <LocationPinMap lat={p.store.latitude} lng={p.store.longitude} height={220} /> : <p className="text-sm text-red-600 font-semibold">The seller has not pinned the store on the map.</p>}
        </Card>
      </div>

      {/* 5. Form versus documents */}
      {(p.comparison?.checks || []).length > 0 && (
        <Card title="Do the form and the documents agree?">
          {p.comparison.checks.map((c) => (
            <div key={c.label} className="flex items-start gap-3 py-2 border-t first:border-t-0 border-gray-100 text-sm">
              <span className={`mt-0.5 px-2 py-0.5 rounded-full text-xs font-bold whitespace-nowrap ${c.status === 'match' ? 'bg-green-100 text-green-800' : c.status === 'mismatch' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'}`}>{c.status === 'match' ? 'Matches' : c.status === 'mismatch' ? 'Does not match' : 'Not read'}</span>
              <div><div className="font-medium text-gray-900">{c.label}</div><div className="text-gray-500">{c.detail}</div></div>
            </div>
          ))}
        </Card>
      )}

      {/* 6. Every document */}
      <Card title={`All documents (${p.documents?.length || 0} uploaded)`}>
        {Array.from(new Set([...(p.requiredDocuments || ['AADHAAR', 'PAN']), ...(p.documents || []).map((d) => d.docType)])).map((t) => {
          const d = docs[t];
          return (
            <div key={t} className="flex items-center justify-between gap-3 py-3 border-t first:border-t-0 border-gray-100">
              <div className="min-w-0"><b className="text-sm">{DOC_LABEL[t] || t}</b>{d && <span className="text-xs text-gray-500"> · {d.fileName}</span>}
                {d?.warnings?.map((w) => <div key={w} className="text-xs text-red-600">{w}</div>)}
                {d && <div className="text-xs text-gray-500">Reading: {label(d.ocrStatus)}{d.confidence ? ` · ${d.confidence}% of fields found` : ''}</div>}</div>
              <OpenBtn d={d} />
            </div>
          );
        })}
      </Card>

      <Card title={`Products they plan to sell (${(p.plannedProducts || []).length})`}>
        {(p.plannedProducts || []).length ? (
          <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left text-gray-500"><th className="py-1 pr-4">Product</th><th className="pr-4">Category</th><th>Price</th></tr></thead>
            <tbody>{p.plannedProducts.map((x, i) => <tr key={i} className="border-t border-gray-100"><td className="py-2 pr-4 font-medium">{x.name}</td><td className="pr-4">{x.category || '-'}</td><td>{x.approxPrice ? `₹${x.approxPrice}` : '-'}</td></tr>)}</tbody></table></div>
        ) : <p className="text-sm text-gray-500">No products listed.</p>}
      </Card>

      <Card title="History">
        {(p.auditTrail || []).length === 0 && <p className="text-sm text-gray-500">No decisions yet.</p>}
        <ol className="space-y-2 text-sm">{(p.auditTrail || []).map((a) => (
          <li key={a.id} className="flex gap-3"><span className="text-gray-400 w-40 shrink-0">{new Date(a.timestamp).toLocaleString()}</span>
            <span><b>{label(a.action)}</b> by {a.performedBy}{a.fromStatus ? `, ${label(a.fromStatus)} to ${label(a.toStatus)}` : ''}{a.reason ? `. ${a.reason}` : ''}</span></li>))}</ol>
      </Card>

      {preview && (
        <div className="fixed inset-0 z-[90] bg-black/60 flex items-center justify-center p-4" onClick={() => setPreview(null)} role="dialog" aria-modal="true" aria-label={preview.name}>
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-auto p-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-3">
              <b>{preview.name}</b>
              <div className="flex items-center gap-2">
                <a href={preview.url} target="_blank" rel="noopener noreferrer" className="text-xs px-2.5 py-1 rounded bg-indigo-50 text-indigo-700 font-semibold hover:bg-indigo-100">Open in new tab ↗</a>
                <button onClick={() => setPreview(null)} aria-label="Close"><X className="w-5 h-5" /></button>
              </div>
            </div>
            {String(preview.type).startsWith('image/') ? <img src={preview.url} alt={preview.name} className="w-full rounded-xl" /> : <iframe title={preview.name} src={preview.url} className="w-full h-[70vh] rounded-xl" />}
          </div>
        </div>
      )}
    </div>
  );
}
