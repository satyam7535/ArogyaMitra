import { useState } from 'react';
import { analyzeWithGraph } from '../services/mlService';
import { saveAnalysisPdf, downloadAnalysisPdf, storeMlAnalysis, storeLlmAnalysis } from '../services/consultationService';
import { Loader2, Download, CheckCircle, AlertCircle, FileText, ThumbsUp, ThumbsDown, Brain, Activity, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const ConsultationAnalysis = ({
  consultation,
  onResolve,
  onEscalate,
  doctors = [],
  onPdfSaved,   // callback(reportUrl) so parent can refresh consultation
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(consultation?.analysisReport || null);
  const [pdfFilename, setPdfFilename] = useState(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [escalateReason, setEscalateReason] = useState('');
  const [step, setStep] = useState('idle'); // idle | analyzing | done

  const handleAnalyze = async () => {
    if (!consultation) return;
    setIsAnalyzing(true);
    setStep('analyzing');

    const patient = consultation.patient || {};
    const payload = {
      symptoms: (consultation.symptoms || []).map(s => s.replace(/_/g, ' ')),
      patientName: patient?.name || 'Patient',
      patientAge: patient?.age,
      patientGender: patient?.gender,
      workerName: consultation.submittedBy?.name || 'Healthcare Worker',
      location: patient?.address || '',
    };

    try {
      // ── Call graph server (runs ML + LLM + generates PDF) ────────────────────
      const graphData = await analyzeWithGraph(payload);

      const { mlResult, llmResult, pdfBase64, filename } = graphData;

      // ── Store ML + LLM results in backend ───────────────────────────────────
      await Promise.all([
        storeMlAnalysis(consultation._id, {
          disease: mlResult.disease,
          confidence: mlResult.confidence,
          precautions: mlResult.precautions,
        }),
        storeLlmAnalysis(consultation._id, {
          summary: llmResult.diagnosis_summary || '',
          recommendations: [
            llmResult.recommended_next_steps || '',
            llmResult.referral_recommendation || '',
          ].filter(Boolean),
          riskLevel: llmResult.severity_assessment?.toLowerCase().includes('high')
            ? 'high'
            : llmResult.severity_assessment?.toLowerCase().includes('low')
              ? 'low'
              : 'moderate',
        }),
      ]);

      // ── Upload PDF to backend → Cloudinary ───────────────────────────────────
      let savedUrl = null;
      try {
        const saved = await saveAnalysisPdf(consultation._id, pdfBase64);
        savedUrl = saved.reportUrl;
        setPdfUrl(savedUrl);
        setPdfFilename(filename);
        if (onPdfSaved) onPdfSaved(savedUrl);
      } catch (pdfErr) {
        console.error('PDF upload failed:', pdfErr);
        // Store PDF locally in memory so worker can still download this session
        const blob = new Blob(
          [Uint8Array.from(atob(pdfBase64), c => c.charCodeAt(0))],
          { type: 'application/pdf' }
        );
        const localUrl = URL.createObjectURL(blob);
        setPdfUrl(localUrl);
        setPdfFilename(filename);
        toast.error('PDF could not be saved to cloud — you can still download it below.');
      }

      setAnalysisResult({ mlResult, llmResult });
      setStep('done');
      toast.success('Analysis complete!');
    } catch (err) {
      setStep('idle');
      toast.error(err.response?.data?.detail || err.message || 'Analysis failed. Is the graph server running?');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!pdfUrl) return;
    setIsDownloading(true);
    try {
      await downloadAnalysisPdf(pdfUrl, pdfFilename || `ArogyaMitra_${consultation.patient?.name || 'Report'}.pdf`);
      toast.success('PDF downloaded!');
    } catch {
      toast.error('Download failed');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleEscalate = async () => {
    if (!selectedDoctor) {
      toast.error('Please select a doctor');
      return;
    }
    if (!escalateReason) {
      toast.error('Please provide a reason for escalation');
      return;
    }
    try {
      await onEscalate(selectedDoctor, escalateReason);
      setSelectedDoctor('');
      setEscalateReason('');
      setAnalysisResult(null);
    } catch (err) {
      toast.error(err.message || 'Escalation failed');
    }
  };

  // ── Loading / idle state ──────────────────────────────────────────────────────
  if (!analysisResult) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden p-6">
        <div className="flex flex-col items-center justify-center py-12">
          {isAnalyzing ? (
            <>
              <div className="relative mb-6">
                <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
                </div>
              </div>
              <p className="text-lg font-semibold text-gray-800 mb-2">Analyzing Consultation</p>
              <div className="flex flex-col items-center gap-2 mt-3">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Activity className="w-4 h-4 text-blue-500" />
                  <span>Running ML model (XAI pipeline)…</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Brain className="w-4 h-4 text-purple-500" />
                  <span>Generating LLM clinical summary…</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <FileText className="w-4 h-4 text-green-500" />
                  <span>Compiling PDF report…</span>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="bg-primary-50 w-14 h-14 rounded-full flex items-center justify-center mb-4">
                <Zap className="w-7 h-7 text-primary-600" />
              </div>
              <p className="text-lg font-semibold text-gray-800 mb-2">Ready for Analysis</p>
              <p className="text-sm text-gray-500 text-center mb-6 max-w-sm">
                Click below to run the full pipeline: ML model prediction → LLM clinical summary → PDF report generation.
              </p>
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors disabled:opacity-60 flex items-center gap-2"
              >
                <Zap size={18} />
                Start Analysis
              </button>
            </>
          )}
        </div>

        {/* Escalate Section — always visible */}
        {doctors && doctors.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden p-6 space-y-4">
            <p className="text-sm font-medium text-gray-700">Or Escalate to Doctor for Second Opinion</p>
            <select
              value={selectedDoctor}
              onChange={(e) => setSelectedDoctor(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">-- Select a doctor --</option>
              {doctors.map(doc => (
                <option key={doc._id} value={doc._id}>{doc.name} ({doc.specialization})</option>
              ))}
            </select>
            <textarea
              value={escalateReason}
              onChange={(e) => setEscalateReason(e.target.value)}
              placeholder="Reason for escalation..."
              rows="3"
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            />
            <button
              onClick={handleEscalate}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-xl transition-colors flex items-center gap-2"
            >
              <ThumbsDown size={18} />
              Escalate to Doctor
            </button>
          </div>
        )}
      </div>
    );
  }

  const { mlResult, llmResult } = analysisResult;

  // ── Results ───────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-4">

      {/* ML Results */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-50 bg-blue-50">
          <Activity className="w-5 h-5 text-blue-600" />
          <h3 className="text-sm font-semibold text-gray-800">ML Model Analysis (XAI)</h3>
        </div>
        <div className="px-6 py-5 space-y-4">
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">Predicted Disease</p>
            <p className="text-xl font-bold text-blue-700">{mlResult.disease || 'Unknown'}</p>
          </div>
          {mlResult.confidence != null && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Confidence Score</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-700"
                    style={{ width: `${Math.min((mlResult.confidence || 0) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-gray-700">
                  {((mlResult.confidence || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}
          {mlResult.precautions?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-2">Precautions</p>
              <ul className="space-y-1.5">
                {mlResult.precautions.map((p, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {mlResult.description && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Description</p>
              <p className="text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2 italic">{mlResult.description}</p>
            </div>
          )}
        </div>
      </div>

      {/* LLM Clinical Summary */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-50 bg-purple-50">
          <Brain className="w-5 h-5 text-purple-600" />
          <h3 className="text-sm font-semibold text-gray-800">LLM Clinical Decision Support</h3>
        </div>
        <div className="px-6 py-5 space-y-4">
          {llmResult.diagnosis_summary && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Diagnosis Summary</p>
              <p className="text-sm text-gray-700 bg-purple-50 rounded-lg px-3 py-2">{llmResult.diagnosis_summary}</p>
            </div>
          )}
          {llmResult.severity_assessment && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Severity Assessment</p>
              <p className="text-sm text-gray-700">{llmResult.severity_assessment}</p>
            </div>
          )}
          {llmResult.recommended_next_steps && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Recommended Next Steps</p>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg px-3 py-2">{llmResult.recommended_next_steps}</p>
            </div>
          )}
          {llmResult.referral_recommendation && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Referral Recommendation</p>
              <p className="text-sm text-gray-700">{llmResult.referral_recommendation}</p>
            </div>
          )}
          {llmResult.confidence_interpretation && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Confidence Interpretation</p>
              <p className="text-sm text-gray-600 italic">{llmResult.confidence_interpretation}</p>
            </div>
          )}
        </div>
      </div>

      {/* PDF Download */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-50 bg-green-50">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <h3 className="text-sm font-semibold text-gray-800">Full Report (PDF)</h3>
        </div>
        <div className="px-6 py-5">
          <p className="text-sm text-gray-600 mb-4">
            {pdfUrl
              ? 'Your full AI analysis report is ready. It includes the ML model output, LLM clinical summary, and all supporting data.'
              : 'PDF report could not be generated. Please re-run the analysis.'}
          </p>
          <button
            onClick={handleDownloadPdf}
            disabled={!pdfUrl || isDownloading}
            className={`flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl font-medium transition-colors ${
              pdfUrl
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isDownloading ? (
              <><Loader2 size={18} className="animate-spin" /> Downloading…</>
            ) : (
              <><Download size={18} /> {pdfUrl ? 'Download Full PDF Report' : 'PDF Not Available'}</>
            )}
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden p-6 space-y-4">
        <p className="text-sm font-semibold text-gray-700">Action Required</p>
        <p className="text-xs text-gray-500">Review the report and choose how to proceed with this consultation.</p>

        {/* Resolve */}
        <button
          onClick={onResolve}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-xl transition-colors"
        >
          <ThumbsUp size={18} />
          Resolve Consultation (Satisfied with AI Result)
        </button>

        {/* Escalate to Doctor */}
        <div className="space-y-3 pt-3 border-t border-gray-100">
          <p className="text-sm font-medium text-gray-700 flex items-center gap-2">
            <AlertCircle size={16} className="text-orange-500" />
            Escalate to a Doctor
          </p>
          {doctors && doctors.length > 0 ? (
            <>
              <select
                value={selectedDoctor}
                onChange={(e) => setSelectedDoctor(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">-- Select a Doctor --</option>
                {doctors.map(doc => (
                  <option key={doc._id} value={doc._id}>{doc.name} ({doc.specialization})</option>
                ))}
              </select>
              <textarea
                value={escalateReason}
                onChange={(e) => setEscalateReason(e.target.value)}
                placeholder="Reason for escalation (e.g. unclear diagnosis, severe symptoms)…"
                rows="3"
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
              <button
                onClick={handleEscalate}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-xl transition-colors flex items-center gap-2"
              >
                <ThumbsDown size={18} />
                Escalate to Doctor
              </button>
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No doctors available for escalation. Please contact admin.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConsultationAnalysis;
