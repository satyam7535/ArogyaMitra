import api from './api';

export const addDoctor = async (data) => {
  const response = await api.post('/doctor', data);
  return response.data;
};

export const getDoctors = async () => {
    const response = await api.get('/doctor');
    return response.data;
};

export const addWorker = async (data) => {
    const response = await api.post('/worker', data);
    return response.data;
};

export const getWorkers = async () => {
    const response = await api.get('/worker');
    return response.data;
};

export const deleteDoctor = async (id) => {
    const response = await api.delete(`/doctor/${id}`);
    return response.data;
};

export const deleteWorker = async (id) => {
    const response = await api.delete(`/worker/${id}`);
    return response.data;
};

// Worker uses this to fetch all doctors for escalation dropdown
export const getDoctorsForWorker = async () => {
    const response = await api.get('/doctor/list');
    return response.data;
};
