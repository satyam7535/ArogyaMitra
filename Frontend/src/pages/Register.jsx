import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { registerAdmin } from '../services/authService'; // We'll add this to authService
import { Button, Input } from '../components/Ui';
import toast, { Toaster } from 'react-hot-toast';

const Register = () => {
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();
    const navigate = useNavigate();

    const onSubmit = async (data) => {
        try {
            await registerAdmin(data);
            toast.success('Registration successful! Please login.');
            setTimeout(() => navigate('/admin-login'), 2000);
        } catch (error) {
            toast.error(error.response?.data?.message || 'Registration failed');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-primary-50 p-4">
            <Toaster />
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-primary-800">ArogyaMitra</h1>
                    <p className="text-gray-500 mt-2">Admin Portal Registration</p>
                </div>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <Input
                        label="Full Name"
                        id="name"
                        placeholder="John Doe"
                        {...register('name', { required: 'Name is required' })}
                        error={errors.name?.message}
                    />
                    <Input
                        label="Email"
                        id="email"
                        type="email"
                        placeholder="admin@example.com"
                        {...register('email', { required: 'Email is required' })}
                        error={errors.email?.message}
                    />
                    <Input
                        label="Phone Number"
                        id="phone"
                        placeholder="+91 9876543210"
                        {...register('phoneNumber', { required: 'Phone Number is required' })}
                        error={errors.phoneNumber?.message}
                    />
                     <Input
                        label="Location/Hospital Name"
                        id="location"
                        placeholder="City Hospital, Delhi"
                        {...register('location', { required: 'Location is required' })}
                        error={errors.location?.message}
                    />
                    <Input
                        label="Password"
                        id="password"
                        type="password"
                        placeholder="********"
                        {...register('password', { required: 'Password is required', minLength: { value: 6, message: 'Password must be at least 6 characters' } })}
                        error={errors.password?.message}
                    />
                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? 'Registering...' : 'Register'}
                    </Button>
                </form>
                <div className="text-center text-sm text-gray-600">
                    Already have an account?{' '}
                    <Link to="/admin-login" className="font-medium text-primary-600 hover:text-primary-500">
                        Sign in
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
