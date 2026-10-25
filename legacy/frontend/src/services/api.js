import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  withCredentials: true, // Send cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Optional: Global error handling (e.g., token expired -> logout)
    if (error.response?.status === 401) {
       // Logic to redirect to login could go here or be handled in AuthContext
    }
    return Promise.reject(error);
  }
);

export default api;
