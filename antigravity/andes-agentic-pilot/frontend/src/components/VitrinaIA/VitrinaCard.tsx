import { useEffect, useMemo, useRef, useState } from 'react';
import type { VitrinaCard as VitrinaCardType } from '../../mocks';

/* -----------------------------------------------------------------------------
 * VitrinaCard — single generative card with 3-stage reveal
 *
 * Stage 1: prompt typewriter (10-15ms / char)  — "Generando..."
 * Stage 2: progress bar  ("Renderizando con Nano Banana Pro... 1.4s avg")
 * Stage 3: image fade-in + copy + CTAs
 *
 * Image URLs from mocks point at a placeholder CDN that won't resolve.
 * onError swaps to a brand-gradient fallback with the recipient name.
 * -------------------------------------------------------------------------- */

type Stage = 'idle' | 'prompt' | 'render' | 'done';

interface VitrinaCardProps {
  card: VitrinaCardType;
  recipientName: string;
  /** if true, the card kicks off its reveal automatically on mount */
  autoPlay?: boolean;
  /** initial delay before auto-play starts */
  autoPlayDelayMs?: number;
}

export default function VitrinaCard({
  card,
  recipientName,
  autoPlay = false,
  autoPlayDelayMs = 0,
}: VitrinaCardProps) {
  const [stage, setStage] = useState<Stage>('idle');
  const [typedPrompt, setTypedPrompt] = useState('');
  const [progress, setProgress] = useState(0);
  const [imageBroken, setImageBroken] = useState(false);
  const [showBrandOverlay, setShowBrandOverlay] = useState(false);
  const [runId, setRunId] = useState(0); // forces effect re-run on replay
  const timersRef = useRef<number[]>([]);

  /* deterministic per-card seed for the render-time label */
  const renderSeconds = useMemo(
    () => Math.max(0.9, Math.min(2.0, card.generation_metadata.generation_time_seconds / 8)),
    [card.generation_metadata.generation_time_seconds],
  );

  const promptText = card.prompt_imagen;

  /* trim very long prompts so the typewriter feels punchy */
  const visiblePrompt = useMemo(
    () => (promptText.length > 220 ? promptText.slice(0, 217).trimEnd() + '...' : promptText),
    [promptText],
  );

  /* ---------- reveal orchestration ---------- */
  useEffect(() => {
    if (stage !== 'prompt') return;
    setTypedPrompt('');
    let i = 0;
    const tick = () => {
      i += 1;
      setTypedPrompt(visiblePrompt.slice(0, i));
      if (i < visiblePrompt.length) {
        const t = window.setTimeout(tick, 10 + Math.random() * 5);
        timersRef.current.push(t);
      } else {
        const t = window.setTimeout(() => setStage('render'), 250);
        timersRef.current.push(t);
      }
    };
    const t = window.setTimeout(tick, 60);
    timersRef.current.push(t);
    return () => {
      timersRef.current.forEach((id) => window.clearTimeout(id));
      timersRef.current = [];
    };
  }, [stage, visiblePrompt, runId]);

  useEffect(() => {
    if (stage !== 'render') return;
    setProgress(0);
    const totalMs = renderSeconds * 1000;
    const stepMs = 60;
    const steps = Math.ceil(totalMs / stepMs);
    let s = 0;
    const id = window.setInterval(() => {
      s += 1;
      setProgress(Math.min(100, Math.round((s / steps) * 100)));
      if (s >= steps) {
        window.clearInterval(id);
        setStage('done');
      }
    }, stepMs);
    return () => window.clearInterval(id);
  }, [stage, renderSeconds, runId]);

  /* ---------- auto-play kickoff ---------- */
  useEffect(() => {
    if (!autoPlay) return;
    const t = window.setTimeout(() => setStage('prompt'), autoPlayDelayMs);
    return () => window.clearTimeout(t);
  }, [autoPlay, autoPlayDelayMs]);

  /* ---------- replay ---------- */
  const replay = () => {
    timersRef.current.forEach((id) => window.clearTimeout(id));
    timersRef.current = [];
    setImageBroken(false);
    setProgress(0);
    setTypedPrompt('');
    setRunId((r) => r + 1);
    setStage('prompt');
  };

  /* ---------- start on first user click when not auto ---------- */
  const startManual = () => {
    if (stage === 'idle') setStage('prompt');
  };

  const brand = card.brand_elements;
  const isVideo = card.card_size === 'video_short_9x16';
  const aspect =
    card.card_size === 'banner_1200x628'
      ? '1200 / 628'
      : card.card_size === 'story_1080x1920' || isVideo
        ? '9 / 16'
        : '1 / 1';

  return (
    <article
      className={`vitrina-card vitrina-card--stage-${stage}`}
      onMouseEnter={() => setShowBrandOverlay(true)}
      onMouseLeave={() => setShowBrandOverlay(false)}
    >
      {/* ---------- VISUAL FRAME ---------- */}
      <div
        className="vitrina-card__visual"
        style={{ aspectRatio: aspect }}
        onClick={startManual}
        role={stage === 'idle' ? 'button' : undefined}
        tabIndex={stage === 'idle' ? 0 : -1}
      >
        {/* IDLE: clickable poster */}
        {stage === 'idle' && (
          <div className="vitrina-card__idle">
            <span className="vitrina-card__sparkle" aria-hidden>
              ✨
            </span>
            <p className="vitrina-card__idle-text">Generar tarjeta</p>
            <span className="vitrina-card__idle-sub">{card.trigger.tipo.replace(/_/g, ' ')}</span>
          </div>
        )}

        {/* PROMPT: typewriter */}
        {stage === 'prompt' && (
          <div className="vitrina-card__prompt">
            <div className="vitrina-card__prompt-header">
              <span className="vitrina-card__sparkle" aria-hidden>
                ✨
              </span>
              <span>Generando con Nano Banana Pro...</span>
            </div>
            <p className="vitrina-card__prompt-text">
              <span className="vitrina-card__prompt-label">prompt:</span> {typedPrompt}
              <span className="vitrina-card__caret" aria-hidden />
            </p>
          </div>
        )}

        {/* RENDER: progress bar */}
        {stage === 'render' && (
          <div className="vitrina-card__render">
            <div className="vitrina-card__render-spinner" aria-hidden>
              <span />
              <span />
              <span />
            </div>
            <p className="vitrina-card__render-label">
              Renderizando con Nano Banana Pro... {renderSeconds.toFixed(1)}s avg
            </p>
            <div className="vitrina-card__progress" aria-hidden>
              <div className="vitrina-card__progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="vitrina-card__render-meta">
              {card.generation_metadata.prompt_tokens} prompt tokens · seed{' '}
              {card.generation_metadata.seed}
            </p>
          </div>
        )}

        {/* DONE: image (or fallback) */}
        {stage === 'done' && (
          <>
            {!imageBroken ? (
              <img
                className="vitrina-card__image"
                src={card.asset_url}
                alt={card.share_assets.alt_text_accessibility}
                onError={() => setImageBroken(true)}
              />
            ) : (
              <div
                className="vitrina-card__fallback"
                style={{
                  background: `linear-gradient(155deg, ${brand.primary_color} 0%, ${brand.accent_color} 100%)`,
                }}
                aria-label={card.share_assets.alt_text_accessibility}
              >
                <div className="vitrina-card__fallback-inner">
                  <span className="vitrina-card__fallback-eyebrow">Para</span>
                  <span className="vitrina-card__fallback-name">{recipientName}</span>
                  <span className="vitrina-card__fallback-title">{card.titulo}</span>
                </div>
                <span className="vitrina-card__fallback-watermark" aria-hidden>
                  AI Preview · Nano Banana Pro
                </span>
              </div>
            )}

            {/* hover overlay: brand elements detected */}
            {showBrandOverlay && (
              <div className="vitrina-card__brand-overlay" role="note">
                <p className="vitrina-card__brand-overlay-title">
                  <span className="vitrina-card__shield" aria-hidden>
                    ◆
                  </span>
                  Brand-aware AI
                </p>
                <ul>
                  <li>
                    <span className="vitrina-card__swatch" style={{ background: brand.primary_color }} />
                    Primario {brand.primary_color}
                  </li>
                  <li>
                    <span className="vitrina-card__swatch" style={{ background: brand.accent_color }} />
                    Acento {brand.accent_color}
                  </li>
                  <li>Logo · {brand.logo_position.replace('-', ' ')}</li>
                  <li>Tipo · {brand.typography}</li>
                  {brand.watermark_visible && <li>Watermark CCLA visible</li>}
                </ul>
              </div>
            )}

            {/* small badge top-right */}
            <span className="vitrina-card__model-badge" aria-hidden>
              {card.generation_metadata.model}
            </span>
          </>
        )}
      </div>

      {/* ---------- BODY ---------- */}
      <div className="vitrina-card__body">
        <div className="vitrina-card__meta">
          <span className={`vitrina-card__chip vitrina-card__chip--${card.trigger.tipo}`}>
            {card.trigger.tipo.replace(/_/g, ' ')}
          </span>
          <span className="vitrina-card__recipient">
            Para <strong>{recipientName}</strong>
          </span>
        </div>

        <h3 className="vitrina-card__title">{card.titulo}</h3>
        <p className="vitrina-card__subtitle">{card.subtitulo}</p>

        <div className="vitrina-card__brand-chips" aria-label="Elementos de marca detectados">
          <span className="vitrina-card__brand-chip">
            <span className="vitrina-card__swatch" style={{ background: brand.primary_color }} />
            Color CCLA
          </span>
          <span className="vitrina-card__brand-chip">Logo · {brand.logo_position.replace('-', ' ')}</span>
          <span className="vitrina-card__brand-chip">{brand.typography.split('/')[0].trim()}</span>
        </div>

        <div className="vitrina-card__actions">
          <button type="button" className="vitrina-card__btn vitrina-card__btn--primary" disabled={stage !== 'done'}>
            <span aria-hidden>💬</span>
            Compartir por WhatsApp
          </button>
          <button type="button" className="vitrina-card__btn vitrina-card__btn--ghost" disabled={stage !== 'done'}>
            <span aria-hidden>⬇</span>
            Descargar
          </button>
          <button
            type="button"
            className="vitrina-card__btn vitrina-card__btn--text"
            onClick={replay}
            disabled={stage === 'prompt' || stage === 'render'}
          >
            ↻ Volver a generar
          </button>
        </div>

        <div className="vitrina-card__metrics" aria-label="Métricas predichas">
          <span>
            <strong>{card.ctr_predicho_pct.toFixed(1)}%</strong> CTR predicho
          </span>
          <span aria-hidden>·</span>
          <span>
            <strong>{card.conversion_predicha_pct.toFixed(1)}%</strong> conversión
          </span>
          <span aria-hidden>·</span>
          <span>${card.generation_metadata.cost_usd_estimated.toFixed(3)} costo</span>
        </div>
      </div>
    </article>
  );
}
