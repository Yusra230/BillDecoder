import React from 'react';
import { FileText, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';

export function EmptyState({
  title = 'No statements processed yet',
  description = 'Upload an electricity bill from K-Electric, LESCO, or IESCO to inspect itemized charges, calculate taxes, and ask questions.',
  actionLabel = 'Upload Statement',
  actionTo = '/upload',
  icon: Icon = FileText,
}) {
  return (
    <div className="bg-white rounded-xl border border-ink-200/90 p-8 sm:p-12 text-center max-w-md mx-auto my-6 shadow-card">
      <div className="w-12 h-12 mx-auto mb-3.5 rounded-xl bg-canvas flex items-center justify-center text-ink-500 border border-ink-200">
        <Icon className="w-5 h-5 text-ink-600" />
      </div>
      <h3 className="text-sm font-semibold text-ink-900 mb-1">{title}</h3>
      <p className="text-xs text-ink-500 mb-5 leading-relaxed">{description}</p>
      {actionTo && (
        <Link
          to={actionTo}
          className="inline-flex items-center px-4 py-2 rounded-lg bg-ink-900 hover:bg-ink-800 text-white text-xs font-semibold transition shadow-subtle"
        >
          <Upload className="w-3.5 h-3.5 mr-1.5" />
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
