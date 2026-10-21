import React from 'react';
import { Link } from 'react-router-dom';
import formatPrice from '../../utils/formatPrice';
import formatDate from '../../utils/formatDate';
import Badge from '../../components/common/Badge';

export const OrdersTable = ({ orders = [], onStatusUpdate }) => {
  const getBadgeVariant = (status) => {
    switch (status) {
      case 'Delivered':
        return 'green';
      case 'Shipped':
      case 'Out for Delivery':
        return 'indigo';
      case 'Processing':
      case 'Confirmed':
        return 'blue';
      case 'Cancelled':
        return 'red';
      default:
        return 'yellow';
    }
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
      <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
        <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
          <tr>
            <th className="px-4 py-3">Order ID</th>
            <th className="px-4 py-3">Customer</th>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Payment</th>
            <th className="px-4 py-3">Amount</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
          {orders.map((ord) => (
            <tr key={ord.id} className="hover:bg-gray-50 transition">
              <td className="px-4 py-3 font-mono font-bold text-indigo-600">{ord.id}</td>
              <td className="px-4 py-3">
                <p className="font-bold text-gray-900">{ord.customerName}</p>
                <p className="text-[10px] text-gray-400">{ord.customerPhone}</p>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">{formatDate(ord.date)}</td>
              <td className="px-4 py-3 whitespace-nowrap">
                <p className="font-semibold text-gray-800">{ord.paymentMethod}</p>
                <span className="text-[10px] text-emerald-600 font-bold">{ord.paymentStatus}</span>
              </td>
              <td className="px-4 py-3 font-bold text-gray-900 whitespace-nowrap">{formatPrice(ord.totalAmount)}</td>
              <td className="px-4 py-3 whitespace-nowrap">
                <Badge variant={getBadgeVariant(ord.status)}>{ord.status}</Badge>
              </td>
              <td className="px-4 py-3 text-right whitespace-nowrap">
                <Link
                  to={`/admin/orders/${ord.id}`}
                  className="text-indigo-600 hover:text-indigo-900 font-bold hover:underline"
                >
                  Manage Details
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrdersTable;
