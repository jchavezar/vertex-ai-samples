import React, { useState, useRef } from 'react';
import { Volume2, VolumeX, RefreshCw, FileText, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';

interface ExecutiveVoiceBriefingProps {
  selectedError: GcpErrorItem;
  diagnostic?: CloudAssistDiagnostic | null;
  isLightMode?: boolean;
}

const AUDIO_CACHE: Record<string, { audioBase64: string; mimeType: string; latencyMs: number }> = {};

export const ExecutiveVoiceBriefing: React.FC<ExecutiveVoiceBriefingProps> = ({
  selectedError,
  diagnostic,
  isLightMode = false
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [copied, setCopied] = useState(false);
  const [latencyText, setLatencyText] = useState<string | null>(
    AUDIO_CACHE[selectedError.id] ? `${AUDIO_CACHE[selectedError.id].latencyMs}ms (Cached)` : null
  );
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const topHypothesis = diagnostic?.hypotheses && diagnostic.hypotheses.length > 0
    ? diagnostic.hypotheses[0]
    : null;

  const incidentSummary = selectedError.summary;
  const serviceName = selectedError.serviceName;
  const rootCause = topHypothesis?.rootCauseText || diagnostic?.recapText || selectedError.fullText;
  const remediation = topHypothesis?.recommendationText || "Expand container memory allocation to 1024 MiB.";

  const briefingTranscript = `Gemini Executive Briefing for ${serviceName}: ` +
    `Incident: ${incidentSummary}. ` +
    `Root Cause: ${rootCause.length > 180 ? rootCause.substring(0, 180) + '...' : rootCause}. ` +
    `Recommended Resolution: ${remediation} Click Execute on GCP in the Middle Panel to apply this fix with real-time audit verification.`;

  const copyTranscript = () => {
    navigator.clipboard.writeText(briefingTranscript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const speakBriefing = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    const cached = AUDIO_CACHE[selectedError.id];
    if (cached) {
      setLatencyText(`${cached.latencyMs}ms (0ms Cache)`);
      const audioSrc = `data:${cached.mimeType};base64,${cached.audioBase64}`;
      const audio = new Audio(audioSrc);
      audioRef.current = audio;
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => setIsPlaying(false);
      await audio.play();
      setIsPlaying(true);
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
        AUDIO_CACHE[selectedError.id] = {
          audioBase64: data.audioBase64,
          mimeType: data.mimeType || 'audio/wav',
          latencyMs: elapsed
        };

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
    <div className="w-full flex flex-col items-start gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={speakBriefing}
          disabled={isLoading}
          className={`px-3.5 py-1.5 rounded-full border text-xs font-bold font-mono flex items-center gap-2 transition-all cursor-pointer shadow-sm ${
            isLightMode
              ? isPlaying
                ? 'bg-rose-100 border-rose-300 text-rose-800 animate-pulse'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-white font-extrabold'
              : isPlaying
                ? 'bg-rose-950 border-rose-500 text-rose-300 animate-pulse'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-cyan-300'
          }`}
          title="Listen to Gemini 3.1 Flash Executive Incident & Remediation Briefing (Achernar Female Voice)"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-500" />
              <span>Synthesizing Gemini 3.1 Audio...</span>
            </>
          ) : isPlaying ? (
            <>
              <VolumeX className="w-3.5 h-3.5 text-rose-500 animate-bounce" />
              <span>Stop Briefing</span>
              {latencyText && <span className="text-[10px] opacity-75 font-normal">({latencyText})</span>}
            </>
          ) : (
            <>
              <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>🔊 Executive Voice Briefing</span>
              {latencyText && <span className="text-[10px] text-emerald-400 font-bold">({latencyText})</span>}
            </>
          )}
        </button>

        <button
          onClick={() => setShowTranscript(!showTranscript)}
          className={`px-3 py-1.5 rounded-full border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
            isLightMode
              ? 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-900 font-bold'
              : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
          }`}
          title="View Briefing Script Transcript"
        >
          <FileText className="w-3.5 h-3.5 text-cyan-500" />
          <span>Transcript</span>
          {showTranscript ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {showTranscript && (
        <div className={`w-full p-4 rounded-2xl border text-xs leading-relaxed shadow-md select-text cursor-text overflow-hidden break-words whitespace-pre-wrap ${
          isLightMode
            ? 'bg-slate-100 border-slate-300 text-slate-950 font-medium'
            : 'bg-slate-950 border-slate-800 text-slate-100 font-normal'
        }`}>
          <div className="flex items-center justify-between border-b pb-2 mb-2.5 border-slate-300/80 dark:border-slate-800">
            <div className="text-[11px] uppercase font-mono font-bold text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5">
              <span>📜 Executive Incident Briefing Transcript</span>
            </div>
            <button
              onClick={copyTranscript}
              className={`px-3 py-1 rounded-lg text-[10px] font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                copied
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : isLightMode
                    ? 'bg-white hover:bg-slate-200 border border-slate-300 text-slate-900 shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700 text-cyan-300'
              }`}
              title="Copy briefing transcript to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-white" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy Text</span>
                </>
              )}
            </button>
          </div>
          <p className={`select-text cursor-text leading-relaxed font-sans text-[13px] ${
            isLightMode ? 'text-slate-950 font-semibold' : 'text-slate-200'
          }`}>
            {briefingTranscript}
          </p>
        </div>
      )}
    </div>
  );
};
