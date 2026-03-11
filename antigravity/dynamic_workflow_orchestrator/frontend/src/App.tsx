import { useState, useRef, useEffect } from 'react';
import { Play, Loader2, FileText, ListChecks, CheckCircle, XCircle } from 'lucide-react';

type EventType = 'update' | 'final' | 'pause' | 'complete';

interface WorkflowEvent {
  author: string;
  type: EventType;
  text: string;
}

export default function App() {
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isWaitingForUser, setIsWaitingForUser] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [summary, setSummary] = useState('');
  const [bullets, setBullets] = useState('');
  const [completed, setCompleted] = useState(false);
  const [cancelled, setCancelled] = useState(false);
  
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [summary, bullets, completed, isWaitingForUser]);

  const runWorkflowStep = async (payload: any) => {
    try {
      const response = await fetch('http://localhost:8007/api/workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...payload, userId: 'user_1' })
      });

      if (!response.body) throw new Error('No readable stream');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as WorkflowEvent;
              
              if (data.type === 'complete') {
                setIsProcessing(false);
              } else if (data.type === 'pause') {
                setIsWaitingForUser(true);
                setIsProcessing(false);
              } else if (data.author === 'System' && data.text === 'Workflow already completed.') {
                setCompleted(true);
              } else if (data.author === 'System' && data.text === 'Workflow cancelled by user.') {
                setCancelled(true);
              } else if (data.author === 'System' && data.text.includes('sequence complete')) {
                 setCompleted(true);
                 setIsProcessing(false);
              } else if (data.author === 'SummaryAgent') {
                if (data.type === 'update' || data.type === 'final') {
                  setSummary(data.text);
                }
              } else if (data.author === 'BulletPointAgent') {
                if (data.type === 'update' || data.type === 'final') {
                  setBullets(data.text);
                }
              }
            } catch (e) {
              console.error('Error parsing SSE', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Workflow failed:', error);
      setIsProcessing(false);
    }
  };

  const startWorkflow = async () => {
    if (!inputText.trim()) return;
    
    setIsProcessing(true);
    setIsWaitingForUser(false);
    setSummary('');
    setBullets('');
    setCompleted(false);
    setCancelled(false);

    const newSessionId = `sess_${Date.now()}`;
    setSessionId(newSessionId);

    await runWorkflowStep({ action: 'start', text: inputText, sessionId: newSessionId });
  };

  const handleContinue = async () => {
    setIsWaitingForUser(false);
    setIsProcessing(true);
    await runWorkflowStep({ action: 'continue', sessionId });
  };

  const handleCancel = async () => {
    setIsWaitingForUser(false);
    setIsProcessing(false);
    setCancelled(true);
    await runWorkflowStep({ action: 'cancel', sessionId });
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            Dynamic Workflow Orchestrator
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-lg">
            Powered by Google Agent Development Kit (ADK). Demonstrating real-time event streaming across sequential agentic steps with human-in-the-loop.
          </p>
        </div>

        {/* Input Section */}
        <div className="glass-panel p-6 space-y-4">
          <label className="block text-sm font-medium text-slate-300">Source Text for Analysis</label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste a long document or text here to see the swarm extract its summary and corresponding insights in real-time..."
            className="w-full glass-input h-40 resize-none font-mono text-sm leading-relaxed"
            disabled={isProcessing || isWaitingForUser}
          />
          <div className="flex justify-end">
            <button
              onClick={startWorkflow}
              disabled={isProcessing || isWaitingForUser || !inputText.trim()}
              className="glass-button flex items-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Processing Workflow...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Execute Event Queue</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Stream */}
        <div className="space-y-6">
          {summary && (
            <div className={`event-card border-l-4 border-l-indigo-500 transition-all duration-500 ${isWaitingForUser ? 'ring-2 ring-indigo-500/50' : ''}`}>
              <div className="flex items-center space-x-3 mb-4 text-indigo-400 border-b border-slate-700/50 pb-3">
                <FileText className="w-5 h-5" />
                <h3 className="text-lg font-semibold tracking-wide">Summary Agent Output</h3>
                {isWaitingForUser && (
                  <span className="ml-auto text-xs font-medium bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-full animate-pulse">
                    Awaiting Review
                  </span>
                )}
              </div>
              <div className="prose prose-invert prose-indigo max-w-none text-slate-300 leading-relaxed">
                {summary}
              </div>
            </div>
          )}
          
          {/* Human-in-the-loop Interactive Prompt */}
          {isWaitingForUser && (
            <div className="glass-panel p-6 border border-amber-500/30 bg-amber-500/5 transition-all">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400">
                  <ListChecks className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-amber-400">Summary Complete!</h3>
                  <p className="text-slate-300 mt-2">
                    Review the summary above. Would you like the Insight Agent to extract key bullet points from this summary?
                  </p>
                </div>
                <div className="flex space-x-4 pt-4">
                  <button 
                    onClick={handleCancel}
                    className="px-6 py-2.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-all font-medium flex items-center space-x-2"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Cancel Workflow</span>
                  </button>
                  <button 
                    onClick={handleContinue}
                    className="px-6 py-2.5 rounded-lg bg-emerald-500 text-white hover:bg-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all font-medium flex items-center space-x-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Generate Bullet Points</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {cancelled && (
             <div className="text-center p-4 bg-slate-800 border border-slate-700 rounded-xl text-slate-400 font-medium tracking-wide transition-all">
               Workflow cancelled by user.
             </div>
          )}

          {bullets && (
            <div className="event-card border-l-4 border-l-cyan-500">
              <div className="flex items-center space-x-3 mb-4 text-cyan-400 border-b border-slate-700/50 pb-3">
                <ListChecks className="w-5 h-5" />
                <h3 className="text-lg font-semibold tracking-wide">Insight Agent Extradition</h3>
              </div>
              <div className="prose prose-invert prose-cyan max-w-none text-slate-300 leading-relaxed">
                {bullets.split('\n').map((bullet, i) => {
                  if (!bullet.trim()) return null;
                  return (
                    <div key={i} className="flex space-x-3 my-2">
                       <span className="text-cyan-500 mt-0.5">•</span>
                       <span>{bullet.replace(/^-\s*/, '').replace(/^\*\s*/, '')}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {completed && (
            <div className="text-center p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 font-medium tracking-wide transition-all">
              ✓ Workflow Sequence Complete
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}
