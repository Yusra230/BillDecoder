import React from 'react';

export function LoadingSpinner({ text = 'Loading data...', size = 'md' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-2',
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div
        className={`${
          sizeClasses[size] || sizeClasses.md
        } rounded-full border-ink-200 border-t-ink-900 animate-spin mb-3`}
      />
      {text && <p className="text-xs font-medium text-ink-500">{text}</p>}
    </div>
  );
}
