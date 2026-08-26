import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Loader2,
  Radio,
  CheckCircle2,
  Zap,
  ShieldCheck,
  Layers
} from 'lucide-react';
import { VoiceScenario, VoiceExecutiveResponse } from '../types';
import { fetchVoiceScenarios, queryVoiceAssistant } from '../services/api';
import { AudioVisualizerCanvas } from './AudioVisualizerCanvas';

const DEFAULT_RESPONSE: VoiceExecutiveResponse = {
  transcript_query: '¿Cuál es el ROI estimado y el periodo de amortización al automatizar la atención a clientes con agentes multimodales en Vertex AI?',
  executive_summary: 'La implementación de agentes multimodales autónomos en Vertex AI proyecta un ahorro neto acumulado de $3.4M USD en 24 meses, reduciendo los costos operativos del Contact Center en un 44% y acelerando el tiempo de resolución a menos de 45 segundos.',
  spoken_voice_script: 'Estimado comité directivo: la automatización con agentes multimodales en Vertex AI generará un retorno de inversión del 340 por ciento en 24 meses, recuperando el capital en sólo 7 meses y reduciendo los costos operativos un 44 por ciento.',
  kpis: [
    { label: 'Retorno ROI', value: '+340%', description: 'Proyección a 24 meses', trend: 'up' },
    { label: 'Ahorro OPEX', value: '-44%', description: 'Reducción en Contact Center', trend: 'up' },
    { label: 'Payback', value: '7.2 Meses', description: 'Periodo de amortización', trend: 'up' },
    { label: 'Precisión', value: '99.4%', description: 'Resolución autónoma E2E', trend: 'up' }
  ],
  pillars: [
    { title: 'Eficiencia Operativa Inmediata', detail: 'Resolución autónoma del 78% de consultas de primer nivel sin intervención humana.', timeline: 'Mes 1 - 3' },
    { title: 'Escalabilidad & Cero Caídas', detail: 'Soporte simultáneo de 50,000 interacciones multicanal con latencia sub-segundo en Google Cloud.', timeline: 'Mes 4 - 6' },
    { title: 'Gobernanza & Soberanía', detail: 'Cumplimiento normativo estricto bajo el protocolo Zero-Leak y cifrado E2E certificado.', timeline: 'Continuo' }
  ],
  governance_note: 'Aprobado bajo protocolo Zero-Leak: los datos corporativos permanecen 100% aislados en su proyecto de Google Cloud sin entrenamiento de modelos externos.'
};

export const VoiceAssistantModule: React.FC = () => {
  const [scenarios, setScenarios] = useState<VoiceScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('sc-1');
  const [inputText, setInputText] = useState<string>(DEFAULT_RESPONSE.transcript_query);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [autoSpeak, setAutoSpeak] = useState<boolean>(false);
  const [response, setResponse] = useState<VoiceExecutiveResponse>(DEFAULT_RESPONSE);
  const [liveTranscript, setLiveTranscript] = useState<string>('');

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    fetchVoiceScenarios().then((data) => {
      setScenarios(data);
      if (data.length > 0) {
        setSelectedScenario(data[0].id);
      }
    });

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'es-MX';
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        setIsRecording(true);
        setLiveTranscript('');
      };

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        setLiveTranscript(transcript);
        setInputText(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const handleToggleRecord = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          setIsRecording(true);
          setLiveTranscript('Escuchando voz en vivo...');
        }
      } else {
        setIsRecording(true);
        setLiveTranscript('Simulando captura directiva en vivo...');
        setTimeout(() => {
          setIsRecording(false);
        }, 3000);
      }
    }
  };

  const handleSpeak = (textToSpeak: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = 'es-MX';
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const handleStopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const handleSubmit = async (queryToRun?: string) => {
    const query = queryToRun || inputText;
    if (!query.trim()) return;

    setIsLoading(true);
    handleStopSpeaking();

    try {
      const result = await queryVoiceAssistant(query);
      setResponse(result);
      if (autoSpeak && result.spoken_voice_script) {
        handleSpeak(result.spoken_voice_script);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectScenario = (sc: VoiceScenario) => {
    setSelectedScenario(sc.id);
    setInputText(sc.query);
    handleSubmit(sc.query);
  };

  return (
    <div className="w-full max-w-[1720px] mx-auto px-6 py-4 space-y-4">
      
      {/* Sleek Scenario Chips Row */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 select-none">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 shrink-0 flex items-center gap-1.5 mr-2">
          <Zap className="w-4 h-4 text-blue-600" /> Escenarios C-Suite:
        </span>
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            onClick={() => handleSelectScenario(sc)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 flex items-center gap-2 cursor-pointer ${
              selectedScenario === sc.id
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <span>{sc.title}</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
              selectedScenario === sc.id ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600'
            }`}>
              {sc.badge}
            </span>
          </button>
        ))}
      </div>

      {/* Main Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left Column: Voice Deck (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          
          <div className="bg-white/95 backdrop-blur-md p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-4">
            
            <div className="flex items-center justify-between">
              <span className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Radio className={`w-4 h-4 ${isRecording ? 'text-rose-600 animate-pulse' : 'text-blue-600'}`} />
                Canal Acústico en Vivo
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                isRecording
                  ? 'bg-rose-100 text-rose-700 border border-rose-200 animate-pulse'
                  : isSpeaking
                  ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                  : 'bg-slate-100 text-slate-600'
              }`}>
                {isRecording ? 'Grabando Audio...' : isSpeaking ? 'Sintetizando Voz...' : 'Micrófono Listo'}
              </span>
            </div>

            {/* Soundwave Visualizer */}
            <div className="rounded-xl overflow-hidden bg-slate-50 border border-slate-200 p-2">
              <AudioVisualizerCanvas isActive={isRecording} isSpeaking={isSpeaking} colorScheme="blue" />
            </div>

            {/* Central Microphone Action */}
            <div className="flex items-center justify-center gap-4 py-2">
              <button
                onClick={handleToggleRecord}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-md ${
                  isRecording
                    ? 'bg-gradient-to-tr from-rose-600 to-red-500 text-white scale-105 ring-4 ring-rose-200 animate-pulse'
                    : 'bg-gradient-to-tr from-blue-700 via-indigo-600 to-blue-500 text-white hover:scale-105 ring-4 ring-blue-100'
                }`}
              >
                {isRecording ? <MicOff className="w-7 h-7" /> : <Mic className="w-7 h-7" />}
              </button>
              <div className="text-left">
                <p className="text-sm font-bold text-slate-900">
                  {isRecording ? 'Escuchando en Vivo...' : 'Hable o Ingrese Consulta'}
                </p>
                <p className="text-xs text-slate-500">
                  {isRecording ? 'Presione para procesar' : 'Haga clic para iniciar micrófono'}
                </p>
              </div>
            </div>

            {liveTranscript && (
              <div className="p-2.5 bg-blue-50/80 border border-blue-200 rounded-xl text-xs text-blue-950 italic text-center">
                "{liveTranscript}"
              </div>
            )}

            {/* Input Form */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <textarea
                rows={2}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ej: ¿Cuál es el ROI de automatizar con agentes multimodales?"
                className="w-full p-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs sm:text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all resize-none"
              />
              <div className="flex items-center justify-between gap-2">
                <button
                  onClick={() => setAutoSpeak(!autoSpeak)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    autoSpeak
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'bg-slate-100 text-slate-500 border border-slate-200'
                  }`}
                >
                  {autoSpeak ? <Volume2 className="w-3.5 h-3.5 text-blue-600" /> : <VolumeX className="w-3.5 h-3.5" />}
                  <span>{autoSpeak ? 'Auto-Voz Activa' : 'Auto-Voz Off'}</span>
                </button>

                <button
                  onClick={() => handleSubmit()}
                  disabled={isLoading || !inputText.trim()}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs sm:text-sm shadow-xs disabled:opacity-50 transition-all cursor-pointer"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Analizando...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Ejecutar Análisis</span>
                    </>
                  )}
                </button>
              </div>
            </div>

          </div>

        </div>

        {/* Right Column: Executive Deliverable (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          
          {isLoading ? (
            <div className="bg-white/90 backdrop-blur-md p-10 rounded-2xl border border-slate-200/90 flex flex-col items-center justify-center text-center space-y-3 min-h-[380px]">
              <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
              <h3 className="text-xl font-black text-slate-900">
                Razonando Modelo Cuantitativo con Gemini 3.7...
              </h3>
              <p className="text-slate-500 text-xs sm:text-sm max-w-md">
                Procesando hipótesis financiera, reducciones de OPEX y generando síntesis vocal ejecutiva.
              </p>
            </div>
          ) : (
            <div className="bg-white/95 backdrop-blur-md p-5 rounded-2xl border border-slate-200/90 shadow-xs space-y-4">
              
              {/* Deliverable Header */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider bg-blue-100 text-blue-800">
                    Dictamen Estratégico C-Suite
                  </span>
                  <span className="text-xs font-semibold text-slate-400">•</span>
                  <span className="text-xs font-semibold text-slate-600">Gemini 3.7 Flash Engine</span>
                </div>

                <div className="flex items-center gap-2">
                  {isSpeaking ? (
                    <button
                      onClick={handleStopSpeaking}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100"
                    >
                      <VolumeX className="w-3.5 h-3.5" /> Detener
                    </button>
                  ) : (
                    <button
                      onClick={() => handleSpeak(response.spoken_voice_script)}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100"
                    >
                      <Volume2 className="w-3.5 h-3.5" /> Escuchar Síntesis
                    </button>
                  )}
                </div>
              </div>

              {/* Executive Summary */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <p className="text-xs sm:text-sm font-semibold text-slate-800 leading-relaxed">
                  {response.executive_summary}
                </p>
              </div>

              {/* 4 Mini KPI Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {response.kpis.map((kpi, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-blue-50/60 border border-blue-200 text-center">
                    <span className="text-[10px] font-black uppercase tracking-wider text-blue-700 block truncate">
                      {kpi.label}
                    </span>
                    <span className="text-xl sm:text-2xl font-black text-blue-950">
                      {kpi.value}
                    </span>
                    <span className="text-[10px] text-slate-500 font-medium mt-0.5 block truncate">
                      {kpi.description}
                    </span>
                  </div>
                ))}
              </div>

              {/* Strategic Pillars */}
              <div className="space-y-2">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-blue-600" /> Pilares de Ejecución Estratégica
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  {response.pillars.map((pillar, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span className="truncate">{pillar.title}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 line-clamp-3 leading-relaxed">
                        {pillar.detail}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Governance & Compliance Footnote */}
              <div className="p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                <p className="text-[11px] text-emerald-800 font-medium leading-normal">
                  {response.governance_note}
                </p>
              </div>

            </div>
          )}

        </div>

      </div>

    </div>
  );
};

export default VoiceAssistantModule;
