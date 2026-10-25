import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getConsultation, acceptAI, escalateToDoctor, downloadAnalysisPdf, getAllDoctors } from '../../services/consultationService';
import ConsultationAnalysis from '../../components/ConsultationAnalysis';
import { ArrowLeft, Download, User, Stethoscope, FileText, Clock, CheckCircle, MessageSquareDot, Paperclip, Zap, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Badge = ({ status }) => {
  const map = {
    pending: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    closed: 'bg-green-50 text-green-700 border-green-200',
    reviewed: 'bg-blue-50 text-blue-700 border-blue-200',
  };
  return (
    <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${map[status] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
      {status?.charAt(0).toUpperCase() + status?.slice(1)}
    </span>
  );
};

const Section = ({ icon: Icon, title, children, iconColor = 'text-primary-600', bgColor = 'bg-primary-50' }) => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
    <div className={`flex items-center gap-3 px-6 py-4 border-b border-gray-50 ${bgColor}`}>
      <Icon className={`w-4 h-4 ${iconColor}`} />
      <h2 className="text-sm font-semibold text-gray-800">{title}</h2>
    </div>
    <div className="px-6 py-5">{children}</div>
  </div>
);

const InfoRow = ({ label, value }) => (
  <div className="flex items-start gap-2">
    <span className="text-xs font-medium text-gray-500 w-32 flex-shrink-0 pt-0.5">{label}</span>
    <span className="text-sm text-gray-800">{value || '—'}</span>
  </div>
);

const ConsultationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [consultation, setConsultation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [doctors, setDoctors] = useState([]); // In a real app, fetch from backend

  useEffect(() => {
    const fetchConsultation = async () => {
      try {
        const data = await getConsultation(id);
        setConsultation(data.consultation);
        // Fetch available doctors for escalation
        try {
          const doctorData = await getAllDoctors();
          setDoctors(doctorData.doctors || []);
        } catch (e) {
          console.error('Could not load doctors:', e);
        }
      } catch (err) {
        toast.error('Could not load consultation');
      } finally {
        setLoading(false);
      }
    };
    fetchConsultation();
  }, [id]);

  const handleDownloadPdf = async () => {
    const reportUrl = consultation?.analysisReport;
    if (!reportUrl) return;
    try {
      await downloadAnalysisPdf(
        reportUrl,
        `ArogyaMitra_${consultation.patient?.name || 'Report'}.pdf`
      );
      toast.success('PDF downloaded!');
    } catch { toast.error('Download failed'); }
  };

  // Called by ConsultationAnalysis when a new PDF is saved to backend
  const handlePdfSaved = async (newReportUrl) => {
    try {
      const data = await getConsultation(id);
      setConsultation(data.consultation);
    } catch {
      // Fallback: just update analysisReport field
      setConsultation(prev => prev ? { ...prev, analysisReport: newReportUrl } : prev);
    }
  };

  const handleResolve = async () => {
    try {
      await acceptAI(id);
      toast.success('Consultation resolved!');
      setShowAnalysis(false);
      // Refresh consultation data
      const data = await getConsultation(id);
      setConsultation(data.consultation);
    } catch (err) {
      toast.error(err.message || 'Failed to resolve consultation');
    }
  };

  const handleEscalate = async (doctorId, reason) => {
    try {
      await escalateToDoctor(id, doctorId);
      toast.success('Consultation escalated to doctor!');
      setShowAnalysis(false);
      // Refresh consultation data
      const data = await getConsultation(id);
      setConsultation(data.consultation);
    } catch (err) {
      toast.error(err.message || 'Failed to escalate consultation');
      throw err;
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-gray-400">
      <div className="flex flex-col items-center gap-3">
        <FileText className="w-8 h-8 animate-pulse" />
        <span className="text-sm">Loading consultation...</span>
      </div>
    </div>
  );

  if (!consultation) return (
    <div className="text-center py-20 text-gray-400">
      <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
      <p className="text-sm">Consultation not found</p>
      <button onClick={() => navigate(-1)} className="mt-4 text-primary-600 text-sm underline">Go back</button>
    </div>
  );

  const { patient, symptoms, notes, attachments, status, workerDecision, assignedDoctor, secondOpinion, createdAt } = consultation;

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      {/* Top bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="w-9 h-9 rounded-xl border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-800">Consultation Details</h1>
            <p className="text-xs text-gray-400 mt-0.5">{new Date(consultation.createdAt).toLocaleString('en-IN')}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge status={status} />
          {!showAnalysis && status === 'pending' && (
            <button
              onClick={() => setShowAnalysis(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition-colors"
            >
              <Zap size={14} />
              Analyze
            </button>
          )}
          {showAnalysis && (
            <button
              onClick={() => setShowAnalysis(false)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Back to Details
            </button>
          )}
          {!showAnalysis && (
            <button
              onClick={handleDownloadPdf}
              disabled={!consultation?.analysisReport}
              title={consultation?.analysisReport ? 'Download PDF report' : 'Run analysis first to generate PDF'}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm font-medium transition-colors ${
                consultation?.analysisReport
                  ? 'border-gray-200 text-gray-700 hover:bg-gray-50'
                  : 'border-gray-100 text-gray-300 cursor-not-allowed bg-gray-50'
              }`}
            >
              <Download size={14} />
              Download PDF
            </button>
          )}
          {!showAnalysis && status !== 'closed' && (
            <button
              onClick={handleResolve}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 hover:bg-green-700 text-white text-sm font-medium transition-colors"
            >
              <XCircle size={14} />
              Close Consultation
            </button>
          )}
        </div>
      </div>

      {/* Analysis Section */}
      {showAnalysis && (
        <ConsultationAnalysis
          consultation={consultation}
          onResolve={handleResolve}
          onEscalate={handleEscalate}
          doctors={doctors}
          onPdfSaved={handlePdfSaved}
        />
      )}

      {/* Details Section - Hidden when showing analysis */}
      {!showAnalysis && (
        <>
          <Section icon={User} title="Patient Information">
            <div className="grid grid-cols-2 gap-3">
              <InfoRow label="Full Name" value={patient?.name} />
              <InfoRow label="Age" value={patient?.age ? `${patient.age} years` : null} />
              <InfoRow label="Gender" value={patient?.gender} />
              <InfoRow label="Phone" value={patient?.phoneNumber} />
              <InfoRow label="Address" value={patient?.address} />
              {patient?.medicalHistory && (
                <div className="col-span-2">
                  <InfoRow label="Medical History" value={patient.medicalHistory} />
                </div>
              )}
            </div>
          </Section>

          {/* Symptoms & Notes */}
          <Section icon={FileText} title="Symptoms & Notes" iconColor="text-purple-600" bgColor="bg-purple-50">
            <div className="space-y-4">
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Symptoms Reported ({symptoms?.length || 0})</p>
                <div className="flex flex-wrap gap-1.5">
                  {(symptoms || []).map((s, i) => (
                    <span key={i} className="text-xs px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full border border-purple-100">
                      {s.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
              {notes && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Worker Notes</p>
                  <p className="text-sm text-gray-700 bg-gray-50 rounded-xl px-4 py-3">{notes}</p>
                </div>
              )}
            </div>
          </Section>

          {/* Attachments */}
          {attachments?.length > 0 && (
            <Section icon={Paperclip} title="Uploaded Attachments" iconColor="text-gray-600" bgColor="bg-gray-50">
              <div className="space-y-2">
                {attachments.map((url, i) => (
                  <a
                    key={i}
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-100 hover:bg-gray-50 hover:border-gray-200 transition-colors group"
                  >
                    <Paperclip size={14} className="text-gray-400 group-hover:text-primary-500" />
                    <span className="text-sm text-primary-600 hover:text-primary-700 truncate">Attachment {i + 1}</span>
                  </a>
                ))}
              </div>
            </Section>
          )}

          {/* Status & Decision */}
          <Section icon={Clock} title="Status & Decision" iconColor="text-amber-600" bgColor="bg-amber-50">
            <div className="grid grid-cols-2 gap-3">
              <InfoRow label="Status" value={<Badge status={status} />} />
              <InfoRow label="Worker Decision" value={workerDecision
                ? <span className={`text-xs px-2 py-0.5 rounded font-medium ${workerDecision === 'accepted' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
                  {workerDecision === 'accepted' ? 'AI Accepted' : 'Escalated to Doctor'}
                </span>
                : null}
              />
            </div>
          </Section>

          {/* Assigned Doctor */}
          {assignedDoctor && (
            <Section icon={Stethoscope} title="Assigned Doctor" iconColor="text-secondary-600" bgColor="bg-secondary-50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-secondary-100 flex items-center justify-center text-secondary-700 font-bold text-sm">
                  {assignedDoctor.name?.[0]?.toUpperCase() || 'D'}
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-800">{assignedDoctor.name}</p>
                  <p className="text-xs text-gray-500">{assignedDoctor.specialization || 'General Practitioner'}</p>
                </div>
              </div>
            </Section>
          )}

          {/* Second Opinion */}
          {secondOpinion?.diagnosis && (
            <Section icon={MessageSquareDot} title="Doctor's Second Opinion" iconColor="text-blue-600" bgColor="bg-blue-50">
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Diagnosis</p>
                  <p className="text-sm text-gray-800 bg-blue-50 rounded-xl px-4 py-3">{secondOpinion.diagnosis}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Recommendation</p>
                  <p className="text-sm text-gray-800 bg-blue-50 rounded-xl px-4 py-3">{secondOpinion.recommendation}</p>
                </div>
                {secondOpinion.respondedAt && (
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <CheckCircle size={12} className="text-green-500" />
                    Responded on {new Date(secondOpinion.respondedAt).toLocaleString('en-IN')}
                  </div>
                )}
              </div>
            </Section>
          )}
        </>
      )}
    </div>
  );
};

export default ConsultationDetail;
