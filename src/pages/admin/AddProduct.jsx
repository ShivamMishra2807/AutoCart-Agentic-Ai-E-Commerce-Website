import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { categories } from '../../data/categories';
import { Save, ArrowLeft } from 'lucide-react';

export const AddProduct = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      status: 'In Stock',
      discount: 0,
    },
  });

  const onSubmit = async (data) => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setLoading(false);
    alert('Product added successfully!');
    navigate('/admin/products');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/admin/products')} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Add New Product</h1>
          <p className="text-xs text-gray-500">Create a new item in the store catalogue</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-5">
        <Input
          label="Product Name"
          required
          placeholder="e.g. boAt Airdopes 141 ANC TWS Earbuds"
          {...register('name', { required: 'Product name is required' })}
          error={errors.name?.message}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Category *
            </label>
            <select
              {...register('category', { required: 'Category is required' })}
              className="w-full text-sm border border-gray-300 rounded-lg py-2.5 px-3 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          <Input
            label="Brand Name"
            required
            placeholder="e.g. boAt, HP, Sony"
            {...register('brand', { required: 'Brand is required' })}
            error={errors.brand?.message}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input
            label="Price (₹)"
            type="number"
            required
            placeholder="e.g. 1499"
            {...register('price', { required: 'Price is required' })}
            error={errors.price?.message}
          />

          <Input
            label="Discount (%)"
            type="number"
            placeholder="e.g. 20"
            {...register('discount')}
          />

          <Input
            label="Initial Stock Qty"
            type="number"
            required
            placeholder="e.g. 100"
            {...register('stock', { required: 'Stock quantity is required' })}
            error={errors.stock?.message}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
            Product Description
          </label>
          <textarea
            rows={4}
            placeholder="Enter detailed description..."
            {...register('description')}
            className="w-full text-sm border border-gray-300 rounded-lg p-3 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <Input
          label="Main Image URL"
          placeholder="https://images.unsplash.com/..."
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
        />

        {imageUrl && (
          <div className="p-3 bg-gray-50 rounded-xl border w-32 h-32 flex items-center justify-center">
            <img src={imageUrl} alt="Preview" className="max-h-full max-w-full object-contain" />
          </div>
        )}

        <div className="pt-4 border-t flex justify-end gap-3">
          <Button variant="outline" onClick={() => navigate('/admin/products')}>Cancel</Button>
          <Button type="submit" variant="primary" isLoading={loading} icon={Save}>
            Save Product
          </Button>
        </div>
      </form>
    </div>
  );
};

export default AddProduct;
