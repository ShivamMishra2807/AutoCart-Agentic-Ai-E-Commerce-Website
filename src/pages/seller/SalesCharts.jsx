import React from 'react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { money } from '../../storefront/parts';

const BRAND = '#d9480f';
const inr = (v) => money(v);

/** One-line plain-language headline for the revenue chart, from the real numbers. */
function headline(days) {
  const total = days.reduce((s, d) => s + d.revenue, 0);
  if (!total) return 'No sales in the last 30 days yet. Add products and share your store link to get your first order.';
  const best = days.reduce((a, b) => (b.revenue > a.revenue ? b : a));
  const week = days.slice(-7).reduce((s, d) => s + d.revenue, 0);
  const prev = days.slice(-14, -7).reduce((s, d) => s + d.revenue, 0);
  const trend = prev ? ` That is ${week >= prev ? 'up' : 'down'} ${Math.abs(Math.round(((week - prev) / prev) * 100))}% on the week before.` : '';
  return `You sold ${inr(total)} in 30 days. Best day: ${best.label} (${inr(best.revenue)}).${trend}`;
}

/** Sales over time, best sellers, and what the seller keeps after AutoCart's commission. */
export default function SalesCharts({ data }) {
  const { salesByDay: days, topProducts: top, earnings: e, categoryMix: mix } = data;
  const summary = headline(days);
  return (
    <section id="sales" className="ac-box" aria-labelledby="sales-h" style={{ marginTop: 24 }}>
      <h2 id="sales-h">Your sales</h2>
      <p style={{ marginTop: 4, fontWeight: 600 }}>{summary}</p>

      <div className="ac-chartgrid">
        <figure aria-label={`Revenue per day, last 30 days. ${summary}`}>
          <figcaption>Revenue per day (last 30 days)</figcaption>
          <div style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={days} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <defs><linearGradient id="rev" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={BRAND} stopOpacity={0.35} /><stop offset="100%" stopColor={BRAND} stopOpacity={0.02} /></linearGradient></defs>
                <CartesianGrid stroke="#f0e4d8" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 14 }} interval={4} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 14 }} width={56} tickLine={false} axisLine={false} tickFormatter={(v) => (v >= 1000 ? `₹${Math.round(v / 1000)}k` : `₹${v}`)} />
                <Tooltip formatter={(v) => [inr(v), 'Revenue']} />
                <Area type="monotone" dataKey="revenue" stroke={BRAND} strokeWidth={2.5} fill="url(#rev)" animationDuration={700} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </figure>

        <figure aria-label="Your best sellers by revenue">
          <figcaption>{top.length ? `${top[0].name} brings in the most` : 'Best sellers will show here'}</figcaption>
          {top.length ? (
            <div style={{ height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={top} layout="vertical" margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 14 }} tickLine={false} axisLine={false} tickFormatter={(n) => (n.length > 18 ? `${n.slice(0, 17)}…` : n)} />
                  <Tooltip formatter={(v) => [inr(v), 'Revenue']} />
                  <Bar dataKey="revenue" fill={BRAND} radius={[0, 8, 8, 0]} animationDuration={700} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="ac-muted">Nothing sold yet.</p>}
        </figure>
      </div>

      <div className="ac-earn" role="group" aria-label="What you keep after commission">
        <div><small>Sold (item total)</small><b>{inr(e.gross)}</b></div>
        <div><small>AutoCart commission</small><b>− {inr(e.commission)}</b><em>{e.gross ? `${Math.round((e.commission / e.gross) * 100)}% overall` : ''}</em></div>
        {data.profit?.costKnown && <div><small>Profit (after your costs)</small><b>{inr(data.profit.amount)}</b><em>{data.profit.productsWithoutCost?.length ? `${data.profit.productsWithoutCost.length} product(s) have no cost price yet` : 'all products counted'}</em></div>}
        <div data-key="1"><small>You keep</small><b>{inr(e.youKeep)}</b><em>before delivery and online payment charges</em></div>
      </div>
      {mix.length > 0 && <p className="ac-muted" style={{ fontSize: 14, marginTop: 10 }}>Commission by category: {mix.map((m) => `${m.category} ${m.commissionPercent}%`).join(' · ')}.</p>}
    </section>
  );
}
