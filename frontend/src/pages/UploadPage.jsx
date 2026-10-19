import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadBillImage } from '../api/client';
import { Card } from '../components/ui/Card';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Zap,
  ArrowRight,
  Shield,
  FileCheck,
  Building2
} from 'lucide-react';

export function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);

  const steps = [
    'Transmitting high-resolution image to processing node',
    'Gemini 3.5 Flash-Lite multimodal document parsing',
    'Extracting readings, itemized charges & statutory taxes',
    'Pydantic schema validation & numeric reconciliation',
  ];

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Unsupported file type. Please upload a PNG, JPG, or JPEG statement image.');
      return;
    }

    if (selectedFile.size > 15 * 1024 * 1024) {
      setError('File size exceeds 15 MB limit.');
      return;
    }

    setError(null);
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || isProcessing) return;

    setIsProcessing(true);
    setError(null);
    setCurrentStep(0);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 2800);

    try {
      const response = await uploadBillImage(file);
      clearInterval(stepInterval);
      setCurrentStep(steps.length);

      if (response.duplicate) {
        // Show brief message if duplicate
        setError(null);
      }

      setTimeout(() => {
        navigate(`/bills/${response.bill_id}`);
      }, response.duplicate ? 400 : 700);
    } catch (err) {
      clearInterval(stepInterval);
      setIsProcessing(false);
      setError(
        err.message ||
          "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."
      );
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-ink-950">
          Upload Utility Statement
        </h2>
        <p className="text-xs text-ink-500 max-w-md mx-auto leading-relaxed">
          Upload any official scan or photograph from <strong>K-Electric</strong>, <strong>LESCO</strong>, or <strong>IESCO</strong>.
        </p>
      </div>

      <Card className="p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dropzone Container */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-6 sm:p-8 text-center transition-all ${
              isDragging
                ? 'border-emerald-600 bg-emerald-50/30'
                : preview
                ? 'border-ink-300 bg-canvas/30'
                : 'border-ink-200 hover:border-ink-400 bg-canvas/20'
            }`}
          >
            {preview ? (
              <div className="space-y-3">
                <div className="relative inline-block max-h-56 overflow-hidden rounded-lg border border-ink-200 bg-white p-2 shadow-subtle">
                  <img
                    src={preview}
                    alt="Statement Preview"
                    className="max-h-52 w-auto object-contain rounded"
                  />
                </div>
                <div className="text-xs font-mono text-ink-700 font-medium">
                  {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                </div>
                {!isProcessing && (
                  <button
                    type="button"
                    onClick={() => {
                      setFile(null);
                      setPreview(null);
                    }}
                    className="text-xs text-ink-500 hover:text-ink-950 underline cursor-pointer"
                  >
                    Select different document
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-3 py-4">
                <div className="w-12 h-12 mx-auto rounded-xl bg-canvas flex items-center justify-center text-ink-600 border border-ink-200 shadow-subtle">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-ink-900">
                    Drag and drop bill image, or{' '}
                    <label className="text-emerald-800 hover:text-emerald-900 underline cursor-pointer font-semibold">
                      browse
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/jpg"
                        onChange={(e) => handleFile(e.target.files[0])}
                        className="hidden"
                      />
                    </label>
                  </p>
                  <p className="text-[11px] text-ink-400 font-mono mt-1">
                    Accepts PNG, JPG, or JPEG up to 15 MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs space-y-2.5">
              <div className="flex items-start space-x-2.5">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <div className="flex-1 font-medium leading-relaxed">{error}</div>
              </div>
              <div className="pt-1 flex items-center space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    setPreview(null);
                    setError(null);
                  }}
                  className="px-3 py-1.5 rounded-md bg-white border border-rose-300 hover:bg-rose-100/60 text-rose-900 text-[11px] font-semibold transition"
                >
                  Try Another Image
                </button>
              </div>
            </div>
          )}

          {/* Processing Progress Tracker */}
          {isProcessing && (
            <div className="p-4 sm:p-5 rounded-xl bg-ink-950 text-white space-y-3.5 shadow-card">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
                  <span className="font-semibold uppercase tracking-wider text-ink-200 text-[11px]">
                    Decoding Statement...
                  </span>
                </div>
                <span className="font-mono text-emerald-400 text-xs">
                  Step {Math.min(currentStep + 1, steps.length)} of {steps.length}
                </span>
              </div>

              <div className="space-y-2">
                {steps.map((st, idx) => {
                  const isDone = currentStep > idx;
                  const isCurrent = currentStep === idx;
                  return (
                    <div
                      key={idx}
                      className={`flex items-center space-x-2.5 text-xs transition-colors ${
                        isCurrent
                          ? 'text-white font-medium'
                          : isDone
                          ? 'text-emerald-400'
                          : 'text-ink-500'
                      }`}
                    >
                      {isDone ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : isCurrent ? (
                        <Loader2 className="w-3.5 h-3.5 text-emerald-400 animate-spin shrink-0" />
                      ) : (
                        <div className="w-3.5 h-3.5 rounded-full border border-ink-700 shrink-0" />
                      )}
                      <span>{st}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center space-x-1.5 text-xs text-ink-500">
              <Shield className="w-3.5 h-3.5 text-emerald-700" />
              <span className="text-[11px]">PII scrubbed per Section 5.3 rules</span>
            </div>

            <button
              type="submit"
              disabled={!file || isProcessing}
              className={`inline-flex items-center px-5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition shadow-subtle ${
                !file || isProcessing
                  ? 'bg-ink-200 text-ink-400 cursor-not-allowed'
                  : 'bg-ink-950 hover:bg-ink-900 text-white cursor-pointer'
              }`}
            >
              <Zap className="w-3.5 h-3.5 mr-2 text-emerald-400" />
              <span>{isProcessing ? 'Processing...' : 'Extract & Verify'}</span>
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
