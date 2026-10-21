import React, { useState } from 'react';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { Save, Store, CreditCard, Bell, Shield } from 'lucide-react';

export const Settings = () => {
  const [storeName, setStoreName] = useState('AuraCart India');
  const [email, setEmail] = useState('support@auracart.in');
  const [phone, setPhone] = useState('+91 1800-123-4567');
  const [currency, setCurrency] = useState('INR (₹)');
  const [taxRate, setTaxRate] = useState('18');
  const [shippingFee, setShippingFee] = useState('40');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">System & Store Settings</h1>
        <p className="text-xs text-gray-500 mt-0.5">Configure store info, tax rules, delivery settings & admin options</p>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-bold border border-emerald-200">
          ✓ Store settings updated successfully!
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Store Information */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
          <h3 className="text-base font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
            <Store className="w-5 h-5 text-indigo-600" /> Store Profile & Contact
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Store Name" value={storeName} onChange={(e) => setStoreName(e.target.value)} />
            <Input label="Support Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input label="Toll-Free Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
            <Input label="Currency Symbol" value={currency} disabled />
          </div>
        </div>

        {/* Tax & Delivery Settings */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
          <h3 className="text-base font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-indigo-600" /> GST Tax & Delivery Fee Config
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="GST Tax Rate (%)" value={taxRate} onChange={(e) => setTaxRate(e.target.value)} />
            <Input label="Default Shipping Fee (₹)" value={shippingFee} onChange={(e) => setShippingFee(e.target.value)} />
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
          <h3 className="text-base font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
            <Bell className="w-5 h-5 text-indigo-600" /> Notifications & Alerts
          </h3>
          <div className="space-y-2 text-xs font-semibold text-gray-700">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4" />
              <span>Send order confirmation emails to customers</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4" />
              <span>Low inventory stock warning alerts to admin</span>
            </label>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button type="submit" variant="primary" size="lg" icon={Save}>
            Save Changes
          </Button>
        </div>
      </form>
    </div>
  );
};

export default Settings;
