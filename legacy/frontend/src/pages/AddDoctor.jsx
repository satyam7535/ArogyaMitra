import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input } from '../components/Ui';
import { addDoctor, getDoctors, deleteDoctor } from '../services/adminService';
import toast, { Toaster } from 'react-hot-toast';
import Modal from '../components/Modal';
import EmptyState from '../components/EmptyState';
import { UserTable } from '../components/UserTable';
import { Plus, Trash } from 'lucide-react';

const Doctors = () => {
    const [doctors, setDoctors] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm();

    const fetchDoctors = async () => {
        try {
            setLoading(true);
            const data = await getDoctors();
            setDoctors(Array.isArray(data) ? data : (data.doctors || []));
        } catch (error) {
            toast.error('Failed to fetch doctors');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDoctors();
    }, []);

    const onSubmit = async (data) => {
        try {
            await addDoctor(data);
            toast.success('Doctor added successfully!');
            reset();
            setIsModalOpen(false);
            fetchDoctors();
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add doctor';
            toast.error(errorMsg);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this doctor?")) return;
        try {
            await deleteDoctor(id);
            toast.success("Doctor deleted successfully");
            fetchDoctors();
        } catch (error) {
             console.error(error);
             toast.error(error.response?.data?.message || "Failed to delete doctor");
        }
    };

    const columns = [
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'phoneNumber', label: 'Phone' },
        { key: 'specialization', label: 'Specialization' },
    ];

    if (loading) return <div className="flex h-full items-center justify-center">Loading...</div>;

    return (
        <div className="space-y-6">
            <Toaster />
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">Doctors</h1>
                 {doctors.length > 0 && (
                    <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
                        <Plus size={20} /> Add Doctor
                    </Button>
                )}
            </div>

            {doctors.length === 0 ? (
                <EmptyState
                    title="No doctors found"
                    description="Get started by adding your first doctor to the system."
                    actionLabel="Add Doctor"
                    onAction={() => setIsModalOpen(true)}
                />
            ) : (
                <UserTable 
                    columns={columns} 
                    data={doctors} 
                    actions={(row) => (
                        <button 
                            onClick={() => handleDelete(row._id || row.id)} 
                            className="text-red-500 hover:text-red-700 transition-colors"
                            title="Delete Doctor"
                        >
                            <Trash size={18} />
                        </button>
                    )}
                />
            )}

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Doctor">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <Input
                        label="Full Name"
                        id="name"
                        placeholder="Dr. John Doe"
                        {...register('name', { required: 'Name is required' })}
                        error={errors.name?.message}
                    />
                    <Input
                        label="Email"
                        id="email"
                        type="email"
                        placeholder="doctor@example.com"
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
                        label="Specialization"
                        id="specialization"
                        placeholder="Cardiologist"
                        {...register('specialization', { required: 'Specialization is required' })}
                        error={errors.specialization?.message}
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
                        {isSubmitting ? 'Adding...' : 'Add Doctor'}
                    </Button>
                </form>
            </Modal>
        </div>
    );
};

export default Doctors;
