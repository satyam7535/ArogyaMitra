import { Plus } from 'lucide-react';
import { Button } from './Ui';

const EmptyState = ({ title, description, actionLabel, onAction }) => {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center p-8 bg-white rounded-lg border border-dashed border-gray-300">
      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
         <Plus size={32} className="text-primary-600" />
      </div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-500 mb-8 max-w-sm">{description}</p>
      <Button onClick={onAction} className="flex items-center gap-2">
        <Plus size={20} />
        {actionLabel}
      </Button>
    </div>
  );
};

export default EmptyState;
