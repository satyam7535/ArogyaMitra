import { useState, useEffect } from 'react';
import { getDoctorAllConsultations } from '../../services/consultationService';
import { FileText, Clock, CheckCircle, TrendingUp, Activity, Stethoscope } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const StatCard = ({ title, value, icon: Icon, color, bgColor, trend }) => (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-500">{title}</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
                {trend !== undefined && (
                    <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                        <TrendingUp size={10} /> {trend}
                    </p>
                )}
            </div>
            <div className={`w-12 h-12 ${bgColor} rounded-2xl flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${color}`} />
            </div>
        </div>
    </div>
);

const DoctorOverview = () => {
    const { t } = useTranslation();
    const [stats, setStats] = useState({ total: 0, pending: 0, reviewed: 0 });
    const [loading, setLoading] = useState(true);
    const [recentConsultations, setRecentConsultations] = useState([]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getDoctorAllConsultations();
                const consultations = data.consultations || [];

                setStats({
                    total: consultations.length,
                    pending: consultations.filter(c => c.status === 'pending').length,
                    reviewed: consultations.filter(c => c.status === 'reviewed').length,
                });
                setRecentConsultations(consultations.slice(0, 5));
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    const statusBadge = (status) => {
        const map = {
            pending: 'bg-yellow-100 text-yellow-700',
            reviewed: 'bg-green-100 text-green-700',
            closed: 'bg-blue-100 text-blue-700',
        };
        return map[status] || 'bg-gray-100 text-gray-600';
    };

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-3 text-gray-400">
                <Activity className="w-8 h-8 animate-pulse" />
                <span className="text-sm">{t('worker.loading_dashboard')}</span>
            </div>
        </div>
    );

    const statCards = [
        { title: t('worker.total_assigned'), value: stats.total, icon: Stethoscope, color: 'text-violet-600', bgColor: 'bg-violet-50', trend: t('worker.escalated_to_you') },
        { title: t('worker.pending_review'), value: stats.pending, icon: Clock, color: 'text-yellow-600', bgColor: 'bg-yellow-50', trend: t('worker.awaiting_opinion') },
        { title: t('common.status.reviewed'), value: stats.reviewed, icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-50' },
    ];

    return (
        <div className="space-y-8">
            {/* Page header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-800">{t('doctor.doctor_welcome')}</h1>
                <p className="text-gray-500 text-sm mt-1">{t('doctor.summary')}</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                {statCards.map((card, i) => <StatCard key={i} {...card} />)}
            </div>

            {/* Recent Consultations */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm">
                <div className="px-6 py-4 border-b border-gray-50">
                    <h2 className="text-base font-semibold text-gray-800">{t('worker.recent_consultations')}</h2>
                </div>
                {recentConsultations.length === 0 ? (
                    <div className="py-16 text-center text-gray-400 text-sm px-6">
                        <FileText className="w-10 h-10 mx-auto mb-3 opacity-30" />
                        {t('worker.no_assigned_consultations')}
                    </div>
                ) : (
                    <div className="divide-y divide-gray-50">
                        {recentConsultations.map((c) => (
                            <div key={c._id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                                <div>
                                    <p className="text-sm font-medium text-gray-800">{c.patient?.name || 'Unknown Patient'}</p>
                                    <p className="text-xs text-gray-400 mt-0.5">{c.symptoms?.slice(0, 3).join(', ')}</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-xs text-gray-400">{new Date(c.createdAt).toLocaleDateString()}</span>
                                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusBadge(c.status)}`}>
                                        {t(`common.status.${c.status}`)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DoctorOverview;
