export const Button = ({ children, className = '', ...props }) => {
  return (
    <button
      className={`px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition duration-200 font-medium ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export const Input = ({ label, id, error, ...props }) => {
  return (
    <div className="flex flex-col gap-1 w-full">
      {label && <label htmlFor={id} className="text-sm font-medium text-gray-700">{label}</label>}
      <input
        id={id}
        className={`px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${error ? 'border-red-500' : 'border-gray-300'}`}
        {...props}
      />
      {error && <span className="text-sm text-red-500">{error}</span>}
    </div>
  );
};
