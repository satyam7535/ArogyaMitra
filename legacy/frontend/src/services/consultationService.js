import axios from 'axios';
import api from './api';

/**
 * Fetch all available doctors (for escalation dropdown)
 */
export const getAllDoctors = async () => {
  const response = await api.get('/doctor/list');
  return response.data;
};

/**
 * Submit a new consultation (multipart/form-data)
 * @param {FormData} formData - includes patientId, symptoms (JSON string), notes, attachments[]
 */
export const submitConsultation = async (formData) => {
  const response = await api.post('/consultation', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getMyConsultations = async () => {
  const response = await api.get('/consultation/my');
  return response.data;
};

export const getConsultations = async () => {
  const response = await api.get('/consultation/admin/all');
  return response.data;
};

export const getConsultation = async (id) => {
  const response = await api.get(`/consultation/${id}`);
  return response.data;
};

export const acceptAI = async (id) => {
  const response = await api.patch(`/consultation/${id}/accept`);
  return response.data;
};

export const escalateToDoctor = async (id, doctorId, reason) => {
  const response = await api.patch(`/consultation/${id}/escalate`, { doctorId, reason });
  return response.data;
};

export const saveAnalysisPdf = async (id, pdfBase64) => {
  // Upload the base64 PDF to backend → Cloudinary, returns { reportUrl }
  const response = await api.post(`/consultation/${id}/analysis/report`, { pdfBase64 });
  return response.data; // { reportUrl, consultation }
};

export const downloadAnalysisPdf = async (reportUrl, filename) => {
  try {
    // Fetch the file as a blob to ensure correct filename and type
    const response = await axios.get(reportUrl, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || 'ArogyaMitra_Analysis_Report.pdf');
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
    // Fallback: try opening in new tab
    window.open(reportUrl, '_blank');
  }
};

export const storeMlAnalysis = async (id, mlResult) => {
  const response = await api.post(`/consultation/${id}/analysis/ml`, { mlResult });
  return response.data;
};

export const storeLlmAnalysis = async (id, llmResult) => {
  const response = await api.post(`/consultation/${id}/analysis/llm`, { llmResult });
  return response.data;
};

export const storeFinalVerdict = async (id, verdict) => {
  const response = await api.post(`/consultation/${id}/analysis/verdict`, { verdict });
  return response.data;
};

// ── Doctor-specific endpoints ──────────────────────────────────────────────────

export const getDoctorPendingConsultations = async () => {
  const response = await api.get('/consultation/pending');
  return response.data;
};

export const getDoctorAllConsultations = async () => {
  const response = await api.get('/consultation/doctor/all');
  return response.data;
};

export const submitSecondOpinion = async (id, { diagnosis, recommendation }) => {
  const response = await api.patch(`/consultation/${id}/respond`, { diagnosis, recommendation });
  return response.data;
};
