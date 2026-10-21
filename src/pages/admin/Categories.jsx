import React, { useState } from 'react';
import { categories as initialCategories } from '../../data/categories';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import Input from '../../components/common/Input';
import Badge from '../../components/common/Badge';
import { Plus, Edit, Trash2 } from 'lucide-react';

export const Categories = () => {
  const [categoryList, setCategoryList] = useState(initialCategories);
  const [modalOpen, setModalOpen] = useState(false);
  const [newCatName, setNewCatName] = useState('');
  const [newCatDesc, setNewCatDesc] = useState('');

  const handleAddCategory = (e) => {
    e.preventDefault();
    if (!newCatName.trim()) return;

    const newObj = {
      id: `cat-${Date.now()}`,
      name: newCatName,
      slug: newCatName.toLowerCase().replace(/\s+/g, '-'),
      description: newCatDesc || 'General Category',
      productCount: 0,
      status: 'Active',
      createdAt: new Date().toISOString().split('T')[0],
      image: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80',
    };

    setCategoryList([newObj, ...categoryList]);
    setNewCatName('');
    setNewCatDesc('');
    setModalOpen(false);
  };

  const handleDelete = (id) => {
    setCategoryList(categoryList.filter((c) => c.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Category Management</h1>
          <p className="text-xs text-gray-500 mt-0.5">Organize catalogue categories and view item counts</p>
        </div>
        <Button variant="primary" icon={Plus} onClick={() => setModalOpen(true)}>
          Add Category
        </Button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
          <thead className="bg-gray-50 font-bold uppercase text-gray-500 tracking-wider">
            <tr>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Slug</th>
              <th className="px-4 py-3">Product Count</th>
              <th className="px-4 py-3">Created Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-medium text-gray-700">
            {categoryList.map((cat) => (
              <tr key={cat.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3 font-bold text-gray-900 flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-gray-100 overflow-hidden shrink-0">
                    <img src={cat.image} alt={cat.name} className="w-full h-full object-cover" />
                  </div>
                  <span>{cat.name}</span>
                </td>
                <td className="px-4 py-3 font-mono text-gray-500">{cat.slug}</td>
                <td className="px-4 py-3 font-bold">{cat.productCount} Items</td>
                <td className="px-4 py-3 text-gray-500">{cat.createdAt}</td>
                <td className="px-4 py-3">
                  <Badge variant="green">{cat.status}</Badge>
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  <button
                    onClick={() => handleDelete(cat.id)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg ml-2"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Add Category">
        <form onSubmit={handleAddCategory} className="space-y-4">
          <Input
            label="Category Name"
            required
            value={newCatName}
            onChange={(e) => setNewCatName(e.target.value)}
            placeholder="e.g. Footwear & Accessories"
          />
          <Input
            label="Description"
            value={newCatDesc}
            onChange={(e) => setNewCatDesc(e.target.value)}
            placeholder="Short description..."
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Category</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Categories;
