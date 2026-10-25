import { createContext, useContext, useState, useEffect } from 'react';
import { loginAdmin, logoutAdmin, getProfile as getAdminProfile } from '../services/authService';
import { loginWorker, logoutWorker } from '../services/workerAuthService';
import { loginDoctor, logoutDoctor } from '../services/doctorAuthService';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount: check for a persisted user in localStorage and re-validate via cookie
  useEffect(() => {
    const checkAuth = async () => {
      const storedRole = localStorage.getItem('userRole');
      try {
        if (storedRole === 'admin') {
          const data = await getAdminProfile();
          setUser({ ...data.user, role: 'admin' });
        } else if (storedRole === 'worker') {
          // Workers don't have a /profile endpoint yet; restore from localStorage
          const stored = localStorage.getItem('userData');
          if (stored) setUser({ ...JSON.parse(stored), role: 'worker' });
          else setUser(null);
        } else if (storedRole === 'doctor') {
          const stored = localStorage.getItem('userData');
          if (stored) setUser({ ...JSON.parse(stored), role: 'doctor' });
          else setUser(null);
        } else {
          setUser(null);
        }
      } catch {
        setUser(null);
        localStorage.removeItem('userRole');
        localStorage.removeItem('userData');
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  // ── Admin Login ───────────────────────────────────────────────────────────────
  const login = async (email, password) => {
    try {
      const data = await loginAdmin(email, password);
      const adminUser = { ...data.admin, role: 'admin' };
      setUser(adminUser);
      localStorage.setItem('userRole', 'admin');
      localStorage.setItem('userData', JSON.stringify(adminUser));
      toast.success('Welcome back, Admin!');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
      return false;
    }
  };

  // ── Admin Logout ──────────────────────────────────────────────────────────────
  const logout = async () => {
    try {
      await logoutAdmin();
    } catch { /* ignore */ }
    setUser(null);
    localStorage.removeItem('userRole');
    localStorage.removeItem('userData');
    toast.success('Logged out successfully');
  };

  // ── Worker Login ──────────────────────────────────────────────────────────────
  const loginAsWorker = async (email, password) => {
    try {
      const data = await loginWorker(email, password);
      const workerUser = { ...data.worker, role: 'worker' };
      setUser(workerUser);
      localStorage.setItem('userRole', 'worker');
      localStorage.setItem('userData', JSON.stringify(workerUser));
      toast.success(`Welcome, ${data.worker.name}!`);
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
      return false;
    }
  };

  // ── Worker Logout ─────────────────────────────────────────────────────────────
  const logoutAsWorker = async () => {
    try {
      await logoutWorker();
    } catch { /* ignore */ }
    setUser(null);
    localStorage.removeItem('userRole');
    localStorage.removeItem('userData');
    toast.success('Logged out successfully');
  };

  // ── Doctor Login ──────────────────────────────────────────────────────────────
  const loginAsDoctor = async (email, password) => {
    try {
      const data = await loginDoctor(email, password);
      const doctorUser = { ...data.doctor, role: 'doctor' };
      setUser(doctorUser);
      localStorage.setItem('userRole', 'doctor');
      localStorage.setItem('userData', JSON.stringify(doctorUser));
      toast.success(`Welcome, Dr. ${data.doctor.name}!`);
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
      return false;
    }
  };

  // ── Doctor Logout ─────────────────────────────────────────────────────────────
  const logoutAsDoctor = async () => {
    try {
      await logoutDoctor();
    } catch { /* ignore */ }
    setUser(null);
    localStorage.removeItem('userRole');
    localStorage.removeItem('userData');
    toast.success('Logged out successfully');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loginAsWorker, logoutAsWorker, loginAsDoctor, logoutAsDoctor, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
