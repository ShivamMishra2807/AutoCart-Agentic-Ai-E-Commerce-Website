import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { emailPattern } from '../../utils/validators';
import { Mail, CheckCircle2, ArrowLeft } from 'lucide-react';

export const ForgotPassword = () => {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 600));
    setLoading(false);
    setSubmitted(true);
  };

  return (
    <div className="max-w-md mx-auto py-12 px-4">
      <div className="bg-white rounded-3xl border border-gray-100 p-8 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-extrabold text-2xl flex items-center justify-center mx-auto shadow-md">
            A
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900">Reset Password</h2>
          <p className="text-xs text-gray-500">Enter your email to receive password reset instructions</p>
        </div>

        {submitted ? (
          <div className="p-6 bg-emerald-50 text-emerald-800 rounded-2xl text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
            <p className="font-bold text-sm">Reset Link Sent!</p>
            <p className="text-xs text-emerald-700">
              We have sent password reset instructions to your email address if an account exists.
            </p>
            <Link to="/login" className="inline-block pt-2 text-xs font-bold text-indigo-600 hover:underline">
              Return to Sign In
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              icon={Mail}
              placeholder="e.g. user@example.com"
              {...register('email', { required: 'Email is required', pattern: emailPattern })}
              error={errors.email?.message}
            />

            <Button type="submit" variant="primary" size="lg" fullWidth isLoading={loading}>
              Send Reset Link
            </Button>
          </form>
        )}

        <div className="text-center pt-2 border-t">
          <Link to="/login" className="inline-flex items-center gap-1 text-xs font-bold text-gray-600 hover:text-indigo-600">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
