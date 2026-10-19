import React from 'react';

export function ProviderBadge({ provider, size = 'md' }) {
  const p = (provider || '').toUpperCase();
  const isSm = size === 'sm';

  const baseClasses = `inline-flex items-center font-medium rounded-md border font-mono ${
    isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
  }`;

  if (p === 'KE' || p === 'KESC') {
    return (
      <span className={`${baseClasses} bg-emerald-50/80 text-emerald-900 border-emerald-200/90`}>
        <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-600" />
        K-Electric
      </span>
    );
  }

  if (p === 'LESCO') {
    return (
      <span className={`${baseClasses} bg-sky-50/80 text-sky-900 border-sky-200/90`}>
        <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-sky-600" />
        LESCO
      </span>
    );
  }

  if (p === 'IESCO') {
    return (
      <span className={`${baseClasses} bg-amber-50/80 text-amber-900 border-amber-200/90`}>
        <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-amber-600" />
        IESCO
      </span>
    );
  }

  return (
    <span className={`${baseClasses} bg-ink-100 text-ink-700 border-ink-200`}>
      {provider || 'Standard'}
    </span>
  );
}

export function StatusBadge({ status }) {
  const isReady = status === 'ready' || status === 'completed';
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border ${
        isReady
          ? 'bg-canvas text-ink-700 border-ink-200'
          : 'bg-amber-50 text-amber-800 border-amber-200'
      }`}
    >
      <span
        className={`w-1.5 h-1.5 mr-1.5 rounded-full ${
          isReady ? 'bg-emerald-600' : 'bg-amber-500 animate-pulse'
        }`}
      />
      {isReady ? 'Parsed' : 'Processing'}
    </span>
  );
}
