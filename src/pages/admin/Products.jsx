import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import formatPrice from '../../utils/formatPrice';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Loader from '../../components/common/Loader';
import { Plus, Edit, Trash2, Search, Filter } from 'lucide-react';
import ConfirmDialog from '../../components/common/ConfirmDialog';

export const Products = () => {
  const [productList, setProductList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('search') || '';
  });
  const [categoryFilter, setCategoryFilter] = useState('All');

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

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

  const handleDelete = (prod) => {
    setSelectedProduct(prod);
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    setProductList((prev) => prev.filter((p) => p.id !== selectedProduct.id));
    setDeleteModalOpen(false);
    setSelectedProduct(null);
  };

  const filtered = productList.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.brand.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (loading) return <Loader fullScreen text="Loading products table..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Product Management</h1>
          <p className="text-xs text-gray-500 mt-0.5">Manage products, prices, stock levels & discounts</p>
        </div>
        <Link to="/admin/products/add">
          <Button variant="primary" icon={Plus}>Add New Product</Button>
        </Link>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div className="relative w-full sm:w-80">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search products by name or brand..."
            className="w-full pl-9 pr-4 py-2 text-xs border rounded-lg focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
          <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-gray-400" />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs border rounded-lg px-3 py-2 bg-white text-gray-700 font-semibold focus:outline-none"
          >
            <option value="All">All Categories</option>
            <option value="Electronics">Electronics</option>
            <option value="Fashion">Fashion</option>
            <option value="Home & Kitchen">Home & Kitchen</option>
            <option value="Beauty & Personal Care">Beauty & Personal Care</option>
            <option value="Sports & Fitness">Sports & Fitness</option>
            <option value="Books & Stationery">Books & Stationery</option>
            <option value="Grocery & Gourmet">Grocery & Gourmet</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">Image</th>
              <th className="px-4 py-3">Product Name</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Stock</th>
              <th className="px-4 py-3">Rating</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {filtered.map((prod) => (
              <tr key={prod.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3">
                  <div className="w-10 h-10 bg-gray-50 rounded border p-1 shrink-0 flex items-center justify-center">
                    <img src={prod.images[0]} alt={prod.name} className="max-h-full max-w-full object-contain" />
                  </div>
                </td>
                <td className="px-4 py-3 max-w-xs">
                  <p className="font-bold text-gray-900 truncate">{prod.name}</p>
                  <p className="text-[10px] text-gray-400">{prod.brand}</p>
                </td>
                <td className="px-4 py-3">{prod.category}</td>
                <td className="px-4 py-3 font-bold text-gray-900">{formatPrice(prod.price)}</td>
                <td className="px-4 py-3 font-bold">{prod.stock}</td>
                <td className="px-4 py-3">★ {prod.rating}</td>
                <td className="px-4 py-3">
                  <Badge variant={prod.stock === 0 ? 'red' : prod.stock < 20 ? 'yellow' : 'green'}>
                    {prod.stockStatus}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                  <Link
                    to={`/admin/products/edit/${prod.id}`}
                    className="p-1.5 inline-block text-indigo-600 hover:bg-indigo-50 rounded-lg"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(prod)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={confirmDelete}
        title="Delete Product"
        message={`Are you sure you want to delete "${selectedProduct?.name}"?`}
        confirmText="Delete Product"
      />
    </div>
  );
};

export default Products;
