import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const LanguageSelector = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (e) => {
    i18n.changeLanguage(e.target.value);
  };

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
      <Globe size={16} className="text-gray-500" />
      <select
        value={i18n.language}
        onChange={changeLanguage}
        className="bg-transparent text-sm font-medium text-gray-700 outline-none cursor-pointer"
      >
        <option value="en">English</option>
        <option value="hi">हिन्दी (Hindi)</option>
        <option value="mr">मराठी (Marathi)</option>
      </select>
    </div>
  );
};

export default LanguageSelector;
