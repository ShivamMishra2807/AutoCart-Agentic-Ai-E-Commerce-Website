import CatalogPulse from '../../storefront/CatalogPulse';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { emailPattern, phonePattern } from '../../utils/validators';
import { UserPlus, Mail, Lock, User, Phone, ShieldAlert } from 'lucide-react';

export const Register = () => {
  const { register: registerAuth } = useAuth();
  const navigate = useNavigate();

  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const passwordVal = watch('password');

  const onSubmit = async (data) => {
    setServerError('');
    setLoading(true);
    try {
      await registerAuth(data);
      navigate('/');
    } catch (err) {
      setServerError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ac ac-auth">
      <div className="bg-white rounded-3xl border border-gray-100 p-8 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-extrabold text-2xl flex items-center justify-center mx-auto shadow-md">
            A
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900">Create Account</h2>
          <p className="text-sm">Want to sell instead? <Link to="/seller/apply" className="font-bold underline">Apply as a seller</Link> (documents needed).</p>
          <p className="text-xs text-gray-500">Join AuraCart India to start shopping today</p>
        </div>

        {serverError && (
          <div className="p-3 bg-red-50 text-red-700 rounded-xl text-xs font-semibold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Full Name"
            icon={User}
            placeholder="e.g. Shivam Sharma"
            {...register('name', { required: 'Full name is required' })}
            error={errors.name?.message}
          />

          <Input
            label="Email Address"
            type="email"
            icon={Mail}
            placeholder="e.g. shivam@example.com"
            {...register('email', { required: 'Email is required', pattern: emailPattern })}
            error={errors.email?.message}
          />

          <Input
            label="Phone Number"
            icon={Phone}
            placeholder="10-digit Indian Mobile"
            {...register('phone', { required: 'Phone is required', pattern: phonePattern })}
            error={errors.phone?.message}
          />

          <Input
            label="Password"
            type="password"
            icon={Lock}
            placeholder="Min 6 characters"
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 6, message: 'Password must be at least 6 characters' },
            })}
            error={errors.password?.message}
          />

          <Input
            label="Confirm Password"
            type="password"
            icon={Lock}
            placeholder="Re-enter password"
            {...register('confirmPassword', {
              required: 'Please confirm password',
              validate: (value) => value === passwordVal || 'Passwords do not match',
            })}
            error={errors.confirmPassword?.message}
          />

          <Button type="submit" variant="primary" size="lg" fullWidth isLoading={loading} icon={UserPlus}>
            Create Account
          </Button>
        </form>

        <div className="text-center text-xs text-gray-500 pt-2 border-t">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-600 font-bold hover:underline">
            Sign In
          </Link>
        </div>
      </div>
      <CatalogPulse />
    </div>
  );
};

export default Register;
