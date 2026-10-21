import React, { useState, useEffect } from 'react';
import SalesChart from '../../admin/components/SalesChart';
import RevenueChart from '../../admin/components/RevenueChart';
import adminService from '../../services/adminService';
import formatPrice from '../../utils/formatPrice';
import Loader from '../../components/common/Loader';
import { BarChart3, TrendingUp, ShoppingBag, Users } from 'lucide-react';

export const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const data = await adminService.getAnalyticsData();
        setAnalytics(data);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <Loader fullScreen text="Calculating store analytics..." />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Sales & Performance Analytics</h1>
        <p className="text-xs text-gray-500 mt-0.5">Deep revenue insights, category breakdown & order trends</p>
      </div>

      {/* Top metric highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm space-y-1">
          <p className="text-xs font-bold text-gray-400 uppercase">Average Order Value (AOV)</p>
          <h3 className="text-2xl font-extrabold text-gray-900">₹3,450</h3>
          <p className="text-xs text-emerald-600 font-bold">+5.2% vs last month</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm space-y-1">
          <p className="text-xs font-bold text-gray-400 uppercase">Conversion Rate</p>
          <h3 className="text-2xl font-extrabold text-gray-900">4.18%</h3>
          <p className="text-xs text-emerald-600 font-bold">+1.1% vs industry avg</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm space-y-1">
          <p className="text-xs font-bold text-gray-400 uppercase">Repeat Customer Rate</p>
          <h3 className="text-2xl font-extrabold text-gray-900">32.4%</h3>
          <p className="text-xs text-emerald-600 font-bold">+4.0% returning shoppers</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SalesChart data={analytics.salesTrends} />
        <RevenueChart data={analytics.categorySales} />
      </div>
    </div>
  );
};

export default Analytics;
