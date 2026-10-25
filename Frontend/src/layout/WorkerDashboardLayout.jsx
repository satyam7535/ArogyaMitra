import WorkerSidebar from '../components/WorkerSidebar';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import ProfileModal from '../components/ProfileModal';
import LanguageSelector from '../components/LanguageSelector';

const WorkerDashboardLayout = () => {
  const { user } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <div className="flex bg-slate-50 min-h-screen">
      <WorkerSidebar />
      <div className="flex-1 flex flex-col">
        {/* Top Header */}
        <header className="px-8 py-5 bg-white border-b border-gray-100 flex justify-between items-center shadow-sm">
          <div>
            <h1 className="text-lg font-semibold text-gray-800">Worker Dashboard</h1>
            <p className="text-xs text-gray-400 mt-0.5">Primary Healthcare Decision Support</p>
          </div>
          <div className="flex items-center gap-6">
            <LanguageSelector />
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.name || 'Worker'}</p>
                <p className="text-xs text-gray-500">Healthcare Worker</p>
              </div>
              <div 
                onClick={() => setIsProfileOpen(true)}
                className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-700 font-bold hover:bg-emerald-200 transition-all cursor-pointer focus:outline-none ring-offset-2 hover:ring-2 hover:ring-emerald-400"
              >
                {user?.name?.[0]?.toUpperCase() || 'W'}
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

export default WorkerDashboardLayout;
