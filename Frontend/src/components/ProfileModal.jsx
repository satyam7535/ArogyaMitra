import { useRef, useEffect } from 'react';
import { X, User, Mail, Phone, MapPin, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ProfileModal = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const modalRef = useRef(null);

  const getRoleLabel = () => {
    switch (user?.role) {
      case 'admin': return 'Administrator';
      case 'doctor': return 'Doctor';
      case 'worker': return 'Healthcare Worker';
      default: return 'User';
    }
  };

  const getDisplayName = () => {
    if (user?.role === 'doctor') return `Dr. ${user?.name}`;
    return user?.name || 'User';
  };

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity p-4 animate-in fade-in duration-200">
      <div 
        ref={modalRef}
        className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden transform transition-all animate-in zoom-in-95 duration-200"
      >
        {/* Header Background */}
        <div className="h-32 bg-gradient-to-r from-primary-600 to-primary-800 relative">
            <button
                onClick={onClose}
                className="absolute top-4 right-4 text-white hover:bg-white/20 rounded-full p-1 transition-colors"
            >
                <X size={20} />
            </button>
        </div>

        {/* Avatar & Basic Info */}
        <div className="px-6 relative">
            <div className="-mt-16 mb-4 flex justify-between items-end">
                <div className="h-32 w-32 rounded-full border-4 border-white bg-white shadow-md flex items-center justify-center overflow-hidden">
                     <div className="h-full w-full bg-primary-100 flex items-center justify-center text-primary-700 text-5xl font-bold">
                        {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                     </div>
                </div>
                <div className="mb-2">
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-primary-100 text-primary-800 border border-primary-200">
                        <Shield size={12} />
                        {getRoleLabel()}
                    </span>
                </div>
            </div>

            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900">{getDisplayName()}</h2>
                <p className="text-gray-500">{user?.email}</p>
                {user?.role === 'doctor' && (
                    <p className="text-primary-600 font-medium text-sm mt-1">{user.specialization}</p>
                )}
            </div>

            {/* Details Grid */}
            <div className="space-y-4 mb-8">
                <div className="flex items-center p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <div className="p-2 bg-white rounded-lg shadow-sm text-gray-500 mr-4">
                        <Mail size={18} />
                    </div>
                    <div>
                        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Email</p>
                        <p className="text-gray-900 font-medium">{user?.email}</p>
                    </div>
                </div>

                <div className="flex items-center p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <div className="p-2 bg-white rounded-lg shadow-sm text-gray-500 mr-4">
                        <Phone size={18} />
                    </div>
                    <div>
                        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Phone</p>
                        <p className="text-gray-900 font-medium">{user?.phoneNumber || 'Not Provided'}</p>
                    </div>
                </div>

                <div className="flex items-center p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <div className="p-2 bg-white rounded-lg shadow-sm text-gray-500 mr-4">
                        <MapPin size={18} />
                    </div>
                    <div>
                        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Location</p>
                        <p className="text-gray-900 font-medium">{user?.location || 'Not Provided'}</p>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileModal;
