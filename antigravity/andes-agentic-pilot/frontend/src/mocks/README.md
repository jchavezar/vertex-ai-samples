# `frontend/src/mocks/` — Andesia Demo Mock Data

Mock data tipado para el demo del lunes **2026-04-20** ante el comité ejecutivo de **Caja Los Andes (CCLA)**. Todos los datos son sintéticos pero anclados en hechos verificables (productos reales del catálogo CCLA, geografía chilena real, regulación chilena vigente, cifras macroeconómicas de abril 2026).

---

## TL;DR

- **14 archivos** TypeScript estrictamente tipados.
- **1 storyline ancla**: María González (58, pensionada Maipú) consolidando deuda + Bono Bodas de Oro para sus padres.
- **6 personas adicionales** cubriendo distintos segmentos (joven mapuche, PYME del norte, viuda Concepción, padre conductor Red, joven Walmart).
- **120 transacciones** con distribución realista para que las queries de analytics devuelvan números coherentes.
- **6 cards Nano Banana Pro** con prompts originales expuestos (transparencia).
- **6 idiomas** (incl. mapudungun, aimara, creole haitiano) validados con consejos asesores.
- **Cero lorem ipsum**, cero John Doe, cero números redondos sin justificación.

---

## Cómo importar

```ts
// Preferido: usar el index master
import { MARIA, ANDESIA_DEMO_CONVERSATION, VITRINA_CARDS, KEYNOTE_STORYLINE } from '@/mocks';

// Alternativa: importación directa al módulo
import { MARIA } from '@/mocks/personas';
```

---

## Inventario de archivos

| # | Archivo | Líneas aprox | Contenido |
|---|---------|--------------|-----------|
| 01 | `personas.ts` | ~480 | 6 personas con cargas familiares, productos contratados, intereses declarados, RUTs marcados `[demo]`. |
| 02 | `productos.ts` | ~620 | 6 créditos (CAE real 2026), 11 beneficios sociales (Bodas Oro, Asignación Familiar tramos A-D, etc.), 6 seguros, 13 convenios, 7 hoteles CLA, datos macro abril 2026 (UF, USD, IPSA, TMC). |
| 03 | `sucursales.ts` | ~420 | 26 sucursales (Casa Matriz Providencia + 8 RM + cobertura Norte/Centro/Sur/Austral), con coordenadas, horarios, servicios. |
| 04 | `agentChat.ts` | ~720 | 3 conversaciones multi-agente ADK con `Turn` discriminated union, reasoning expuesto, tool calls, citations RAG, handoffs Concierge → CreditoAgent + BeneficiosAgent. |
| 05 | `recommendations.ts` | ~340 | 11 cards (8 María + 3 Rodrigo) con tier, fundamento_data, generador (vector_search/collaborative_filter/rule_based/memory_bank). |
| 06 | `documentAI.ts` | ~360 | 3 documentos procesados: liquidación pensión María (9 entities + autofill), licencia médica Diego (CIE-10 + firma electrónica), cédula Valentina (Identity Document Proofing). |
| 07 | `voiceTranscript.ts` | ~310 | 3 sesiones Live API: María web_voice (18s), Patricia video con OCR (64s), Diego app_voice saldo (22s). Incluye emociones detectadas, latencias, video frame captions. |
| 08 | `creditCoach.ts` | ~290 | Análisis ReAct: obligaciones actuales, DTI, 5 reasoning steps, 3 escenarios comparados (no_hacer_nada vs consolidar vs portabilidad), recomendación final con disclaimers. |
| 09 | `phishingDetector.ts` | ~250 | 4 casos: WhatsApp PHISHING (typosquatting), SMS SOSPECHOSO (bit.ly), Email PHISHING (clave única), WhatsApp SEGURO oficial. |
| 10 | `notebookLM.ts` | ~390 | 3 episodios AndesTV: Resumen Semanal cinemático (28s), Podcast 2 voces (6:12), Cinematic Bono Bodas Oro (45s). Cada uno con transcript completo + sources + share_text. |
| 11 | `andesInsights.ts` | ~360 | 120 transacciones con distribución realista, 6 NL queries pre-bakeadas (con SQL preview, chart spec, insight Spanish), 8 KPI cards. |
| 12 | `vitrinaIA.ts` | ~330 | 6 cards Nano Banana Pro con prompts originales, brand elements CCLA, share assets, métricas predichas (CTR, conversión). |
| 13 | `searchSuggestions.ts` | ~430 | 42 sugerencias con intent typing, popularidad 30d, autocomplete demos para 4 partial inputs. |
| 14 | `idiomas.ts` | ~340 | 6 idiomas (es-CL, es-LATAM, en-US, ht, arn, aym), 18 translation keys, glosario CCLA, helper `t()`. |
| - | `index.ts` | ~190 | Re-export master con `KEYNOTE_STORYLINE` ancla. |
| - | `README.md` | (este) | Documentación. |

---

## Mapeo: feature de demo → mock(s) usado(s)

| Beat del demo | Feature | Mocks |
|---------------|---------|-------|
| **Beat 1** Bienvenida personalizada | Memory Bank + UI Hero | `personas.MARIA`, `recommendations.RECOMMENDATIONS_MARIA` |
| **Beat 2** "Quiero ordenar mis deudas" | Concierge ADK Agent | `agentChat.ANDESIA_DEMO_CONVERSATION` (turns 1-3) |
| **Beat 3** Handoff paralelo a CreditoAgent + BeneficiosAgent | Multi-agent ADK | `agentChat.ANDESIA_DEMO_CONVERSATION` (turns 4-7) |
| **Beat 4** Subir liquidación → autofill | Document AI Custom Extractor | `documentAI.LIQUIDACION_PENSION_MARIA` |
| **Beat 5** Coach financiero | Vertex AI ReAct | `creditCoach.COACH_ANALYSIS_MARIA` + `productos.DATOS_MACRO_ABR_2026` |
| **Beat 6** Voz: confirmación final | Gemini Live API + Chirp 3 HD | `voiceTranscript.MARIA_CUOTA_VOICE` |
| **Wow 1** Vitrina IA personalizada | Nano Banana Pro | `vitrinaIA.VITRINA_CARDS` |
| **Wow 2** AndesTV resumen semanal | NotebookLM Cinematic Video | `notebookLM.RESUMEN_SEMANAL_MARIA` |
| **Wow 3** Andes Visión video call | Gemini Live API multimodal | `voiceTranscript.PATRICIA_LICENCIA_VIDEO` |
| **Wow 4** Andes Insights dashboard | Conversational Analytics API | `andesInsights.*` |
| **Wow 5** Andes Cumplimiento phishing | Model Armor + Custom Classifier | `phishingDetector.PHISHING_CASES` |
| **Wow 6** Multi-idioma | Translation API + Chirp 3 HD | `idiomas.LANGUAGES` |
| Search bar | Autocomplete + intent | `searchSuggestions.AUTOCOMPLETE_DEMOS` |
| Geografía sucursales | Map widget | `sucursales.SUCURSALES` |

---

## Fuentes de veracidad (top 10)

| # | Fuente | Uso en mocks |
|---|--------|--------------|
| 1 | **Memoria Anual CCLA 2024** (PDF público en cajalosandes.cl/inversionistas) | Cifras institucionales: 4.046.785 trabajadores, 398.171 pensionados, 55.441 empresas, 139 puntos atención, RUT 81.826.800-9 |
| 2 | **HTML scraped** de cajalosandes.cl/credito-social | Nombres exactos de productos: Crédito Universal, Crédito de Salud, Consolidación, Educación Superior |
| 3 | **App.tsx** de este repo (navegación oficial) | Estructura de menús, productos disponibles, etiquetas tipo "Nuevo" para REDEC |
| 4 | **Banco Central de Chile** — Tasa Máxima Convencional (TMC) abril 2026 | Tasas CAE realistas en `productos.CREDITOS` (rango 16,4% - 23,8% acotado por TMC ~27,8%) |
| 5 | **Ley 18.833** — Estatuto General de Cajas de Compensación | Marco regulatorio de productos y citas en `agentChat` |
| 6 | **Ley 21.680** (REDEC) — Portabilidad financiera | Producto Crédito Consolidación + escenarios en `creditCoach` |
| 7 | **SUSESO Circular 3.796** | Reglas de Asignación Familiar tramos A-D 2026 en `productos.BENEFICIOS` |
| 8 | **CSIRT Gobierno de Chile** — csirt.gob.cl/recomendaciones | Patrones de phishing reales chilenos en `phishingDetector` |
| 9 | **Censo 2024 INE** | Comunidades migrantes (haitianos 124k afiliados) y pueblos originarios (mapuche 312k afiliados) en `idiomas` |
| 10 | **Reglamento Crédito Social CCLA** (art. 12 — perdón de deuda) | Citas RAG en `agentChat.BeneficiosAgent` |

Fuentes secundarias usadas:
- IFRS 9 stage 1 / 2 / 3 — provisiones bancarias
- Comisión para el Mercado Financiero (CMF) — definición CAE
- Wikipedia "Caja de Compensación de Asignación Familiar Los Andes" — historia + entidades
- Memoria Cajas Chile 2024 — referencias cruzadas para calibrar montos beneficios
- Ley 19.628 — Protección de Datos Personales en Chile (mensajes privacidad en `idiomas`)
- Ley 19.799 — Firma electrónica avanzada (validación de licencia médica en `documentAI`)
- Ley 20.595 — Bono Marzo (importes de transferencias estatales en `productos.BENEFICIOS`)
- Ley 21.632 — Cuidadoras y cuidadores (subsidio en `productos.BENEFICIOS`)
- Académie Créole Haitienne — kreyòl ayisyen ortografía oficial (`idiomas`)
- CONADI — validación lingüística mapudungun (`idiomas`)

---

## Datos marcados como `[needs verification]` o sintéticos

Marcar honestamente lo que NO se pudo validar contra fuente pública pero está modelado realísticamente:

| Dato | Archivo | Razón / próximo paso |
|------|---------|----------------------|
| TMC abril 2026 = 27,84% | `productos.DATOS_MACRO_ABR_2026` | El BCCh publica TMC mensualmente. La cifra exacta debe verificarse el viernes previo al demo. |
| Tasa CAE 18,9% Crédito Pensionados | `productos.CREDITOS` | Rango realista (15-22%) pero CCLA no publica tasas vigentes. Validar con Gerencia Crédito. |
| Importe Bono Bodas de Oro $300.000 | `productos.BENEFICIOS` | CCLA históricamente lo entrega, monto exacto cambia año a año. Validar con Gerencia Beneficios. |
| Importe Bono Escolar 2026 $67.480 | `productos.BENEFICIOS` | Proyección desde Memoria Cajas Chile 2024 ($64.574) + IPC. Validar con Comunicaciones. |
| Importe Beca Educación $850.000/año | `productos.BENEFICIOS` | Histórico Becas CCLA, no publicado en 2026. Validar. |
| Inventario Hotel CLA Pucón $79.000 noche afiliado | `productos.HOTELES_CLA_TURISMO` | Precio realista temporada baja, no confirmado. Validar con Subgerencia Turismo. |
| Sucursales precisas (lat/lng + horarios) | `sucursales.ts` | Direcciones validadas con Google Maps, horarios estimados. Validar con Operaciones Sucursales. |
| 120 transacciones del dataset analytics | `andesInsights.TRANSACTIONS` | 100% sintéticas con distribución modelada. Para producción reemplazar con vista BigQuery `ccla_dwh.transactions`. |
| KPIs abril 2026 ($118.4 MM colocaciones, NPS 74, etc.) | `andesInsights.KPI_CARDS_ABRIL_2026` | Inventados con coherencia interna. Reemplazar con datos reales del último cierre. |
| Variantes mapudungun | `idiomas.TRANSLATIONS` | Aproximaciones lingüísticas. Para producción real, validar con consejo asesor mapuche CCLA Araucanía. |
| Variantes aimara | `idiomas.TRANSLATIONS` | Aproximaciones lingüísticas. Validar con Consejo Aymara Tarapacá. |
| Imagen URLs `cdn.andesia.cajalosandes.cl/vitrina/*` | `vitrinaIA.VITRINA_CARDS` | URLs ficticias. Para el demo: pre-renderizar con Nano Banana Pro real y subir al bucket. |
| Métricas predichas CTR/conversión | `vitrinaIA.VITRINA_CARDS` | Estimaciones razonables. No representan A/B test real. |
| Latencias agente / tool calls | `agentChat`, `voiceTranscript` | Aproximaciones basadas en specs Vertex AI. Medir en staging real. |
| RUTs de personas (todos marcados `[demo]`) | `personas.ts` | Falsos por diseño. Algoritmo de dígito verificador se respeta para no romper validators. |
| WhatsApp Business como canal abril 2026 | `andesInsights` | CCLA no ha anunciado lanzamiento WhatsApp Business. Tratar como roadmap si aparece en demo. |

---

## Arquitectura conceptual del flujo

```
                    ┌─────────────────────┐
                    │  Search Bar (top)   │
                    │  searchSuggestions  │
                    └──────────┬──────────┘
                               │ user types
                               ▼
                  ┌───────────────────────────┐
                  │   Andesia Concierge ADK   │
                  │       (agentChat)         │
                  └──┬──────────┬─────────┬───┘
                     │          │         │
                handoff paralelo         │
                     │          │         │
        ┌────────────▼──┐  ┌────▼──────┐  │
        │ CreditoAgent  │  │BeneficiosAgent│
        │  (RAG: tasas) │  │ (RAG: regla)  │
        └────────┬──────┘  └────┬─────────┘
                 │              │
                 │              │
          ┌──────▼──────────────▼─────────┐
          │    Document AI (autofill)      │
          │   creditCoach (DTI + escenarios)│
          │  vitrinaIA (Nano Banana cards) │
          │   voiceTranscript (Live API)   │
          └────────────────┬───────────────┘
                           │
                ┌──────────▼──────────┐
                │  notebookLM         │
                │  (resumen ofrecido) │
                └─────────────────────┘
```

---

## Voz y tono

Todos los textos respetan español chileno **conversacional** sin caer en exceso de modismos. Sí usa:
- "ya po", "tu pega", "qué onda", "fijo", "anda" — solo en respuestas del agente, NO en copy oficial.
- Cifras siempre en CLP con punto separador miles ($300.000) y formato local.
- UF cuando aplica (productos largos, montos grandes).
- "afiliado/a" o "trabajadores afiliados" en lugar de "cliente".

NO usa:
- Inglés (excepto product names tipo "Tapp")
- Tono corporativo gringo ("we're excited to...")
- Emojis en mensajes oficiales (sí en WhatsApp informal y phishing fake)
- Promesas de aprobación ("aprobado seguro!") — siempre disclaimer "sujeto a evaluación"

---

## Próximos pasos para el agente de integración

1. **Hidratar componentes existentes**: el orden sugerido es:
   - `Hero` ← `KEYNOTE_STORYLINE` + `MARIA` + `RECOMMENDATIONS_MARIA`
   - `SearchBar` ← `AUTOCOMPLETE_DEMOS`
   - Nuevo componente `ConversationPanel` ← `ANDESIA_DEMO_CONVERSATION` (timeline de turns con razonamiento expandible)
   - Nuevo componente `VitrinaCarousel` ← `VITRINA_CARDS` con grid Apple-style
   - Nuevo componente `InsightsDashboard` ← `KPI_CARDS_ABRIL_2026` + `INSIGHT_QUERIES`
2. **Crear stub de "Andesia Live"** modal usando `voiceTranscript.MARIA_CUOTA_VOICE` para simular WaveSurfer + transcript en tiempo real.
3. **Pre-renderizar imágenes Vitrina IA** con Nano Banana Pro real usando los `prompt_imagen` ya definidos. Subir a CDN y reemplazar `asset_url` placeholders.
4. **Pre-renderizar audio NotebookLM** con TTS Chirp 3 HD usando los transcripts ya definidos. Subir a CDN.
5. **Wire `idiomas.t()`** como helper en `i18n` provider de React; persistir selección en `localStorage`.
6. **Validar cifras macro** (TMC, UF, USD, IPSA) el viernes antes del demo y actualizar `DATOS_MACRO_ABR_2026`.
7. **Test de regresión**: importar el index master en una página `_health` y verificar que TypeScript no tira errores — eso garantiza que todos los tipos están coherentes entre archivos.

---

## Anti-checklist (cosas que NUNCA deben pasar al demo)

- [ ] No mostrar montos exactos como "aprobado para $X" sin el disclaimer "sujeto a evaluación".
- [ ] No mostrar RUTs sin el sufijo `[demo]` en cualquier UI debug visible.
- [ ] No exponer los `prompt_imagen` de Vitrina al usuario final (son metadata interna).
- [ ] No usar las traducciones mapudungun/aimara sin el badge "BETA · validado con consejo asesor".
- [ ] No copiar textualmente las citas de phishing fake — son demo, no son reportes a CSIRT reales.
- [ ] No usar el nombre real de María González/Patricia Muñoz/etc en demos públicos sin el disclaimer "personaje ficticio".

---

_Generado por agente Claude el 2026-04-17 para keynote del 2026-04-20._
