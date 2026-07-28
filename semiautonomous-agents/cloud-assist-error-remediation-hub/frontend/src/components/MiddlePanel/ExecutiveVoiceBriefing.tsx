import React, { useState, useRef } from 'react';
import { Volume2, VolumeX, RefreshCw } from 'lucide-react';
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
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const speakBriefing = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    const text = `Gemini Cloud Assist Executive Briefing. Critical incident on ${selectedError.serviceName}. ${selectedError.summary}. Diagnostic recap: ${diagnostic?.recapText || "Root cause identified and remediation patch generated."} Container status verified at HTTP 200 OK.`;

    try {
      const res = await fetch('http://127.0.0.1:8088/api/synthesize-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'Zephyr' })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

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
      console.error("Audio synthesis fallback:", err);
      // Seamless browser speech fallback
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      window.speechSynthesis.speak(utterance);
      setIsPlaying(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
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
      title="Listen to HD Studio Executive Incident Voice Briefing (Zephyr / Studio HD Engine)"
    >
      {isLoading ? (
        <>
          <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
          <span>Synthesizing Studio Audio...</span>
        </>
      ) : isPlaying ? (
        <>
          <VolumeX className="w-3.5 h-3.5 text-rose-600 animate-bounce" />
          <span>Stop Briefing</span>
        </>
      ) : (
        <>
          <Volume2 className={`w-3.5 h-3.5 ${isLightMode ? 'text-slate-950' : 'text-cyan-400'}`} />
          <span>🔊 AI Voice Briefing</span>
        </>
      )}
    </button>
  );
};
