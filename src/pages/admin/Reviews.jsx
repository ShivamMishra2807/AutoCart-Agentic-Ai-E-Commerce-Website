import React, { useState } from 'react';
import Badge from '../../components/common/Badge';
import formatDate from '../../utils/formatDate';
import { Star, CheckCircle, EyeOff, Trash2 } from 'lucide-react';

export const Reviews = () => {
  const [reviewList, setReviewList] = useState([
    {
      id: 'rev-1',
      customer: 'Shivam Sharma',
      product: 'boAt Airdopes 141 ANC TWS Earbuds',
      rating: 5,
      comment: 'Excellent active noise cancellation and super long battery backup! Best TWS under 1500.',
      date: '2026-08-21',
      status: 'Approved',
    },
    {
      id: 'rev-2',
      customer: 'Priya Patel',
      product: 'Prestige Iris 750W Mixer Grinder',
      rating: 4,
      comment: 'Sturdy motor and fast grinding. The juicer jar is very clear and easy to clean.',
      date: '2026-08-22',
      status: 'Approved',
    },
    {
      id: 'rev-3',
      customer: 'Ananya Roy',
      product: 'HP Pavilion 15 Core i5 Laptop',
      rating: 5,
      comment: 'Powerful 13th gen processor! Boot time is super fast and display is crystal sharp.',
      date: '2026-08-23',
      status: 'Approved',
    },
    {
      id: 'rev-4',
      customer: 'Spam User',
      product: 'OnePlus Nord CE 4 5G',
      rating: 1,
      comment: 'Buy from external link discount deal at cheap-site.com',
      date: '2026-08-24',
      status: 'Hidden',
    },
  ]);

  const toggleApprove = (id) => {
    setReviewList((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: r.status === 'Approved' ? 'Hidden' : 'Approved' } : r))
    );
  };

  const handleDelete = (id) => {
    setReviewList(reviewList.filter((r) => r.id !== id));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Review & Rating Moderation</h1>
        <p className="text-xs text-gray-500 mt-0.5">Moderate customer feedback, ratings and product comments</p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Product</th>
              <th className="px-4 py-3">Rating</th>
              <th className="px-4 py-3">Comment</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {reviewList.map((rev) => (
              <tr key={rev.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3 font-bold text-gray-900">{rev.customer}</td>
                <td className="px-4 py-3 font-semibold max-w-xs truncate">{rev.product}</td>
                <td className="px-4 py-3 font-bold text-amber-500 whitespace-nowrap">★ {rev.rating} / 5</td>
                <td className="px-4 py-3 max-w-md text-gray-600 italic">"{rev.comment}"</td>
                <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{formatDate(rev.date)}</td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge variant={rev.status === 'Approved' ? 'green' : 'red'}>{rev.status}</Badge>
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap space-x-2">
                  <button
                    onClick={() => toggleApprove(rev.id)}
                    className="text-xs font-bold text-indigo-600 hover:underline"
                  >
                    {rev.status === 'Approved' ? 'Hide' : 'Approve'}
                  </button>
                  <button onClick={() => handleDelete(rev.id)} className="text-red-600 hover:text-red-800 ml-2">
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Reviews;
