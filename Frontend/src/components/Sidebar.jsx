import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Users, LogOut, Stethoscope } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

const Sidebar = () => {
  const { t } = useTranslation();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { name: t('common.overview'), path: '/dashboard', icon: LayoutDashboard },
    { name: t('common.doctors'),  path: '/dashboard/doctors', icon: Stethoscope },
    { name: t('common.workers'),  path: '/dashboard/workers', icon: Users },
  ];

  return (
    <div className="flex flex-col w-64 h-screen px-4 py-8 bg-white border-r">
      <div className="flex items-center gap-3 mb-10 px-2">
        <img src="/bg.png" alt="ArogyaMitra Logo" className="w-10 h-10 object-contain rounded-lg shadow-sm" />
        <h2 className="text-2xl font-bold text-primary-800">ArogyaMitra</h2>
      </div>
      
      <div className="flex flex-col flex-1 gap-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              <Icon size={20} />
              {item.name}
            </button>
          );
        })}
      </div>

      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 mt-auto"
      >
        <LogOut size={20} />
        {t('common.logout')}
      </button>
    </div>
  );
};

export default Sidebar;
