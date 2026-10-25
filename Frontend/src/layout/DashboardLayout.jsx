import Sidebar from '../components/Sidebar';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import ProfileModal from '../components/ProfileModal';
import LanguageSelector from '../components/LanguageSelector';

const DashboardLayout = () => {
  const { user } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <div className="flex bg-gray-50 min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <header className="px-8 py-5 bg-white border-b flex justify-between items-center">
            <h1 className="text-xl font-semibold text-gray-800">Admin Dashboard</h1>
            <div className="flex items-center gap-6">
                <LanguageSelector />
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{user?.name || 'Admin'}</p>
                        <p className="text-xs text-gray-500">Administrator</p>
                    </div>
                    <button 
                        onClick={() => setIsProfileOpen(true)}
                        className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-bold hover:bg-primary-200 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                    >
                        {user?.name?.[0] || 'A'}
                    </button>
                </div>
            </div>
        </header>
        <main className="p-8 overflow-y-auto h-[calc(100vh-80px)]">
           <Outlet />
        </main>
        <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
      </div>
    </div>
  );
};

export default DashboardLayout;
