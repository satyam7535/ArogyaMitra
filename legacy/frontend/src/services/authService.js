import api from './api';

export const loginAdmin = async (email, password) => {
  const response = await api.post('/admin/login', { email, password });
  return response.data;
};

export const registerAdmin = async (userData) => {
  const response = await api.post('/admin/register', userData);
  return response.data;
};

export const logoutAdmin = async () => {

  const response = await api.post('/admin/logout');
  return response.data;
};

export const getProfile = async () => {
    const response = await api.get('/admin/profile');
    return response.data;
};
