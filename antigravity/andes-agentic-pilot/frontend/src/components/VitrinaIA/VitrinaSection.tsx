import { useEffect, useMemo, useRef, useState } from 'react';
import { ALL_PERSONAS, VITRINA_CARDS, type Persona, type VitrinaCard as VitrinaCardType } from '../../mocks';
import VitrinaCard from './VitrinaCard';
import './VitrinaSection.css';

/* -----------------------------------------------------------------------------
 * VitrinaSection — "Tu beneficio, contado por IA"
 *
 * Showcase of personalised generative cards (Nano Banana Pro = Gemini 3 Image).
 * Self-contained: mount as <VitrinaSection /> anywhere inside <main>.
 *
 * Layout:
 *   - Header with eyebrow / title / subtitle / "Powered by" pill
 *   - Carousel (<1024px) or 3-up grid (>=1024px) of VitrinaCards
 *   - "Generar tarjeta para mí" CTA — disabled, opens "Try it live" tooltip
 *
 * The first visible card auto-plays its 3-stage reveal after 500ms.
 * -------------------------------------------------------------------------- */

function getRecipientName(card: VitrinaCardType, personasById: Map<string, Persona>): string {
  const p = personasById.get(card.persona_id);
  if (!p) return 'tu afiliado';
  // Prefer first name only — the cards feel more personal that way
  return p.primer_nombre ?? p.nombre_completo.split(' ')[0];
}

export default function VitrinaSection() {
  const [activeIdx, setActiveIdx] = useState(0);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isWide, setIsWide] = useState<boolean>(() =>
    typeof window !== 'undefined' ? window.innerWidth >= 1024 : true,
  );
  const trackRef = useRef<HTMLDivElement>(null);

  const personasById = useMemo(() => {
    const m = new Map<string, Persona>();
    ALL_PERSONAS.forEach((p) => m.set(p.id, p));
    return m;
  }, []);

  const cards = VITRINA_CARDS;

  /* responsive: track viewport for grid vs carousel */
  useEffect(() => {
    const onResize = () => setIsWide(window.innerWidth >= 1024);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  /* dismiss tooltip on outside click */
  useEffect(() => {
    if (!showTooltip) return;
    const t = window.setTimeout(() => setShowTooltip(false), 4500);
    return () => window.clearTimeout(t);
  }, [showTooltip]);

  const goPrev = () => setActiveIdx((i) => Math.max(0, i - 1));
  const goNext = () => setActiveIdx((i) => Math.min(cards.length - 1, i + 1));

  /* scroll the carousel track when activeIdx changes (mobile) */
  useEffect(() => {
    if (isWide) return;
    const track = trackRef.current;
    if (!track) return;
    const child = track.children[activeIdx] as HTMLElement | undefined;
    if (child) {
      track.scrollTo({ left: child.offsetLeft - track.offsetLeft, behavior: 'smooth' });
    }
  }, [activeIdx, isWide]);

  return (
    <section className="vitrina-section" aria-label="Vitrina IA de tarjetas personalizadas">
      {/* dotted/glow ornaments — pure decorative */}
      <div className="vitrina-section__glow vitrina-section__glow--a" aria-hidden />
      <div className="vitrina-section__glow vitrina-section__glow--b" aria-hidden />

      <div className="vitrina-section__container">
        <header className="vitrina-section__header">
          <div className="vitrina-section__header-text">
            <span className="vitrina-section__eyebrow">VITRINA IA</span>
            <h2 className="vitrina-section__title">Tu beneficio, contado por IA</h2>
            <p className="vitrina-section__subtitle">
              Tarjetas personalizadas generadas en vivo con Gemini 3 Image — listas para WhatsApp.
            </p>
          </div>
          <div className="vitrina-section__pill" title="gemini-3-pro-image-preview">
            <span className="vitrina-section__pill-dot" aria-hidden />
            Powered by <strong>Nano Banana Pro</strong>
          </div>
        </header>

        {/* ---------- CARDS: grid on wide, scroll-snap carousel on narrow ---------- */}
        <div className={`vitrina-section__stage${isWide ? ' is-grid' : ' is-carousel'}`}>
          {!isWide && (
            <button
              type="button"
              className="vitrina-section__nav vitrina-section__nav--prev"
              onClick={goPrev}
              aria-label="Tarjeta anterior"
              disabled={activeIdx === 0}
            >
              ‹
            </button>
          )}

          <div className="vitrina-section__track" ref={trackRef}>
            {cards.map((card, idx) => (
              <div
                className={`vitrina-section__slot${idx === activeIdx ? ' is-active' : ''}`}
                key={card.id}
              >
                <VitrinaCard
                  card={card}
                  recipientName={getRecipientName(card, personasById)}
                  autoPlay={idx === 0}
                  autoPlayDelayMs={500}
                />
              </div>
            ))}
          </div>

          {!isWide && (
            <button
              type="button"
              className="vitrina-section__nav vitrina-section__nav--next"
              onClick={goNext}
              aria-label="Siguiente tarjeta"
              disabled={activeIdx === cards.length - 1}
            >
              ›
            </button>
          )}
        </div>

        {/* dots indicator (carousel only) */}
        {!isWide && (
          <div className="vitrina-section__dots" role="tablist" aria-label="Navegar tarjetas">
            {cards.map((c, idx) => (
              <button
                key={c.id}
                type="button"
                role="tab"
                aria-selected={idx === activeIdx}
                aria-label={`Ir a tarjeta ${idx + 1}`}
                className={`vitrina-section__dot${idx === activeIdx ? ' is-active' : ''}`}
                onClick={() => setActiveIdx(idx)}
              />
            ))}
          </div>
        )}

        {/* ---------- BOTTOM CTA ---------- */}
        <div className="vitrina-section__cta">
          <div className="vitrina-section__cta-inner">
            <button
              type="button"
              className="vitrina-section__cta-btn"
              onClick={() => setShowTooltip((s) => !s)}
              aria-haspopup="dialog"
              aria-expanded={showTooltip}
            >
              <span aria-hidden>✨</span>
              Generar tarjeta para mí
            </button>
            <span className="vitrina-section__cta-note">Demo: 6 tarjetas pre-renderizadas</span>
            {showTooltip && (
              <div className="vitrina-section__tooltip" role="dialog">
                <strong>Try it live</strong>
                <p>
                  En producción esta tarjeta se genera en ~1.4s con Gemini 3 Pro Image, usando los
                  datos del afiliado y respetando el manual de marca CCLA.
                </p>
                <p className="vitrina-section__tooltip-meta">
                  Disponible en el roadmap Q3 2026 · contacto: andesia@cajalosandes.cl
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
