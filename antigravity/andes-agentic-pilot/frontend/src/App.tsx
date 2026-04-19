import { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import DocumentAISection from './components/DocumentAI';
import HeroShowcase from './components/HeroShowcase';
import { AndesiaChat } from './components/AndesiaChat';
import { CreditSimulator, CreditAgentArchitecture } from './components/CreditSimulator';
import type { CreditEvent } from './components/CreditSimulator';

/* -----------------------------------------------------------------------------
 * Caja Los Andes — high-fidelity public-site replica
 *
 * Source of truth for nav, copy, asset URLs and design tokens:
 *   frontend/scraped/  (raw HTML + CSS pulled from cajalosandes.cl on 2026-04-18)
 *
 * Layout sections (top → bottom):
 *   <SegmentBar />        thin segments strip (Trabajadores · Pensionados · …)
 *   <MainHeader />        official logo + Mi Portal CTA + AI SearchBar
 *   <PrimaryNav />        7-item mega-nav (Licencias · Créditos · Seguros …)
 *   <Hero />              two big "Guía de beneficios" / REDEC promo cards
 *   <Banner />            "Revisa tus pagos en exceso" cross-service banner
 *   <CardsCopec />        Tapp + Urgencia Dental cards
 *   <Afiliacion />        sucursal-virtual / afiliación promo strip
 *   <Footer />            real link groups + sellos + redes + app stores
 *   <Suseso />            black SUSESO disclaimer ribbon
 *   <CookieBanner />      dismissible cookie strip
 * -------------------------------------------------------------------------- */

/* === Audience selector (segments) =========================================
 * Order verbatim from scraped/homepage.html nav-list (ds-header-navbar).
 * Inversionistas is the lone left-side link; the rest are segments. */

const topbarLinks = [
  { label: 'Inversionistas', href: 'https://inversionistas.cajalosandes.cl/' },
];

const segments = [
  { label: 'Trabajadores', href: 'https://www.cajalosandes.cl', active: true },
  { label: 'Somos Andes', href: 'https://somosandes.cajalosandes.cl/' },
  { label: 'Pensionados', href: 'https://pensionados.cajalosandes.cl' },
  { label: 'Empresas', href: 'https://empresa.cajalosandes.cl' },
  { label: 'Ex afiliados', href: 'https://exafiliados.cajalosandes.cl' },
];

/* === Quick-access tiles (below the hero carousel) ==========================
 * Icons via Material Symbols to match the ds-icon pictograms on the real site. */

const quickTiles = [
  { label: 'Crédito Social', icon: 'directions_car', href: '#' },
  { label: 'Licencia Médica', icon: 'medical_services', href: '#' },
  { label: 'Ahorro', icon: 'savings', href: '#' },
  { label: 'Beneficios', icon: 'local_offer', href: '#' },
  { label: 'Sucursal Virtual', icon: 'account_balance', href: '#' },
  { label: 'Centro de Ayuda', icon: 'support_agent', href: '#' },
];

/* === Primary nav with mega-menu submenus (verbatim from scraped JSON) ===== */

interface NavItem {
  label: string;
  href: string;
  banner?: { image: string; paragraph: string };
  submenu?: { label: string; href: string; tag?: string }[];
  /* Agentic items (no real URL) — open an in-page experience instead of navigating. */
  agent?: 'credit';
}

const primaryNav: NavItem[] = [
  { label: 'Inicio', href: 'https://www.cajalosandes.cl' },
  {
    label: 'Simulador',
    href: '#',
    agent: 'credit',
  },
  {
    label: 'Licencias',
    href: 'https://www.cajalosandes.cl/licencias-medicas',
    banner: {
      image: '/images/licencias.webp',
      paragraph: 'Te ayudamos en la gestión de tus Licencias Médicas',
    },
    submenu: [
      { label: 'Ver todo Licencias Médicas', href: '#' },
      { label: 'Requisitos y Documentos', href: '#' },
      { label: 'Etapas y Plazos de una Licencia', href: '#' },
      { label: 'Cálculo de una Licencia Médica', href: '#' },
      { label: 'Pago de una Licencia Médica', href: '#' },
      { label: 'Rechazo de una Licencia Médica', href: '#' },
      { label: '¿Qué es una Licencia Médica?', href: '#' },
      { label: 'Licencias Médicas Electrónicas', href: '#' },
      { label: 'Licencias Médicas Prescritas', href: '#' },
    ],
  },
  {
    label: 'Créditos',
    href: 'https://www.cajalosandes.cl/creditos',
    banner: {
      image: '/images/generated/credito-hipotecario.png',
      paragraph:
        'Aprende a gestionar tus finanzas para escoger la alternativa que realmente necesitas',
    },
    submenu: [
      { label: 'Simula tu crédito', href: '#' },
      { label: 'Crédito Universal', href: '#' },
      { label: 'Crédito de Salud', href: '#' },
      { label: 'Crédito Consolidación de Deuda', href: '#' },
      { label: 'Tasas de Interés', href: '#' },
      { label: 'Alzamiento de Hipotecas', href: '#' },
      { label: 'Medios de Pago', href: '#' },
      { label: 'Reembolso por Pagos en Exceso', href: '#' },
      { label: 'Portabilidad Financiera', href: '#' },
      { label: 'Reprogramación', href: '#' },
      { label: 'Crédito Educación Superior', href: '#' },
      { label: 'Educación Financiera', href: '#' },
      { label: 'REDEC', href: '#', tag: 'Nuevo' },
      { label: 'Ver todo Créditos', href: '#' },
    ],
  },
  {
    label: 'Seguros',
    href: 'https://www.cajalosandes.cl/seguros',
    banner: {
      image: '/images/seguro.webp',
      paragraph:
        'Descubre un seguro que encaje con tus necesidades y estilo de vida. Protégete a ti y a tus cercanos.',
    },
    submenu: [
      { label: 'Seguro Automotriz', href: '#' },
      { label: 'Seguro Catastrófico', href: '#', tag: 'Nuevo' },
      { label: 'Seguro Escolar', href: '#' },
      { label: 'Seguro de Vida Familiar Full', href: '#' },
      { label: 'Seguro Hogar Smart', href: '#' },
      { label: 'Seguro Asistencia en Viajes', href: '#' },
      { label: 'Seguro Venta Telefónica', href: '#' },
      { label: 'Seguro Automotriz Pérdida Total', href: '#' },
      { label: 'Seguro de Cesantía Crédito Social', href: '#' },
      { label: 'Seguro Empleo Protegido', href: '#' },
      { label: 'Full Asistencia', href: '#' },
      { label: 'Declarar un siniestro', href: '#' },
      { label: 'Ver todo Seguros', href: '#' },
    ],
  },
  {
    label: 'Ahorro',
    href: '#',
    banner: {
      image: '/images/ahorro.webp',
      paragraph: 'Construye tu futuro con productos pensados para tus metas.',
    },
    submenu: [
      { label: 'Mis Metas', href: '#' },
      { label: 'Fondos Mutuos', href: '#' },
      { label: 'Ahorro APV', href: '#' },
      { label: 'Ahorro Vivienda', href: '#' },
    ],
  },
  { label: 'Turismo', href: 'https://www.cajalosandes.cl/turismo' },
  {
    label: 'Beneficios',
    href: '#',
    submenu: [
      { label: 'Destacados del mes', href: '#', tag: 'Top' },
      { label: 'Salud y Deporte', href: '#' },
      { label: 'Educación', href: '#' },
      { label: 'Cultura y Panoramas', href: '#' },
      { label: 'Comunidad +50', href: '#' },
    ],
  },
  {
    label: 'Apoyo Social',
    href: 'https://www.cajalosandes.cl/apoyo-social',
    banner: {
      image: '/images/generated/bodas-de-oro.png',
      paragraph: 'Creamos beneficios que te ayuden en tu vida.',
    },
    submenu: [
      { label: 'Programa Cuidadores', href: '#', tag: 'Top' },
      { label: 'Asignación Familiar', href: '#' },
      { label: 'Cargas Familiares', href: '#' },
      { label: 'Subsidio Único Familiar', href: '#' },
      { label: 'Aporte Familiar Permanente', href: '#' },
      { label: 'Actualización de Tramos', href: '#' },
      { label: 'Ver todo Apoyo Social', href: '#' },
    ],
  },
];

/* === Footer link groups (verbatim from scraped HTML) ====================== */

const footerSomosAndes = [
  { label: 'Somos', href: 'https://somosandes.cajalosandes.cl/somos' },
  { label: 'Inversionistas', href: 'https://somosandes.cajalosandes.cl/inversionistas' },
  { label: 'Información pública', href: 'https://somosandes.cajalosandes.cl/somos/transparencia' },
  { label: 'Aviso de privacidad', href: 'https://somosandes.cajalosandes.cl/somos/transparencia' },
  { label: 'Línea ética', href: 'https://somosandes.cajalosandes.cl/linea-etica' },
  { label: 'Sostenibilidad', href: 'https://somosandes.cajalosandes.cl/sostenibilidad' },
  { label: 'Trabaja en Caja Los Andes', href: 'https://somosandes.cajalosandes.cl/somos/trabaja-en-caja-los-andes' },
  { label: 'Consulta Tu Caja de Compensación', href: 'https://consultatucaja.cajasdechile.cl/Consulta/Rut' },
  { label: 'Portal de proveedores', href: 'https://www.cajalosandes.cl/portalproveedores' },
  { label: 'Consulta de boletas emitidas', href: '#' },
  { label: 'Bases legales', href: 'https://www.cajalosandes.cl/baseslegales' },
];

const footerContacto = [
  { label: 'Centro de ayuda', href: 'https://www.cajalosandes.cl/centro-de-ayuda' },
  { label: 'Sucursales', href: 'https://www.cajalosandes.cl/centro-de-ayuda/sucursales' },
];

const footerSocials = [
  { label: 'Facebook', href: 'https://www.facebook.com/CajaLosAndesCL', icon: '/icons/icon-facebook.svg' },
  { label: 'Instagram', href: 'https://www.instagram.com/cajalosandes/', icon: '/icons/icon-instagram.svg' },
  { label: 'X', href: 'https://x.com/cajalosandes', icon: '/icons/icon-x.png' },
  { label: 'YouTube', href: 'https://www.youtube.com/user/canalandes', icon: '/icons/icon-youtube.svg' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com/company/cajalosandes', icon: '/icons/icon-linkedin.svg' },
];

const footerSellos = [
  { src: '/images/sello-gptw.webp', alt: 'Great Place to Work' },
  { src: '/images/sello-activos.webp', alt: 'Caja Los Andes Activos' },
  { src: '/images/sello-chile-inclusivo.webp', alt: 'Chile Inclusivo' },
  { src: '/images/sello-iguala.webp', alt: 'Sello Iguala' },
];

/* === Components =========================================================== */

/* TopUtilityBar = the thin "Centro de ayuda" strip that floats on the very top.
 * Real site: tiny right-aligned link with a help icon, no segments here.    */
function TopUtilityBar() {
  return (
    <div className="cla-topbar" role="navigation" aria-label="Utilidad">
      <div className="cla-container cla-topbar__inner">
        <div className="cla-topbar__right">
          <a
            href="https://www.cajalosandes.cl/centro-de-ayuda"
            className="cla-topbar__help"
          >
            <span className="material-symbols-outlined" aria-hidden>
              help
            </span>
            Centro de ayuda
          </a>
        </div>
      </div>
    </div>
  );
}

/* MainHeader = the unified blue bar (header-desk-pub--trabajadores).
 *  ┌──────────────────────────────────────────────────────────────────┐
 *  │ [CCHC logo] CAJA LOS ANDES |Tapp|   ←segments→   [Mi Portal]    │
 *  └──────────────────────────────────────────────────────────────────┘                  */
function MainHeader() {
  return (
    <header className="cla-header" role="banner">
      <div className="cla-container cla-header__inner">
        <div className="cla-header__logo">
          <a href="/" className="cla-header__logo-link" aria-label="Inicio – Caja Los Andes">
            {/* Real header wordmark extracted from claHeaderPublic.umd.js (wr fn).
                White SVG, rendered at native 173x40 — no filter inversion. */}
            <img src="/logo-cchs-wordmark.svg" alt="Caja Los Andes" />
          </a>
          <span className="cla-header__divider" aria-hidden />
          <a
            href="https://www.tapp.cl/"
            target="_blank"
            rel="noopener noreferrer"
            className="cla-header__tapp"
            aria-label="Tapp"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="56"
              height="24"
              viewBox="0 0 56 24"
              fill="none"
              aria-hidden
            >
              <path d="M6.72193 15.113H4.92726C4.6811 15.113 4.48169 15.3092 4.48169 15.5511V17.3392C4.48169 17.5811 4.6811 17.7773 4.92726 17.7773H6.64025H6.72193C6.96809 17.7773 7.1675 17.5811 7.1675 17.3392V15.5511C7.1675 15.3092 6.96753 15.113 6.72193 15.113Z" fill="#F9BE00" />
              <path d="M48.8314 3.55835C45.0116 3.55835 41.891 6.52154 41.6758 10.257C41.6679 10.3005 41.6628 10.3452 41.6628 10.3911V10.5688V17.0461V21.7739V22.0695V22.2477V23.2681V23.5637C41.6628 23.8056 41.8622 24.0023 42.1084 24.0023H42.403H43.6113H43.8214H43.9031C44.1492 24.0023 44.3486 23.8062 44.3486 23.5637V23.3167C44.3498 23.3005 44.3509 23.2848 44.3509 23.2681V23.1133V22.26V22.2243V22.0695V17.0461V16.0179C45.5 17.1612 47.1358 17.7798 48.8314 17.7798C52.7902 17.7798 55.9999 14.5959 55.9999 10.6688C55.9999 6.74226 52.7902 3.55835 48.8314 3.55835ZM48.8314 15.1138C46.3568 15.1138 44.3509 13.124 44.3509 10.6693C44.3509 8.21463 46.3568 6.22483 48.8314 6.22483C51.3059 6.22483 53.3119 8.21463 53.3119 10.6693C53.3119 13.124 51.3059 15.1138 48.8314 15.1138Z" fill="white" />
              <path d="M33.1532 3.55835C29.3334 3.55835 26.2128 6.52154 25.9976 10.257C25.9897 10.3005 25.9846 10.3452 25.9846 10.3911V10.5688V17.0461V21.7739V22.0695V22.2477V23.2681V23.5637C25.9846 23.8056 26.184 24.0023 26.4302 24.0023H26.7242H27.9325H28.1426H28.2243C28.4705 24.0023 28.6699 23.8062 28.6699 23.5637V23.3167C28.671 23.3005 28.6721 23.2848 28.6721 23.2681V23.1133V22.26V22.2243V22.0695V17.0461V16.0179C29.8212 17.1612 31.4571 17.7798 33.1526 17.7798C37.112 17.7798 40.3211 14.5959 40.3211 10.6688C40.3223 6.74226 37.1126 3.55835 33.1532 3.55835ZM33.1532 15.1138C30.6786 15.1138 28.6727 13.124 28.6727 10.6693C28.6727 8.21463 30.6786 6.22483 33.1532 6.22483C35.6277 6.22483 37.6336 8.21463 37.6336 10.6693C37.6336 13.124 35.6277 15.1138 33.1532 15.1138Z" fill="white" />
              <path d="M24.1945 10.5688C24.1945 10.5576 24.1934 10.5464 24.1928 10.5352C24.1207 6.66962 20.9398 3.55835 17.026 3.55835C13.0671 3.55835 9.85742 6.74226 9.85742 10.6693C9.85742 14.5964 13.0671 17.7803 17.026 17.7803C18.7215 17.7803 20.3573 17.1618 21.5064 16.0185V17.0467C21.5064 17.0545 21.5076 17.0623 21.5076 17.0701V17.3422C21.5076 17.5842 21.707 17.7809 21.9531 17.7809H22.2461H23.4543H23.6656H23.7472C23.9934 17.7809 24.1928 17.5848 24.1928 17.3422V17.0712C24.1934 17.0629 24.1939 17.055 24.1939 17.0461V10.5688H24.1945ZM17.026 15.1138C14.5514 15.1138 12.5455 13.124 12.5455 10.6693C12.5455 8.21463 14.5514 6.22483 17.026 6.22483C19.5005 6.22483 21.5064 8.21463 21.5064 10.6693C21.5059 13.124 19.5 15.1138 17.026 15.1138Z" fill="white" />
              <path d="M11.2035 0.00170898H10.9088H9.40878H6.98885H6.2729H2.24024H0.740175H0.445569C0.199408 0.00170898 0 0.197839 0 0.440348V0.735941V1.93452V2.23011C0 2.47206 0.199408 2.66875 0.445569 2.66875H2.15856H2.24024H2.2408H4.48048V11.8472V12.0528V13.0458C4.48048 13.0463 4.48048 13.0469 4.48048 13.0469V13.3414C4.48048 13.5833 4.67989 13.78 4.92605 13.78H6.63904H6.72072C6.96688 13.78 7.16629 13.5839 7.16629 13.3414V13.0938C7.16742 13.0776 7.16854 13.062 7.16854 13.0458V12.0651V12.0294V11.8472V2.66819H9.40822H9.40878H11.1218H11.2035C11.4496 2.66819 11.649 2.47206 11.649 2.22955V1.93396V0.735941V0.440348C11.649 0.197839 11.4496 0.00170898 11.2035 0.00170898Z" fill="white" />
            </svg>
          </a>
        </div>
        <ul className="cla-segments__list" aria-label="Audiencias">
          {topbarLinks.map((l) => (
            <li key={l.label}>
              <a href={l.href} className="cla-segments__item cla-segments__item--alt">
                {l.label}
              </a>
            </li>
          ))}
          {segments.map((s) => (
            <li key={s.label}>
              <a
                href={s.href}
                className={`cla-segments__item${s.active ? ' is-active' : ''}`}
              >
                {s.label}
              </a>
            </li>
          ))}
        </ul>
        <a
          className="cla-header__cta"
          href="https://miportal.cajalosandes.cl/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span className="material-symbols-outlined" aria-hidden>
            person
          </span>
          Mi Portal
        </a>
      </div>
    </header>
  );
}

function PrimaryNav({
  onOpenCredit,
  onOpenAgentInfo,
}: {
  onOpenCredit: () => void;
  onOpenAgentInfo: () => void;
}) {
  const [openIdx, setOpenIdx] = useState<number | null>(null);

  return (
    <nav className="cla-nav" aria-label="Navegación principal">
      <div className="cla-container cla-nav__inner">
        <ul className="cla-nav__list">
          {primaryNav.map((item, idx) => (
            <li
              key={item.label}
              className={`cla-nav__item${openIdx === idx ? ' is-open' : ''}${item.agent ? ' cla-nav__item--agent' : ''}`}
              onMouseEnter={() => item.submenu && setOpenIdx(idx)}
              onMouseLeave={() => setOpenIdx((cur) => (cur === idx ? null : cur))}
            >
              <a
                href={item.href}
                className={`cla-nav__link${idx === 0 ? ' is-active' : ''}`}
                aria-haspopup={item.submenu ? 'true' : undefined}
                aria-expanded={openIdx === idx}
                onClick={
                  item.agent === 'credit'
                    ? (e) => {
                        e.preventDefault();
                        onOpenCredit();
                      }
                    : undefined
                }
              >
                {item.label}
                {item.agent === 'credit' && (
                  <>
                    <span className="cla-nav__agent-badge" aria-label="Agente de IA — Nuevo">
                      <svg
                        className="cla-nav__agent-spark"
                        viewBox="0 0 24 24"
                        aria-hidden
                      >
                        <path d="M12 2 L13.5 9.2 L20.7 10.5 L13.5 11.8 L12 19 L10.5 11.8 L3.3 10.5 L10.5 9.2 Z" />
                      </svg>
                      <span className="cla-nav__agent-text">AGENTE</span>
                      <span className="cla-nav__agent-pip">NUEVO</span>
                    </span>
                    <button
                      type="button"
                      className="cla-nav__agent-info"
                      aria-label="Ver arquitectura del agente"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        onOpenAgentInfo();
                      }}
                    >
                      <span className="material-symbols-outlined" aria-hidden>
                        info
                      </span>
                    </button>
                  </>
                )}
                {item.submenu && (
                  <span className="material-symbols-outlined cla-nav__chev" aria-hidden>
                    expand_more
                  </span>
                )}
              </a>
              {item.submenu && openIdx === idx && (
                <div className="cla-nav__mega" role="menu">
                  <div className="cla-container cla-nav__mega-grid">
                    {item.banner && (
                      <div className="cla-nav__mega-banner">
                        <img src={item.banner.image} alt="" />
                        <p>{item.banner.paragraph}</p>
                        <a className="cla-nav__mega-banner-cta" href={item.href}>
                          Ver todo
                          <span className="material-symbols-outlined" aria-hidden>
                            arrow_forward
                          </span>
                        </a>
                      </div>
                    )}
                    <ul className="cla-nav__mega-list">
                      {item.submenu.map((sub) => (
                        <li key={sub.label}>
                          <a href={sub.href}>
                            {sub.label}
                            {sub.tag && (
                              <span className="cla-nav__mega-tag">{sub.tag}</span>
                            )}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
        {/* Elegant icon-trigger search anchored on the nav-right.
            Expands inline on focus — keeps the header silhouette clean. */}
        <div className="cla-nav__search">
          <SearchBar />
        </div>
      </div>
    </nav>
  );
}

/* Hero = full-width carousel slide ("ALIVIA HOY tus gastos financieros").
   The real site uses a Modyo <ds-banner-carousel/> auto-play widget; we
   replicate the visible slide structure 1:1, including the page indicator
   ("1/2") and prev/next arrows, but without auto-play.                   */
function Hero() {
  return (
    <section className="cla-hero" aria-label="Promociones destacadas">
      <div className="cla-container">
        <div className="cla-carousel">
          <button
            type="button"
            className="cla-carousel__arrow cla-carousel__arrow--prev"
            aria-label="Slide anterior"
          >
            <span className="material-symbols-outlined" aria-hidden>
              chevron_left
            </span>
          </button>

          <article className="cla-carousel__slide">
            <div className="cla-carousel__copy">
              <h1 className="cla-carousel__title">
                <span className="cla-carousel__title-strong">ALIVIA HOY</span>
                <span className="cla-carousel__title-soft">tus gastos financieros</span>
              </h1>
              <ul className="cla-carousel__badges" aria-label="Beneficios">
                <li>
                  <span className="material-symbols-outlined" aria-hidden>
                    check_circle
                  </span>
                  100% ONLINE
                </li>
                <li>
                  <span className="material-symbols-outlined" aria-hidden>
                    check_circle
                  </span>
                  RÁPIDO
                </li>
                <li>
                  <span className="material-symbols-outlined" aria-hidden>
                    check_circle
                  </span>
                  DCTO. POR PLANILLA
                </li>
              </ul>
              <a className="cla-btn cla-carousel__cta" href="#">
                Solicita tu crédito
                <span className="material-symbols-outlined" aria-hidden>
                  arrow_forward
                </span>
              </a>
            </div>
            <div className="cla-carousel__visual" aria-hidden>
              <img src="/images/generated/hero-familia.png" alt="" />
            </div>
          </article>

          <button
            type="button"
            className="cla-carousel__arrow cla-carousel__arrow--next"
            aria-label="Siguiente slide"
          >
            <span className="material-symbols-outlined" aria-hidden>
              chevron_right
            </span>
          </button>

          <span className="cla-carousel__counter" aria-hidden>
            1 / 2
          </span>
        </div>
      </div>
    </section>
  );
}

/* Quick-access tile row — six round icon tiles below the hero. */
function QuickTiles() {
  return (
    <section className="cla-quick" aria-label="Accesos rápidos">
      <div className="cla-container cla-quick__grid">
        {quickTiles.map((t) => (
          <a key={t.label} href={t.href} className="cla-quick__tile">
            <span className="cla-quick__icon" aria-hidden>
              <span className="material-symbols-outlined">{t.icon}</span>
            </span>
            <span className="cla-quick__label">{t.label}</span>
          </a>
        ))}
      </div>
    </section>
  );
}

function CrossServiceBanner() {
  return (
    <section className="cla-banner" aria-label="Pagos en exceso">
      <div className="cla-container">
        <div className="cla-banner__card">
          <div
            className="cla-banner__image"
            style={{ backgroundImage: 'url(/images/BEX-Desk.webp)' }}
            aria-hidden
          />
          <div className="cla-banner__copy">
            <h3>Revisa tus pagos en exceso</h3>
            <p>
              Consulta de forma rápida y fácil si tienes un pago en exceso en
              alguno de nuestros productos financieros y solicita tu reembolso.
            </p>
            <a className="cla-btn cla-btn--primary" href="#">
              Consultar ahora
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function CardsCopec() {
  return (
    <section className="cla-cards" aria-label="Productos destacados">
      <div className="cla-container cla-cards__grid">
        <article className="cla-card-info">
          <img className="cla-card-info__img" src="/images/tapp.webp" alt="" />
          <div className="cla-card-info__body">
            <h4>¡Abre tu cuenta Tapp!</h4>
            <p>Y toma las riendas de tus finanzas.</p>
            <a className="cla-btn cla-btn--primary cla-btn--fluid" href="https://www.tapp.cl/">
              Descarga Tapp
            </a>
          </div>
        </article>
        <article className="cla-card-info">
          <img className="cla-card-info__img" src="/images/dental.webp" alt="" />
          <div className="cla-card-info__body">
            <h4>Urgencia Dental con copago $100</h4>
            <p>
              Atiéndete de urgencia por dolor dental en Centros Médicos y
              Dentales RedSalud.
            </p>
            <a className="cla-btn cla-btn--primary cla-btn--fluid" href="#">
              Agenda tu hora
            </a>
          </div>
        </article>
      </div>
    </section>
  );
}

function Afiliacion() {
  return (
    <section className="cla-afiliacion" aria-label="Afiliación">
      <div className="cla-container cla-afiliacion__inner">
        <div className="cla-afiliacion__copy">
          <span className="cla-afiliacion__eyebrow">Hazte afiliado</span>
          <h2>Tu Caja, sin moverte de casa.</h2>
          <p>
            Solicita tu afiliación a Caja Los Andes 100% en línea y empieza a
            disfrutar beneficios, créditos sociales, salud, vivienda y
            recreación pensados para ti y tu familia.
          </p>
          <div className="cla-afiliacion__cta">
            <a
              className="cla-btn cla-btn--primary"
              href="https://miportal.cajalosandes.cl/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Ingresar a Sucursal Virtual
            </a>
            <a className="cla-btn cla-btn--secondary" href="#">
              Quiero afiliarme
            </a>
          </div>
        </div>
        <div className="cla-afiliacion__visual" aria-hidden>
          <img src="/caja_los_andes_mockup_image_1776471826515.png" alt="" />
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="ds-footer">
      <div className="cla-container">
        <div className="ds-footer__grid">
          {/* Sobre Caja */}
          <section className="ds-footer__brand">
            <div className="ds-footer__logos">
              <img src="/icon-footer-logo-ccla.svg" alt="" />
              <img src="/logo_cchs.svg" alt="Caja Los Andes" />
            </div>
            <h4>Sobre Caja Los Andes</h4>
            <p>
              Trabajamos en favor del bienestar social, entregamos herramientas
              para que las personas disfruten hoy la vida que sueñan.
            </p>
          </section>

          {/* Somos Andes + Reconocimientos */}
          <section className="ds-footer__col">
            <h4>Somos Andes</h4>
            <ul>
              {footerSomosAndes.map((l) => (
                <li key={l.label}>
                  <a href={l.href}>{l.label}</a>
                </li>
              ))}
            </ul>
            <h4 className="ds-footer__sub-title">Reconocimientos</h4>
            <ul className="ds-footer__sellos">
              {footerSellos.map((s) => (
                <li key={s.alt}>
                  <img src={s.src} alt={s.alt} />
                </li>
              ))}
            </ul>
          </section>

          {/* Contacto + Síguenos */}
          <section className="ds-footer__col">
            <h4>Contáctanos</h4>
            <ul>
              {footerContacto.map((l) => (
                <li key={l.label}>
                  <a href={l.href}>{l.label}</a>
                </li>
              ))}
            </ul>
            <h4 className="ds-footer__sub-title">Síguenos</h4>
            <ul className="ds-footer__social">
              {footerSocials.map((s) => (
                <li key={s.label}>
                  <a href={s.href} aria-label={s.label}>
                    <img src={s.icon} alt="" />
                  </a>
                </li>
              ))}
            </ul>
          </section>

          {/* Descarga app */}
          <section className="ds-footer__col">
            <h4>Descarga la App</h4>
            <ul className="ds-footer__stores">
              <li>
                <a
                  href="https://play.google.com/store/apps/details?id=cajalosandes.cla&hl=es"
                  className="ds-footer__store"
                >
                  <img src="/icons/icon-playstore.svg" alt="" />
                  <span>Google Play</span>
                </a>
              </li>
              <li>
                <a
                  href="https://itunes.apple.com/cl/app/app-caja-los-andes/id1233296359?mt=8"
                  className="ds-footer__store"
                >
                  <img src="/icons/icon-appstore.svg" alt="" />
                  <span>App Store</span>
                </a>
              </li>
            </ul>
          </section>
        </div>
      </div>

      <div className="ds-footer__suseso">
        Las Cajas de Compensación son fiscalizadas por la Superintendencia de
        Seguridad Social (www.suseso.cl)
      </div>
    </footer>
  );
}

function CookieBanner({ onClose }: { onClose: () => void }) {
  return (
    <div className="cla-cookies" role="dialog" aria-label="Aviso de cookies">
      <div className="cla-container cla-cookies__inner">
        <p>
          Usamos cookies propias y de terceros para mejorar tu experiencia y
          mostrarte contenido personalizado. Al continuar navegando aceptas su
          uso.
        </p>
        <div className="cla-cookies__buttons">
          <button
            className="cla-btn cla-btn--ghost cla-btn--sm"
            onClick={onClose}
            type="button"
          >
            Configurar
          </button>
          <button
            className="cla-btn cla-btn--primary cla-btn--sm"
            onClick={onClose}
            type="button"
          >
            Aceptar
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [showCookies, setShowCookies] = useState(true);
  const [creditOpen, setCreditOpen] = useState(false);
  const [archOpen, setArchOpen] = useState(false);
  /* Events from the credit agent — shared so the architecture pipeline
   * can animate in sync with the simulator's WebSocket. */
  const [creditEvents, setCreditEvents] = useState<CreditEvent[]>([]);

  return (
    <div className="cla-app">
      <TopUtilityBar />
      <MainHeader />
      <PrimaryNav
        onOpenCredit={() => setCreditOpen(true)}
        onOpenAgentInfo={() => setArchOpen(true)}
      />
      <main>
        <Hero />
        <QuickTiles />
        <HeroShowcase />
        <CrossServiceBanner />
        <CardsCopec />
        <Afiliacion />
        <DocumentAISection />
      </main>
      <Footer />
      {showCookies && <CookieBanner onClose={() => setShowCookies(false)} />}
      <AndesiaChat />
      <CreditSimulator
        open={creditOpen}
        onClose={() => setCreditOpen(false)}
        onOpenArchitecture={() => setArchOpen(true)}
        onEvents={setCreditEvents}
      />
      <CreditAgentArchitecture
        open={archOpen}
        onClose={() => setArchOpen(false)}
        events={creditEvents}
      />
    </div>
  );
}

export default App;
