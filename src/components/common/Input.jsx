import React, { forwardRef } from 'react';

export const Input = forwardRef(
  (
    {
      label,
      error,
      type = 'text',
      placeholder = '',
      icon: Icon,
      className = '',
      containerClassName = '',
      required = false,
      ...props
    },
    ref
  ) => {
    return (
      <div className={`w-full ${containerClassName}`}>
        {label && (
          <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
            {label} {required && <span className="text-red-500">*</span>}
          </label>
        )}
        <div className="relative rounded-md shadow-sm">
          {Icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <Icon className="h-4 w-4" />
            </div>
          )}
          <input
            ref={ref}
            type={type}
            placeholder={placeholder}
            className={`block w-full rounded-lg border text-sm transition-colors py-2.5 ${
              Icon ? 'pl-9' : 'pl-3.5'
            } pr-3.5 ${
              error
                ? 'border-red-300 text-red-900 focus:outline-none focus:ring-1 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500'
            } ${className}`}
            {...props}
          />
        </div>
        {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
