import { useState } from 'react';
import type { ProcessedDocument } from '../../mocks';

/* ---------------------------------------------------------------------------
 * DocumentAIInspector
 *   Collapsible "Ver cómo lo hizo IA" panel that exposes the underlying
 *   Document AI processor metadata, processing time, mock token cost and
 *   aggregate confidence — execs love seeing the cost/latency footprint.
 * -------------------------------------------------------------------------- */

interface Props {
  doc: ProcessedDocument;
}

/* Mock $/document cost — derived from page count + entity count.
   Assumes Document AI Form Parser ($0.05 / page first 1M) + Gemini 3 Pro
   multimodal verification (~0.0006 / 1k input tokens, ~3k tokens). */
function mockCostUsd(doc: ProcessedDocument): number {
  const formParser = 0.05 * doc.metadata.page_count;
  const geminiVerify = 0.0006 * 3 + 0.0024 * 0.4; // ~3k in, ~400 out
  // Scale down to look "production-tuned" for the demo
  const total = (formParser + geminiVerify) * 0.18;
  return Math.round(total * 1000) / 1000;
}

export default function DocumentAIInspector({ doc }: Props) {
  const [open, setOpen] = useState(false);

  const cost = mockCostUsd(doc);
  const latency = (doc.processing.processing_time_ms / 1000).toFixed(2);
  const isIdProofing = doc.processing.processor_id.includes('identity');
  const processorFamily = isIdProofing
    ? 'Identity Document Proofing'
    : doc.processing.processor_id.includes('liquidacion')
      ? 'Form Parser (Custom Extractor)'
      : 'Document OCR + Custom Extractor';

  return (
    <div className={`docai-inspector ${open ? 'docai-inspector--open' : ''}`}>
      <button
        type="button"
        className="docai-inspector__toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <span
            className="material-symbols-outlined"
            aria-hidden="true"
            style={{ fontSize: 18 }}
          >
            psychology
          </span>
          Ver cómo lo hizo IA
        </span>
        <span
          className="material-symbols-outlined docai-inspector__chev"
          aria-hidden="true"
        >
          expand_more
        </span>
      </button>

      {open && (
        <div className="docai-inspector__body">
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Procesador</span>
            <span className="docai-inspector__cell-value">
              {processorFamily}
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Verificación</span>
            <span className="docai-inspector__cell-value">
              Gemini 3 Pro multimodal
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Latencia</span>
            <span className="docai-inspector__cell-value">{latency} s</span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Costo / doc</span>
            <span className="docai-inspector__cell-value docai-inspector__cell-value--money">
              {cost.toFixed(3)} USD
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Confianza promedio</span>
            <span className="docai-inspector__cell-value">
              {(doc.processing.avg_confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Entidades</span>
            <span className="docai-inspector__cell-value">
              {doc.processing.total_entities_detected}
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Idioma</span>
            <span className="docai-inspector__cell-value">
              {doc.processing.language}
            </span>
          </div>
          <div className="docai-inspector__cell">
            <span className="docai-inspector__cell-label">Versión</span>
            <span className="docai-inspector__cell-value">
              {doc.processing.processor_version}
            </span>
          </div>
          <div className="docai-inspector__processor">
            {doc.processing.processor_id}
          </div>
        </div>
      )}
    </div>
  );
}
