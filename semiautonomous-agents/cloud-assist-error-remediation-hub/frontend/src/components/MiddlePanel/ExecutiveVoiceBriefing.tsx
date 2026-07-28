import React, { useState, useRef } from 'react';
import { Volume2, VolumeX, RefreshCw, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';

interface ExecutiveVoiceBriefingProps {
  selectedError: GcpErrorItem;
  diagnostic?: CloudAssistDiagnostic | null;
  isLightMode?: boolean;
}

export const ExecutiveVoiceBriefing: React.FC<ExecutiveVoiceBriefingProps> = ({
  selectedError,
  diagnostic,
  isLightMode = false
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [latencyText, setLatencyText] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Build a comprehensive, natural executive incident briefing & resolution script
  const topHypothesis = diagnostic?.hypotheses && diagnostic.hypotheses.length > 0
    ? diagnostic.hypotheses[0]
    : null;

  const incidentSummary = selectedError.summary;
  const serviceName = selectedError.serviceName;
  const rootCause = topHypothesis?.rootCauseText || diagnostic?.recapText || selectedError.fullText;
  const remediation = topHypothesis?.recommendationText || "Expand container memory allocation to 1024 Megabytes and apply the code patch.";

  const briefingTranscript = `Good day. Here is your Gemini Cloud Assist Executive Incident Briefing for ${serviceName}. ` +
    `An incident occurred involving: ${incidentSummary}. ` +
    `Root Cause Analysis: ${rootCause}. ` +
    `Recommended Resolution: ${remediation} Click Execute on GCP in the Middle Panel to apply this fix with real-time Cloud Audit Log verification.`;

  const speakBriefing = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    setLatencyText(null);
    const t0 = performance.now();

    try {
      const res = await fetch('http://127.0.0.1:8088/api/synthesize-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: briefingTranscript, voice: 'Achernar' })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const elapsed = Math.round(performance.now() - t0);
      setLatencyText(`${elapsed}ms`);

      if (data.audioBase64) {
        const audioSrc = `data:${data.mimeType || 'audio/wav'};base64,${data.audioBase64}`;
        const audio = new Audio(audioSrc);
        audioRef.current = audio;
        audio.onended = () => setIsPlaying(false);
        audio.onerror = () => setIsPlaying(false);
        await audio.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error("Audio synthesis error:", err);
      setIsPlaying(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-1">
      <div className="flex items-center gap-2">
        <button
          onClick={speakBriefing}
          disabled={isLoading}
          className={`px-3.5 py-1.5 rounded-full border text-xs font-bold font-mono flex items-center gap-2 transition-all cursor-pointer shadow-sm ${
            isLightMode
              ? isPlaying
                ? 'bg-rose-100 border-rose-300 text-rose-800 animate-pulse'
                : 'bg-white hover:bg-slate-100 border-slate-300 text-slate-950 font-extrabold'
              : isPlaying
                ? 'bg-rose-950 border-rose-500 text-rose-300 animate-pulse'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-cyan-300'
          }`}
          title="Listen to Gemini 3.1 Flash Executive Incident & Remediation Briefing"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
              <span>Generating Gemini 3.1 Briefing...</span>
            </>
          ) : isPlaying ? (
            <>
              <VolumeX className="w-3.5 h-3.5 text-rose-600 animate-bounce" />
              <span>Stop Briefing</span>
              {latencyText && <span className="text-[10px] opacity-75 font-normal">({latencyText})</span>}
            </>
          ) : (
            <>
              <Volume2 className={`w-3.5 h-3.5 ${isLightMode ? 'text-slate-950' : 'text-cyan-400'}`} />
              <span>🔊 Executive Voice Briefing</span>
              {latencyText && <span className="text-[10px] text-emerald-600 font-bold">({latencyText})</span>}
            </>
          )}
        </button>

        <button
          onClick={() => setShowTranscript(!showTranscript)}
          className={`p-1.5 rounded-full border text-[11px] font-mono flex items-center gap-1 transition-all cursor-pointer ${
            isLightMode
              ? 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-700'
              : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
          }`}
          title="View Briefing Script Transcript"
        >
          <FileText className="w-3 h-3 text-cyan-500" />
          <span>Transcript</span>
          {showTranscript ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {showTranscript && (
        <div className={`mt-1.5 p-3 rounded-xl border text-xs leading-relaxed max-w-xl shadow-lg font-mono ${
          isLightMode
            ? 'bg-slate-50 border-slate-300 text-slate-900'
            : 'bg-slate-950 border-slate-800 text-slate-200'
        }`}>
          <div className="text-[10px] uppercase font-bold text-cyan-500 mb-1 flex items-center gap-1">
            <span>📜 Executive Incident Briefing Transcript</span>
          </div>
          <p>{briefingTranscript}</p>
        </div>
      )}
    </div>
  );
};
