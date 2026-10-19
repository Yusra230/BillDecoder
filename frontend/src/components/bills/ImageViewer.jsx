import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Eye, ZoomIn, ZoomOut, Maximize2, X, FileImage } from 'lucide-react';
import { getBillImageUrl } from '../../api/client';

export function ImageViewer({ billId, filename }) {
  const [zoom, setZoom] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const imgUrl = getBillImageUrl(billId);

  return (
    <>
      <Card className="p-5 space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-ink-200/80">
          <div className="flex items-center space-x-2">
            <FileImage className="w-4 h-4 text-ink-700" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
              Source Bill Scan
            </h3>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center px-2 py-1 rounded-md bg-canvas hover:bg-ink-100 border border-ink-200 text-ink-700 text-xs font-medium transition"
          >
            <Maximize2 className="w-3.5 h-3.5 mr-1 text-ink-500" />
            Inspect
          </button>
        </div>

        <div className="relative overflow-hidden rounded-lg bg-canvas border border-ink-200/90 max-h-[460px] flex items-center justify-center p-2 group cursor-pointer"
             onClick={() => setIsModalOpen(true)}>
          <img
            src={imgUrl}
            alt={filename || 'Utility Statement'}
            className="max-h-[440px] w-auto object-contain rounded transition-transform group-hover:scale-[1.01]"
          />
          <div className="absolute inset-0 bg-ink-950/0 group-hover:bg-ink-950/10 transition-colors flex items-center justify-center">
            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-ink-950/80 text-white text-[11px] font-medium px-3 py-1.5 rounded-md shadow-card">
              Click to Zoom Document
            </span>
          </div>
        </div>

        <p className="text-[11px] text-ink-400 text-center font-mono">
          Original scan inspected for PII exclusion & grounded facts
        </p>
      </Card>

      {/* Full screen modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-ink-950/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6">
          <div className="relative bg-white rounded-xl max-w-5xl w-full max-h-[92vh] flex flex-col overflow-hidden shadow-elevated border border-ink-200">
            <div className="h-14 px-5 border-b border-ink-200 flex items-center justify-between bg-canvas">
              <span className="text-xs font-semibold text-ink-800 font-mono">
                {filename || billId}
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}
                  className="p-1.5 rounded-md bg-white border border-ink-200 hover:bg-ink-50 text-ink-700"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="text-xs font-mono font-medium text-ink-600 w-12 text-center">
                  {Math.round(zoom * 100)}%
                </span>
                <button
                  onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}
                  className="p-1.5 rounded-md bg-white border border-ink-200 hover:bg-ink-50 text-ink-700"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setIsModalOpen(false);
                    setZoom(1);
                  }}
                  className="p-1.5 rounded-md bg-ink-200 hover:bg-ink-300 text-ink-800 ml-2"
                  title="Close Inspector"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-auto p-4 sm:p-8 bg-canvas/60 flex items-center justify-center">
              <img
                src={imgUrl}
                alt="Enlarged Bill Scan"
                style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
                className="max-w-full h-auto transition-transform rounded border border-ink-200 shadow-card"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
