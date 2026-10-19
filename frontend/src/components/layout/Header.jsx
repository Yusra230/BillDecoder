import React from 'react';
import { Menu, Activity, ShieldCheck, Zap } from 'lucide-react';

export function Header({ title, subtitle, onToggleMobileMenu }) {
  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-md border-b border-ink-200/90 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
      {/* Left: Mobile hamburger & Titles */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleMobileMenu}
          className="p-2 -ml-2 rounded-lg text-ink-600 hover:text-ink-900 hover:bg-ink-100 lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-sm sm:text-base font-semibold text-ink-900 tracking-tight flex items-center space-x-2">
            <span>{title}</span>
          </h1>
          {subtitle && (
            <p className="text-[11px] text-ink-500 hidden sm:block truncate max-w-md">
              {subtitle}
            </p>
          )}
        </div>
      </div>

      {/* Right: Engine Badges */}
      <div className="flex items-center space-x-2.5">
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-canvas border border-ink-200 text-[11px] font-medium text-ink-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="hidden sm:inline">Engine</span>
          <span>Online</span>
        </div>

      </div>
    </header>
  );
}
