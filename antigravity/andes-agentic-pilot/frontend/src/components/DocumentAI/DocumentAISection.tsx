import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type DragEvent,
} from 'react';
import {
  ALL_PROCESSED_DOCUMENTS,
  LIQUIDACION_PENSION_MARIA,
  LICENCIA_MEDICA_DIEGO,
  CEDULA_VALENTINA,
  type ProcessedDocument,
  type ExtractedEntity,
} from '../../mocks';
import DocumentAIInspector from './DocumentAIInspector';
import './DocumentAISection.css';

/* ---------------------------------------------------------------------------
 * DocumentAISection
 *   Drop-zone demo: user drops a document (or clicks one of three example
 *   chips) and watches Document AI extract entities (bbox overlays + scan
 *   line) → auto-fills the destination form field-by-field with a glowy
 *   "AI" badge marking each AI-sourced field.
 *
 *   Self-contained. Mount with `<DocumentAISection />` from outside.
 * -------------------------------------------------------------------------- */

type Stage = 'idle' | 'scanning' | 'boxes' | 'done';

interface ChipDef {
  id: string;
  label: string;
  emoji: string;
  doc: ProcessedDocument;
}

const CHIPS: ChipDef[] = [
  {
    id: 'liq',
    label: 'Probar con liquidación',
    emoji: 'description',
    doc: LIQUIDACION_PENSION_MARIA,
  },
  {
    id: 'lic',
    label: 'Probar con licencia médica',
    emoji: 'medical_services',
    doc: LICENCIA_MEDICA_DIEGO,
  },
  {
    id: 'ced',
    label: 'Probar con cédula',
    emoji: 'badge',
    doc: CEDULA_VALENTINA,
  },
];

/* Design space for the rendered "doc" — bbox coords from mocks fit comfortably
   inside a 600x792 page (US-letter @72dpi-ish). */
const DOC_W = 600;
const DOC_H = 792;

function confidenceClass(c: number): string {
  if (c >= 0.95) return 'docai-conf docai-conf--high';
  if (c >= 0.8) return 'docai-conf docai-conf--mid';
  return 'docai-conf docai-conf--low';
}

function formatValue(v: string | number): string {
  if (typeof v === 'number') {
    if (v >= 1000) return v.toLocaleString('es-CL');
    return String(v);
  }
  return v;
}

function formatCurrencyCLP(v: number): string {
  return `$ ${v.toLocaleString('es-CL')}`;
}

/* Build a friendly mock-document layout based on which doc the user picked. */
function MockDocPage({ doc }: { doc: ProcessedDocument }) {
  const isLiq = doc.id === 'doc-001';
  const isLic = doc.id === 'doc-002';
  const isCed = doc.id === 'doc-003';

  return (
    <div className="docai-doc__inner">
      {isLiq && (
        <>
          <div className="docai-doc__title">LIQUIDACIÓN DE PENSIÓN</div>
          <div className="docai-doc__subtitle">
            INSTITUTO DE PREVISIÓN SOCIAL · I.P.S.
          </div>
          <div className="docai-doc__divider" style={{ top: 80 }} />
          <div className="docai-doc__label" style={{ top: 100, left: 30 }}>
            RUT
          </div>
          <div className="docai-doc__field" style={{ top: 145, left: 120 }}>
            12.345.678-5
          </div>
          <div className="docai-doc__label" style={{ top: 130, left: 430 }}>
            Periodo
          </div>
          <div className="docai-doc__field" style={{ top: 145, left: 430 }}>
            MARZO 2026
          </div>
          <div className="docai-doc__label" style={{ top: 165, left: 30 }}>
            Nombre
          </div>
          <div className="docai-doc__field" style={{ top: 175, left: 120 }}>
            GONZALEZ PEREIRA MARIA CECILIA
          </div>
          <div className="docai-doc__label" style={{ top: 200, left: 30 }}>
            Pagador
          </div>
          <div className="docai-doc__field" style={{ top: 210, left: 120 }}>
            I.P.S. — INSTITUTO DE PREVISION SOCIAL
          </div>
          <div className="docai-doc__divider" style={{ top: 270 }} />
          <div className="docai-doc__label" style={{ top: 285, left: 30 }}>
            Detalle haberes / descuentos
          </div>
          <div className="docai-doc__field" style={{ top: 320, left: 30 }}>
            Pensión bruta
          </div>
          <div className="docai-doc__field" style={{ top: 320, left: 420 }}>
            $ 542.800
          </div>
          <div className="docai-doc__field" style={{ top: 345, left: 30 }}>
            Descuento salud (FONASA)
          </div>
          <div className="docai-doc__field" style={{ top: 345, left: 420 }}>
            $ 38.660
          </div>
          <div className="docai-doc__field" style={{ top: 370, left: 30 }}>
            Crédito Caja Los Andes
          </div>
          <div className="docai-doc__field" style={{ top: 370, left: 420 }}>
            $ 16.820
          </div>
          <div className="docai-doc__divider" style={{ top: 405 }} />
          <div
            className="docai-doc__field"
            style={{ top: 420, left: 30, fontWeight: 700 }}
          >
            LÍQUIDO A PAGAR
          </div>
          <div
            className="docai-doc__field"
            style={{
              top: 420,
              left: 420,
              fontWeight: 700,
              color: 'var(--cla-blue-dark)',
            }}
          >
            $ 487.320
          </div>
          <div className="docai-doc__label" style={{ top: 470, left: 30 }}>
            Banco depósito
          </div>
          <div className="docai-doc__field" style={{ top: 480, left: 120 }}>
            BANCO ESTADO CTA RUT
          </div>
          <div className="docai-doc__divider" style={{ top: 720 }} />
          <div
            className="docai-doc__field"
            style={{ top: 735, left: 30, fontSize: 9, color: '#6B7280' }}
          >
            Documento generado por IPS · Folio 220-548291 · No requiere firma manuscrita
          </div>
        </>
      )}

      {isLic && (
        <>
          <div className="docai-doc__title">LICENCIA MÉDICA ELECTRÓNICA</div>
          <div className="docai-doc__subtitle">
            COMPIN — SUSESO · LME 45-82-1934
          </div>
          <div className="docai-doc__divider" style={{ top: 80 }} />
          <div className="docai-doc__label" style={{ top: 90, left: 380 }}>
            N° LME
          </div>
          <div className="docai-doc__field" style={{ top: 90, left: 380 }}>
            LME-45821934
          </div>
          <div className="docai-doc__label" style={{ top: 150, left: 30 }}>
            RUT trabajador
          </div>
          <div className="docai-doc__field" style={{ top: 165, left: 130 }}>
            13.987.654-3
          </div>
          <div className="docai-doc__label" style={{ top: 185, left: 30 }}>
            Nombre
          </div>
          <div className="docai-doc__field" style={{ top: 195, left: 130 }}>
            RIQUELME BUSTAMANTE DIEGO ESTEBAN
          </div>
          <div className="docai-doc__divider" style={{ top: 240 }} />
          <div className="docai-doc__label" style={{ top: 255, left: 30 }}>
            Profesional emisor
          </div>
          <div className="docai-doc__field" style={{ top: 270, left: 130 }}>
            14.582.901-K
          </div>
          <div className="docai-doc__field" style={{ top: 295, left: 130 }}>
            DRA. CONSTANZA MOLINA TAPIA
          </div>
          <div className="docai-doc__field" style={{ top: 320, left: 130 }}>
            MEDICINA GENERAL
          </div>
          <div className="docai-doc__divider" style={{ top: 360 }} />
          <div className="docai-doc__label" style={{ top: 370, left: 30 }}>
            Reposo
          </div>
          <div className="docai-doc__field" style={{ top: 380, left: 130 }}>
            TIPO 1 — ENF/ACC COMUN
          </div>
          <div className="docai-doc__field" style={{ top: 410, left: 130 }}>
            14-04-2026
          </div>
          <div className="docai-doc__field" style={{ top: 410, left: 320 }}>
            7 (SIETE) DIAS
          </div>
          <div className="docai-doc__divider" style={{ top: 450 }} />
          <div className="docai-doc__label" style={{ top: 458, left: 30 }}>
            Diagnóstico
          </div>
          <div className="docai-doc__field" style={{ top: 465, left: 130 }}>
            J11.1 — INFLUENZA, OTRAS MANIFESTACIONES RESP.
          </div>
          <div className="docai-doc__divider" style={{ top: 690 }} />
          <div
            className="docai-doc__field"
            style={{ top: 705, left: 100, fontSize: 10, color: '#6B7280' }}
          >
            FIRMA ELECTRÓNICA AVANZADA — VALIDADA POR COMPIN-MR · 14-04-2026 08:09:12
          </div>
        </>
      )}

      {isCed && (
        <>
          <div className="docai-doc__title">CÉDULA DE IDENTIDAD</div>
          <div className="docai-doc__subtitle">
            REPÚBLICA DE CHILE — SERVICIO DE REGISTRO CIVIL
          </div>
          <div className="docai-doc__divider" style={{ top: 80 }} />
          {/* Photo placeholder */}
          <div
            style={{
              position: 'absolute',
              top: 130,
              left: 40,
              width: 180,
              height: 220,
              background:
                'linear-gradient(135deg, #DFE3E5 0%, #F6F7F7 100%)',
              border: '1px solid #C9D0D3',
              borderRadius: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#A8B3B7',
              fontSize: 10,
              letterSpacing: 1,
            }}
          >
            FOTO
          </div>
          <div className="docai-doc__label" style={{ top: 145, left: 250 }}>
            RUN
          </div>
          <div className="docai-doc__field" style={{ top: 165, left: 250 }}>
            21.567.890-4
          </div>
          <div className="docai-doc__label" style={{ top: 185, left: 250 }}>
            Nombres
          </div>
          <div className="docai-doc__field" style={{ top: 200, left: 250 }}>
            VALENTINA BELEN
          </div>
          <div className="docai-doc__label" style={{ top: 215, left: 250 }}>
            Apellidos
          </div>
          <div className="docai-doc__field" style={{ top: 230, left: 250 }}>
            AGUILERA TAPIA
          </div>
          <div className="docai-doc__label" style={{ top: 245, left: 250 }}>
            Nacimiento
          </div>
          <div className="docai-doc__field" style={{ top: 260, left: 250 }}>
            18 SEP 2006
          </div>
          <div className="docai-doc__label" style={{ top: 275, left: 250 }}>
            Nacionalidad
          </div>
          <div className="docai-doc__field" style={{ top: 290, left: 250 }}>
            CHILENA
          </div>
          <div className="docai-doc__divider" style={{ top: 380 }} />
          <div className="docai-doc__label" style={{ top: 395, left: 30 }}>
            (Reverso)
          </div>
          <div className="docai-doc__label" style={{ top: 410, left: 30 }}>
            Emisión
          </div>
          <div className="docai-doc__field" style={{ top: 425, left: 80 }}>
            03-11-2024
          </div>
          <div className="docai-doc__label" style={{ top: 410, left: 250 }}>
            Vencimiento
          </div>
          <div className="docai-doc__field" style={{ top: 425, left: 250 }}>
            03-11-2034
          </div>
          <div
            className="docai-doc__field"
            style={{ top: 720, left: 30, fontSize: 9, color: '#6B7280' }}
          >
            Documento de identidad oficial · MRZ verificado
          </div>
        </>
      )}
    </div>
  );
}

/* Renders the bounding boxes for the entities currently revealed. */
function BoundingBoxOverlay({
  entities,
  scaleX,
  scaleY,
}: {
  entities: ExtractedEntity[];
  scaleX: number;
  scaleY: number;
}) {
  return (
    <>
      {entities.map((e, i) => {
        const color = e.bbox.color ?? 'var(--cla-blue)';
        return (
          <div
            key={`${e.type}-${i}`}
            className="docai-bbox"
            style={
              {
                left: e.bbox.x * scaleX,
                top: e.bbox.y * scaleY,
                width: e.bbox.width * scaleX,
                height: e.bbox.height * scaleY,
                ['--bbox-color' as string]: color,
              } as React.CSSProperties
            }
          >
            <span
              className="docai-bbox__label"
              style={{ background: color }}
            >
              {e.display_label}
            </span>
          </div>
        );
      })}
    </>
  );
}

export default function DocumentAISection() {
  const [stage, setStage] = useState<Stage>('idle');
  const [activeDoc, setActiveDoc] = useState<ProcessedDocument | null>(null);
  const [revealedEntities, setRevealedEntities] = useState<number>(0);
  const [revealedFields, setRevealedFields] = useState<number>(0);
  const [hover, setHover] = useState(false);
  const [docScale, setDocScale] = useState(1);
  const dropRef = useRef<HTMLDivElement>(null);
  const docContainerRef = useRef<HTMLDivElement>(null);
  const timeoutsRef = useRef<number[]>([]);

  const clearTimers = useCallback(() => {
    timeoutsRef.current.forEach((t) => window.clearTimeout(t));
    timeoutsRef.current = [];
  }, []);

  /* Recompute scale so 600x792 doc fits inside its container nicely. */
  useEffect(() => {
    function recalc() {
      const el = docContainerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const sx = rect.width / DOC_W;
      const sy = rect.height / DOC_H;
      const s = Math.min(sx, sy);
      if (s > 0) setDocScale(s);
    }
    recalc();
    const ro = new ResizeObserver(recalc);
    if (docContainerRef.current) ro.observe(docContainerRef.current);
    window.addEventListener('resize', recalc);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', recalc);
    };
  }, [activeDoc, stage]);

  useEffect(() => {
    return () => clearTimers();
  }, [clearTimers]);

  const startProcessing = useCallback(
    (doc: ProcessedDocument) => {
      clearTimers();
      setActiveDoc(doc);
      setRevealedEntities(0);
      setRevealedFields(0);
      setStage('scanning');

      // Stage 2 — bounding boxes appear progressively (every ~180ms after 1s)
      const t1 = window.setTimeout(() => {
        setStage('boxes');
        const perBox = 180;
        for (let i = 0; i < doc.entities.length; i++) {
          const t = window.setTimeout(() => {
            setRevealedEntities(i + 1);
          }, i * perBox);
          timeoutsRef.current.push(t);
        }

        // Stage 3 — auto-fill form fields after all boxes (with stagger 150ms)
        const afterBoxes = doc.entities.length * perBox + 350;
        const t3 = window.setTimeout(() => {
          setStage('done');
          for (let j = 0; j < doc.autofill.length; j++) {
            const tj = window.setTimeout(() => {
              setRevealedFields(j + 1);
            }, j * 150);
            timeoutsRef.current.push(tj);
          }
        }, afterBoxes);
        timeoutsRef.current.push(t3);
      }, 1000);
      timeoutsRef.current.push(t1);
    },
    [clearTimers],
  );

  const reset = useCallback(() => {
    clearTimers();
    setStage('idle');
    setActiveDoc(null);
    setRevealedEntities(0);
    setRevealedFields(0);
  }, [clearTimers]);

  /* ---- DnD wiring (chips simulate same path) ----------------------------- */

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setHover(true);
  };
  const onDragLeave = () => setHover(false);
  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setHover(false);
    if (stage !== 'idle') return;
    // Real file ignored — we always pick the liquidación as the canonical demo.
    startProcessing(LIQUIDACION_PENSION_MARIA);
  };

  /* ---- Derived values for the right column ------------------------------- */

  const visibleEntities = useMemo(
    () => (activeDoc ? activeDoc.entities.slice(0, revealedEntities) : []),
    [activeDoc, revealedEntities],
  );

  const visibleFields = useMemo(
    () => (activeDoc ? activeDoc.autofill.slice(0, revealedFields) : []),
    [activeDoc, revealedFields],
  );

  const showRightContent = stage === 'done' || (stage === 'boxes' && revealedEntities > 0);

  return (
    <section className="docai-section" aria-labelledby="docai-title">
      <div className="docai-container">
        <header className="docai-header">
          <span className="docai-pill">
            <span className="docai-pill__dot" />
            Powered by Vertex AI Document AI
          </span>
          <h2 id="docai-title" className="docai-title">
            Sube tu documento — y olvídate del formulario
          </h2>
          <p className="docai-subtitle">
            Document AI extrae los datos en segundos. Tú solo confirmas.
          </p>
        </header>

        <div className="docai-grid">
          {/* ===== LEFT — Drop zone ===== */}
          <div
            ref={dropRef}
            className={[
              'docai-dropzone',
              hover ? 'docai-dropzone--hover' : '',
              stage !== 'idle' ? 'docai-dropzone--processing' : '',
            ]
              .filter(Boolean)
              .join(' ')}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            role="button"
            tabIndex={0}
            aria-label="Zona de carga de documentos"
          >
            {stage === 'idle' && (
              <div className="docai-dropzone__empty">
                <div className="docai-dropzone__icon" aria-hidden="true">
                  <span className="material-symbols-outlined">cloud_upload</span>
                </div>
                <div className="docai-dropzone__hint-title">
                  Arrastra tu liquidación, licencia o cédula aquí
                </div>
                <div className="docai-dropzone__hint-sub">
                  PDF o JPG · hasta 10 MB · procesado on-device en Chile (us-central1)
                </div>
                <div className="docai-dropzone__chips" role="group" aria-label="Ejemplos">
                  {CHIPS.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className="docai-chip"
                      onClick={() => startProcessing(c.doc)}
                    >
                      <span
                        className="material-symbols-outlined docai-chip__emoji"
                        aria-hidden="true"
                      >
                        {c.emoji}
                      </span>
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {stage !== 'idle' && activeDoc && (
              <>
                <div className="docai-doc-toolbar">
                  <button
                    type="button"
                    className="docai-toolbtn"
                    onClick={reset}
                  >
                    Probar otro
                  </button>
                </div>
                <div className="docai-doc-stage" ref={docContainerRef}>
                  <div
                    className="docai-doc"
                    style={{ width: DOC_W * docScale, height: DOC_H * docScale }}
                  >
                    <div
                      className="docai-doc__canvas"
                      style={{ transform: `scale(${docScale})` }}
                    >
                      <MockDocPage doc={activeDoc} />
                      {(stage === 'boxes' || stage === 'done') && (
                        <BoundingBoxOverlay
                          entities={visibleEntities}
                          scaleX={1}
                          scaleY={1}
                        />
                      )}
                    </div>

                    {stage === 'scanning' && (
                      <div className="docai-scan" aria-hidden="true">
                        <div className="docai-scan__glow" />
                        <div className="docai-scan__line" />
                      </div>
                    )}
                  </div>
                </div>

                <div className="docai-status">
                  <span
                    className={
                      stage === 'done'
                        ? 'docai-status__dot docai-status__dot--ok'
                        : 'docai-status__dot'
                    }
                  />
                  {stage === 'scanning' &&
                    `OCR + layout… ${activeDoc.processing.processor_display_name}`}
                  {stage === 'boxes' &&
                    `Extrayendo entidades · ${revealedEntities} / ${activeDoc.entities.length}`}
                  {stage === 'done' &&
                    `Listo · ${activeDoc.processing.total_entities_detected} entidades · ${(
                      activeDoc.processing.processing_time_ms / 1000
                    ).toFixed(2)} s`}
                </div>
              </>
            )}
          </div>

          {/* ===== RIGHT — Results ===== */}
          <div className="docai-results">
            {!showRightContent && (
              <div className="docai-results__placeholder">
                <span
                  className="material-symbols-outlined docai-results__placeholder-icon"
                  aria-hidden="true"
                >
                  arrow_back
                </span>
                <div className="docai-results__placeholder-text">
                  Aquí aparecerán los datos extraídos →
                </div>
              </div>
            )}

            {showRightContent && activeDoc && (
              <>
                <div className="docai-results__header">
                  <div>
                    <h3 className="docai-results__heading">Datos extraídos</h3>
                    <div className="docai-results__filename">
                      {activeDoc.metadata.filename}
                    </div>
                  </div>
                  <span className="docai-results__meta">
                    <span
                      className="material-symbols-outlined"
                      aria-hidden="true"
                      style={{ fontSize: 14 }}
                    >
                      check_circle
                    </span>
                    confianza {(activeDoc.processing.avg_confidence * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="docai-table" aria-live="polite">
                  <div className="docai-table__head">
                    <div>Campo</div>
                    <div>Valor</div>
                    <div>Conf.</div>
                  </div>
                  {visibleEntities.map((e, i) => (
                    <div className="docai-table__row" key={`${e.type}-row-${i}`}>
                      <div className="docai-table__label">{e.display_label}</div>
                      <div className="docai-table__value">
                        {typeof e.value === 'number' &&
                        e.type.toLowerCase().includes('clp')
                          ? formatCurrencyCLP(e.value)
                          : formatValue(e.value)}
                      </div>
                      <div>
                        <span className={confidenceClass(e.confidence)}>
                          {Math.round(e.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {stage === 'done' && (
                  <>
                    <div className="docai-form-card">
                      <div className="docai-form-card__title">
                        <span
                          className="material-symbols-outlined"
                          aria-hidden="true"
                          style={{ fontSize: 18 }}
                        >
                          auto_awesome
                        </span>
                        Solicitud auto-completada
                        <span className="docai-form-card__sub">
                          · {activeDoc.destino_formulario}
                        </span>
                      </div>
                      <div className="docai-form-grid">
                        {visibleFields.map((f, i) => (
                          <div
                            className="docai-field"
                            key={`${f.campo_id}-${i}`}
                            style={{ animationDelay: `${i * 30}ms` }}
                          >
                            <label
                              className="docai-field__label"
                              htmlFor={`docai-${f.campo_id}-${i}`}
                            >
                              {f.campo_label}
                              <span className="docai-ai-badge" aria-label="Auto-completado por IA">
                                <span
                                  className="material-symbols-outlined"
                                  aria-hidden="true"
                                  style={{ fontSize: 10 }}
                                >
                                  auto_awesome
                                </span>
                                AI
                              </span>
                            </label>
                            <input
                              id={`docai-${f.campo_id}-${i}`}
                              className="docai-field__input"
                              defaultValue={
                                typeof f.valor === 'number' &&
                                f.campo_id.includes('liquid')
                                  ? formatCurrencyCLP(f.valor)
                                  : String(f.valor)
                              }
                              readOnly
                            />
                          </div>
                        ))}
                      </div>
                      {activeDoc.warnings.length > 0 && (
                        <div className="docai-warning">
                          <strong>Atención:</strong> {activeDoc.warnings[0]}
                        </div>
                      )}
                    </div>

                    <div className="docai-cta">
                      <button type="button" className="docai-btn-primary">
                        <span
                          className="material-symbols-outlined"
                          aria-hidden="true"
                          style={{ fontSize: 18 }}
                        >
                          send
                        </span>
                        Confirmar y enviar
                      </button>
                      <button type="button" className="docai-link-btn">
                        Editar campos
                      </button>
                    </div>

                    <DocumentAIInspector doc={activeDoc} />
                  </>
                )}
              </>
            )}
          </div>
        </div>
      </div>
      {/* Pre-load all docs into module graph (no-op runtime tree-shake guard) */}
      <span hidden aria-hidden="true">
        {ALL_PROCESSED_DOCUMENTS.length}
      </span>
    </section>
  );
}
