import { useState, useEffect } from 'react';
import { getDoctors, getWorkers } from '../services/adminService';
import { getConsultations } from '../services/consultationService';
import { Users, Stethoscope, FileText, Activity, TrendingUp } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const StatCard = ({ title, value, icon: Icon, color, bgColor, trend }) => (
  <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
        <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
          <TrendingUp size={10} /> {trend}
        </p>
      </div>
      <div className={`w-12 h-12 ${bgColor} rounded-2xl flex items-center justify-center`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
    </div>
  </div>
);

const Overview = () => {
  const { t } = useTranslation();
  const [stats, setStats] = useState({ doctors: 0, workers: 0, consultations: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [docs, wrks, cons] = await Promise.all([
          getDoctors(),
          getWorkers(),
          getConsultations()
        ]);
        setStats({
          doctors: docs.doctors?.length || 0,
          workers: wrks.workers?.length || 0,
          consultations: cons.consultations?.length || 0
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3 text-gray-400">
        <Activity className="w-8 h-8 animate-pulse" />
        <span className="text-sm">{t('common.loading')}</span>
      </div>
    </div>
  );

  const cards = [
    { title: t('admin.total_doctors'), value: stats.doctors, icon: Stethoscope, color: 'text-primary-600', bgColor: 'bg-primary-50', trend: t('admin.active_in_organization') },
    { title: t('admin.total_workers'), value: stats.workers, icon: Users, color: 'text-secondary-600', bgColor: 'bg-secondary-50', trend: t('admin.active_in_organization') },
    { title: t('admin.total_consultations'), value: stats.consultations, icon: FileText, color: 'text-purple-600', bgColor: 'bg-purple-50', trend: t('admin.active_in_organization') },
  ];

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">{t('common.dashboard')}</h1>
        <p className="text-gray-500 text-sm mt-1">{t('admin.summary')}</p>
      </div>

      {/* Stats container */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card, i) => <StatCard key={i} {...card} />)}
      </div>

      {/* Quick view / Activity graph placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-64 flex flex-col items-center justify-center text-gray-400">
          <Activity size={32} className="mb-2 opacity-20" />
          <p className="text-sm font-medium">Activity Trends Coming Soon</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-64 flex flex-col items-center justify-center text-gray-400">
          <Users size={32} className="mb-2 opacity-20" />
          <p className="text-sm font-medium">User Distribution Coming Soon</p>
        </div>
      </div>
    </div>
  );
};

export default Overview;
