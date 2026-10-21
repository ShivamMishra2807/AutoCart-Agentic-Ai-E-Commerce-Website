import React from 'react';
import { useForm } from 'react-hook-form';
import Input from '../common/Input';
import Button from '../common/Button';
import { emailPattern, phonePattern, pinCodePattern } from '../../utils/validators';

export const AddressForm = ({ initialData = {}, onSubmit }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      fullName: initialData.fullName || 'Shivam Sharma',
      phone: initialData.phone || '9876543210',
      addressLine: initialData.addressLine || 'Flat 402, Green Park Apartments, Sector 15',
      city: initialData.city || 'Noida',
      state: initialData.state || 'Uttar Pradesh',
      pinCode: initialData.pinCode || '201301',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
      <h3 className="text-base font-extrabold text-gray-900 border-b pb-3">
        Delivery Address
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          label="Full Name"
          required
          placeholder="e.g. Shivam Sharma"
          {...register('fullName', { required: 'Full name is required' })}
          error={errors.fullName?.message}
        />

        <Input
          label="Phone Number"
          required
          placeholder="10-digit Indian Mobile"
          {...register('phone', {
            required: 'Phone number is required',
            pattern: phonePattern,
          })}
          error={errors.phone?.message}
        />
      </div>

      <Input
        label="Street Address / Flat No / Building"
        required
        placeholder="e.g. House No. 42, Mg Road"
        {...register('addressLine', { required: 'Address is required' })}
        error={errors.addressLine?.message}
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Input
          label="City"
          required
          placeholder="e.g. Noida"
          {...register('city', { required: 'City is required' })}
          error={errors.city?.message}
        />

        <Input
          label="State"
          required
          placeholder="e.g. Uttar Pradesh"
          {...register('state', { required: 'State is required' })}
          error={errors.state?.message}
        />

        <Input
          label="PIN Code"
          required
          placeholder="e.g. 201301"
          {...register('pinCode', {
            required: 'PIN code is required',
            pattern: pinCodePattern,
          })}
          error={errors.pinCode?.message}
        />
      </div>

      <div className="pt-4 flex justify-end">
        <Button type="submit" variant="primary" size="lg">
          Deliver to this Address &rarr;
        </Button>
      </div>
    </form>
  );
};

export default AddressForm;
