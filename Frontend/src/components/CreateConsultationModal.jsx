import { useState, useEffect, useCallback } from 'react';
import { getPatients } from '../services/patientService';
import { predict } from '../services/mlService';
import { submitConsultation } from '../services/consultationService';
import ConsultationResultPanel from './ConsultationResultPanel';
import toast from 'react-hot-toast';
import { X, ChevronRight, ChevronLeft, Loader2, FlaskConical, Stethoscope, Paperclip, User, FileText } from 'lucide-react';

const STEP_LABELS = ['Patient & Notes', 'Symptoms', 'Attachments'];
const FILE_TYPES = [
  { key: 'bloodTest',  label: 'Blood Test Report',  accept: '.pdf,.jpg,.jpeg,.png' },
  { key: 'xray',       label: 'X-Ray Report',        accept: '.pdf,.jpg,.jpeg,.png' },
  { key: 'ecg',        label: 'ECG Report',           accept: '.pdf,.jpg,.jpeg,.png' },
  { key: 'other1',     label: 'Other Report 1',       accept: '*' },
  { key: 'other2',     label: 'Other Report 2',       accept: '*' },
];

const SYMPTOM_LIST = [
  'itching','skin rash','nodal skin eruptions','continuous sneezing','shivering','chills','joint pain',
  'stomach pain','acidity','ulcers on tongue','muscle wasting','vomiting','burning micturition',
  'fatigue','weight gain','anxiety','cold hands and feets','mood swings','weight loss','restlessness',
  'lethargy','patches in throat','irregular sugar level','cough','high fever','sunken eyes',
  'breathlessness','sweating','dehydration','indigestion','headache','yellowish skin','dark urine',
  'nausea','loss of appetite','pain behind the eyes','back pain','constipation','abdominal pain',
  'diarrhoea','mild fever','yellow urine','yellowing of eyes','acute liver failure','fluid overload',
  'swelling of stomach','swelled lymph nodes','malaise','blurred and distorted vision','phlegm',
  'throat irritation','redness of eyes','sinus pressure','runny nose','congestion','chest pain',
  'weakness in limbs','fast heart rate','pain during bowel movements','pain in anal region',
  'bloody stool','irritation in anus','neck pain','dizziness','cramps','bruising','obesity',
  'swollen legs','swollen blood vessels','puffy face and eyes','enlarged thyroid','brittle nails',
  'swollen extremeties','excessive hunger','extra marital contacts','drying and tingling lips',
  'slurred speech','knee pain','hip joint pain','muscle weakness','stiff neck','swelling joints',
  'movement stiffness','spinning movements','loss of balance','unsteadiness','weakness of one body side',
  'loss of smell','bladder discomfort','foul smell of urine','continuous feel of urine','passage of gases',
  'internal itching','toxic look (typhos)','depression','irritability','muscle pain',
  'altered sensorium','red spots over body','belly pain','abnormal menstruation','dischromic patches',
  'watering from eyes','increased appetite','polyuria','family history','mucoid sputum',
  'rusty sputum','lack of concentration','visual disturbances','receiving blood transfusion',
  'receiving unsterile injections','coma','stomach bleeding','distention of abdomen',
  'history of alcohol consumption','fluid overload','blood in sputum','prominent veins on calf',
  'palpitations','painful walking','pus filled pimples','blackheads','scurring',
  'skin peeling','silver like dusting','small dents in nails','inflammatory nails','blister',
  'red sore around nose','yellow crust ooze',
];

const CreateConsultationModal = ({ isOpen, onClose, onCreated }) => {
  const [step, setStep] = useState(0);
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [symptomSearch, setSymptomSearch] = useState('');
  const [files, setFiles] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [mlResult, setMlResult] = useState(null);
  const [consultationId, setConsultationId] = useState(null);
  const [stepError, setStepError] = useState('');

  useEffect(() => {
    if (isOpen) {
      getPatients().then(d => setPatients(d.patients || [])).catch(console.error);
    }
  }, [isOpen]);

  const reset = () => {
    setStep(0); setPatientId(''); setNotes(''); setSelectedSymptoms([]);
    setSymptomSearch(''); setFiles({}); setMlResult(null); setConsultationId(null); setStepError('');
  };

  const handleClose = () => { reset(); onClose(); };

  const toggleSymptom = (symptom) => {
    setSelectedSymptoms(prev =>
      prev.includes(symptom) ? prev.filter(s => s !== symptom) : [...prev, symptom]
    );
  };

  const filteredSymptoms = SYMPTOM_LIST.filter(s =>
    s.includes(symptomSearch.toLowerCase().replace(/\s/g, '_'))
    || s.replace(/_/g, ' ').includes(symptomSearch.toLowerCase())
  ).slice(0, 80);

  const handleFileChange = (key, file) => {
    setFiles(prev => ({ ...prev, [key]: file }));
  };

  const handleSave = async () => {
    setStepError('');
    if (!patientId) return setStepError('Please select a patient.');
    if (selectedSymptoms.length < 1) return setStepError('Please select at least one symptom.');

    setIsAnalyzing(true);
    try {
      // Submit consultation to backend without ML analysis
      const formData = new FormData();
      formData.append('patientId', patientId);
      formData.append('symptoms', JSON.stringify(selectedSymptoms));
      if (notes) formData.append('notes', notes);
      Object.values(files).forEach(file => {
        if (file) formData.append('attachments', file);
      });

      const consultRes = await submitConsultation(formData);
      toast.success('Consultation saved successfully!');
      handleClose();
      onCreated?.(consultRes.consultation);
    } catch (err) {
      toast.error(err.response?.data?.message || err.message || 'Failed to save consultation');
      setStepError(err.response?.data?.message || 'Failed to save consultation. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNext = () => {
    setStepError('');
    if (step === 0 && !patientId) return setStepError('Please select a patient first.');
    if (step === 1 && selectedSymptoms.length < 1) return setStepError('Please select at least one symptom.');
    if (step === 2) { handleSave(); return; }
    setStep(s => s + 1);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-primary-50 rounded-xl flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-gray-800">New Consultation</h2>
              <p className="text-xs text-gray-400">AI-assisted disease assessment</p>
            </div>
          </div>
          <button onClick={handleClose} className="w-8 h-8 flex items-center justify-center rounded-xl hover:bg-gray-100 text-gray-400 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Step progress */}
        {step < 3 && (
          <div className="px-6 py-4 flex items-center gap-2 flex-shrink-0">
            {STEP_LABELS.map((label, i) => (
              <div key={i} className="flex items-center gap-2 flex-1">
                <div className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center transition-colors ${
                  i < step ? 'bg-secondary-600 text-white' : i === step ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-400'
                }`}>{i + 1}</div>
                <span className={`text-xs font-medium ${i === step ? 'text-gray-800' : 'text-gray-400'}`}>{label}</span>
                {i < 2 && <div className={`flex-1 h-0.5 rounded ${i < step ? 'bg-secondary-400' : 'bg-gray-100'}`} />}
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 pb-4">

          {/* Step 0: Patient & Notes */}
          {step === 0 && (
            <div className="space-y-4 pt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  <User size={14} className="inline mr-1.5 text-gray-400" />Select Patient *
                </label>
                <select
                  value={patientId}
                  onChange={e => setPatientId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-colors"
                >
                  <option value="">-- Select a registered patient --</option>
                  {patients.map(p => (
                    <option key={p._id} value={p._id}>{p.name} ({p.age} yrs, {p.gender})</option>
                  ))}
                </select>
                {patients.length === 0 && (
                  <p className="text-xs text-amber-600 mt-1.5">No patients found. Register a patient from the Patients tab first.</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  <FileText size={14} className="inline mr-1.5 text-gray-400" />Additional Notes
                </label>
                <textarea
                  rows={4}
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Observations, patient history, context..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-colors resize-none"
                />
              </div>
            </div>
          )}

          {/* Step 1: Symptoms */}
          {step === 1 && (
            <div className="space-y-3 pt-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">Select all symptoms the patient is experiencing:</p>
                <span className="text-xs bg-primary-50 text-primary-700 px-2.5 py-1 rounded-full font-medium">
                  {selectedSymptoms.length} selected
                </span>
              </div>
              <input
                type="text"
                placeholder="Search symptoms..."
                value={symptomSearch}
                onChange={e => setSymptomSearch(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-colors"
              />
              {selectedSymptoms.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {selectedSymptoms.map(s => (
                    <span key={s} className="flex items-center gap-1 text-xs bg-primary-100 text-primary-800 px-2.5 py-1 rounded-full font-medium">
                      {s.replace(/_/g, ' ')}
                      <button onClick={() => toggleSymptom(s)} className="hover:text-red-500 ml-0.5">×</button>
                    </span>
                  ))}
                </div>
              )}
              <div className="max-h-52 overflow-y-auto flex flex-wrap gap-1.5 border border-gray-100 rounded-xl p-3 bg-gray-50">
                {filteredSymptoms.map(symptom => (
                  <button
                    key={symptom}
                    onClick={() => toggleSymptom(symptom)}
                    className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                      selectedSymptoms.includes(symptom)
                        ? 'bg-primary-600 text-white border-primary-600'
                        : 'bg-white text-gray-700 border-gray-200 hover:border-primary-300'
                    }`}
                  >
                    {symptom.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Attachments */}
          {step === 2 && (
            <div className="space-y-3 pt-4">
              <p className="text-sm text-gray-600">Upload patient health reports (optional, up to 5 files):</p>
              <div className="space-y-3">
                {FILE_TYPES.map(({ key, label, accept }) => (
                  <div key={key} className="flex items-center gap-4 p-4 rounded-xl border border-gray-200 bg-gray-50 hover:bg-white transition-colors">
                    <div className="w-9 h-9 bg-primary-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Paperclip className="w-4 h-4 text-primary-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-700">{label}</p>
                      {files[key] ? (
                        <p className="text-xs text-secondary-600 mt-0.5 truncate">{files[key].name}</p>
                      ) : (
                        <p className="text-xs text-gray-400 mt-0.5">No file chosen</p>
                      )}
                    </div>
                    <label className="cursor-pointer">
                      <span className="text-xs px-3 py-1.5 rounded-lg border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 transition-colors font-medium">
                        {files[key] ? 'Change' : 'Upload'}
                      </span>
                      <input
                        type="file"
                        accept={accept}
                        className="hidden"
                        onChange={e => handleFileChange(key, e.target.files[0] || null)}
                      />
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-400">Supported: PDF, JPG, PNG. The ML model uses symptoms, reports are stored for doctor review.</p>
            </div>
          )}

          {/* Step 3: Results - Removed. Results will be shown in consultation detail */}

          {/* Saving overlay */}
          {isAnalyzing && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center rounded-2xl gap-4 z-10">
              <div className="flex flex-col items-center gap-3">
                <div className="relative">
                  <FileText className="w-10 h-10 text-primary-300" />
                  <Loader2 className="w-6 h-6 text-primary-600 absolute -top-1 -right-1 animate-spin" />
                </div>
                <p className="text-base font-semibold text-gray-700">Saving Consultation...</p>
                <p className="text-sm text-gray-400">Please wait...</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {step < 3 && (
          <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between flex-shrink-0">
            <div className="flex-1">
              {stepError && <p className="text-sm text-red-500">{stepError}</p>}
            </div>
            <div className="flex gap-3">
              {step > 0 && (
                <button
                  onClick={() => { setStep(s => s - 1); setStepError(''); }}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  <ChevronLeft size={16} />
                  Back
                </button>
              )}
              <button
                onClick={handleNext}
                disabled={isAnalyzing}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition-colors disabled:opacity-60"
              >
                {step === 2 ? (
                  isAnalyzing ? (
                    <><Loader2 size={16} className="animate-spin" /> Saving...</>
                  ) : (
                    <><FileText size={16} /> Save Consultation</>
                  )
                ) : (
                  <>Next <ChevronRight size={16} /></>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateConsultationModal;
