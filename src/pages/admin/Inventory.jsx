import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import Badge from '../../components/common/Badge';
import formatPrice from '../../utils/formatPrice';
import Loader from '../../components/common/Loader';
import { Search, Save, AlertCircle } from 'lucide-react';

export const Inventory = () => {
  const [productList, setProductList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('All');
  const [editingId, setEditingId] = useState(null);
  const [tempStock, setTempStock] = useState('');

  useEffect(() => {
    const fetchProds = async () => {
      setLoading(true);
      try {
        const data = await adminService.getAllProducts();
        setProductList(data);
      } finally {
        setLoading(false);
      }
    };
    fetchProds();
  }, []);

  const handleEditStock = (prod) => {
    setEditingId(prod.id);
    setTempStock(prod.stock);
  };

  const handleSaveStock = (id) => {
    const qty = Number(tempStock);
    setProductList((prev) =>
      prev.map((p) => {
        if (p.id === id) {
          const status = qty === 0 ? 'Out of Stock' : qty <= 15 ? 'Low Stock' : 'In Stock';
          return { ...p, stock: qty, stockStatus: status };
        }
        return p;
      })
    );
    setEditingId(null);
  };

  const filtered = productList.filter((p) => {
    if (filterStatus === 'In Stock') return p.stock > 15;
    if (filterStatus === 'Low Stock') return p.stock > 0 && p.stock <= 15;
    if (filterStatus === 'Out of Stock') return p.stock === 0;
    return true;
  });

  if (loading) return <Loader fullScreen text="Loading stock inventory..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Inventory & Stock Control</h1>
        <p className="text-xs text-gray-500 mt-0.5">Monitor inventory stock levels, low-stock alerts & update quantities</p>
      </div>

      <div className="flex items-center gap-3 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <span className="text-xs font-bold text-gray-500 uppercase">Stock Filter:</span>
        {['All', 'In Stock', 'Low Stock', 'Out of Stock'].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              filterStatus === st ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">Product Name</th>
              <th className="px-4 py-3">SKU</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Current Stock</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Quick Stock Update</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {filtered.map((prod) => (
              <tr key={prod.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3 font-bold text-gray-900">{prod.name}</td>
                <td className="px-4 py-3 font-mono text-gray-500">{prod.id}</td>
                <td className="px-4 py-3">{prod.category}</td>
                <td className="px-4 py-3 font-extrabold">{formatPrice(prod.price)}</td>
                <td className="px-4 py-3 font-bold">
                  {editingId === prod.id ? (
                    <input
                      type="number"
                      value={tempStock}
                      onChange={(e) => setTempStock(e.target.value)}
                      className="w-20 px-2 py-1 border rounded text-xs focus:ring-1 focus:ring-indigo-500"
                    />
                  ) : (
                    prod.stock
                  )}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={prod.stock === 0 ? 'red' : prod.stock <= 15 ? 'yellow' : 'green'}>
                    {prod.stockStatus}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right">
                  {editingId === prod.id ? (
                    <button
                      onClick={() => handleSaveStock(prod.id)}
                      className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 hover:underline"
                    >
                      <Save className="w-3.5 h-3.5" /> Save
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEditStock(prod)}
                      className="text-xs font-bold text-indigo-600 hover:underline"
                    >
                      Update Stock
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Inventory;
