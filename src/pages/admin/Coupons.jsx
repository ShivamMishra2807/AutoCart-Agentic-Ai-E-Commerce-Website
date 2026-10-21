import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import Input from '../../components/common/Input';
import Badge from '../../components/common/Badge';
import formatPrice from '../../utils/formatPrice';
import formatDate from '../../utils/formatDate';
import Loader from '../../components/common/Loader';
import { Plus, Ticket, Trash2 } from 'lucide-react';

export const Coupons = () => {
  const [couponList, setCouponList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const [code, setCode] = useState('');
  const [discountType, setDiscountType] = useState('Percentage');
  const [discountValue, setDiscountValue] = useState('');
  const [minOrder, setMinOrder] = useState('');

  useEffect(() => {
    const fetchCoupons = async () => {
      setLoading(true);
      try {
        const data = await adminService.getAllCoupons();
        setCouponList(data);
      } finally {
        setLoading(false);
      }
    };
    fetchCoupons();
  }, []);

  const handleAddCoupon = (e) => {
    e.preventDefault();
    if (!code.trim() || !discountValue) return;

    const newObj = {
      id: `coup-${Date.now()}`,
      code: code.toUpperCase(),
      discountType,
      discountValue: Number(discountValue),
      minOrderAmount: Number(minOrder) || 0,
      maxDiscount: 1000,
      startDate: new Date().toISOString().split('T')[0],
      expiryDate: '2026-12-31',
      usageLimit: 1000,
      usedCount: 0,
      status: 'Active',
      description: `${discountType === 'Percentage' ? `${discountValue}% OFF` : `Flat ₹${discountValue} OFF`} on order`,
    };

    setCouponList([newObj, ...couponList]);
    setCode('');
    setDiscountValue('');
    setMinOrder('');
    setModalOpen(false);
  };

  const handleDelete = (id) => {
    setCouponList(couponList.filter((c) => c.id !== id));
  };

  if (loading) return <Loader fullScreen text="Loading coupons..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Coupon & Discount Management</h1>
          <p className="text-xs text-gray-500 mt-0.5">Create promo codes, minimum order criteria & discount limits</p>
        </div>
        <Button variant="primary" icon={Plus} onClick={() => setModalOpen(true)}>
          Create New Coupon
        </Button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Discount</th>
              <th className="px-4 py-3">Min Order</th>
              <th className="px-4 py-3">Usage</th>
              <th className="px-4 py-3">Expiry Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {couponList.map((coup) => (
              <tr key={coup.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3 font-mono font-bold text-indigo-600 flex items-center gap-1.5">
                  <Ticket className="w-4 h-4 text-indigo-500" /> {coup.code}
                </td>
                <td className="px-4 py-3 font-bold text-gray-900">
                  {coup.discountType === 'Percentage' ? `${coup.discountValue}% OFF` : formatPrice(coup.discountValue)}
                </td>
                <td className="px-4 py-3 font-semibold">{formatPrice(coup.minOrderAmount)}</td>
                <td className="px-4 py-3 text-gray-500">{coup.usedCount} / {coup.usageLimit}</td>
                <td className="px-4 py-3 text-gray-500">{formatDate(coup.expiryDate)}</td>
                <td className="px-4 py-3">
                  <Badge variant={coup.status === 'Active' ? 'green' : 'red'}>{coup.status}</Badge>
                </td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => handleDelete(coup.id)} className="text-red-600 hover:text-red-800">
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Create Discount Coupon">
        <form onSubmit={handleAddCoupon} className="space-y-4">
          <Input
            label="Coupon Code"
            required
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="e.g. DIWALI30"
          />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Discount Type
              </label>
              <select
                value={discountType}
                onChange={(e) => setDiscountType(e.target.value)}
                className="w-full text-sm border rounded-lg p-2.5"
              >
                <option value="Percentage">Percentage (%)</option>
                <option value="Fixed Amount">Fixed Amount (₹)</option>
              </select>
            </div>

            <Input
              label="Discount Value"
              type="number"
              required
              value={discountValue}
              onChange={(e) => setDiscountValue(e.target.value)}
              placeholder={discountType === 'Percentage' ? 'e.g. 20' : 'e.g. 200'}
            />
          </div>

          <Input
            label="Minimum Order Amount (₹)"
            type="number"
            value={minOrder}
            onChange={(e) => setMinOrder(e.target.value)}
            placeholder="e.g. 999"
          />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Coupon</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Coupons;
