import api from './api';

export const loginDoctor = async (email, password) => {
  const response = await api.post('/doctor/login', { email, password });
  return response.data;
};

export const logoutDoctor = async () => {
  const response = await api.post('/doctor/logout');
  return response.data;
};
