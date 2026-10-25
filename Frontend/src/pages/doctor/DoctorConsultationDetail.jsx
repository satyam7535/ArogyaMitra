import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getConsultation, submitSecondOpinion } from '../../services/consultationService';
import { ArrowLeft, User, Stethoscope, FileText, Clock, CheckCircle, MessageSquareDot, Paperclip, Brain, AlertTriangle, Send } from 'lucide-react';
import toast from 'react-hot-toast';

const Badge = ({ status }) => {
    const map = {
        pending: 'bg-yellow-50 text-yellow-700 border-yellow-200',
        reviewed: 'bg-green-50 text-green-700 border-green-200',
        closed: 'bg-blue-50 text-blue-700 border-blue-200',
    };
    return (
        <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${map[status] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
            {status?.charAt(0).toUpperCase() + status?.slice(1)}
        </span>
    );
};

const Section = ({ icon: Icon, title, children, iconColor = 'text-violet-600', bgColor = 'bg-violet-50' }) => (
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

const DoctorConsultationDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [consultation, setConsultation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [diagnosis, setDiagnosis] = useState('');
    const [recommendation, setRecommendation] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchConsultation = async () => {
            try {
                const data = await getConsultation(id);
                setConsultation(data.consultation);
            } catch (err) {
                toast.error('Could not load consultation');
            } finally {
                setLoading(false);
            }
        };
        fetchConsultation();
    }, [id]);

    const handleSubmitOpinion = async (e) => {
        e.preventDefault();
        if (!diagnosis.trim() || !recommendation.trim()) {
            toast.error('Both diagnosis and recommendation are required');
            return;
        }
        try {
            setSubmitting(true);
            await submitSecondOpinion(id, { diagnosis: diagnosis.trim(), recommendation: recommendation.trim() });
            toast.success('Second opinion submitted successfully!');
            // Refresh consultation
            const data = await getConsultation(id);
            setConsultation(data.consultation);
            setDiagnosis('');
            setRecommendation('');
        } catch (err) {
            toast.error(err.response?.data?.message || 'Failed to submit opinion');
        } finally {
            setSubmitting(false);
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
            <button onClick={() => navigate(-1)} className="mt-4 text-violet-600 text-sm underline">Go back</button>
        </div>
    );

    const { patient, symptoms, notes, attachments, status, submittedBy, secondOpinion, mlAnalysis, llmAnalysis, finalVerdict, createdAt } = consultation;

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
                        <p className="text-xs text-gray-400 mt-0.5">{new Date(createdAt).toLocaleString('en-IN')}</p>
                    </div>
                </div>
                <Badge status={status} />
            </div>

            {/* Patient Information */}
            <Section icon={User} title="Patient Information">
                <div className="grid grid-cols-2 gap-3">
                    <InfoRow label="Full Name" value={patient?.name} />
                    <InfoRow label="Age" value={patient?.age ? `${patient.age} years` : null} />
                    <InfoRow label="Gender" value={patient?.gender} />
                    {patient?.medicalHistory && (
                        <div className="col-span-2">
                            <InfoRow label="Medical History" value={patient.medicalHistory} />
                        </div>
                    )}
                </div>
            </Section>

            {/* Submitted By */}
            <Section icon={User} title="Submitted By" iconColor="text-secondary-600" bgColor="bg-secondary-50">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-secondary-100 flex items-center justify-center text-secondary-700 font-bold text-sm">
                        {submittedBy?.name?.[0]?.toUpperCase() || 'W'}
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-800">{submittedBy?.name || 'Unknown Worker'}</p>
                        <p className="text-xs text-gray-500">{submittedBy?.email}</p>
                    </div>
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
                                <Paperclip size={14} className="text-gray-400 group-hover:text-violet-500" />
                                <span className="text-sm text-violet-600 hover:text-violet-700 truncate">Attachment {i + 1}</span>
                            </a>
                        ))}
                    </div>
                </Section>
            )}

            {/* ML Analysis */}
            {mlAnalysis?.disease && (
                <Section icon={Brain} title="ML Analysis" iconColor="text-indigo-600" bgColor="bg-indigo-50">
                    <div className="space-y-3">
                        <InfoRow label="Predicted Disease" value={mlAnalysis.disease} />
                        <InfoRow label="Confidence" value={mlAnalysis.confidence ? `${(mlAnalysis.confidence * 100).toFixed(1)}%` : null} />
                        {mlAnalysis.precautions?.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-gray-500 mb-1.5">Precautions</p>
                                <ul className="space-y-1">
                                    {mlAnalysis.precautions.map((p, i) => (
                                        <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                                            <span className="text-indigo-400 mt-0.5">•</span> {p}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </Section>
            )}

            {/* LLM Analysis */}
            {llmAnalysis?.summary && (
                <Section icon={Brain} title="LLM Analysis" iconColor="text-teal-600" bgColor="bg-teal-50">
                    <div className="space-y-3">
                        <div>
                            <p className="text-xs font-medium text-gray-500 mb-1">Summary</p>
                            <p className="text-sm text-gray-700 bg-teal-50/50 rounded-xl px-4 py-3">{llmAnalysis.summary}</p>
                        </div>
                        {llmAnalysis.riskLevel && (
                            <div className="flex items-center gap-2">
                                <AlertTriangle size={14} className={
                                    llmAnalysis.riskLevel === 'high' ? 'text-red-500' :
                                        llmAnalysis.riskLevel === 'moderate' ? 'text-yellow-500' : 'text-green-500'
                                } />
                                <span className="text-sm font-medium capitalize">{llmAnalysis.riskLevel} Risk</span>
                            </div>
                        )}
                        {llmAnalysis.recommendations?.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-gray-500 mb-1.5">Recommendations</p>
                                <ul className="space-y-1">
                                    {llmAnalysis.recommendations.map((r, i) => (
                                        <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                                            <span className="text-teal-400 mt-0.5">•</span> {r}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </Section>
            )}

            {/* Final Verdict */}
            {finalVerdict?.conclusion && (
                <Section icon={CheckCircle} title="Final AI Verdict" iconColor="text-amber-600" bgColor="bg-amber-50">
                    <p className="text-sm text-gray-700 bg-amber-50/50 rounded-xl px-4 py-3">{finalVerdict.conclusion}</p>
                </Section>
            )}

            {/* Second Opinion - Form or Read-Only */}
            {status === 'pending' ? (
                <Section icon={Stethoscope} title="Submit Your Second Opinion" iconColor="text-violet-600" bgColor="bg-violet-50">
                    <form onSubmit={handleSubmitOpinion} className="space-y-4">
                        <div>
                            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Diagnosis *</label>
                            <textarea
                                value={diagnosis}
                                onChange={(e) => setDiagnosis(e.target.value)}
                                placeholder="Enter your diagnosis based on the patient's symptoms and analysis..."
                                rows={3}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none bg-gray-50 hover:bg-white transition-colors"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Recommendation *</label>
                            <textarea
                                value={recommendation}
                                onChange={(e) => setRecommendation(e.target.value)}
                                placeholder="Enter your treatment recommendations, medication suggestions, or follow-up advice..."
                                rows={3}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none bg-gray-50 hover:bg-white transition-colors"
                            />
                        </div>
                        <div className="flex justify-end">
                            <button
                                type="submit"
                                disabled={submitting || !diagnosis.trim() || !recommendation.trim()}
                                className="flex items-center gap-2 px-6 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
                            >
                                <Send size={14} />
                                {submitting ? 'Submitting...' : 'Submit Opinion'}
                            </button>
                        </div>
                    </form>
                </Section>
            ) : secondOpinion?.diagnosis ? (
                <Section icon={MessageSquareDot} title="Your Second Opinion" iconColor="text-green-600" bgColor="bg-green-50">
                    <div className="space-y-4">
                        <div>
                            <p className="text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Diagnosis</p>
                            <p className="text-sm text-gray-800 bg-green-50 rounded-xl px-4 py-3">{secondOpinion.diagnosis}</p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Recommendation</p>
                            <p className="text-sm text-gray-800 bg-green-50 rounded-xl px-4 py-3">{secondOpinion.recommendation}</p>
                        </div>
                        {secondOpinion.respondedAt && (
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                <CheckCircle size={12} className="text-green-500" />
                                Responded on {new Date(secondOpinion.respondedAt).toLocaleString('en-IN')}
                            </div>
                        )}
                    </div>
                </Section>
            ) : null}
        </div>
    );
};

export default DoctorConsultationDetail;
