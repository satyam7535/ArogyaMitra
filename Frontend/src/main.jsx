import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import './index.css';
import './i18n';

// ── Admin Pages ───────────────────────────────────────────────────────────────
import RoleSelect from './pages/RoleSelect';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Overview from './pages/Overview';
import Doctors from './pages/AddDoctor';
import Workers from './pages/AddWorker';
import DashboardLayout from './layout/DashboardLayout';

// ── Worker Pages ──────────────────────────────────────────────────────────────
import WorkerLogin from './pages/WorkerLogin';
import WorkerDashboardLayout from './layout/WorkerDashboardLayout';
import WorkerOverview from './pages/worker/WorkerOverview';
import WorkerPatients from './pages/worker/WorkerPatients';
import WorkerConsultations from './pages/worker/WorkerConsultations';
import ConsultationDetail from './pages/worker/ConsultationDetail';

// ── Doctor Pages ──────────────────────────────────────────────────────────────────
import DoctorLogin from './pages/DoctorLogin';
import DoctorDashboardLayout from './layout/DoctorDashboardLayout';
import DoctorOverview from './pages/doctor/DoctorOverview';
import DoctorConsultations from './pages/doctor/DoctorConsultations';
import DoctorConsultationDetail from './pages/doctor/DoctorConsultationDetail';

// ── Route Guards ──────────────────────────────────────────────────────────────
const ProtectedRoute = ({ children, role }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Loading...</div>;
  if (!user) return <Navigate to="/" replace />;
  if (role && user.role !== role) {
    // Redirect to appropriate dashboard
    if (user.role === 'worker') return <Navigate to="/worker-dashboard" replace />;
    if (user.role === 'admin') return <Navigate to="/dashboard" replace />;
    if (user.role === 'doctor') return <Navigate to="/doctor-dashboard" replace />;
  }
  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* ── Root: Role selector ─────────────────────────────────── */}
      <Route path="/" element={<RoleSelect />} />

      {/* ── Public Routes ──────────────────────────────────────────── */}
      <Route path="/admin-login" element={<Login />} />
      <Route path="/worker-login" element={<WorkerLogin />} />
      <Route path="/doctor-login" element={<DoctorLogin />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      {/* ── Admin Dashboard ────────────────────────────────────────── */}
      <Route path="/dashboard" element={
        <ProtectedRoute role="admin">
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Overview />} />
        <Route path="doctors" element={<Doctors />} />
        <Route path="workers" element={<Workers />} />
      </Route>

      {/* ── Worker Dashboard ───────────────────────────────────────── */}
      <Route path="/worker-dashboard" element={
        <ProtectedRoute role="worker">
          <WorkerDashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<WorkerOverview />} />
        <Route path="patients" element={<WorkerPatients />} />
        <Route path="consultations" element={<WorkerConsultations />} />
        <Route path="consultations/:id" element={<ConsultationDetail />} />
      </Route>

      {/* ── Doctor Dashboard ─────────────────────────────────────────────── */}
      <Route path="/doctor-dashboard" element={
        <ProtectedRoute role="doctor">
          <DoctorDashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<DoctorOverview />} />
        <Route path="consultations" element={<DoctorConsultations />} />
        <Route path="consultations/:id" element={<DoctorConsultationDetail />} />
      </Route>

      {/* ── Fallback ───────────────────────────────────────────────── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
