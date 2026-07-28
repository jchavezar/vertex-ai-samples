import React, { useState, useRef } from 'react';
import { Volume2, VolumeX, RefreshCw, FileText, ChevronDown, ChevronUp, Copy, Check, Zap } from 'lucide-react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';

interface ExecutiveVoiceBriefingProps {
  selectedError: GcpErrorItem;
  diagnostic?: CloudAssistDiagnostic | null;
  isLightMode?: boolean;
}

// In-memory audio cache per error ID for 0ms instant replay latency
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

  // Concise Executive Briefing Script (Optimized for fast 1.5s - 2.5s Gemini 3.1 Flash TTS generation)
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

    // 0ms Instant Replay if cached
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
        // Cache audio buffer for instant replay
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
    <div className="w-full max-w-full flex flex-col items-start gap-2 overflow-hidden">
      <div className="flex flex-wrap items-center gap-2">
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
          title="Listen to Gemini 3.1 Flash Executive Incident & Remediation Briefing (Achernar Female Voice)"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
              <span>Synthesizing Gemini 3.1 Audio...</span>
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
          className={`px-3 py-1.5 rounded-full border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
            isLightMode
              ? 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-800 font-semibold'
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
        <div className={`w-full max-w-full p-3.5 rounded-xl border text-xs leading-relaxed shadow-lg font-mono select-text cursor-text overflow-hidden break-words whitespace-pre-wrap ${
          isLightMode
            ? 'bg-slate-50 border-slate-300 text-slate-900'
            : 'bg-slate-950 border-slate-800 text-slate-200'
        }`}>
          <div className="flex items-center justify-between border-b pb-2 mb-2 border-slate-200 dark:border-slate-800">
            <div className="text-[10px] uppercase font-bold text-cyan-600 flex items-center gap-1.5">
              <span>📜 Executive Incident Briefing Transcript</span>
            </div>
            <button
              onClick={copyTranscript}
              className={`px-2.5 py-1 rounded text-[10px] font-mono flex items-center gap-1 transition-all cursor-pointer ${
                copied
                  ? 'bg-emerald-600 text-white'
                  : isLightMode
                    ? 'bg-slate-200 hover:bg-slate-300 text-slate-800'
                    : 'bg-slate-800 hover:bg-slate-700 text-cyan-300'
              }`}
              title="Copy briefing transcript to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" />
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
          <p className="select-text cursor-text text-slate-800 dark:text-slate-200 leading-relaxed font-sans text-[12px] font-normal">
            {briefingTranscript}
          </p>
        </div>
      )}
    </div>
  );
};
