import { useState, useEffect } from 'react';
import { getPatients } from '../../services/patientService';
import AddPatientModal from '../../components/AddPatientModal';
import { UserPlus, Search, Users, Phone, MapPin, Calendar } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const WorkerPatients = () => {
  const { t } = useTranslation();
  const [patients, setPatients] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const data = await getPatients();
      const list = data.patients || [];
      setPatients(list);
      setFiltered(list);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPatients(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(patients.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.gender.toLowerCase().includes(q) ||
      (p.phoneNumber || '').includes(q)
    ));
  }, [search, patients]);

  const genderBadge = (g) => {
    const map = { male: 'bg-blue-50 text-blue-700', female: 'bg-pink-50 text-pink-700', other: 'bg-gray-100 text-gray-600' };
    return map[g] || 'bg-gray-100 text-gray-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{t('common.patients')}</h1>
          <p className="text-gray-500 text-sm mt-0.5">{patients.length} {t('worker.registered_by_organization')}</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-secondary-600 hover:bg-secondary-700 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
        >
          <UserPlus size={16} />
          {t('worker.add_patient')}
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          placeholder={t('worker.search_patients')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:border-transparent transition-colors"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-gray-400">
            <div className="flex flex-col items-center gap-3">
              <Users className="w-8 h-8 animate-pulse" />
              <span className="text-sm">{t('worker.loading_patients')}</span>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Users className="w-12 h-12 mb-3 opacity-20" />
            <p className="text-sm font-medium">{search ? t('worker.no_patients_found') : t('worker.no_patients_yet')}</p>
            {!search && (
              <button
                onClick={() => setIsModalOpen(true)}
                className="mt-4 text-sm text-secondary-600 underline hover:text-secondary-700"
              >
                {t('worker.register_first_patient')}
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-50 bg-gray-50/50">
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">{t('common.table.patient')}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">{t('common.table.age_gender')}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">{t('common.table.contact')}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">{t('common.table.address')}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-4">{t('common.table.registered')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((patient) => (
                  <tr key={patient._id} className="hover:bg-gray-50 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                          {patient.name[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{patient.name}</p>
                          {patient.medicalHistory && (
                            <p className="text-xs text-gray-400 mt-0.5 max-w-[160px] truncate">{patient.medicalHistory}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-700 font-medium">{patient.age} yrs</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block ${genderBadge(patient.gender)}`}>
                        {t(`common.gender.${patient.gender}`)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {patient.phoneNumber ? (
                        <div className="flex items-center gap-1.5 text-sm text-gray-600">
                          <Phone size={12} className="text-gray-400" />
                          {patient.phoneNumber}
                        </div>
                      ) : <span className="text-gray-400 text-sm">—</span>}
                    </td>
                    <td className="px-6 py-4">
                      {patient.address ? (
                        <div className="flex items-center gap-1.5 text-sm text-gray-600 max-w-[180px]">
                          <MapPin size={12} className="text-gray-400 flex-shrink-0" />
                          <span className="truncate">{patient.address}</span>
                        </div>
                      ) : <span className="text-gray-400 text-sm">—</span>}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <Calendar size={11} />
                        {new Date(patient.createdAt).toLocaleDateString()}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AddPatientModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdded={fetchPatients}
      />
    </div>
  );
};

export default WorkerPatients;
