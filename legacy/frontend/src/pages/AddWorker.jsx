import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input } from '../components/Ui';
import { addWorker, getWorkers, deleteWorker } from '../services/adminService';
import toast, { Toaster } from 'react-hot-toast';
import Modal from '../components/Modal';
import EmptyState from '../components/EmptyState';
import { UserTable } from '../components/UserTable';
import { Plus, Trash } from 'lucide-react';

const Workers = () => {
    const [workers, setWorkers] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm();

    const fetchWorkers = async () => {
        try {
            setLoading(true);
            const data = await getWorkers();
            setWorkers(Array.isArray(data) ? data : (data.workers || []));
        } catch (error) {
            toast.error('Failed to fetch workers');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchWorkers();
    }, []);

    const onSubmit = async (data) => {
        try {
            await addWorker(data);
            toast.success('Worker added successfully!');
            reset();
            setIsModalOpen(false);
            fetchWorkers();
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add worker';
            toast.error(errorMsg);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this worker?")) return;
        try {
            await deleteWorker(id);
            toast.success("Worker deleted successfully");
            fetchWorkers();
        } catch (error) {
             console.error(error);
             toast.error(error.response?.data?.message || "Failed to delete worker");
        }
    };

    const columns = [
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'phoneNumber', label: 'Phone' },
    ];

    if (loading) return <div className="flex h-full items-center justify-center">Loading...</div>;

    return (
        <div className="space-y-6">
            <Toaster />
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">Health Workers</h1>
                 {workers.length > 0 && (
                    <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
                        <Plus size={20} /> Add Worker
                    </Button>
                )}
            </div>

            {workers.length === 0 ? (
                <EmptyState
                    title="No workers found"
                    description="Get started by adding your first health worker to the system."
                    actionLabel="Add Worker"
                    onAction={() => setIsModalOpen(true)}
                />
            ) : (
                <UserTable 
                    columns={columns} 
                    data={workers} 
                    actions={(row) => (
                        <button 
                            onClick={() => handleDelete(row._id || row.id)} 
                            className="text-red-500 hover:text-red-700 transition-colors"
                            title="Delete Worker"
                        >
                            <Trash size={18} />
                        </button>
                    )}
                />
            )}

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Worker">
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
                        placeholder="worker@example.com"
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
                        label="Password"
                        id="password"
                        type="password"
                        placeholder="********"
                        {...register('password', { required: 'Password is required', minLength: { value: 6, message: 'Min 6 chars' } })}
                        error={errors.password?.message}
                    />
                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? 'Adding...' : 'Add Worker'}
                    </Button>
                </form>
            </Modal>
        </div>
    );
};

export default Workers;
