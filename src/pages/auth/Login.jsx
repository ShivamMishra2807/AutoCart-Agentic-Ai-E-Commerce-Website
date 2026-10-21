import CatalogPulse from '../../storefront/CatalogPulse';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { emailPattern } from '../../utils/validators';
import RoleTabs from './RoleTabs';
import { LogIn, Lock, Mail, ShieldAlert } from 'lucide-react';

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data) => {
    setServerError('');
    setLoading(true);
    try {
      const res = await login(data.email, data.password);
      if (res.user.role === 'ADMIN') {
        navigate('/admin');
      } else if (res.user.role === 'SELLER') {
        navigate('/seller/dashboard');
      } else {
        navigate(from, { replace: true });
      }
    } catch (err) {
      setServerError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCustomer = () => {
    setValue('email', 'customer@example.com');
    setValue('password', 'password');
  };

  const fillDemoAdmin = () => {
    setValue('email', 'admin@auracart.com');
    setValue('password', 'admin123');
  };

  return (
    <div className="ac ac-auth">
      <div className="bg-white rounded-3xl border border-gray-100 p-8 shadow-xl space-y-6">
        {location.state?.customerOnly ? <p className="text-center text-sm font-semibold text-gray-700">Sign in with your customer account to buy.</p> : <RoleTabs current="customer" />}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-extrabold text-2xl flex items-center justify-center mx-auto shadow-md">
            A
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900">Welcome Back</h2>
          <p className="text-xs text-gray-500">Sign in to access your cart, orders & wishlist</p>
        </div>

        {/* Quick Demo Login Fill Buttons */}
        {import.meta.env.DEV && (
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-200/80 text-xs">
            <b>Development only:</b> customer@example.com / password
          </div>
        )}


        {serverError && (
          <div className="p-3 bg-red-50 text-red-700 rounded-xl text-xs font-semibold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            icon={Mail}
            placeholder="e.g. customer@example.com"
            {...register('email', { required: 'Email is required', pattern: emailPattern })}
            error={errors.email?.message}
          />

          <Input
            label="Password"
            type="password"
            icon={Lock}
            placeholder="••••••••"
            {...register('password', { required: 'Password is required' })}
            error={errors.password?.message}
          />

          <div className="flex items-center justify-between text-xs">
            <label className="flex items-center gap-2 cursor-pointer text-gray-600">
              <input type="checkbox" className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5" />
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password" className="text-indigo-600 font-semibold hover:underline">
              Forgot Password?
            </Link>
          </div>

          <Button type="submit" variant="primary" size="lg" fullWidth isLoading={loading} icon={LogIn}>
            Sign In
          </Button>
        </form>

        <div className="text-center text-xs text-gray-500 pt-2 border-t">
          <div className="mb-2"><Link to="/seller/login" className="text-indigo-600 font-semibold hover:underline">Seller sign in</Link></div>
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 font-bold hover:underline">
            Register Now
          </Link>
        </div>
      </div>
      <CatalogPulse />
    </div>
  );
};

export default Login;
