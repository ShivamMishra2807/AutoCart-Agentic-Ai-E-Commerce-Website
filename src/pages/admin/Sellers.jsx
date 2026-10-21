import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Store, X, ChevronRight } from 'lucide-react';
import api from '../../services/api';
import adminService from '../../services/adminService';
import Badge from '../../components/common/Badge';
import formatPrice from '../../utils/formatPrice';
import Loader from '../../components/common/Loader';
import SellerProfileView, { RiskBadge } from './SellerProfileView';

const Stat = ({ n, label: l, warn }) => (
  <div className={`rounded-xl border p-3 ${warn ? 'border-amber-300 bg-amber-50' : 'border-gray-200 bg-white'}`}><div className="text-2xl font-extrabold tabular-nums text-gray-900">{n}</div><div className="text-xs text-gray-500">{l}</div></div>
);

/** All sellers. Click a row to see the seller's contact, live numbers and the documents they were approved with. */
export const Sellers = () => {
  const [sellerList, setSellerList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [detail, setDetail] = useState(null); // { loading } | data
  const [err, setErr] = useState('');

  useEffect(() => {
    (async () => {
      setLoading(true);
      try { setSellerList(await adminService.getAllSellers()); } finally { setLoading(false); }
    })();
  }, []);

  const openSeller = async (id) => {
    setErr(''); setDetail({ loading: true });
    try { setDetail((await api.get(`/admin/sellers/${id}/detail`)).data); } catch { setDetail(null); setErr('Could not open that seller.'); }
  };

  const filtered = sellerList.filter((s) => `${s.name} ${s.companyName}`.toLowerCase().includes(search.toLowerCase()));
  if (loading) return <Loader fullScreen text="Loading sellers directory..." />;
  const d = detail && !detail.loading ? detail : null;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Sellers</h1>
        <p className="text-sm text-gray-500 mt-0.5">Click a seller to see their details, documents and live numbers. Approvals and rejections happen in Seller applications.</p>
      </div>
      {err && <div role="alert" className="px-4 py-3 rounded-xl bg-red-50 text-red-800 text-sm">{err}</div>}

      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div className="relative w-full sm:w-80">
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search sellers by store name..." aria-label="Search sellers"
            className="w-full pl-9 pr-4 py-2 text-sm border rounded-lg focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider text-xs">
            <tr><th className="px-4 py-3">Store / Company</th><th className="px-4 py-3">City</th><th className="px-4 py-3">Products</th><th className="px-4 py-3">Orders*</th><th className="px-4 py-3">Revenue*</th><th className="px-4 py-3">Status</th><th className="px-4 py-3" /></tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {filtered.map((sel) => (
              <tr key={sel.id} onClick={() => openSeller(sel.id)} onKeyDown={(e) => e.key === 'Enter' && openSeller(sel.id)} tabIndex={0} role="button" aria-label={`Open ${sel.name}`}
                className="hover:bg-indigo-50 cursor-pointer transition focus:outline-none focus:bg-indigo-50">
                <td className="px-4 py-3"><p className="font-bold text-gray-900 flex items-center gap-1.5"><Store className="w-4 h-4 text-indigo-600" /> {sel.name}</p><p className="text-xs text-gray-400">{sel.companyName}</p></td>
                <td className="px-4 py-3">{sel.city}</td>
                <td className="px-4 py-3 font-bold">{sel.productsCount}</td>
                <td className="px-4 py-3 font-bold">{sel.ordersCount}</td>
                <td className="px-4 py-3 font-bold text-gray-900">{formatPrice(sel.totalRevenue)}</td>
                <td className="px-4 py-3"><Badge variant={sel.status === 'Approved' ? 'green' : 'yellow'}>{sel.status}</Badge></td>
                <td className="px-4 py-3 text-right text-indigo-600 font-bold whitespace-nowrap">Details <ChevronRight className="inline w-4 h-4" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500">* Orders and revenue in this list are sample figures stored with each seller. Open a seller to see live numbers worked out from real orders.</p>

      {detail && (
        <div className="fixed inset-0 z-[80] flex justify-end bg-black/40" onClick={() => setDetail(null)} role="dialog" aria-modal="true" aria-label="Seller details">
          <div className="w-full max-w-4xl h-full overflow-y-auto bg-slate-50 p-5 space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-2xl font-extrabold text-gray-900">{d?.seller.companyName || d?.seller.name || 'Loading…'}</h2>
                {d && <p className="text-sm text-gray-600">Seller ID {d.seller.id} · {d.seller.name} · {d.seller.city || 'no city'} · {d.seller.status}{d.seller.joinedDate ? ` · joined ${d.seller.joinedDate}` : ''}</p>}
                {d && <p className="text-sm text-gray-600">{[d.seller.email, d.seller.phone].filter(Boolean).join(' · ') || 'No contact details saved'}</p>}
              </div>
              <button onClick={() => setDetail(null)} aria-label="Close" className="p-2 rounded-lg hover:bg-gray-200"><X className="w-5 h-5" /></button>
            </div>
            {!d && <div className="p-10 text-center text-gray-500">Loading…</div>}
            {d && (
              <>
                <section aria-label="Live numbers">
                  <h3 className="font-bold text-gray-900 mb-2">Live numbers (from real orders)</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                    <Stat n={d.live.products} label="Products live" /><Stat n={d.live.orders} label="Orders with their items" /><Stat n={formatPrice(d.live.revenue)} label="Item sales" />
                    <Stat n={formatPrice(d.live.commission)} label="AutoCart commission" /><Stat n={d.live.lowStock + d.live.outOfStock} label="Low or out of stock" warn={d.live.outOfStock > 0} />
                  </div>
                </section>
                {d.products.length > 0 && (
                  <section className="bg-white rounded-2xl border border-gray-200 p-4">
                    <h3 className="font-bold text-gray-900 mb-2">Products</h3>
                    <ul className="divide-y divide-gray-100 text-sm">{d.products.map((x) => <li key={x.id} className="flex justify-between py-1.5"><span className="truncate pr-3">{x.name}</span><span className="text-gray-600 whitespace-nowrap">{formatPrice(x.price)} · {x.stock} in stock</span></li>)}</ul>
                  </section>
                )}
                {d.application ? (
                  <>
                    <div className="flex items-center gap-3 flex-wrap"><h3 className="font-bold text-gray-900">Onboarding application</h3><RiskBadge score={d.application.riskScore} category={(d.application.documents || []).length < 2 ? 'Incomplete' : d.application.riskCategory} size="sm" />
                      <Link to="/admin/ai-seller-onboarding" className="text-sm font-bold text-indigo-600 underline">Open in Seller applications to decide</Link></div>
                    <SellerProfileView p={d.application} />
                  </>
                ) : <section className="bg-white rounded-2xl border border-dashed border-gray-300 p-6 text-sm text-gray-600">No onboarding application is linked to this seller. They were added directly (sample data), so there are no Aadhaar, PAN or location records to show.</section>}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sellers;
