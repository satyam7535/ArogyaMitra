import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Stethoscope, UserRound, ArrowRight, Heart } from 'lucide-react';

const roles = [
  {
    id: 'admin',
    title: 'Admin',
    subtitle: 'Manage doctors, workers & system overview',
    icon: ShieldCheck,
    route: '/admin-login',
    gradient: 'from-sky-400 to-blue-600',
    border: 'border-sky-100 hover:border-sky-300',
    bg: 'hover:bg-sky-50',
    iconBg: 'bg-sky-100',
    iconColor: 'text-sky-600',
    badge: 'bg-sky-100 text-sky-700',
    dot: 'bg-sky-400',
  },
  {
    id: 'worker',
    title: 'Healthcare Worker',
    subtitle: 'Register patients, create AI-powered consultations',
    icon: UserRound,
    route: '/worker-login',
    gradient: 'from-emerald-400 to-teal-600',
    border: 'border-emerald-100 hover:border-emerald-300',
    bg: 'hover:bg-emerald-50',
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    badge: 'bg-emerald-100 text-emerald-700',
    dot: 'bg-emerald-400',
  },
  {
    id: 'doctor',
    title: 'Doctor',
    subtitle: 'Review escalated cases & provide second opinions',
    icon: Stethoscope,
    route: '/doctor-login',
    gradient: 'from-violet-400 to-purple-600',
    border: 'border-violet-100 hover:border-violet-300',
    bg: 'hover:bg-violet-50',
    iconBg: 'bg-violet-100',
    iconColor: 'text-violet-600',
    badge: 'bg-violet-100 text-violet-700',
    dot: 'bg-violet-400',
  },
];

const RoleSelect = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50 to-emerald-50 flex flex-col items-center justify-center px-4 py-12">

      {/* Background blobs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-sky-200/30 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-24 w-80 h-80 bg-emerald-200/30 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 left-1/3 w-72 h-72 bg-violet-200/20 rounded-full blur-3xl" />
      </div>

      <div className="text-center mb-12 flex flex-col items-center">
        <div className="mb-6">
          <img src="/bg.png" alt="ArogyaMitra Logo" className="w-28 h-28 object-contain" />
        </div>
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">ArogyaMitra</h1>
      </div>

      {/* Role heading */}
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-6">
        Select your role to continue
      </h2>

      {/* Role cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 w-full max-w-3xl">
        {roles.map((role) => {
          const Icon = role.icon;
          return (
            <button
              key={role.id}
              onClick={() => navigate(role.route)}
              className={`group relative flex flex-col items-start text-left bg-white ${role.bg} border-2 ${role.border} rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-200 hover:-translate-y-1`}
            >
              {/* Icon */}
              <div className={`w-12 h-12 ${role.iconBg} rounded-xl flex items-center justify-center mb-4`}>
                <Icon className={`w-6 h-6 ${role.iconColor}`} />
              </div>

              {/* Title */}
              <h3 className="text-base font-bold text-gray-900 mb-1">{role.title}</h3>

              {/* Subtitle */}
              <p className="text-xs text-gray-500 leading-relaxed flex-1">{role.subtitle}</p>

              {/* Arrow CTA */}
              <div className={`mt-5 flex items-center gap-1.5 text-xs font-semibold ${role.iconColor}`}>
                Login as {role.title.split(' ')[0]}
                <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
              </div>

              {/* Gradient bar at top */}
              <div className={`absolute top-0 left-6 right-6 h-0.5 bg-gradient-to-r ${role.gradient} rounded-full opacity-0 group-hover:opacity-100 transition-opacity`} />
            </button>
          );
        })}
      </div>

      {/* Footer */}
      <p className="mt-12 text-xs text-gray-400 text-center">
        ArogyaMitra • Techathon 3.0 &nbsp;|&nbsp; Designed for frontline healthcare workers
      </p>
    </div>
  );
};

export default RoleSelect;
