import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchBillDetail, askBillQuestions } from '../api/client';
import { Card } from '../components/ui/Card';
import { ProviderBadge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { 
  ArrowLeft, 
  Send, 
  Sparkles, 
  HelpCircle, 
  Check, 
  Copy, 
  Bot, 
  User, 
  ShieldCheck, 
  MessageSquare
} from 'lucide-react';

export function QAPage() {
  const { id } = useParams();
  const [billData, setBillData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState(null);
  const [customQuestion, setCustomQuestion] = useState('');
  const [thread, setThread] = useState([]);
  const [copiedIdx, setCopiedIdx] = useState(null);

  // 12 Competition standard questions
  const presetQuestions = [
    { id: 'Q1', text: 'How much of my bill is taxes?', category: 'Taxes & Surcharges' },
    { id: 'Q4', text: 'What is the late payment surcharge on this bill?', category: 'Taxes & Surcharges' },
    { id: 'Q8', text: 'What are the Fuel Price Adjustments (FPA/FCA) charges on this bill?', category: 'Taxes & Surcharges' },
    { id: 'Q2', text: 'How many months in my history went above 200 units?', category: 'Consumption & History' },
    { id: 'Q5', text: 'Did I consume more units this month than the same month last year?', category: 'Consumption & History' },
    { id: 'Q6', text: 'What was my highest unit consumption in the last 12 months and when?', category: 'Consumption & History' },
    { id: 'Q7', text: 'What is the difference between my summer units (Jun-Aug) and winter units (Dec-Feb)?', category: 'Consumption & History' },
    { id: 'Q9', text: 'What is the trend of units consumed over the last 3 months?', category: 'Consumption & History' },
    { id: 'Q3', text: 'Is this a net-metered connection or a standard one, and how can you tell?', category: 'Technical & Projections' },
    { id: 'Q10', text: 'What are my expected units for next month based on history?', category: 'Technical & Projections' },
    { id: 'Q11', text: 'If I spread my electricity costs evenly across the year, what would I pay monthly?', category: 'Technical & Projections' },
    { id: 'Q12', text: 'What would my bill roughly be if I use the same units as last month?', category: 'Technical & Projections' },
  ];

  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const res = await fetchBillDetail(id);
        setBillData(res);
        if (res.qa_history && res.qa_history.length > 0) {
          setThread(res.qa_history);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [id]);

  const handleAsk = async (questionText, qid = null) => {
    if (!questionText.trim() || asking) return;

    setAsking(true);
    setError(null);

    const questionPayload = qid ? [{ question_id: qid, question: questionText }] : questionText;

    try {
      const response = await askBillQuestions(id, questionPayload);
      if (response.entries) {
        setThread((prev) => [...prev, ...response.entries]);
      } else if (response.answers) {
        const ans = Object.values(response.answers)[0];
        setThread((prev) => [
          ...prev,
          {
            question_id: qid || 'custom',
            question: questionText,
            answer: ans,
            answered_at: new Date().toISOString(),
          },
        ]);
      }
      setCustomQuestion('');
    } catch (err) {
      setError(err.message || 'Failed to generate answer.');
    } finally {
      setAsking(false);
    }
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  if (loading) {
    return <LoadingSpinner text="Connecting to grounded bill assistant..." />;
  }

  const { level1, metadata } = billData || {};

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-6">
      {/* Header and Back Link */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-ink-200/80">
        <div className="flex items-center space-x-3">
          <Link
            to={`/bills/${id}`}
            className="p-2 rounded-lg bg-white border border-ink-200 hover:bg-canvas text-ink-700 transition shadow-subtle shrink-0"
            title="Return to Statement"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <ProviderBadge provider={level1?.provider} size="sm" />
              <span className="text-xs font-semibold text-ink-700">
                {level1?.bill_month || 'Statement'}
              </span>
              <span className="text-[11px] text-ink-400 font-mono">({id})</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-ink-950 tracking-tight mt-0.5">
              Customer Inquiry Assistant (Level 2)
            </h2>
          </div>
        </div>

        <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-50/80 border border-emerald-200/90 text-[11px] font-medium text-emerald-900 self-start sm:self-auto">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
          <span>Grounded in Statement Facts</span>
        </div>
      </div>

      {/* Preset Questions Accordion/Chips */}
      <Card className="p-4 space-y-3 bg-canvas/50 border-ink-200">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-500 flex items-center">
            <HelpCircle className="w-3.5 h-3.5 mr-1.5 text-ink-400" />
            Quick Competition Questions (Click to Ask):
          </span>
          <span className="text-[11px] text-ink-400 font-mono">12 Pre-configured</span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {presetQuestions.map((pq) => (
            <button
              key={pq.id}
              onClick={() => handleAsk(pq.text, pq.id)}
              disabled={asking}
              className="text-xs px-2.5 py-1.5 rounded-md bg-white border border-ink-200 hover:border-ink-400 hover:bg-canvas text-ink-700 font-medium transition text-left cursor-pointer disabled:opacity-50 shadow-subtle"
            >
              <strong className="text-ink-900 mr-1 font-mono text-[11px]">{pq.id}:</strong>
              <span>{pq.text}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Conversation Thread */}
      <div className="space-y-4 min-h-[300px]">
        {thread.length === 0 ? (
          <div className="bg-white rounded-xl border border-ink-200/90 p-8 sm:p-12 text-center text-ink-500 shadow-card">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-ink-400" />
            <h3 className="text-sm font-semibold text-ink-900">No questions asked yet</h3>
            <p className="text-xs text-ink-400 mt-1 max-w-sm mx-auto leading-relaxed">
              Select one of the quick questions above or submit any inquiry regarding charges, meter readings, or tariff rules.
            </p>
          </div>
        ) : (
          thread.map((entry, idx) => (
            <div key={idx} className="space-y-3">
              {/* Question Bubble */}
              <div className="flex items-start space-x-2.5 justify-end">
                <div className="max-w-xl bg-ink-950 text-white rounded-xl rounded-tr-xs p-3.5 shadow-subtle text-xs font-medium">
                  {entry.question_id && entry.question_id !== 'custom' && (
                    <span className="inline-block text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 mb-1">
                      {entry.question_id}
                    </span>
                  )}
                  <p className="leading-relaxed">{entry.question}</p>
                </div>
                <div className="w-7 h-7 rounded-lg bg-ink-200 flex items-center justify-center text-ink-700 shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Answer Bubble */}
              <div className="flex items-start space-x-2.5 justify-start">
                <div className="w-7 h-7 rounded-lg bg-emerald-700 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-subtle">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="max-w-2xl bg-white border border-ink-200/90 rounded-xl rounded-tl-xs p-4 shadow-card text-xs space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-ink-400 border-b border-ink-100 pb-2">
                    <span className="font-semibold text-emerald-800 flex items-center">
                      <Sparkles className="w-3 h-3 mr-1 text-emerald-600" />
                      Grounded Answer
                    </span>
                    <button
                      onClick={() => handleCopy(entry.answer, idx)}
                      className="hover:text-ink-800 flex items-center transition cursor-pointer text-ink-500"
                      title="Copy Answer"
                    >
                      {copiedIdx === idx ? (
                        <>
                          <Check className="w-3 h-3 mr-1 text-emerald-700" />
                          <span className="text-emerald-800">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3 mr-1" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-ink-900 leading-relaxed font-normal whitespace-pre-wrap">
                    {entry.answer}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator for ongoing question */}
        {asking && (
          <div className="flex items-start space-x-2.5 justify-start">
            <div className="w-7 h-7 rounded-lg bg-emerald-700 flex items-center justify-center text-white shrink-0 animate-pulse">
              <Bot className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="bg-white border border-ink-200 rounded-xl p-3.5 text-xs shadow-card">
              <div className="flex items-center space-x-2 text-ink-600">
                <div className="w-3 h-3 rounded-full border-2 border-emerald-700 border-t-transparent animate-spin" />
                <span>Consulting bill facts and calculating mathematical figures...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 text-xs">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Fixed/Sticky Bottom Question Form */}
      <div className="sticky bottom-4 z-20 pt-2">
        <div className="bg-white/95 backdrop-blur-md rounded-xl border border-ink-200/90 p-2 shadow-elevated">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAsk(customQuestion);
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={customQuestion}
              onChange={(e) => setCustomQuestion(e.target.value)}
              placeholder="Ask any question grounded in this bill (e.g., taxes, late fee, solar units, seasonal trends)..."
              disabled={asking}
              className="flex-1 bg-canvas border border-ink-200/80 rounded-lg px-3.5 py-2 text-xs text-ink-900 placeholder-ink-400 focus:outline-none focus:ring-1 focus:ring-ink-900 focus:border-ink-900 transition"
            />
            <button
              type="submit"
              disabled={!customQuestion.trim() || asking}
              className={`inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition shadow-subtle shrink-0 ${
                !customQuestion.trim() || asking
                  ? 'bg-ink-200 text-ink-400 cursor-not-allowed'
                  : 'bg-ink-950 hover:bg-ink-900 text-white cursor-pointer'
              }`}
            >
              <Send className="w-3.5 h-3.5 mr-1.5" />
              <span>Ask</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
