import React, { useState, useEffect } from 'react';
import StatCard from '../../admin/components/StatCard';
import SalesChart from '../../admin/components/SalesChart';
import RevenueChart from '../../admin/components/RevenueChart';
import RecentOrders from '../../admin/components/RecentOrders';
import TopProducts from '../../admin/components/TopProducts';
import LowStockProducts from '../../admin/components/LowStockProducts';
import adminService from '../../services/adminService';
import formatPrice from '../../utils/formatPrice';
import { DollarSign, ShoppingBag, Users, Package, Clock, AlertTriangle } from 'lucide-react';
import Loader from '../../components/common/Loader';
import AdminAttention from './AdminAttention';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const sData = await adminService.getDashboardStats();
        const aData = await adminService.getAnalyticsData();
        const oData = await adminService.getAllOrders();
        setStats(sData);
        setAnalytics(aData);
        setOrders(oData);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <Loader fullScreen text="Loading dashboard metrics..." />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
          Admin console
        </h1>
        <p className="text-xs text-gray-500 mt-1">Real-time statistics & business metrics for AuraCart India</p>
      </div>

      <AdminAttention />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <StatCard
          title="Total Revenue"
          value={formatPrice(stats.totalRevenue)}
          change="12.5%"
          isPositive={true}
          icon={DollarSign}
          color="emerald"
        />
        <StatCard
          title="Total Orders"
          value={stats.totalOrders.toLocaleString('en-IN')}
          change="8.2%"
          isPositive={true}
          icon={ShoppingBag}
          color="indigo"
        />
        <StatCard
          title="Registered Users"
          value={stats.totalUsers.toLocaleString('en-IN')}
          change="15.4%"
          isPositive={true}
          icon={Users}
          color="blue"
        />
        <StatCard
          title="Total Products"
          value={stats.totalProducts}
          icon={Package}
          color="indigo"
        />
        <StatCard
          title="Pending Orders"
          value={stats.pendingOrders}
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Low Stock Items"
          value={stats.lowStockProducts}
          icon={AlertTriangle}
          color="rose"
        />
      </div>

      {/* Recharts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SalesChart data={analytics.salesTrends} />
        <RevenueChart data={analytics.categorySales} />
      </div>

      {/* Widget Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <RecentOrders orders={orders} />
        </div>
        <div className="lg:col-span-1">
          <TopProducts />
        </div>
        <div className="lg:col-span-1">
          <LowStockProducts />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
