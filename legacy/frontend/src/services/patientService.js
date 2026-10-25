import api from './api';

export const registerPatient = async (data) => {
  const response = await api.post('/patient', data);
  return response.data;
};

export const getPatients = async () => {
  const response = await api.get('/patient');
  return response.data;
};

export const getPatient = async (id) => {
  const response = await api.get(`/patient/${id}`);
  return response.data;
};
