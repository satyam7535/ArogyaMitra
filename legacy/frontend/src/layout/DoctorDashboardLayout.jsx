import DoctorSidebar from '../components/DoctorSidebar';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import ProfileModal from '../components/ProfileModal';
import LanguageSelector from '../components/LanguageSelector';

const DoctorDashboardLayout = () => {
    const { user } = useAuth();
    const [isProfileOpen, setIsProfileOpen] = useState(false);

    return (
        <div className="flex bg-slate-50 min-h-screen">
            <DoctorSidebar />
            <div className="flex-1 flex flex-col">
                {/* Top Header */}
                <header className="px-8 py-5 bg-white border-b border-gray-100 flex justify-between items-center shadow-sm">
                    <div>
                        <h1 className="text-lg font-semibold text-gray-800">Doctor Dashboard</h1>
                        <p className="text-xs text-gray-400 mt-0.5">Review escalated cases & provide expert opinions</p>
                    </div>
                    <div className="flex items-center gap-6">
                        <LanguageSelector />
                        <div className="flex items-center gap-4">
                            <div className="text-right">
                                <p className="text-sm font-medium text-gray-900">Dr. {user?.name || 'Doctor'}</p>
                                <p className="text-xs text-gray-500">{user?.specialization || 'Specialist'}</p>
                            </div>
                            <div 
                                onClick={() => setIsProfileOpen(true)}
                                className="w-10 h-10 bg-violet-100 rounded-full flex items-center justify-center text-violet-700 font-bold hover:bg-violet-200 transition-all cursor-pointer focus:outline-none ring-offset-2 hover:ring-2 hover:ring-violet-400"
                            >
                                {user?.name?.[0]?.toUpperCase() || 'D'}
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="p-8 overflow-y-auto h-[calc(100vh-80px)]">
                    <Outlet />
                </main>
                <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
            </div>
        </div>
    );
};

export default DoctorDashboardLayout;
