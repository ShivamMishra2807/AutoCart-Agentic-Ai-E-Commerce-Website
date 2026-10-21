import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import Badge from '../../components/common/Badge';
import formatPrice from '../../utils/formatPrice';
import formatDate from '../../utils/formatDate';
import Loader from '../../components/common/Loader';
import { Search } from 'lucide-react';

export const Users = () => {
  const [userList, setUserList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const data = await adminService.getAllUsers();
        setUserList(data);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const toggleStatus = (id) => {
    setUserList((prev) =>
      prev.map((u) => (u.id === id ? { ...u, status: u.status === 'Active' ? 'Inactive' : 'Active' } : u))
    );
  };

  const filtered = userList.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loader fullScreen text="Loading user directory..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">User Management</h1>
          <p className="text-xs text-gray-500 mt-0.5">Manage customer accounts, roles and status</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div className="relative w-full sm:w-80">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users by name or email..."
            className="w-full pl-9 pr-4 py-2 text-xs border rounded-lg focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
          <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-gray-400" />
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Phone</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Orders</th>
              <th className="px-4 py-3">Total Spent</th>
              <th className="px-4 py-3">Joined Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {filtered.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3">
                  <p className="font-bold text-gray-900">{u.name}</p>
                  <p className="text-[10px] text-gray-400">{u.email}</p>
                </td>
                <td className="px-4 py-3">{u.phone || 'N/A'}</td>
                <td className="px-4 py-3 font-bold text-indigo-600">{u.role}</td>
                <td className="px-4 py-3 font-bold">{u.ordersCount} Orders</td>
                <td className="px-4 py-3 font-extrabold text-gray-900">{formatPrice(u.totalSpent)}</td>
                <td className="px-4 py-3 text-gray-500">{formatDate(u.joinedDate)}</td>
                <td className="px-4 py-3">
                  <Badge variant={u.status === 'Active' ? 'green' : 'red'}>{u.status}</Badge>
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => toggleStatus(u.id)}
                    className="text-xs font-bold text-indigo-600 hover:underline"
                  >
                    {u.status === 'Active' ? 'Deactivate' : 'Activate'}
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

export default Users;
