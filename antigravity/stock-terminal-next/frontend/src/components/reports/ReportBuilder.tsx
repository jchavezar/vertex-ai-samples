import React, { useState } from 'react';
import { FileText, Play, CheckCircle2, Loader2, Printer } from 'lucide-react';

interface ReportBuilderProps {
  onClose?: () => void;
}

interface ReportData {
  type: string;
  ticker: string;
  profile?: any;
  financials?: any;
  segments?: any;
  geo_breakdown?: any;
  swot?: any;
  charts?: any;
  news?: any;
  eps_surprise?: string;
  revenue_surprise?: string;
  transcript_summary?: string;
  guidance?: string;
  themes?: any[];
}

const ReportBuilder: React.FC<ReportBuilderProps> = () => {
  const [ticker, setTicker] = useState('NVDA');
  const [reportType, setReportType] = useState<'primer' | 'earnings'>('primer');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startGeneration = async () => {
    setIsGenerating(true);
    setProgress(0);
    setReportData(null);
    setError(null);
    setCurrentStep("Initializing Agent...");

    try {
      // Connect to Backend Stream
      const response = await fetch(`http://localhost:8001/report/stream?ticker=${ticker}&type=${reportType}`);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // The last element is either an empty string (if ends in newline) or a partial line
        // We keep it in the buffer for the next chunk
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const msg = JSON.parse(line);
            if (msg.type === 'progress') {
              setProgress(msg.progress * 100);
              setCurrentStep(msg.step);
            } else if (msg.type === 'complete') {
              setReportData(msg.data);
              setIsGenerating(false);
              setProgress(100);
            } else if (msg.type === 'error') {
              setError(msg.message);
              setIsGenerating(false);
            }
          } catch (e) {
            console.error("JSON Parse Error", e);
          }
        }
      }
    } catch (e) {
      setError(String(e));
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bg-app)] text-[var(--text-primary)]">
      {/* Configuration Header */}
      {!reportData && !isGenerating && (
        <div className="p-8 flex flex-col items-center justify-center h-full space-y-8 animate-in fade-in zoom-in duration-500">
           <div className="text-center space-y-2">
             <div className="w-16 h-16 bg-[var(--brand)]/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-[var(--brand)]">
                <FileText size={32} />
             </div>
             <h2 className="text-2xl font-bold">Report Generator</h2>
             <p className="text-[var(--text-muted)] max-w-md">
               Autonomous agent workflow to generate comprehensive financial reports.
             </p>
           </div>
           
           <div className="w-full max-w-md space-y-4 bg-[var(--bg-card)] p-6 rounded-2xl border border-[var(--border)] shadow-xl">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-1.5 block">Ticker Symbol</label>
                <input 
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full bg-[var(--bg-app)] border border-[var(--border)] rounded-lg px-4 py-3 text-lg font-mono tracking-widest focus:ring-2 focus:ring-[var(--brand)] outline-none transition-all"
                  placeholder="e.g. NVDA"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                 <button 
                   onClick={() => setReportType('primer')}
                   className={`p-3 rounded-lg border text-sm font-medium transition-all ${reportType === 'primer' ? 'border-[var(--brand)] bg-[var(--brand)]/10 text-[var(--brand)]' : 'border-[var(--border)] hover:bg-[var(--bg-app)]'}`}
                 >
                   Company Primer
                 </button>
                 <button 
                   onClick={() => setReportType('earnings')}
                   className={`p-3 rounded-lg border text-sm font-medium transition-all ${reportType === 'earnings' ? 'border-[var(--brand)] bg-[var(--brand)]/10 text-[var(--brand)]' : 'border-[var(--border)] hover:bg-[var(--bg-app)]'}`}
                 >
                   Earnings Recap
                 </button>
              </div>
              
            {error && (
              <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2 border border-red-100 animate-in slide-in-from-top-2">
                <div className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
                {error}
              </div>
            )}

              <button 
                onClick={startGeneration}
                className="w-full py-4 bg-[var(--brand)] text-white rounded-xl font-bold text-lg hover:brightness-110 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
              >
                <Play size={20} fill="currentColor" /> Generate Report
              </button>
           </div>
        </div>
      )}

      {/* Progress View */}
      {isGenerating && (
        <div className="flex flex-col items-center justify-center h-full space-y-8 animate-in fade-in duration-500">
           {/* Circular Clock Progress */}
           <div className="relative w-64 h-64 flex items-center justify-center">
              <svg className="w-full h-full rotate-[-90deg]">
                <circle cx="128" cy="128" r="120" stroke="var(--border)" strokeWidth="8" fill="none" />
                <circle 
                  cx="128" cy="128" r="120" 
                  stroke="var(--brand)" 
                  strokeWidth="8" 
                  fill="none" 
                  strokeDasharray={753}
                  strokeDashoffset={753 - (753 * progress) / 100}
                  className="transition-[stroke-dashoffset] duration-500 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                 <span className="text-4xl font-bold font-mono">{Math.round(progress)}%</span>
                 <span className="text-sm text-[var(--text-muted)] mt-2 animate-pulse">{currentStep}</span>
              </div>
           </div>
           
           <div className="flex flex-col items-center gap-2 text-[var(--text-muted)] text-sm">
             <Loader2 className="animate-spin" size={20} />
             <span>Orchestrating Agents...</span>
           </div>
        </div>
      )}

      {/* Report Preview */}
      {reportData && !isGenerating && (
         <div className="flex-1 overflow-hidden flex flex-col animate-in slide-in-from-bottom-5 duration-700">
            {/* Toolbar */}
            <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-card)] flex justify-between items-center shrink-0">
               <div className="flex items-center gap-3">
                 <div className="p-2 bg-green-500/10 text-green-500 rounded-lg">
                   <CheckCircle2 size={20} />
                 </div>
                 <div>
                   <h3 className="font-bold">{reportData.ticker} {reportData.type}</h3>
                   <p className="text-xs text-[var(--text-muted)]">Generated Successfully</p>
                 </div>
               </div>
               <div className="flex gap-2">
                 <button 
                   onClick={() => window.print()}
                   className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-app)] border border-[var(--border)] rounded-lg hover:bg-[var(--border)] transition-colors text-sm font-medium"
                 >
                   <Printer size={16} /> Print
                 </button>
                 <button 
                   onClick={() => setReportData(null)}
                   className="flex items-center gap-2 px-4 py-2 bg-[var(--brand)] text-white rounded-lg hover:brightness-110 transition-colors text-sm font-medium shadow-lg shadow-blue-500/20"
                 >
                   New Report
                 </button>
               </div>
            </div>
            
            {/* Template Container */}
            <div className="flex-1 overflow-y-auto p-8 bg-[#1a1b1e] print:p-0 print:overflow-visible">
               <div className="bg-white text-black max-w-[210mm] mx-auto min-h-[297mm] shadow-2xl print:shadow-none print:w-full print:max-w-none rounded-sm overflow-hidden">
                 {reportData.type === 'Company Primer' ? (
                   <PrimerTemplate data={reportData} />
                 ) : (
                   <EarningsTemplate data={reportData} />
                 )}
               </div>
            </div>
         </div>
      )}
    </div>
  );
};

// --- Sub-Templates (Inline for atomicity, can move later) ---

const PrimerTemplate: React.FC<{ data: ReportData }> = ({ data }) => {
  return (
    <div className="p-8 flex flex-col h-full gap-6 font-sans text-xs">
      {/* Header */}
      <div className="border-b-2 border-black pb-4 mb-2">
        <div className="flex justify-between items-end">
          <h1 className="text-3xl font-bold tracking-tight uppercase">Company Primer</h1>
          <div className="text-right">
             <h2 className="text-2xl font-black text-blue-800">{data.ticker}</h2>
             <p className="text-gray-500">{new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>

      {/* Row 1: Overview & Board */}
      <div className="grid grid-cols-3 gap-6">
         <div className="col-span-2 border border-gray-300 p-4 rounded-sm">
            <h3 className="font-bold border-b border-gray-200 pb-2 mb-2">Company Overview</h3>
            <p className="leading-relaxed text-gray-700">{data.profile?.description || "No description available."}</p>
            <div className="mt-4 grid grid-cols-2 gap-4 text-gray-600">
               <div><span className="font-semibold">Sector:</span> {data.profile?.sector}</div>
               <div><span className="font-semibold">Industry:</span> {data.profile?.industry}</div>
               <div><span className="font-semibold">Market Cap:</span> {data.profile?.market_cap}</div>
               <div><span className="font-semibold">P/E Ratio:</span> {data.profile?.pe_ratio}</div>
            </div>
         </div>
         <div className="col-span-1 border border-gray-300 p-4 rounded-sm flex flex-col justify-center items-center bg-gray-50 text-center">
            <h3 className="font-bold text-gray-900 mb-2">Consensus Target</h3>
            <div className="text-4xl font-black text-green-600">$145.00</div>
            <div className="text-gray-500 mt-1">Buy Rating (Strong)</div>
         </div>
      </div>

      {/* Row 2: Financials & Charts */}
      <div className="grid grid-cols-2 gap-6">
         {/* Table */}
         <div className="border border-gray-300 rounded-sm overflow-hidden">
             <div className="bg-gray-100 p-2 font-bold border-b border-gray-300">Latest Financials (8 Quarters)</div>
             <table className="w-full text-right">
                <thead className="bg-gray-50 text-gray-500">
                   <tr>
                     <th className="p-2 text-left">Period</th>
                     <th className="p-2">Rev ($B)</th>
                     <th className="p-2">EPS ($)</th>
                   </tr>
                </thead>
                <tbody>
                   {(data.financials?.quarters || []).map((q: string, i: number) => (
                      <tr key={i} className="border-t border-gray-100">
                        <td className="p-2 text-left font-medium">{q}</td>
                        <td className="p-2">{data.financials?.revenue[i]}</td>
                        <td className="p-2">{data.financials?.eps[i]}</td>
                      </tr>
                   ))}
                </tbody>
             </table>
         </div>

         {/* Segments Pie Charts (Mock Visuals for "Nice Colorful") */}
         <div className="border border-gray-300 rounded-sm p-4 flex flex-col gap-4">
             <h3 className="font-bold mb-2">Revenue Breakdown</h3>
             <div className="flex gap-4 h-32">
                {/* Visual Bars Mock */}
                <div className="flex-1 flex items-end gap-1 justify-between border-b border-gray-300 pb-1">
                   {[40, 60, 45, 80, 70, 90, 85, 100].map((h, i) => (
                      <div key={i} className="w-full bg-blue-600 hover:bg-blue-500 transition-colors rounded-t-sm" style={{ height: `${h}%` }}></div>
                   ))}
                </div>
                <div className="flex flex-col justify-center gap-1 text-[10px] w-1/3">
                   {data.segments?.map((s: any, i: number) => (
                      <div key={i} className="flex justify-between">
                         <span className="truncate">{s.name}</span>
                         <span className="font-bold text-blue-800">{s.value}%</span>
                      </div>
                   ))}
                </div>
             </div>
         </div>
      </div>

      {/* Row 3: SWOT */}
      <div className="border border-gray-300 rounded-sm p-0 overflow-hidden">
         <div className="bg-gray-800 text-white p-2 font-bold text-center uppercase tracking-widest">SWOT Analysis</div>
         <div className="grid grid-cols-2 grid-rows-2">
            <div className="p-4 border-r border-b border-gray-300 bg-green-50/50">
               <h4 className="font-bold text-green-800 mb-2 uppercase text-[10px]">Strengths</h4>
               <ul className="list-disc pl-4 space-y-1 text-gray-700">
                  {data.swot?.Strengths.map((item: string, i: number) => <li key={i}>{item}</li>)}
               </ul>
            </div>
            <div className="p-4 border-b border-gray-300 bg-red-50/50">
               <h4 className="font-bold text-red-800 mb-2 uppercase text-[10px]">Weaknesses</h4>
               <ul className="list-disc pl-4 space-y-1 text-gray-700">
                  {data.swot?.Weaknesses.map((item: string, i: number) => <li key={i}>{item}</li>)}
               </ul>
            </div>
            <div className="p-4 border-r border-gray-300 bg-blue-50/50">
               <h4 className="font-bold text-blue-800 mb-2 uppercase text-[10px]">Opportunities</h4>
               <ul className="list-disc pl-4 space-y-1 text-gray-700">
                  {data.swot?.Opportunities.map((item: string, i: number) => <li key={i}>{item}</li>)}
               </ul>
            </div>
            <div className="p-4 bg-orange-50/50">
               <h4 className="font-bold text-orange-800 mb-2 uppercase text-[10px]">Threats</h4>
               <ul className="list-disc pl-4 space-y-1 text-gray-700">
                  {data.swot?.Threats.map((item: string, i: number) => <li key={i}>{item}</li>)}
               </ul>
            </div>
         </div>
      </div>

    </div>
  );
};

const EarningsTemplate: React.FC<{ data: ReportData }> = ({ data }) => {
    return (
        <div className="p-8 flex flex-col h-full gap-6 font-sans text-xs">
          <div className="bg-blue-900 text-white p-6 rounded-lg text-center">
             <h1 className="text-3xl font-bold mb-2">Post Earnings Recap</h1>
             <div className="text-xl opacity-80">{data.ticker} | Q4 2025</div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
               <div className="p-6 bg-green-50 border border-green-200 rounded-lg text-center">
                   <div className="text-gray-500 uppercase tracking-wider font-bold text-[10px]">EPS Surprise</div>
                   <div className="text-4xl font-black text-green-700 mt-2">{data.eps_surprise}</div>
               </div>
               <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg text-center">
                   <div className="text-gray-500 uppercase tracking-wider font-bold text-[10px]">Revenue Surprise</div>
                   <div className="text-4xl font-black text-blue-700 mt-2">{data.revenue_surprise}</div>
               </div>
          </div>

          <div className="border-t-2 border-dashed border-gray-200 my-2"></div>

          <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-800 border-l-4 border-blue-600 pl-3">Transcript Summary</h3>
              <p className="leading-7 text-gray-700 text-sm">{data.transcript_summary || "No summary available."}</p>
          </div>
          
           <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-800 border-l-4 border-purple-600 pl-3">Key Themes & Sentiment</h3>
              <div className="grid grid-cols-2 gap-4">
                  {data.themes?.map((t: any, i: number) => (
                      <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                          <div className="font-bold text-gray-900">{t.topic}</div>
                          <div className={`mt-1 text-xs font-semibold px-2 py-0.5 rounded-full inline-block ${t.sentiment.includes("Bullish") ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                            {t.sentiment}
                          </div>
                      </div>
                  ))}
              </div>
          </div>
        </div>
    )
}

export default ReportBuilder;
