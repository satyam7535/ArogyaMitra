import { useState, useEffect } from 'react';
import { getDoctorAllConsultations } from '../../services/consultationService';
import { useNavigate } from 'react-router-dom';
import { FileText, Search, ExternalLink } from 'lucide-react';

const STATUS_STYLES = {
    pending: { dot: 'bg-yellow-400', text: 'text-yellow-700', bg: 'bg-yellow-50 border-yellow-200' },
    reviewed: { dot: 'bg-green-400', text: 'text-green-700', bg: 'bg-green-50 border-green-200' },
    closed: { dot: 'bg-blue-400', text: 'text-blue-700', bg: 'bg-blue-50 border-blue-200' },
};

const DoctorConsultations = () => {
    const [consultations, setConsultations] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const navigate = useNavigate();

    const fetchConsultations = async () => {
        try {
            setLoading(true);
            const data = await getDoctorAllConsultations();
            const list = data.consultations || [];
            setConsultations(list);
            setFiltered(list);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchConsultations(); }, []);

    useEffect(() => {
        let list = consultations;
        if (filterStatus !== 'all') list = list.filter(c => c.status === filterStatus);
        const q = search.toLowerCase();
        if (q) {
            list = list.filter(c =>
                (c.patient?.name || '').toLowerCase().includes(q) ||
                (c.symptoms || []).some(s => s.toLowerCase().includes(q))
            );
        }
        setFiltered(list);
    }, [search, filterStatus, consultations]);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Consultations</h1>
                    <p className="text-gray-500 text-sm mt-0.5">{consultations.length} consultation{consultations.length !== 1 ? 's' : ''} assigned to you</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search by patient name or symptom..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    />
                </div>
                <div className="flex gap-2">
                    {['all', 'pending', 'reviewed'].map(s => (
                        <button
                            key={s}
                            onClick={() => setFilterStatus(s)}
                            className={`px-3.5 py-2 rounded-xl text-xs font-medium capitalize transition-colors border ${filterStatus === s
                                    ? 'bg-violet-600 text-white border-violet-600'
                                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                                }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-20 text-gray-400">
                        <div className="flex flex-col items-center gap-3">
                            <FileText className="w-8 h-8 animate-pulse" />
                            <span className="text-sm">Loading consultations...</span>
                        </div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                        <FileText className="w-12 h-12 mb-3 opacity-20" />
                        <p className="text-sm font-medium">{search || filterStatus !== 'all' ? 'No consultations match your filters' : 'No consultations assigned yet'}</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-50 bg-gray-50/50">
                                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">Patient</th>
                                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">Symptoms</th>
                                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">Submitted By</th>
                                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">Status</th>
                                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">Date</th>
                                    <th className="px-6 py-4"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {filtered.map(c => {
                                    const st = STATUS_STYLES[c.status] || STATUS_STYLES.pending;
                                    return (
                                        <tr key={c._id} className="hover:bg-gray-50 transition-colors group">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2.5">
                                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center text-violet-700 font-semibold text-xs">
                                                        {(c.patient?.name || '?')[0].toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-semibold text-gray-800">{c.patient?.name || 'Unknown'}</p>
                                                        <p className="text-xs text-gray-400">{c.patient?.age} yrs, {c.patient?.gender}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex flex-wrap gap-1 max-w-[200px]">
                                                    {(c.symptoms || []).slice(0, 2).map((s, i) => (
                                                        <span key={i} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">{s.replace(/_/g, ' ')}</span>
                                                    ))}
                                                    {c.symptoms?.length > 2 && (
                                                        <span className="text-xs text-gray-400 px-1">+{c.symptoms.length - 2}</span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <p className="text-sm text-gray-700">{c.submittedBy?.name || 'Unknown'}</p>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium border ${st.bg} ${st.text}`}>
                                                    <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                                                    {c.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-xs text-gray-400">
                                                    {new Date(c.createdAt).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <button
                                                    onClick={() => navigate(`/doctor-dashboard/consultations/${c._id}`)}
                                                    className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-violet-600 hover:text-violet-700 font-medium"
                                                >
                                                    View <ExternalLink size={12} />
                                                </button>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DoctorConsultations;
