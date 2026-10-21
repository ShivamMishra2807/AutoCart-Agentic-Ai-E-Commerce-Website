import React from 'react';
import Button from './Button';

export const EmptyState = ({
  icon: Icon,
  title,
  description,
  actionText,
  onAction,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center bg-white rounded-xl border border-gray-100 shadow-sm ${className}`}>
      {Icon && (
        <div className="p-4 bg-indigo-50 text-indigo-600 rounded-full mb-4">
          <Icon className="w-8 h-8" />
        </div>
      )}
      <h3 className="text-lg font-bold text-gray-900 mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-500 max-w-md mb-6">{description}</p>}
      {actionText && onAction && (
        <Button onClick={onAction} variant="primary">
          {actionText}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
