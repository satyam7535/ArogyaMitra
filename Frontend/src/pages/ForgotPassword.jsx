import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { Button, Input } from '../components/Ui';
import toast, { Toaster } from 'react-hot-toast';

const ForgotPassword = () => {
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

    const onSubmit = async (data) => {
        // Mock API call for now since backend endpoint doesn't exist yet
        console.log('Forgot Password Request:', data);
        await new Promise(resolve => setTimeout(resolve, 1000));
        toast.success('If an account exists, a reset link has been sent to your email.');
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-primary-50 p-4">
            <Toaster />
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-primary-800">ArogyaMitra</h1>
                    <p className="text-gray-500 mt-2">Reset Password</p>
                </div>
                <p className="text-sm text-gray-600 text-center">
                    Enter your email address and we'll send you a link to reset your password.
                </p>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <Input
                        label="Email"
                        id="email"
                        type="email"
                        placeholder="admin@example.com"
                        {...register('email', { required: 'Email is required' })}
                        error={errors.email?.message}
                    />
                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? 'Sending...' : 'Send Reset Link'}
                    </Button>
                </form>
                <div className="text-center text-sm text-gray-600">
                    Remember your password?{' '}
                    <Link to="/admin-login" className="font-medium text-primary-600 hover:text-primary-500">
                        Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
