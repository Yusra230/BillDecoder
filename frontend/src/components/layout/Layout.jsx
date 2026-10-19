import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function Layout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Close mobile sidebar on page navigation
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  const getPageInfo = () => {
    const path = location.pathname;
    if (path === '/') {
      return {
        title: 'Utility Dashboard',
        subtitle: 'Statement processing, consumption analytics, and dues overview',
      };
    }
    if (path === '/upload') {
      return {
        title: 'Upload Utility Statement',
        subtitle: 'Multimodal vision decoding for K-Electric, LESCO, and IESCO',
      };
    }
    if (path.startsWith('/bills/') && path.endsWith('/ask')) {
      return {
        title: 'Grounded Assistant',
        subtitle: 'Customer inquiry answering verified against billing data points',
      };
    }
    if (path.startsWith('/bills/')) {
      return {
        title: 'Statement Breakdown',
        subtitle: 'Line-item charges, tariff readings, taxes, and audit details',
      };
    }
    return {
      title: 'VoltDecoder',
      subtitle: 'AI Utility Intelligence',
    };
  };

  const { title, subtitle } = getPageInfo();

  return (
    <div className="min-h-screen bg-canvas text-ink-900 flex flex-col">
      {/* Sidebar (Desktop fixed, Mobile drawer) */}
      <Sidebar 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)} 
      />

      {/* Main Container */}
      <div className="lg:pl-64 flex flex-col flex-1 min-w-0 transition-all">
        <Header
          title={title}
          subtitle={subtitle}
          onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
