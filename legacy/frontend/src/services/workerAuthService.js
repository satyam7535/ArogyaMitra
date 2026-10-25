import api from './api';

export const loginWorker = async (email, password) => {
  const response = await api.post('/worker/login', { email, password });
  return response.data;
};

export const logoutWorker = async () => {
  const response = await api.post('/worker/logout');
  return response.data;
};
