import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Users, FileText, LogOut, Stethoscope } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

const WorkerSidebar = () => {
  const { t } = useTranslation();
  const { logoutAsWorker } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { name: t('common.overview'),       path: '/worker-dashboard',               icon: LayoutDashboard },
    { name: t('common.patients'),       path: '/worker-dashboard/patients',      icon: Users },
    { name: t('common.consultations'),  path: '/worker-dashboard/consultations', icon: FileText },
  ];

  const handleLogout = async () => {
    await logoutAsWorker();
    navigate('/');
  };

  return (
    <div className="flex flex-col w-64 h-screen px-4 py-8 bg-white border-r border-gray-100 shadow-sm">
      {/* Brand */}
      <div className="flex items-center gap-3 mb-10 px-2">
        <img src="/bg.png" alt="ArogyaMitra Logo" className="w-10 h-10 object-contain rounded-lg shadow-sm" />
        <div>
          <h2 className="text-lg font-bold text-gray-800 leading-none">ArogyaMitra</h2>
          <p className="text-xs text-secondary-600 font-medium mt-0.5">Worker Portal</p>
        </div>
      </div>

      {/* Nav */}
      <div className="flex flex-col flex-1 gap-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path ||
            (item.path !== '/worker-dashboard' && location.pathname.startsWith(item.path));
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all',
                isActive
                  ? 'bg-secondary-50 text-secondary-700 shadow-sm border border-secondary-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              )}
            >
              <Icon size={18} className={isActive ? 'text-secondary-600' : ''} />
              {item.name}
            </button>
          );
        })}
      </div>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-500 rounded-xl hover:bg-red-50 transition-colors mt-auto"
      >
        <LogOut size={18} />
        {t('common.logout')}
      </button>
    </div>
  );
};

export default WorkerSidebar;
