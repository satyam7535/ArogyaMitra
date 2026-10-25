import { useState } from 'react';
import { acceptAI, escalateToDoctor } from '../services/consultationService';
import { downloadPredictPdf } from '../services/mlService';
import { getDoctorsForWorker } from '../services/adminService';
import toast from 'react-hot-toast';
import {
  Brain, MessageSquare, CheckCircle2, AlertTriangle, Download,
  TrendingUp, ChevronDown, ChevronUp, Loader2, Stethoscope, X, ArrowUpRight
} from 'lucide-react';

// ── Sub-components ─────────────────────────────────────────────────────────────

const ConfidenceBadge = ({ value }) => {
  const color = value >= 75 ? 'text-green-700 bg-green-50 border-green-200'
    : value >= 50 ? 'text-yellow-700 bg-yellow-50 border-yellow-200'
    : 'text-red-700 bg-red-50 border-red-200';
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${color}`}>{value}%</span>
  );
};

const SeverityBar = ({ value }) => {
  const pct = Math.round((value / 7) * 100);
  const color = value >= 5 ? 'bg-red-500' : value >= 3 ? 'bg-yellow-500' : 'bg-green-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-gray-700 w-8">{value}/7</span>
    </div>
  );
};

// ── Main Component ─────────────────────────────────────────────────────────────

const ConsultationResultPanel = ({ mlResult, consultationId, patients, patientId, symptoms, onClose, onCreated }) => {
  const [showLime, setShowLime] = useState(false);
  const [showEscalate, setShowEscalate] = useState(false);
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [loadingDoctors, setLoadingDoctors] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const patient = patients.find(p => p._id === patientId);

  const handleAccept = async () => {
    setActionLoading(true);
    try {
      await acceptAI(consultationId);
      toast.success('Consultation closed. AI result accepted.');
      onCreated?.();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to accept result');
    } finally { setActionLoading(false); }
  };

  const handleEscalateOpen = async () => {
    setLoadingDoctors(true);
    try {
      const data = await getDoctorsForWorker();
      setDoctors(Array.isArray(data) ? data : (data.doctors || []));
      setShowEscalate(true);
    } catch { toast.error('Could not load doctors'); }
    finally { setLoadingDoctors(false); }
  };

  const handleEscalate = async () => {
    if (!selectedDoctor) return toast.error('Please select a doctor');
    setActionLoading(true);
    try {
      await escalateToDoctor(consultationId, selectedDoctor);
      toast.success('Consultation escalated to doctor for second opinion.');
      onCreated?.();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to escalate');
    } finally { setActionLoading(false); }
  };

  const handleDownloadPdf = async () => {
    try {
      toast.loading('Generating PDF report...');
      await downloadPredictPdf(
        {
          symptoms: symptoms.map(s => s.replace(/_/g, ' ')),
          patientName: patient?.name || 'Patient',
          patientAge: patient?.age,
          patientGender: patient?.gender,
          workerName: 'Healthcare Worker',
        },
        `ArogyaMitra_${patient?.name || 'Report'}_${Date.now()}.pdf`
      );
      toast.dismiss();
      toast.success('PDF downloaded!');
    } catch { toast.error('PDF generation failed'); }
  };

  return (
    <div className="space-y-4 pt-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
        <Brain className="w-4 h-4 text-primary-600" />
        AI Analysis Complete
      </div>

      {/* Primary Diagnosis Card */}
      <div className="bg-primary-50 border border-primary-100 rounded-xl p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <p className="text-xs font-medium text-primary-500 uppercase tracking-wider">Primary Diagnosis</p>
            <p className="text-xl font-bold text-primary-800 mt-0.5">{mlResult.primaryDiagnosis}</p>
            <p className="text-xs text-primary-600 mt-1 leading-relaxed">{mlResult.description}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <ConfidenceBadge value={mlResult.confidenceScore} />
            <p className="text-xs text-gray-500 mt-1.5">Confidence</p>
          </div>
        </div>
        <div className="mt-3">
          <p className="text-xs text-gray-500 mb-1">Severity Score</p>
          <SeverityBar value={mlResult.severityScore} />
        </div>
      </div>

      {/* Top 3 Predictions */}
      <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-600 flex items-center gap-1.5">
            <TrendingUp size={12} /> Differential Diagnoses (Top 3)
          </p>
        </div>
        <div className="divide-y divide-gray-50">
          {mlResult.topPredictions?.map((p, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-2.5">
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${i === 0 ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'}`}>{i + 1}</span>
                <span className="text-sm text-gray-700">{p.disease}</span>
              </div>
              <ConfidenceBadge value={p.confidence} />
            </div>
          ))}
        </div>
      </div>

      {/* Matched Symptoms */}
      {mlResult.matchedSymptoms?.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 mb-1.5">Matched Symptoms ({mlResult.matchedSymptoms.length})</p>
          <div className="flex flex-wrap gap-1.5">
            {mlResult.matchedSymptoms.map((s, i) => (
              <span key={i} className="text-xs px-2.5 py-1 bg-green-50 text-green-700 rounded-full border border-green-100">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Precautions */}
      {mlResult.precautions?.length > 0 && (
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
          <p className="text-xs font-semibold text-amber-700 mb-2">Recommended Precautions</p>
          <ol className="space-y-1">
            {mlResult.precautions.map((p, i) => (
              <li key={i} className="text-xs text-amber-800 flex items-start gap-2">
                <span className="font-bold">{i + 1}.</span> {p}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* LIME Explanation (collapsible) */}
      {mlResult.limeExplanation?.length > 0 && (
        <div className="border border-gray-100 rounded-xl overflow-hidden">
          <button
            onClick={() => setShowLime(v => !v)}
            className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
          >
            <p className="text-xs font-semibold text-gray-600">AI Explanation (LIME)</p>
            {showLime ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showLime && (
            <div className="divide-y divide-gray-50">
              {mlResult.limeExplanation.map((l, i) => (
                <div key={i} className="flex items-center justify-between px-4 py-2">
                  <span className="text-xs text-gray-700">{l.feature}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-medium ${l.impact > 0 ? 'text-green-700' : 'text-red-600'}`}>
                      {l.impact > 0 ? '+' : ''}{l.impact}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${l.direction.includes('Supports') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
                      {l.direction.includes('Supports') ? '✓ Supports' : '✗ Against'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Disclaimer */}
      <div className="flex items-start gap-2 bg-yellow-50 border border-yellow-100 rounded-xl p-3">
        <AlertTriangle size={14} className="text-yellow-600 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-yellow-700 leading-relaxed">
          This is an AI-assisted prediction and <strong>not a clinical diagnosis</strong>. If you're not confident in this result, escalate to a doctor for a second opinion.
        </p>
      </div>

      {/* Escalate Doctor Selector */}
      {showEscalate && (
        <div className="border border-blue-100 bg-blue-50 rounded-xl p-4 space-y-3">
          <p className="text-sm font-semibold text-blue-800 flex items-center gap-2">
            <Stethoscope size={15} /> Select a Doctor for Second Opinion
          </p>
          <select
            value={selectedDoctor}
            onChange={e => setSelectedDoctor(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-blue-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">-- Choose Doctor --</option>
            {doctors.map(d => (
              <option key={d._id} value={d._id}>{d.name} — {d.specialization || 'General'}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <button onClick={() => setShowEscalate(false)} className="flex-1 px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-white transition-colors">
              Cancel
            </button>
            <button
              onClick={handleEscalate}
              disabled={actionLoading || !selectedDoctor}
              className="flex-1 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <ArrowUpRight size={14} />}
              Confirm Escalation
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
        <button
          onClick={handleDownloadPdf}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 text-gray-700 text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          <Download size={16} />
          Download PDF
        </button>
        <button
          onClick={handleEscalateOpen}
          disabled={actionLoading || loadingDoctors || showEscalate}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100 text-sm font-medium transition-colors disabled:opacity-60"
        >
          {loadingDoctors ? <Loader2 size={14} className="animate-spin" /> : <ArrowUpRight size={16} />}
          Escalate to Doctor
        </button>
        <button
          onClick={handleAccept}
          disabled={actionLoading}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-secondary-600 hover:bg-secondary-700 text-white text-sm font-medium transition-colors disabled:opacity-60"
        >
          {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={16} />}
          Accept & Close
        </button>
      </div>
    </div>
  );
};

export default ConsultationResultPanel;
