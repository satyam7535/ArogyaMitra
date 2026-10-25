import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Button, Input } from '../components/Ui';
import { Stethoscope, Shield } from 'lucide-react';

const WorkerLogin = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();
  const { loginAsWorker } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    const success = await loginAsWorker(data.email, data.password);
    if (success) navigate('/worker-dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 via-primary-50 to-accent-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header band */}
          <div className="bg-gradient-to-r from-secondary-600 to-primary-600 px-8 py-8 text-white text-center">
            <img src="/bg.png" alt="ArogyaMitra Logo" className="w-14 h-14 object-contain mx-auto mb-3" />
            <h1 className="text-2xl font-bold">ArogyaMitra</h1>
            <p className="text-white/80 text-sm mt-1">Healthcare Worker Portal</p>
          </div>

          {/* Form */}
          <div className="px-8 py-8 space-y-5">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-800">Sign in to your account</h2>
              <p className="text-gray-500 text-sm mt-1">Enter your credentials provided by the admin</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label="Email Address"
                id="email"
                type="email"
                placeholder="worker@clinic.com"
                {...register('email', { required: 'Email is required' })}
                error={errors.email?.message}
              />
              <Input
                label="Password"
                id="password"
                type="password"
                placeholder="••••••••"
                {...register('password', { required: 'Password is required' })}
                error={errors.password?.message}
              />
              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-secondary-600 hover:bg-secondary-700 focus:ring-secondary-500"
              >
                {isSubmitting ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="text-center text-sm text-gray-500">
              Are you an Admin?{' '}
              <Link to="/admin-login" className="font-medium text-primary-600 hover:text-primary-500">
                Admin Login
              </Link>
            </div>
          </div>
        </div>

        {/* Note */}
        <div className="mt-4 flex items-center gap-2 text-xs text-gray-500 justify-center">
          <Shield size={12} />
          <span>Secure access for authorized healthcare workers only</span>
        </div>
      </div>
    </div>
  );
};

export default WorkerLogin;
