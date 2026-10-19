import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Zap, 
  X,
  FileText,
  Shield,
  Activity,
  Cpu
} from 'lucide-react';

export function Sidebar({ isOpen, onClose }) {
  const navItems = [
    { name: 'Overview', to: '/', icon: LayoutDashboard },
    { name: 'Upload Statement', to: '/upload', icon: UploadCloud },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 bg-ink-950/40 backdrop-blur-xs z-40 lg:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 w-64 bg-white border-r border-ink-200/90 z-50 flex flex-col transition-transform duration-200 ease-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0 shadow-elevated' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-ink-200/80 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-ink-950 flex items-center justify-center text-white shadow-subtle">
              <Zap className="w-4 h-4 text-emerald-400 fill-emerald-400" />
            </div>
            <div>
              <span className="font-semibold text-sm tracking-tight text-ink-900 block leading-tight">
                BillDecoder
              </span>
              <span className="text-[10px] font-medium tracking-wide text-ink-500 uppercase">
                Utility Intelligence
              </span>
            </div>
          </div>

          {/* Close button on mobile */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-100 lg:hidden"
            aria-label="Close navigation"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Section */}
        <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
          <div>
            <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-ink-400 uppercase">
              Platform
            </div>
            <nav className="space-y-0.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    onClick={() => onClose && onClose()}
                    className={({ isActive }) =>
                      `flex items-center px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-ink-900 text-white font-semibold shadow-subtle'
                          : 'text-ink-600 hover:text-ink-950 hover:bg-ink-100/70'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 mr-2.5 shrink-0" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Coverage Grid */}
          <div className="pt-2">
            <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-ink-400 uppercase">
              Supported Utilities
            </div>
            <div className="space-y-1.5 px-3">
              <div className="flex items-center justify-between py-1.5 px-2 rounded-md bg-canvas text-xs border border-ink-200/60">
                <span className="font-medium text-ink-700">K-Electric (KE)</span>
                <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between py-1.5 px-2 rounded-md bg-canvas text-xs border border-ink-200/60">
                <span className="font-medium text-ink-700">LESCO Lahore</span>
                <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between py-1.5 px-2 rounded-md bg-canvas text-xs border border-ink-200/60">
                <span className="font-medium text-ink-700">IESCO Islamabad</span>
                <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                  Online
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Engine Footer */}
        <div className="p-3.5 border-t border-ink-200/80 bg-canvas/60">
          <div className="p-3 rounded-lg bg-white border border-ink-200 text-xs shadow-subtle">
            <div className="flex items-center space-x-2 text-ink-800 font-semibold mb-1">
              <Cpu className="w-3.5 h-3.5 text-emerald-700" />
              <span className="text-[11px]">BillDecoder Engine</span>
            </div>
            <p className="text-[11px] text-ink-500 leading-relaxed">
              Multimodal extraction verified with Pydantic schemas.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
