import React from 'react';

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  loading = false,
  className = '',
  ...props 
}) => {
  const baseStyle = 'font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-[#6C63FF] text-white hover:bg-[#5845D4] hover:shadow-lg hover:shadow-[#6C63FF]/30',
    secondary: 'bg-[#FF6584] text-white hover:bg-[#E84B6B] hover:shadow-lg hover:shadow-[#FF6584]/30',
    tertiary: 'bg-[#43E8D8] text-slate-900 hover:bg-[#2FD4C4] hover:shadow-lg hover:shadow-[#43E8D8]/30',
    outline: 'border-2 border-[#6C63FF] text-[#6C63FF] hover:bg-[#6C63FF] hover:text-white',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-2.5 text-base',
    lg: 'px-8 py-3.5 text-lg',
  };

  const disabledStyle = disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <button
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${disabledStyle} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="animate-spin">⚙️</span>}
      {children}
    </button>
  );
};

export const Card = ({ children, className = '' }) => (
  <div className={`bg-white border border-slate-200 rounded-2xl p-6 shadow-md hover:shadow-lg transition-all duration-300 ${className}`}>
    {children}
  </div>
);

export const Input = ({ label, error, className = '', ...props }) => (
  <div className="w-full">
    {label && <label className="block text-sm font-semibold text-slate-700 mb-2">{label}</label>}
    <input
      className={`w-full px-4 py-2.5 bg-white border border-slate-300 text-slate-900 rounded-lg focus:outline-none focus:border-[#6C63FF] focus:ring-2 focus:ring-[#6C63FF]/20 transition-all ${error ? 'border-[#FF6584]' : ''} ${className}`}
      {...props}
    />
    {error && <p className="text-[#FF6584] text-sm mt-1">{error}</p>}
  </div>
);

export const FileInput = ({ label, accept, onChange, error, className = '' }) => (
  <div className="w-full">
    {label && <label className="block text-sm font-semibold text-slate-700 mb-2">{label}</label>}
    <input
      type="file"
      accept={accept}
      onChange={onChange}
      className={`w-full px-4 py-2.5 bg-white border-2 border-dashed border-slate-300 text-slate-700 rounded-lg cursor-pointer hover:border-[#6C63FF] transition-all ${error ? 'border-[#FF6584]' : ''} ${className}`}
    />
    {error && <p className="text-[#FF6584] text-sm mt-1">{error}</p>}
  </div>
);

export const Badge = ({ children, variant = 'primary', className = '' }) => {
  const variants = {
    primary: 'bg-[#6C63FF]/20 text-[#6C63FF]',
    success: 'bg-[#43E8D8]/20 text-[#43E8D8]',
    error: 'bg-[#FF6584]/20 text-[#FF6584]',
    warning: 'bg-yellow-500/20 text-yellow-400',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const Spinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };
  return (
    <div className={`${sizes[size]} border-4 border-[#6C63FF]/20 border-t-[#6C63FF] rounded-full animate-spin`} />
  );
};

export const Alert = ({ type = 'info', message, onClose }) => {
  const typeStyles = {
    success: 'bg-emerald-50 border-emerald-400 text-emerald-700',
    error: 'bg-rose-50 border-rose-400 text-rose-700',
    warning: 'bg-amber-50 border-amber-400 text-amber-700',
    info: 'bg-indigo-50 border-indigo-400 text-indigo-700',
  };
  return (
    <div className={`border-l-4 ${typeStyles[type]} p-4 rounded-lg flex justify-between items-center mb-4`}>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="text-xl hover:opacity-70">
          ✕
        </button>
      )}
    </div>
  );
};
