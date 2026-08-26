import React, { useState, useEffect } from 'react';
import {
  Film,
  Sparkles,
  Play,
  Copy,
  Check,
  TrendingUp,
  Share2,
  Layers,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { CreativeTemplate, ExecutiveCampaign } from '../types';
import { fetchCreativeTemplates, generateCampaign } from '../services/api';
import { ReelPlayerModal } from './ReelPlayerModal';

export const CreativeStudioModule: React.FC = () => {
  const [templates, setTemplates] = useState<CreativeTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [promptTopic, setPromptTopic] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [campaign, setCampaign] = useState<ExecutiveCampaign | null>(null);
  const [isReelPlayerOpen, setIsReelPlayerOpen] = useState<boolean>(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [activeChannelTab, setActiveChannelTab] = useState<number>(0);

  useEffect(() => {
    fetchCreativeTemplates().then(async (data) => {
      setTemplates(data);
      if (data.length > 0) {
        setSelectedTemplate(data[0].id);
        setPromptTopic(data[0].topic);
        try {
          setIsLoading(true);
          const initialCampaign = await generateCampaign(data[0].topic);
          setCampaign(initialCampaign);
        } catch (e) {
          console.error("Initial campaign fetch error:", e);
        } finally {
          setIsLoading(false);
        }
      }
    });
  }, []);

  const handleGenerate = async (topicToRun?: string) => {
    const topic = topicToRun || promptTopic;
    if (!topic.trim()) return;

    setIsLoading(true);
    try {
      const result = await generateCampaign(topic);
      setCampaign(result);
    } catch (error) {
      console.error('Error generating campaign:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectTemplate = (tmpl: CreativeTemplate) => {
    setSelectedTemplate(tmpl.id);
    setPromptTopic(tmpl.topic);
    handleGenerate(tmpl.topic);
  };

  const handleCopyText = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="w-full max-w-[1720px] mx-auto px-6 py-6 space-y-8">
      
      {/* Title Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-fuchsia-100 flex flex-col xl:flex-row xl:items-center justify-between gap-6 bg-gradient-to-r from-fuchsia-50/60 via-white to-pink-50/60">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-fuchsia-600 text-white shadow-sm">
              Módulo B • Creatividad Generativa
            </span>
            <span className="text-sm font-semibold text-fuchsia-900">
              Generador de Campañas & Reels Multimedia
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Estudio Creativo & Storyboards Cinemáticos
          </h2>
          <p className="text-slate-600 text-lg font-medium max-w-3xl">
            Generación instantánea de campañas de nivel C-Suite: conceptos rectores, storyboards de 4 paneles con locución en off, copy multicanal y modelado de retorno financiero.
          </p>
        </div>

        {campaign && (
          <button
            onClick={() => setIsReelPlayerOpen(true)}
            className="flex items-center gap-2.5 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-fuchsia-600 to-pink-600 hover:from-fuchsia-700 hover:to-pink-700 text-white font-black text-base shadow-lg transition-all scale-100 hover:scale-105 shrink-0"
          >
            <Play className="w-5 h-5 fill-current" />
            <span>Reproducir Reel Cinemático</span>
          </button>
        )}
      </div>

      {/* Input Section & Templates */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 5 Cols: Topic Generator & Pre-set Templates */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-5">
            <h3 className="text-lg font-black text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-fuchsia-600" />
              Iniciativa de Campaña o Producto
            </h3>

            <textarea
              rows={4}
              value={promptTopic}
              onChange={(e) => setPromptTopic(e.target.value)}
              placeholder="Describa el producto, servicio o iniciativa ejecutiva que desea promocionar..."
              className="w-full p-4 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 text-base font-medium focus:ring-2 focus:ring-fuchsia-500 focus:bg-white transition-all resize-none"
            />

            <div className="flex justify-end">
              <button
                onClick={() => handleGenerate()}
                disabled={isLoading || !promptTopic.trim()}
                className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-fuchsia-700 hover:bg-fuchsia-800 text-white font-bold text-base shadow-md disabled:opacity-50 transition-all"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Diseñando Campaña...</span>
                  </>
                ) : (
                  <>
                    <Film className="w-5 h-5" />
                    <span>Generar Campaña 360°</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Preset Executive Templates */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4">
            <h3 className="text-base font-black text-slate-900 uppercase tracking-wider text-slate-500">
              Plantillas Directivas Pre-Cargadas
            </h3>
            <div className="space-y-3">
              {templates.map((tmpl) => (
                <button
                  key={tmpl.id}
                  onClick={() => handleSelectTemplate(tmpl)}
                  className={`w-full text-left p-4 rounded-2xl border transition-all duration-200 flex items-center justify-between gap-3 ${
                    selectedTemplate === tmpl.id
                      ? 'bg-fuchsia-50/80 border-fuchsia-300 shadow-sm ring-1 ring-fuchsia-300'
                      : 'bg-white hover:bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black uppercase text-fuchsia-700 bg-fuchsia-100 px-2 py-0.5 rounded">
                        {tmpl.impact}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">{tmpl.industry}</span>
                    </div>
                    <p className="text-base font-bold text-slate-900 leading-snug">
                      {tmpl.title}
                    </p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-slate-400 shrink-0" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right 7 Cols: Generated Campaign Overview & Storyboard */}
        <div className="lg:col-span-7 space-y-6">
          
          {isLoading && (
            <div className="glass-panel p-16 rounded-3xl border border-slate-200 flex flex-col items-center justify-center text-center space-y-4 min-h-[520px]">
              <div className="w-16 h-16 rounded-full bg-fuchsia-50 text-fuchsia-600 flex items-center justify-center animate-spin">
                <Loader2 className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-black text-slate-900">
                Diseñando Storyboard & Narrativa Visual...
              </h3>
              <p className="text-slate-600 text-base max-w-md">
                Vertex AI está ensamblando los 4 paneles cinemáticos, redactando guiones de locución y proyectando métricas financieras de CAC y ROI.
              </p>
            </div>
          )}

          {!isLoading && !campaign && (
            <div className="glass-panel p-16 rounded-3xl border border-slate-200 flex flex-col items-center justify-center text-center space-y-4 min-h-[520px]">
              <div className="w-16 h-16 rounded-2xl bg-fuchsia-100 text-fuchsia-700 flex items-center justify-center shadow-inner">
                <Film className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-black text-slate-900">
                Generador de Campañas Listo
              </h3>
              <p className="text-slate-600 text-base max-w-lg">
                Seleccione una plantilla o escriba una iniciativa para desplegar la campaña multimedia en alta definición en la pantalla de 100".
              </p>
            </div>
          )}

          {!isLoading && campaign && (
            <div className="space-y-6">
              
              {/* Campaign Header Card */}
              <div className="glass-panel-elevated p-6 rounded-3xl border-2 border-fuchsia-200 space-y-4 bg-gradient-to-br from-white via-fuchsia-50/20 to-pink-50/20">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-fuchsia-600 text-white">
                    Campaña 360° Aprobada
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Tono:</span>
                    <span className="text-xs font-bold text-fuchsia-800 bg-fuchsia-100 px-2.5 py-1 rounded-full">
                      {campaign.tone_of_voice}
                    </span>
                  </div>
                </div>

                <h3 className="text-2xl sm:text-3xl font-black text-slate-900">
                  {campaign.campaign_title}
                </h3>

                <p className="text-lg font-semibold text-slate-700">
                  {campaign.central_concept}
                </p>

                {/* Slogan Banner */}
                <div className="p-4 rounded-2xl bg-slate-900 text-white flex items-center justify-between gap-4 shadow-md">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-widest text-fuchsia-400 block">
                      Slogan Ejecutivo Institucional
                    </span>
                    <span className="text-xl sm:text-2xl font-black tracking-tight">
                      "{campaign.executive_slogan}"
                    </span>
                  </div>
                  <button
                    onClick={() => setIsReelPlayerOpen(true)}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-sm shrink-0"
                  >
                    <Play className="w-4 h-4 fill-current" /> Ver Reel
                  </button>
                </div>
              </div>

              {/* 4-Panel Visual Storyboard Grid */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-fuchsia-600" />
                    Storyboard Visual de 4 Paneles
                  </h4>
                  <span className="text-xs font-bold text-slate-500">Secuencia Cinemática</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {campaign.storyboard.map((panel, idx) => (
                    <div
                      key={idx}
                      className="glass-panel p-5 rounded-2xl border border-slate-200 hover:border-fuchsia-300 transition-all hover:shadow-md space-y-3 flex flex-col justify-between"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-black uppercase tracking-wider text-fuchsia-700 bg-fuchsia-100 px-2 py-0.5 rounded">
                            {panel.visual_badge} • Panel {panel.panel_number}
                          </span>
                          <span className="text-xs font-bold text-slate-400 font-mono">
                            {panel.duration_seconds}s
                          </span>
                        </div>
                        <h5 className="text-base font-black text-slate-900">{panel.title}</h5>
                        
                        {/* On-Screen Punchy Text */}
                        <div className="p-2.5 rounded-xl bg-slate-100 border border-slate-200 text-xs sm:text-sm font-black text-slate-800">
                          "{panel.on_screen_text}"
                        </div>

                        {/* Visual Description */}
                        <p className="text-xs sm:text-sm text-slate-600 font-medium line-clamp-3">
                          {panel.visual_description}
                        </p>
                      </div>

                      {/* Voiceover Footer */}
                      <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 font-medium">
                        <span className="font-bold text-slate-700">Locución: </span>
                        "{panel.voiceover_script}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Multichannel Copy Tabs */}
              <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <Share2 className="w-4 h-4 text-fuchsia-600" />
                    Copy Adaptado Multicanal
                  </h4>
                </div>

                <div className="flex gap-2 border-b border-slate-200 pb-2">
                  {campaign.channels_copy.map((ch, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveChannelTab(idx)}
                      className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                        activeChannelTab === idx
                          ? 'bg-fuchsia-100 text-fuchsia-800 shadow-sm'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {ch.channel}
                    </button>
                  ))}
                </div>

                {campaign.channels_copy[activeChannelTab] && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-500">
                        Formato: {campaign.channels_copy[activeChannelTab].format_type}
                      </span>
                      <span className="text-xs font-black uppercase text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {campaign.channels_copy[activeChannelTab].target_metric}
                      </span>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-800 text-sm sm:text-base font-medium whitespace-pre-wrap">
                      {campaign.channels_copy[activeChannelTab].content}
                    </div>

                    <div className="flex justify-end">
                      <button
                        onClick={() => handleCopyText(campaign.channels_copy[activeChannelTab].content, activeChannelTab)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-bold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
                      >
                        {copiedIndex === activeChannelTab ? (
                          <>
                            <Check className="w-4 h-4 text-emerald-600" />
                            <span>Copiado</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            <span>Copiar Contenido</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Financial Projection Dashboard (Big Numbers for 100" Screen) */}
              <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                  Proyección Financiera & Retorno de Inversión (ROI)
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 block">
                      Retorno Proyectado
                    </span>
                    <span className="text-4xl font-black text-emerald-700">
                      {campaign.financial_projection.roi_porcentaje}
                    </span>
                    <span className="text-xs text-emerald-700 font-medium block mt-1">
                      Payback en {campaign.financial_projection.payback_period}
                    </span>
                  </div>

                  <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-200">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-800 block">
                      Optimización de CAC
                    </span>
                    <span className="text-4xl font-black text-blue-700">
                      {campaign.financial_projection.cac_impact}
                    </span>
                    <span className="text-xs text-blue-700 font-medium block mt-1">
                      {campaign.financial_projection.conversion_multiplier} Conversión
                    </span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
                      Presupuesto Sugerido
                    </span>
                    <span className="text-3xl sm:text-4xl font-black text-slate-900">
                      {campaign.financial_projection.recommended_budget}
                    </span>
                    <span className="text-xs text-slate-500 font-medium block mt-1">
                      Distribución Omnicanal
                    </span>
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>

      </div>

      {/* Reel Player Modal */}
      {campaign && (
        <ReelPlayerModal
          isOpen={isReelPlayerOpen}
          onClose={() => setIsReelPlayerOpen(false)}
          campaignTitle={campaign.campaign_title}
          slogan={campaign.executive_slogan}
          panels={campaign.storyboard}
        />
      )}

    </div>
  );
};
