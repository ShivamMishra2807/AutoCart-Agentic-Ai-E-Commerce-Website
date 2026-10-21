import React, { useCallback, useEffect, useState } from 'react';
import {
  CheckCircle2, XCircle, MessageSquareWarning, PauseCircle, RefreshCw,
  Bot, Sparkles, Send, ChevronDown, ChevronUp, ShieldAlert, AlertTriangle,
} from 'lucide-react';
import api from '../../services/api';
import SellerProfileView, { RiskBadge, readiness } from './SellerProfileView';
import '../../storefront/forms.css';

const TABS = [
  ['PENDING_ADMIN_APPROVAL', 'Ready to review'],
  ['NEEDS_MANUAL_REVIEW', 'Needs a closer look'],
  ['NEEDS_MORE_INFORMATION', 'Waiting for seller'],
  ['DRAFT', 'Still filling in'],
  ['APPROVED', 'Approved'],
  ['REJECTED', 'Rejected'],
  ['', 'All'],
];
const TONE = {
  PENDING_ADMIN_APPROVAL: 'bg-blue-100 text-blue-800', NEEDS_MANUAL_REVIEW: 'bg-amber-100 text-amber-800', NEEDS_MORE_INFORMATION: 'bg-orange-100 text-orange-800',
  APPROVED: 'bg-green-100 text-green-800', REJECTED: 'bg-red-100 text-red-800', SUSPENDED: 'bg-gray-200 text-gray-800', DRAFT: 'bg-gray-100 text-gray-700',
};
const label = (s) => (s === 'DRAFT' ? 'Not submitted yet' : String(s || '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase()));

function renderFormattedInline(text) {
  if (!text) return '';
  const parts = [];
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={key++} className="font-semibold text-white">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code key={key++} className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono text-xs border border-indigo-900/50">
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      parts.push(
        <em key={key++} className="italic text-slate-300">
          {token.slice(1, -1)}
        </em>
      );
    }
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

function FormattedAiReply({ text }) {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let currentList = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="list-disc list-inside space-y-1.5 my-2 pl-2 text-slate-200">
          {currentList.map((item, idx) => (
            <li key={idx} className="text-sm leading-relaxed">
              {renderFormattedInline(item)}
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((rawLine, idx) => {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      return;
    }

    const headerMatch = line.match(/^#{1,4}\s+(.+)$/);
    if (headerMatch) {
      flushList();
      elements.push(
        <h4 key={`h-${idx}`} className="font-bold text-sm text-indigo-300 mt-3 mb-1">
          {renderFormattedInline(headerMatch[1])}
        </h4>
      );
      return;
    }

    const bulletMatch = line.match(/^([•\-\*]|\d+\.)\s+(.+)$/);
    if (bulletMatch) {
      currentList.push(bulletMatch[2]);
      return;
    }

    flushList();
    elements.push(
      <p key={`p-${idx}`} className="text-sm text-slate-100 leading-relaxed my-1">
        {renderFormattedInline(line)}
      </p>
    );
  });

  flushList();
  return <div className="space-y-1">{elements}</div>;
}

/** Review one seller application: the facts first (risk, checklist, Aadhaar, PAN, location), then the decision. */
export default function SellerOnboardingAI() {
  const [tab, setTab] = useState('PENDING_ADMIN_APPROVAL');
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [profile, setProfile] = useState(null);
  const [reason, setReason] = useState('');
  const [mode, setMode] = useState(null); // REJECT | REQUEST_INFO | SUSPEND
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState(null);
  const [loadError, setLoadError] = useState('');

  // Agent F: Admin AI Assistant State
  const [aiOpen, setAiOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [aiError, setAiError] = useState('');

  const askAssistant = async (queryText) => {
    const q = (queryText || aiPrompt).trim();
    if (!q) return;
    setAiLoading(true);
    setAiError('');
    try {
      const { data } = await api.post('/ai/admin-assistant', {
        prompt: q,
        applicationId: selected || undefined,
      });
      setAiResult(data);
      setAiOpen(true);
    } catch (e) {
      setAiError(e?.response?.data?.detail || 'Failed to query Admin AI Assistant.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleConfirmAiAction = async (result) => {
    if (!result) return;
    setAiLoading(true);
    setAiError('');
    try {
      const payload = {
        prompt: `confirm ${result.action || ''} ${result.applicationId || ''}`,
        applicationId: result.applicationId,
        action: result.action,
        confirmed: true,
      };
      const { data } = await api.post('/ai/admin-assistant', payload);
      setAiResult(data);
      loadList();
      if (result.applicationId) {
        open(result.applicationId);
      }
    } catch (e) {
      setAiError(e?.response?.data?.detail || e?.response?.data?.reply || 'Failed to execute confirmed action.');
    } finally {
      setAiLoading(false);
    }
  };

  const loadList = useCallback(async () => {
    try {
      const { data } = await api.get('/seller/applications', { params: tab ? { status: tab } : {} });
      setRows(data); setLoadError('');
    } catch (e) { setLoadError(e?.response?.status === 403 ? 'Only administrators can see applications.' : 'Could not load applications.'); }
  }, [tab]);
  useEffect(() => { loadList(); }, [loadList]);

  const open = async (id) => {
    setSelected(id); setMode(null); setReason(''); setProfile(null); setToast(null);
    try { const { data } = await api.get(`/seller/applications/${id}`); setProfile(data); } catch { setToast({ bad: true, text: 'Could not open that application.' }); }
  };

  const decide = async (action) => {
    setBusy(true);
    try {
      const { data } = await api.post(`/admin/seller-applications/${selected}/action`, { action, reason });
      setProfile(data.profile); setMode(null); setReason('');
      setToast({ text: { APPROVE: 'Approved. The seller and store are live.', REJECT: 'Rejected. The seller can see your reason.', REQUEST_INFO: 'Sent back to the seller.', SUSPEND: 'Store suspended.' }[action] });
      loadList();
    } catch (e) { setToast({ bad: true, text: e?.response?.data?.detail || 'That did not work.' }); }
    setBusy(false);
  };

  const p = profile;
  const canDecide = p && ['PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW'].includes(p.status);
  const blockers = p ? readiness(p).blockers : [];

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Seller applications</h1>
          <p className="text-gray-600 text-sm mt-1">Open an application, check every item, then decide. The risk score is only a guide. You make the decision.</p>
        </div>
        <button onClick={loadList} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-sm font-semibold hover:bg-gray-50"><RefreshCw className="w-4 h-4" /> Refresh</button>
      </div>

      {toast && <div role="status" className={`px-4 py-3 rounded-xl text-sm font-semibold ${toast.bad ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'}`}>{toast.text}</div>}
      {loadError && <div role="alert" className="px-4 py-3 rounded-xl bg-red-50 text-red-800 text-sm">{loadError}</div>}

      {/* Admin-only AI Risk Assistant (Agent F) */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 rounded-2xl text-white p-4 shadow-sm border border-indigo-700">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-400/30">
              <Bot className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm tracking-wide">Admin AI Risk Assistant (Agent F)</h3>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Read-Only Advisory
                </span>
              </div>
              <p className="text-xs text-indigo-200">
                Deterministic risk analysis, discrepancy checks, and queue summarization without autonomous actions.
              </p>
            </div>
          </div>
          <button
            onClick={() => setAiOpen(!aiOpen)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-white transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            {aiOpen ? 'Collapse' : 'Ask Agent F'}
            {aiOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {aiOpen && (
          <div className="mt-4 pt-4 border-t border-indigo-700/60 space-y-3">
            {/* Quick Action Chips */}
            <div className="flex flex-wrap gap-2 text-xs">
              <button
                type="button"
                onClick={() => { setAiPrompt('Summarize pending applications'); askAssistant('Summarize pending applications'); }}
                disabled={aiLoading}
                className="px-3 py-1.5 rounded-lg bg-indigo-700/60 hover:bg-indigo-600/60 border border-indigo-500/40 text-indigo-100 disabled:opacity-50"
              >
                📊 Summarize pending
              </button>
              <button
                type="button"
                onClick={() => { setAiPrompt('Which applications have missing documents?'); askAssistant('Which applications have missing documents?'); }}
                disabled={aiLoading}
                className="px-3 py-1.5 rounded-lg bg-indigo-700/60 hover:bg-indigo-600/60 border border-indigo-500/40 text-indigo-100 disabled:opacity-50"
              >
                📑 Missing documents
              </button>
              <button
                type="button"
                onClick={() => { setAiPrompt('Are there discrepancies in applications?'); askAssistant('Are there discrepancies in applications?'); }}
                disabled={aiLoading}
                className="px-3 py-1.5 rounded-lg bg-indigo-700/60 hover:bg-indigo-600/60 border border-indigo-500/40 text-indigo-100 disabled:opacity-50"
              >
                ⚖️ Cross-document discrepancies
              </button>
              <button
                type="button"
                onClick={() => { setAiPrompt('List high-risk applications requiring manual review'); askAssistant('List high-risk applications requiring manual review'); }}
                disabled={aiLoading}
                className="px-3 py-1.5 rounded-lg bg-indigo-700/60 hover:bg-indigo-600/60 border border-indigo-500/40 text-indigo-100 disabled:opacity-50"
              >
                🚨 Manual review list
              </button>
              {selected && (
                <button
                  type="button"
                  onClick={() => {
                    const q = `Explain the risk score for application ${selected}`;
                    setAiPrompt(q);
                    askAssistant(q);
                  }}
                  disabled={aiLoading}
                  className="px-3 py-1.5 rounded-lg bg-amber-600/40 hover:bg-amber-600/60 border border-amber-400/40 text-amber-100 disabled:opacity-50"
                >
                  🔍 Explain risk for {selected}
                </button>
              )}
            </div>

            {/* Input bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                askAssistant();
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Ask about pending queues, risk breakdown, discrepancies (e.g., 'Explain risk for app-123')..."
                className="flex-1 bg-indigo-950/70 border border-indigo-600/50 rounded-xl px-3.5 py-2 text-sm text-white placeholder-indigo-300/60 focus:outline-none focus:border-indigo-400"
              />
              <button
                type="submit"
                disabled={aiLoading || !aiPrompt.trim()}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-semibold text-sm disabled:opacity-50 transition"
              >
                {aiLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Send className="w-4 h-4" /> Ask
                  </>
                )}
              </button>
            </form>

            {aiError && (
              <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-red-200 text-xs">
                {aiError}
              </div>
            )}

            {aiResult && (
              <div className="p-4 rounded-xl bg-slate-900/90 border border-indigo-700/60 text-sm space-y-3">
                <div className="flex items-center justify-between text-xs text-indigo-300">
                  <span className="font-semibold">Analysis Result:</span>
                  {aiResult.toolsExecuted?.length > 0 && (
                    <div className="flex gap-1.5 flex-wrap">
                      {aiResult.toolsExecuted.map((t) => (
                        <span key={t} className="px-2 py-0.5 rounded bg-indigo-800/80 text-[10px] text-indigo-200 font-mono">
                          tool: {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="text-slate-100 font-sans leading-relaxed text-sm">
                  <FormattedAiReply text={aiResult.reply} />
                </div>

                {/* Interactive Confirmation Box */}
                {aiResult.requiresConfirmation && (
                  <div className="p-3.5 rounded-xl bg-amber-950/80 border border-amber-500/70 space-y-3 my-2">
                    <div className="flex items-center gap-2 text-amber-300 font-bold text-xs uppercase tracking-wider">
                      <AlertTriangle className="w-4 h-4 text-amber-400" /> Administrative Confirmation Required
                    </div>
                    <div className="text-xs text-amber-100 leading-relaxed">
                      Please confirm you wish to execute this operation in the live database.
                    </div>
                    <div className="flex items-center gap-2 pt-1">
                      <button
                        type="button"
                        disabled={aiLoading}
                        onClick={() => handleConfirmAiAction(aiResult)}
                        className="px-3.5 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Confirm Execution
                      </button>
                      <button
                        type="button"
                        disabled={aiLoading}
                        onClick={() => setAiResult((prev) => ({ ...prev, requiresConfirmation: false, reply: `${prev.reply}\n\n[Action cancelled by administrator]` }))}
                        className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Interactive Clickable Application Cards */}
                {(aiResult.applications || aiResult.pendingSummary?.applications || aiResult.affectedApplications)?.length > 0 && (
                  <div className="mt-3 space-y-2 pt-2 border-t border-indigo-800/40">
                    <div className="text-xs font-semibold text-indigo-300">
                      Applications ({((aiResult.applications || aiResult.pendingSummary?.applications || aiResult.affectedApplications)).length}) — Click to inspect profile:
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      {(aiResult.applications || aiResult.pendingSummary?.applications || aiResult.affectedApplications).map((app) => (
                        <button
                          key={app.id}
                          type="button"
                          onClick={() => open(app.id)}
                          className={`text-left p-2.5 rounded-lg border transition text-xs flex justify-between items-center group ${
                            selected === app.id
                              ? 'bg-indigo-900 border-indigo-400'
                              : 'bg-slate-800/80 hover:bg-slate-700/80 border-slate-700 hover:border-indigo-500'
                          }`}
                        >
                          <div className="min-w-0 pr-2">
                            <div className="font-semibold text-slate-200 group-hover:text-white truncate">
                              {app.companyName || app.storeName || app.name}
                            </div>
                            <div className="text-[11px] text-slate-400 truncate">
                              {app.applicantName || app.id} · {app.city || 'Kalyan'}
                            </div>
                          </div>
                          <div className="shrink-0 text-right">
                            <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                              Risk {app.riskScore ?? '—'}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Structured Risk Details if returned */}
                {aiResult.riskAnalysis && (
                  <div className="mt-3 p-3 rounded-lg bg-indigo-950/60 border border-indigo-800/60 space-y-2 text-xs">
                    <div className="font-bold text-indigo-200">
                      Score Breakdown (v{aiResult.riskAnalysis.scoringVersion}):
                    </div>
                    {aiResult.riskAnalysis.contributingFactors?.length > 0 ? (
                      <ul className="list-disc list-inside space-y-1 text-slate-200">
                        {aiResult.riskAnalysis.contributingFactors.map((f, i) => (
                          <li key={i}>
                            <span className="font-semibold text-amber-300">{f.factor}</span> (+{f.points} pts): {f.description}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-emerald-300">✓ No risk penalties applied. Baseline score: 10/100 (Low Risk).</div>
                    )}
                  </div>
                )}

                <div className="text-[11px] text-slate-400 border-t border-indigo-800/40 pt-2 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                  Human Decision Mandate: AI Risk Assistant provides advisory synthesis. Final onboarding decisions are performed by human staff.
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex gap-2 flex-wrap">
        {TABS.map(([key, name]) => (
          <button key={key || 'all'} onClick={() => { setTab(key); setSelected(null); setProfile(null); }} aria-pressed={tab === key}
            className={`px-4 py-2 rounded-full text-sm font-semibold border ${tab === key ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-600'}`}>{name}</button>
        ))}
      </div>

      <div className="grid lg:grid-cols-[300px_1fr] gap-5 items-start">
        <div className="bg-white rounded-2xl border border-gray-200 divide-y divide-gray-100 overflow-hidden">
          {rows.length === 0 && <p className="p-5 text-sm text-gray-500">No applications here yet.</p>}
          {rows.map((a) => (
            <button key={a.id} onClick={() => open(a.id)} className={`w-full text-left p-4 hover:bg-gray-50 flex items-center gap-3 ${selected === a.id ? 'bg-indigo-50' : ''}`}>
              <div className="min-w-0 flex-1">
                <b className="text-gray-900 block truncate">{a.companyName}</b>
                <div className="text-sm text-gray-500 truncate">{a.applicantName} · {a.city}</div>
                <div className="mt-1 flex items-center gap-2 flex-wrap">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold whitespace-nowrap ${TONE[a.status] || TONE.DRAFT}`}>{label(a.status)}</span>
                  <span className="text-xs text-gray-500">
                    {a.requiredDocumentCount != null ? a.requiredDocumentCount : Math.min(a.documentCount || 0, 2)} of 2 required documents uploaded
                    {a.optionalDocumentCount > 0 ? ` (${a.optionalDocumentCount} optional)` : ''}
                  </span>
                </div>
              </div>
              <RiskBadge score={a.riskScore} category={(a.requiredDocumentCount != null ? a.requiredDocumentCount : a.documentCount) < 2 ? 'Incomplete' : a.riskCategory} size="sm" />
            </button>
          ))}
        </div>

        <div className="space-y-4 min-w-0">
          {!selected && <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-10 text-center text-gray-500">Choose an application to see the full seller profile.</div>}
          {selected && !p && <div className="bg-white rounded-2xl border border-gray-200 p-10 text-center text-gray-500">Loading…</div>}
          {p && (
            <>
              <section className="bg-white rounded-2xl border-2 border-indigo-200 p-4 sticky top-2 z-10 shadow-sm" aria-label="Decision">
                <div className="flex flex-wrap items-center gap-3 justify-between">
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${TONE[p.status] || TONE.DRAFT}`}>{label(p.status)}</span>
                  {canDecide && !mode && (
                    <div className="flex flex-wrap gap-2">
                      <button disabled={busy || blockers.length > 0} onClick={() => decide('APPROVE')} title={blockers.length ? `Missing: ${blockers.join(', ')}` : ''}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 hover:bg-green-700 text-white font-semibold text-sm disabled:opacity-40 disabled:cursor-not-allowed"><CheckCircle2 className="w-4 h-4" /> Approve and go live</button>
                      <button onClick={() => setMode('REQUEST_INFO')} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold text-sm"><MessageSquareWarning className="w-4 h-4" /> Ask for more</button>
                      <button onClick={() => setMode('REJECT')} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-sm"><XCircle className="w-4 h-4" /> Reject</button>
                    </div>
                  )}
                  {p.status === 'APPROVED' && !mode && <button onClick={() => setMode('SUSPEND')} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-300 text-sm font-semibold"><PauseCircle className="w-4 h-4" /> Suspend store</button>}
                </div>
                {canDecide && blockers.length > 0 && !mode && <p className="text-sm text-red-700 mt-2"><b>Approve is locked.</b> Missing: {blockers.join(', ')}. Use "Ask for more" to request them.</p>}
                {p.rejectionReason && <p className="text-sm text-red-700 mt-2"><b>Reason given:</b> {p.rejectionReason}</p>}
                {mode && (
                  <div className="mt-3 space-y-2">
                    <label htmlFor="reason" className="block text-sm font-semibold text-gray-800">{mode === 'REQUEST_INFO' ? 'What do you need from the seller?' : mode === 'SUSPEND' ? 'Why is the store being suspended?' : 'Why is it being rejected?'} The seller will see this.</label>
                    <textarea id="reason" value={reason} onChange={(e) => setReason(e.target.value)} rows={3} className="w-full rounded-xl border border-gray-300 p-3 text-sm" />
                    <div className="flex gap-2">
                      <button disabled={busy || !reason.trim()} onClick={() => decide(mode)} className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-sm disabled:opacity-50">Confirm</button>
                      <button onClick={() => { setMode(null); setReason(''); }} className="px-4 py-2 rounded-xl border border-gray-300 text-sm font-semibold">Cancel</button>
                    </div>
                  </div>
                )}
              </section>
              <SellerProfileView p={p} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
