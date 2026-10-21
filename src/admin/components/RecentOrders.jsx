import React from 'react';
import { Link } from 'react-router-dom';
import formatPrice from '../../utils/formatPrice';
import Badge from '../../components/common/Badge';

export const RecentOrders = ({ orders = [] }) => {
  const recent = orders.slice(0, 5);

  return (
    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-extrabold text-gray-900">Recent Orders</h3>
        <Link to="/admin/orders" className="text-xs font-bold text-indigo-600 hover:underline">
          View All &rarr;
        </Link>
      </div>

      <div className="space-y-3">
        {recent.map((ord) => (
          <div key={ord.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl text-xs">
            <div>
              <p className="font-mono font-bold text-indigo-600">{ord.id}</p>
              <p className="font-semibold text-gray-800">{ord.customerName}</p>
            </div>
            <div className="text-right">
              <p className="font-extrabold text-gray-900">{formatPrice(ord.totalAmount)}</p>
              <Badge size="sm" variant={ord.status === 'Delivered' ? 'green' : 'indigo'}>
                {ord.status}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentOrders;
