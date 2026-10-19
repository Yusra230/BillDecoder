import React from 'react';

export function Card({ children, className = '', hover = false, ...props }) {
  return (
    <div
      className={`bg-white rounded-xl border border-ink-200/85 p-5 shadow-card ${
        hover ? 'transition-all duration-150 hover:shadow-card-hover hover:border-ink-300/90' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function StatCard({ title, value, subtitle, icon: Icon, badge }) {
  return (
    <Card hover className="relative flex flex-col justify-between overflow-hidden">
      <div className="flex items-start justify-between">
        <span className="text-[11px] font-semibold tracking-wider text-ink-500 uppercase">
          {title}
        </span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-canvas border border-ink-200/70 flex items-center justify-center text-ink-600">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-ink-950 tabular-numbers">
          {value}
        </div>
        {subtitle && (
          <p className="text-[11px] text-ink-500 mt-1 flex items-center">
            {subtitle}
          </p>
        )}
      </div>
    </Card>
  );
}
