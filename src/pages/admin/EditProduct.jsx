import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import Loader from '../../components/common/Loader';
import productService from '../../services/productService';
import { categories } from '../../data/categories';
import { Save, ArrowLeft } from 'lucide-react';

export const EditProduct = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  useEffect(() => {
    const fetchProd = async () => {
      setLoading(true);
      try {
        const prod = await productService.getProductById(id);
        reset({
          name: prod.name,
          category: prod.category,
          brand: prod.brand,
          price: prod.price,
          discount: prod.discount,
          stock: prod.stock,
          description: prod.description,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchProd();
  }, [id, reset]);

  const onSubmit = async () => {
    setSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setSaving(false);
    alert('Product updated successfully!');
    navigate('/admin/products');
  };

  if (loading) return <Loader fullScreen text="Loading product data..." />;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/admin/products')} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Edit Product #{id}</h1>
          <p className="text-xs text-gray-500">Update product specifications and pricing</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-5">
        <Input
          label="Product Name"
          required
          {...register('name', { required: 'Product name is required' })}
          error={errors.name?.message}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Category
            </label>
            <select
              {...register('category')}
              className="w-full text-sm border border-gray-300 rounded-lg py-2.5 px-3 focus:ring-1 focus:ring-indigo-500"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          <Input
            label="Brand Name"
            {...register('brand')}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input
            label="Price (₹)"
            type="number"
            {...register('price')}
          />

          <Input
            label="Discount (%)"
            type="number"
            {...register('discount')}
          />

          <Input
            label="Stock Qty"
            type="number"
            {...register('stock')}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
            Product Description
          </label>
          <textarea
            rows={4}
            {...register('description')}
            className="w-full text-sm border border-gray-300 rounded-lg p-3 focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="pt-4 border-t flex justify-end gap-3">
          <Button variant="outline" onClick={() => navigate('/admin/products')}>Cancel</Button>
          <Button type="submit" variant="primary" isLoading={saving} icon={Save}>
            Update Product
          </Button>
        </div>
      </form>
    </div>
  );
};

export default EditProduct;
