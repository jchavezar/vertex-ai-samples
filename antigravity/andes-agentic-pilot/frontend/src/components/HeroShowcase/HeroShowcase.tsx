import './HeroShowcase.css';

/* -----------------------------------------------------------------------------
 * HeroShowcase — "Activos visuales generados con Nano Banana"
 *
 * Static gallery of 6 HD images pre-rendered with Imagen 4 (and re-prompted
 * via the same Gemini 2.5 Flash Image / Nano Banana family that powers our
 * VitrinaIA component). Lives between the QuickTiles and the live VitrinaIA
 * section so the customer sees BOTH:
 *   1) Curated brand-aligned visuals (this strip) — proof we can pre-bake.
 *   2) Live-generated personalised cards (VitrinaSection) — proof we can do it
 *      on-demand per affiliate.
 *
 * All images live under /images/generated/* and ship a visible "Generado con
 * Gemini · Nano Banana" pill watermark stamped at generation time.
 * -------------------------------------------------------------------------- */

interface ShowcaseItem {
  src: string;
  alt: string;
  title: string;
  subtitle: string;
  prompt: string;
}

const ITEMS: ShowcaseItem[] = [
  {
    src: '/images/generated/hero-familia.png',
    alt: 'Familia chilena multi-generacional en su living, vista de la cordillera al fondo',
    title: 'Familia Andes',
    subtitle: 'Comunicación segmento Trabajadores',
    prompt: 'Familia chilena multigeneracional, hogar luminoso, golden hour, 50mm.',
  },
  {
    src: '/images/generated/credito-hipotecario.png',
    alt: 'Pareja joven chilena recibiendo las llaves de su nueva casa',
    title: 'Crédito Hipotecario',
    subtitle: 'Hero campaña Vivienda',
    prompt: 'Pareja joven recibiendo llaves de su nueva casa, barrio chileno.',
  },
  {
    src: '/images/generated/bodas-de-oro.png',
    alt: 'Pareja adulta mayor chilena celebrando sus Bodas de Oro',
    title: 'Bodas de Oro · Ley 20.506',
    subtitle: 'Beneficio Pensionados',
    prompt: 'Pareja chilena 70+ celebrando 50 años de matrimonio, luz cálida.',
  },
  {
    src: '/images/generated/becas-educacion.png',
    alt: 'Estudiante universitario chileno con notebook en biblioteca moderna',
    title: 'Becas y Educación',
    subtitle: 'Programa Apoyo Educacional',
    prompt: 'Estudiante universitario chileno tomando notas, biblioteca moderna.',
  },
  {
    src: '/images/generated/turismo-cordillera.png',
    alt: 'Familia mirando la cordillera de los Andes al atardecer',
    title: 'Turismo y Recreación',
    subtitle: 'Promo Centros Turísticos CCLA',
    prompt: 'Cordillera de los Andes al atardecer, familia mirando el paisaje.',
  },
  {
    src: '/images/generated/andesia-orb.png',
    alt: 'Esfera abstracta cyan con motivo cordillerano que representa a Andesia',
    title: 'Andesia · Marca asistente',
    subtitle: 'Identidad visual del agente',
    prompt: 'Esfera de plasma cyan abstracta con motivo cordillerano sutil.',
  },
];

export default function HeroShowcase() {
  return (
    <section className="hs-section" aria-label="Galería de assets generados con IA">
      <div className="hs-section__glow hs-section__glow--a" aria-hidden />
      <div className="hs-section__glow hs-section__glow--b" aria-hidden />

      <div className="hs-section__container">
        <header className="hs-section__header">
          <div className="hs-section__header-text">
            <span className="hs-section__eyebrow">ASSETS HD GENERADOS POR IA</span>
            <h2 className="hs-section__title">
              Tu comunicación, en imagen — generada con Nano Banana
            </h2>
            <p className="hs-section__subtitle">
              Cada imagen de esta galería fue generada con{' '}
              <strong>Gemini · Nano Banana</strong> en Vertex AI a 2400×1350,
              alineada al manual de marca de Caja Los Andes y lista para
              campañas, redes y portal del afiliado.
            </p>
          </div>
          <div className="hs-section__pill" title="imagen-4.0-generate-001 · Vertex AI">
            <span className="hs-section__pill-dot" aria-hidden />
            Powered by <strong>Gemini · Nano Banana</strong>
          </div>
        </header>

        <ul className="hs-section__grid">
          {ITEMS.map((item) => (
            <li key={item.src} className="hs-card">
              <div className="hs-card__visual">
                <img src={item.src} alt={item.alt} loading="lazy" />
                <span className="hs-card__chip" aria-hidden>
                  HD · 16:9
                </span>
              </div>
              <div className="hs-card__body">
                <h3 className="hs-card__title">{item.title}</h3>
                <p className="hs-card__subtitle">{item.subtitle}</p>
                <p className="hs-card__prompt">
                  <span className="hs-card__prompt-label">prompt:</span> {item.prompt}
                </p>
              </div>
            </li>
          ))}
        </ul>

        <footer className="hs-section__footer">
          <span className="hs-section__footer-dot" aria-hidden />
          <p>
            <strong>6 activos</strong> generados en menos de 2 minutos · modelo{' '}
            <code>imagen-4.0-generate-001</code> · región <code>us-central1</code> ·
            watermark visible aplicado en post-proceso.
          </p>
        </footer>
      </div>
    </section>
  );
}
