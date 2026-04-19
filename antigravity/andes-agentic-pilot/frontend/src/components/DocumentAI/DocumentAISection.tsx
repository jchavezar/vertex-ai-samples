import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
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

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? '';

/* Live extraction result returned by /api/extract (Gemini 3 Flash). */
interface LiveField {
  label: string;
  value: string;
  confidence: number;
  category?: string;
}
interface LiveExtraction {
  doc_type?: string;
  summary?: string;
  fields?: LiveField[];
  totals?: LiveField[];
  warnings?: string[];
}
interface LiveResponse {
  filename?: string;
  mime?: string;
  bytes?: number;
  elapsed_ms?: number;
  model?: string;
  extraction: LiveExtraction;
}

export default function DocumentAISection() {
  const [stage, setStage] = useState<Stage>('idle');
  const [activeDoc, setActiveDoc] = useState<ProcessedDocument | null>(null);
  const [revealedEntities, setRevealedEntities] = useState<number>(0);
  const [revealedFields, setRevealedFields] = useState<number>(0);
  const [hover, setHover] = useState(false);
  const [docScale, setDocScale] = useState(1);
  /* "Live" mode — user uploaded a real file, we render the actual bytes and
     send them to Gemini 3 Flash for extraction. Mutually exclusive with the
     chip-driven mock flow. */
  const [liveFile, setLiveFile] = useState<File | null>(null);
  const [livePreviewUrl, setLivePreviewUrl] = useState<string | null>(null);
  const [liveStage, setLiveStage] = useState<'idle' | 'extracting' | 'done' | 'error'>('idle');
  const [liveResponse, setLiveResponse] = useState<LiveResponse | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const [liveElapsed, setLiveElapsed] = useState<number>(0);
  const dropRef = useRef<HTMLDivElement>(null);
  const docContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const timeoutsRef = useRef<number[]>([]);
  const liveTickRef = useRef<number | null>(null);

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

  /* ---- LIVE upload path: real file → Gemini 3 Flash extraction ---------- */

  const stopLiveTick = useCallback(() => {
    if (liveTickRef.current !== null) {
      window.clearInterval(liveTickRef.current);
      liveTickRef.current = null;
    }
  }, []);

  const resetLive = useCallback(() => {
    stopLiveTick();
    setLiveResponse(null);
    setLiveError(null);
    setLiveStage('idle');
    setLiveElapsed(0);
    setLivePreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    setLiveFile(null);
  }, [stopLiveTick]);

  useEffect(() => {
    return () => {
      stopLiveTick();
      if (livePreviewUrl) URL.revokeObjectURL(livePreviewUrl);
    };
    // intentionally only on unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLiveUpload = useCallback(
    async (file: File) => {
      // Tear down any previous mock state — live mode owns the screen now.
      clearTimers();
      setStage('idle');
      setActiveDoc(null);
      // And reset live state cleanly.
      stopLiveTick();
      if (livePreviewUrl) URL.revokeObjectURL(livePreviewUrl);
      const url = URL.createObjectURL(file);
      setLiveFile(file);
      setLivePreviewUrl(url);
      setLiveResponse(null);
      setLiveError(null);
      setLiveStage('extracting');
      setLiveElapsed(0);

      const t0 = performance.now();
      liveTickRef.current = window.setInterval(() => {
        setLiveElapsed(Math.round(performance.now() - t0));
      }, 100);

      try {
        const fd = new FormData();
        fd.append('file', file);
        const resp = await fetch(`${API_BASE}/api/extract`, {
          method: 'POST',
          body: fd,
        });
        if (!resp.ok) {
          const body = await resp.text();
          throw new Error(`HTTP ${resp.status}: ${body.slice(0, 200)}`);
        }
        const data = (await resp.json()) as LiveResponse;
        stopLiveTick();
        setLiveElapsed(Math.round(performance.now() - t0));
        setLiveResponse(data);
        setLiveStage('done');
      } catch (err) {
        stopLiveTick();
        setLiveStage('error');
        setLiveError((err as Error).message);
      }
    },
    [clearTimers, livePreviewUrl, stopLiveTick],
  );

  /* ---- DnD + click-to-browse wiring -------------------------------------- */

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setHover(true);
  };
  const onDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };
  const onDragLeave = () => setHover(false);
  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setHover(false);
    const f = e.dataTransfer?.files?.[0];
    if (f) void handleLiveUpload(f);
  };

  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) void handleLiveUpload(f);
    // reset so re-selecting the same file fires onChange again
    e.target.value = '';
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
            Powered by Gemini 3 Flash · Vertex AI
          </span>
          <h2 id="docai-title" className="docai-title">
            Sube tu documento — y olvídate del formulario
          </h2>
          <p className="docai-subtitle">
            Gemini 3 Flash hace OCR + comprensión semántica en una sola llamada. Tú solo confirmas.
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
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            aria-label="Zona de carga de documentos"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,application/pdf"
              hidden
              onChange={onFileInputChange}
            />
            {/* LIVE preview — user uploaded a real file. Renders the actual
                bytes (image as <img>, PDF in an <object>) instead of a mock. */}
            {liveFile && livePreviewUrl && (
              <>
                <div className="docai-doc-toolbar">
                  <button
                    type="button"
                    className="docai-toolbtn docai-toolbtn--primary"
                    onClick={openFilePicker}
                  >
                    <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 16 }}>
                      upload_file
                    </span>
                    Cambiar archivo
                  </button>
                  <button
                    type="button"
                    className="docai-toolbtn"
                    onClick={resetLive}
                  >
                    Volver
                  </button>
                </div>
                <div className="docai-live-stage">
                  {liveFile.type.startsWith('image/') ? (
                    <img
                      src={livePreviewUrl}
                      alt={liveFile.name}
                      className="docai-live-image"
                    />
                  ) : (
                    <object
                      data={livePreviewUrl}
                      type={liveFile.type || 'application/pdf'}
                      className="docai-live-pdf"
                    >
                      <div className="docai-live-pdf__fallback">
                        <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 48 }}>
                          picture_as_pdf
                        </span>
                        <div>{liveFile.name}</div>
                        <div style={{ fontSize: 11, opacity: 0.7 }}>
                          {(liveFile.size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    </object>
                  )}
                  {liveStage === 'extracting' && (
                    <div className="docai-scan" aria-hidden="true">
                      <div className="docai-scan__glow" />
                      <div className="docai-scan__line" />
                    </div>
                  )}
                </div>
                <div className="docai-status">
                  <span
                    className={
                      liveStage === 'done'
                        ? 'docai-status__dot docai-status__dot--ok'
                        : liveStage === 'error'
                        ? 'docai-status__dot docai-status__dot--err'
                        : 'docai-status__dot'
                    }
                  />
                  {liveStage === 'extracting' &&
                    `Gemini 3 Flash analizando ${liveFile.name} · ${(liveElapsed / 1000).toFixed(1)} s`}
                  {liveStage === 'done' && liveResponse &&
                    `Listo · ${liveResponse.extraction?.fields?.length ?? 0} campos · ${(
                      (liveResponse.elapsed_ms ?? liveElapsed) / 1000
                    ).toFixed(2)} s · ${liveResponse.model ?? 'gemini-3-flash'}`}
                  {liveStage === 'error' && `Error: ${liveError ?? 'desconocido'}`}
                </div>
              </>
            )}

            {!liveFile && stage === 'idle' && (
              <div className="docai-dropzone__empty">
                <div className="docai-dropzone__icon" aria-hidden="true">
                  <span className="material-symbols-outlined">cloud_upload</span>
                </div>
                <div className="docai-dropzone__hint-title">
                  Arrastra tu liquidación, licencia o cédula aquí
                </div>
                <div className="docai-dropzone__hint-sub">
                  PDF o JPG · hasta 10 MB · procesado por Gemini 3 Flash
                </div>
                <button
                  type="button"
                  className="docai-pickbtn"
                  onClick={openFilePicker}
                >
                  <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 18 }}>
                    upload_file
                  </span>
                  Seleccionar archivo
                </button>
                <div className="docai-dropzone__or">o prueba uno de los ejemplos</div>
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

            {!liveFile && stage !== 'idle' && activeDoc && (
              <>
                <div className="docai-doc-toolbar">
                  <button
                    type="button"
                    className="docai-toolbtn"
                    onClick={openFilePicker}
                  >
                    Subir otro
                  </button>
                  <button
                    type="button"
                    className="docai-toolbtn"
                    onClick={reset}
                  >
                    Volver
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
            {/* LIVE extraction results from Gemini 3 Flash */}
            {liveFile && (
              <>
                <div className="docai-results__header">
                  <div>
                    <h3 className="docai-results__heading">
                      {liveResponse?.extraction?.doc_type ?? 'Analizando documento…'}
                    </h3>
                    <div className="docai-results__filename">{liveFile.name}</div>
                  </div>
                  <span className="docai-results__meta">
                    <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 14 }}>
                      bolt
                    </span>
                    {liveResponse?.model ?? 'gemini-3-flash-preview'}
                  </span>
                </div>

                {liveStage === 'extracting' && (
                  <div className="docai-live-loading">
                    <div className="docai-live-spinner" aria-hidden />
                    <div>
                      <div className="docai-live-loading__title">Extrayendo con Gemini 3 Flash…</div>
                      <div className="docai-live-loading__sub">
                        OCR + comprensión semántica en una sola llamada · {(liveElapsed / 1000).toFixed(1)} s
                      </div>
                    </div>
                  </div>
                )}

                {liveStage === 'error' && (
                  <div className="docai-warning">
                    <strong>No se pudo extraer:</strong> {liveError ?? 'error desconocido'}
                  </div>
                )}

                {liveStage === 'done' && liveResponse && (
                  <>
                    {liveResponse.extraction?.summary && (
                      <p className="docai-live-summary">{liveResponse.extraction.summary}</p>
                    )}

                    {liveResponse.extraction?.fields && liveResponse.extraction.fields.length > 0 && (
                      <div className="docai-table" aria-live="polite">
                        <div className="docai-table__head">
                          <div>Campo</div>
                          <div>Valor</div>
                          <div>Conf.</div>
                        </div>
                        {liveResponse.extraction.fields.map((f, i) => (
                          <div className="docai-table__row" key={`live-${i}`}>
                            <div className="docai-table__label">{f.label}</div>
                            <div className="docai-table__value">{f.value}</div>
                            <div>
                              <span className={confidenceClass(f.confidence ?? 0.9)}>
                                {Math.round((f.confidence ?? 0.9) * 100)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {liveResponse.extraction?.totals && liveResponse.extraction.totals.length > 0 && (
                      <div className="docai-totals">
                        <div className="docai-totals__title">Totales detectados</div>
                        {liveResponse.extraction.totals.map((t, i) => (
                          <div className="docai-totals__row" key={`tot-${i}`}>
                            <span className="docai-totals__label">{t.label}</span>
                            <span className="docai-totals__value">{t.value}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {liveResponse.extraction?.warnings && liveResponse.extraction.warnings.length > 0 && (
                      <div className="docai-warning">
                        <strong>Atención:</strong> {liveResponse.extraction.warnings.join(' · ')}
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {!liveFile && !showRightContent && (
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

            {!liveFile && showRightContent && activeDoc && (
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
