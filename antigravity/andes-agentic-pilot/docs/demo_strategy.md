# Caja Los Andes — Vertex AI Agentic Demo Strategy

**Briefing date:** Monday 2026-04-20
**Build window:** Sunday 2026-04-19 (one day)
**Audience:** Non-technical executives at Caja Los Andes (Chilean caja de compensación)
**Repo:** `/home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/antigravity/andes-agentic-pilot/`

---

## 1. Executive summary

The recommendation is to demo **one persona, one journey, three hero capabilities** — not a feature dump. The persona is **María González, 58, pensionada de Caja Los Andes hace 22 años**, who arrives at the Sucursal Virtual wanting to consolidate two consumer debts into a single crédito social and check whether she qualifies for the Bono Bodas de Oro her late mother never claimed. This single journey naturally exercises (a) a **Concierge multi-agent router** (ADK + A2A) that hands off to specialist agents, (b) **Document AI + RAG grounded in Ley 18.833 and Caja Los Andes reglamentos**, and (c) the **Gemini Live API** for a Spanish voice turn at the end where María calls back to confirm. Every step is rendered in a right-side **"Agent Inspector" panel** that visualizes reasoning, tool calls, agent handoffs, and grounded citations — this is the explainability story executives will remember. The MVP is buildable in one day because the backend is a thin FastAPI streaming layer over **ADK 1.x with `gemini-3.1-pro-preview`** and the frontend already has the brand chrome in place. Stretch features (live voice, video avatar) are layered cleanly on top if Sunday goes well, but skipped without breaking the core narrative.

---

## 2. Capability survey (current as of April 2026)

| Capability | Current artifact (2026) | Why it matters for Caja Los Andes |
|---|---|---|
| **Vertex AI Agent Builder** | Umbrella product: ADK + Agent Engine + Conversational Agents + Agentspace, with Agent2Agent (A2A) protocol and 100+ enterprise connectors. [Overview](https://cloud.google.com/products/agent-builder) | The "platform story" slide. Frames the demo as enterprise-grade, not a chatbot. |
| **Agent Development Kit (ADK)** | Open-source, Python/TS/Go/Java. Primitives: `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`, `WorkflowAgent`. Tool calling (functions, OpenAPI, MCP). Callbacks for pre/post hooks. Streaming via Live API. [adk.dev](https://adk.dev/) | The actual code we ship Sunday. ~100 LoC for the multi-agent system. |
| **Gemini 3.1 Pro** | `gemini-3.1-pro-preview` (the `gemini-3-pro-preview` referenced in the current `main.py` was discontinued 2026-03-26 — must update). 1M token context, multimodal in (text/code/image/audio/video/PDF), `thinking_level: low\|high` parameter, multimodal function responses, streaming function calling. [Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro) | Powers reasoning. `thinking_level: high` for the reglamento interpretation step makes a great explainability moment. |
| **Live API** | `gemini-live-2.5-flash-native-audio` (GA). 24 languages including Spanish, voice activity detection, affective dialog, tool use, low-latency bidirectional audio. [Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api) | Spanish voice turn for the pensionado persona. Stretch goal — but a huge wow moment. |
| **Agent Engine** | Managed runtime. Sessions + Memory Bank (long-term, per-user, LLM-extracted). OpenTelemetry tracing, Cloud Trace, Eval service, secure code sandbox, IAM identity per agent. [Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) | Memory Bank is the *enterprise* proof point: "she logs in next month and the agent remembers." |
| **Vertex AI Search / RAG Engine** | Out-of-the-box RAG, vector + keyword hybrid, citations, connectors for Drive/Cloud Storage/Slack/Jira. [RAG Engine docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview) | Grounding on Ley 18.833 + Caja Los Andes reglamentos = compliance answer with citations. |
| **Document AI** | Spanish-supported processors: Invoice Parser (es), Expense Parser (es), Layout Parser (es), Form Parser (es), Custom Extractor (es, generative). Pay Slip Parser exists (English). [Processors list](https://docs.cloud.google.com/document-ai/docs/processors-list) | Custom Extractor on a liquidación de sueldo / finiquito → auto-prefill of crédito social application. |
| **Function calling / tools** | Native to Gemini + ADK. Supports OpenAPI specs and MCP servers. Streaming function calling in Gemini 3.1. | "Connect to Caja's existing core banking" story without writing a connector from scratch. |
| **A2A protocol** | Open protocol, 50+ partners (Box, Salesforce, ServiceNow, UiPath, Deloitte). Agents publish capability cards, negotiate text/form/audio/video. [a2a-protocol.org](https://a2a-protocol.org/) | Lets us claim "Concierge can hand off to a partner agent (e.g., a SURA insurance bot) without us rewriting either side." |
| **Evaluation / Observability** | Gen AI Evaluation service + Cloud Trace + Cloud Logging + Model Armor (runtime safety) + Security Command Center. | The "trust" slide. Show a trace screenshot at the end. |
| **Memory Bank** | Long-term per-user memory generated by `GenerateMemories` from session history. [Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) | The "she comes back next month" slide. |
| **Imagen / Veo** | Image / video generation. Lower priority for a B2C welfare context. | Skip unless time permits. A Veo-generated 10-second "presenter avatar" for the welcome screen is a possible flair. |

---

## 3. Use case mapping (capability → Caja Los Andes scenario)

| Capability | Scenario A (demo MVP) | Scenario B (talking point) | Scenario C (talking point) |
|---|---|---|---|
| Multi-agent (ADK + A2A) | **Concierge router** dispatches to specialists: `CreditoAgent`, `BeneficiosAgent`, `SaludAgent`, `PensionadosAgent` | A2A handoff to partner insurer (SURA) for cotización de seguro | Internal handoff to a `CumplimientoAgent` that vets the recommendation against Ley 18.833 |
| Gemini 3.1 Pro `thinking_level: high` | Reasoning over which crédito product fits María (consolidación vs. nuevo) | Risk-tier scoring for pre-approval | Eligibility logic for stacked beneficios |
| Live API (voice, ES) | María calls back, voice agent in Spanish confirms her application | Pensionado IVR replacement for crédito social inquiries | Empleador hotline for licencias médicas status |
| Vertex AI Search / RAG | Grounded answer on bono nupcialidad with citation to reglamento article | Q&A over circulares de la Superintendencia de Seguridad Social | Internal FAQ for sucursal staff |
| Document AI (Custom Extractor, es) | Upload of liquidación de sueldo → auto-fill of solicitud de crédito | Finiquito ingestion for fondo de cesantía claims | Cédula de identidad scan for KYC pre-fill |
| Memory Bank | Remembers María's debt-consolidation goal next visit | Remembers preferred sucursal and contact channel | Surfaces "you started an application 3 days ago, want to resume?" |
| Function calling / MCP | Mock tools: `getAfiliadoProfile`, `simulateCredito`, `checkBeneficiosElegibles`, `submitSolicitud` | MCP connector to a fake "Caja core banking" | OpenAPI spec for SAP HCM integration |
| Proactive nudge | After resolving debt, agent says "Detecté que calificas para Bono Bodas de Oro de tu madre" | Suggests turismo benefit before vacaciones | Reminds about pago automático crédito |
| Agent Engine Eval / Observability | Show OpenTelemetry trace of one full interaction at the end | Eval dashboard with hallucination/groundedness scores | Model Armor blocking a prompt injection demo |

---

## 4. Live demo storyline (5–8 min)

### Persona
**María González**, 58 años, pensionada de Caja Los Andes hace 22 años, reside en Maipú. Tiene un crédito de consumo en otro banco al 28% anual y una tarjeta de retail. Quiere consolidar. Su madre acaba de cumplir 50 años de matrimonio.

### Beat-by-beat (60–90 sec each)

**Beat 0 — Setup (15 sec).** Open the andes-agentic-pilot frontend. The Sucursal Virtual page looks like cajalosandes.cl. Bottom-right: a discreet "Asistente Virtual" launcher (replaces the current "Quantum Hub"). Click it. The Agent Inspector panel slides in from the right, taking ~40% of the screen.

> *Narration:* "Esto es lo que ven los afiliados. A la derecha, lo que normalmente queda oculto: el panel de inspección que les voy a mostrar a ustedes."

**Beat 1 — Concierge greets, identifies user, classifies intent (60 sec).** María (we) says: *"Hola, quiero ver si puedo juntar mis deudas en un solo crédito y también escuché algo de un bono para mi mamá."*

- Inspector shows: `ConciergeAgent` activated → tool call `getAfiliadoProfile(rut="...")` (animated pill) → result preview ("María González · Pensionada · 22 años de afiliación · segmento Plata") → reasoning trace bubble: *"Detecté dos intenciones: (1) consolidación de crédito, (2) consulta de beneficios para tercero. Voy a invocar dos especialistas en paralelo."*
- Two colored agent cards animate in: **CreditoAgent** (azul Caja) and **BeneficiosAgent** (amarillo Caja). Handoff arrows draw from Concierge to each.

> *Wow #1:* execs see two agents launched, *in parallel*, with their delegations explained in plain Spanish.
> *Explainability:* hover any pill, see the JSON. Hover any agent, see its system prompt + allowed tools.

**Beat 2 — CreditoAgent simulates and reasons (90 sec).** CreditoAgent calls `simulateCredito(monto=4500000, plazo=36)`, then `getDeudasExternas()` (mock CMF endpoint). It uses `thinking_level: high` — a "pensando…" indicator pulses for ~3 seconds while the thinking trace streams (collapsed by default; user clicks to expand). Output: a clean recommendation card *"Crédito Social Consolidación · CAE 18.9% · cuota $142.300 · ahorro mensual estimado $58.200"*.

> *Wow #2:* a real product card with a real number.
> *Explainability:* expand the thinking panel to show the chain: "1. Suma deudas externas $4.5M. 2. Compara CAE vigente. 3. Verifica capacidad de pago contra pensión declarada. 4. Aplica tope reglamentario 25× sueldo (no aplica, es pensionada — uso regla pensionados art. X)."

**Beat 3 — BeneficiosAgent grounds the answer in regulation (75 sec).** In parallel, BeneficiosAgent ran a RAG query over a corpus containing Ley 18.833 + Caja Los Andes reglamentos + circulares SUSESO. Returns: *"El Bono Bodas de Oro corresponde a afiliados con 50 años de matrimonio acreditados; tu madre, si fue afiliada, califica. Monto: $300.000."*

- Each sentence has a citation pill ([Reglamento Beneficios Art. 24](#)). Click → side drawer shows the actual paragraph highlighted.

> *Wow #3:* "Esto no es ChatGPT inventando — está citando el reglamento real."
> *Explainability:* show the RAG retrieval — top 3 chunks with similarity scores, the exact prompt sent to Gemini, and the grounding instruction.

**Beat 4 — Document AI auto-fills the application (60 sec).** Concierge says: *"Para enviar la solicitud necesito tu última liquidación de pensión."* María drags-and-drops a PDF (we use a pre-loaded sample). Inspector shows: `DocumentAI.CustomExtractor(es)` running, then a structured JSON appears (RUT, monto pensión, AFP, descuentos), then the form on screen auto-populates field by field with a subtle highlight animation.

> *Wow #4:* "Cero tipeo. La IA leyó el PDF y llenó el formulario."
> *Explainability:* show the bounding boxes on the PDF (Document AI OCR overlay) — execs see the agent literally pointing at the numbers it extracted.

**Beat 5 — Memory + proactive nudge (45 sec).** Before submit, ConciergeAgent says: *"Antes de enviar — recuerdo que en marzo consultaste por turismo en Pucón. Tu nuevo flujo de caja te dejaría $58k libres al mes; ¿quieres que reserve el cupo de turismo bonificado?"* Inspector shows a `MemoryBank.retrieve(user="maria")` call with the prior session summary.

> *Wow #5:* the cross-session memory moment. Execs lean in.

**Beat 6 — Live API voice close (60 sec, STRETCH).** Click the mic. The hub flips to voice mode. Speak in Spanish: *"Confírmame que la cuota es bajo $150 mil."* Gemini Live answers in natural Spanish voice ~500 ms latency: *"Sí María, la cuota es $142.300, bajo tu límite."* Inspector shows the live transcription and the function call the voice agent made under the hood.

> *Wow #6:* same agent, now talking. Same tools, same memory.

**Beat 7 — Trust slide (30 sec).** One screenshot: Cloud Trace timeline of the whole interaction (every span, every tool call), and a one-line Eval score (groundedness 0.94, helpfulness 0.91). *"Cada conversación queda trazada y evaluada — esto es lo que ustedes pueden auditar."*

### Total time budget
| Beat | Time | Drop if running long? |
|---|---|---|
| 0 Setup | 0:15 | No |
| 1 Concierge + parallel handoff | 1:00 | No |
| 2 Crédito simulation | 1:30 | No |
| 3 RAG + citations | 1:15 | No |
| 4 Document AI | 1:00 | No |
| 5 Memory nudge | 0:45 | Optional |
| 6 Voice close | 1:00 | **Stretch — first to drop** |
| 7 Trust slide | 0:30 | No |
| **Total** | **~7:15** | |

---

## 5. UI patterns for explainability

The Agent Inspector panel is the demo's secret weapon. It is the right-hand 40% of the viewport, dark theme to contrast the Caja Los Andes light brand chrome. Reference inspirations: **Anthropic Console's tool-use viewer**, **Perplexity's citation pills**, **LangSmith's run tree**, **Claude artifacts' side panel**.

### 5.1 Reasoning panel (chain-of-thought)
- Collapsed by default as a single line: *"Razonando… (3.2s, thinking_level: high)"* with a thin pulsing bar.
- Click to expand: streamed thinking tokens render in a slightly faded monospace style, prefixed with a small lightbulb glyph.
- Inspiration: ChatGPT's "Show thinking" toggle, Claude's `<thinking>` rendering.

### 5.2 Tool call pills (animated)
- Each tool invocation appears as a horizontal pill: `[icon] toolName(args summary) → result chip`.
- States: `pending` (shimmer), `running` (spinner), `success` (green check), `error` (red).
- Click expands JSON in/out below the pill with syntax highlighting.
- Inspiration: Anthropic Console tool-use blocks; Vercel AI SDK demo pages.

### 5.3 Multi-agent handoff visualization
- Top of inspector shows a small **agent constellation**: nodes are agents, edges are handoffs. As an agent activates, its node pulses; as it hands off, an arrow animates between nodes.
- Each node colored by domain (azul = Crédito, amarillo = Beneficios, verde = Salud, gris = Concierge).
- Hover a node → tooltip with system prompt, model, allowed tools.
- Inspiration: LangGraph Studio's graph view, n8n's workflow canvas, A2A's Agent Card concept.

### 5.4 Grounding citations
- Inline `[1]` `[2]` superscripts in the chat message.
- Hover → tooltip with chunk preview + source filename.
- Click → opens right-edge drawer with the source PDF rendered and the cited paragraph highlighted.
- Inspiration: Perplexity, NotebookLM, Glean.

### 5.5 Memory display
- Persistent collapsible "🧠 Lo que sé de ti" widget at top of chat:
  - "Pensionada hace 22 años · Maipú · prefiere WhatsApp · interés activo: turismo Pucón (mar-2026)"
- Memories appear with a fade-in when retrieved during a turn.
- Inspiration: ChatGPT's Memory feature UI, Mem.ai sidebar.

### 5.6 Live voice mode
- Hub transforms: chat list fades to a single big animated waveform.
- Live transcription scrolls below (user in white, agent in azul).
- Tool calls still appear in inspector — same panel, same pills.
- Inspiration: OpenAI Realtime demo, Hume AI voice UI.

### 5.7 The "audit drawer" (trust)
- Bottom of inspector: "Ver traza completa" → opens an OpenTelemetry-style timeline (just an image is fine for the demo) showing every span. Sells observability without us needing to wire Cloud Trace by Sunday.

---

## 6. Build plan ranked (impact × effort × strategic fit)

Scale: 1 (low) – 5 (high). "Build" = items the user actually codes Sunday.

| # | Demo element | Impact | Effort | Fit | Build? |
|---|---|---|---|---|---|
| 1 | Agent Inspector panel (right-side, dark) | 5 | 3 | 5 | **MVP** |
| 2 | Concierge + 2 specialist agents (ADK, mocked tools) | 5 | 3 | 5 | **MVP** |
| 3 | Tool call pills with mocked latencies | 5 | 2 | 5 | **MVP** |
| 4 | Multi-agent constellation + handoff arrows | 5 | 3 | 5 | **MVP** |
| 5 | Streaming thinking trace from Gemini 3.1 Pro | 4 | 2 | 4 | **MVP** |
| 6 | RAG over 3-5 reglamento PDFs (use Vertex AI Search OR a local FAISS index — see open question) | 5 | 3 | 5 | **MVP** |
| 7 | Citation pills + source drawer | 5 | 2 | 5 | **MVP** |
| 8 | Document AI on a pre-canned liquidación PDF | 5 | 4 | 5 | **MVP (mock OK)** |
| 9 | Form auto-fill animation | 4 | 2 | 4 | **MVP** |
| 10 | Memory Bank widget (use a JSON file fixture, not the real service) | 4 | 1 | 4 | **MVP** |
| 11 | Trust slide (static screenshot of Cloud Trace + eval scores) | 4 | 1 | 5 | **MVP** |
| 12 | Live API voice turn in Spanish | 5 | 4 | 4 | **STRETCH** |
| 13 | Real Memory Bank wired to Agent Engine | 3 | 4 | 3 | **SKIP** |
| 14 | Real Vertex AI Search index (vs. local) | 3 | 4 | 4 | **STRETCH** |
| 15 | A2A handoff to a partner mock agent | 4 | 4 | 3 | **STRETCH** |
| 16 | Veo presenter avatar | 3 | 4 | 2 | **SKIP** |
| 17 | Model Armor / prompt injection block demo | 4 | 3 | 3 | **STRETCH (talking point only)** |
| 18 | Real OpenTelemetry export to Cloud Trace | 3 | 4 | 3 | **SKIP** |

---

## 7. MVP vs stretch scope

### MVP (must ship Sunday night)
1. **Backend (`backend/main.py`):**
   - Update model from discontinued `gemini-3-pro-preview` to `gemini-3.1-pro-preview`.
   - Implement ADK `LlmAgent`s: `concierge`, `credito_agent`, `beneficios_agent`. Use `WorkflowAgent` or simple `LlmAgent` with `transfer_to_agent` tool for the handoff.
   - Mock tools (Python functions, no external calls): `get_afiliado_profile`, `simulate_credito`, `get_deudas_externas`, `query_reglamentos` (returns hardcoded grounded chunks), `extract_liquidacion`, `submit_solicitud`.
   - Stream every step over Server-Sent Events (`/api/agent/stream`) with a strict event schema:
     ```
     event: agent_start  data: {"agent":"concierge"}
     event: thinking     data: {"text":"..."}
     event: tool_call    data: {"id":"t1","name":"...","args":{...}}
     event: tool_result  data: {"id":"t1","result":{...}}
     event: handoff      data: {"from":"concierge","to":"credito_agent"}
     event: message      data: {"text":"...","citations":[...]}
     event: done         data: {}
     ```
2. **Frontend:**
   - Replace "Quantum Hub" with a clean **"Asistente Virtual"** launcher matching Caja brand.
   - Build `<AgentInspector />` panel: agent constellation header, event stream rendered as cards (thinking, tool, handoff, message).
   - Build `<ToolPill />`, `<ThinkingBlock />`, `<CitationPill />`, `<HandoffArrow />`, `<MemoryWidget />`.
   - Pre-canned PDF preview component for the liquidación step (with fake bounding boxes drawn over the image).
   - Form auto-fill animation: a 5-field form that populates with stagger.
3. **Demo data:**
   - 3-5 Caja Los Andes reglamento snippets in JSON (Bono Bodas de Oro, Crédito Social, Pensionados, Turismo Bonificado, Bono Escolaridad).
   - One pre-canned liquidación PDF (or just an image).
   - One María persona JSON with debts, pension amount, segment.
4. **Run script:** `make demo` → starts backend on 8091, frontend on 5173, opens browser.
5. **Backup:** record a screen-capture of the full flow Sunday night as fallback if something breaks Monday morning.

### Stretch (Sunday afternoon, only if MVP done by 14:00)
1. **Live API voice turn (Beat 6).** Use `gemini-live-2.5-flash-native-audio` via WebSocket from the browser. Wire one tool (`get_simulacion`). Spanish voice.
2. **Real Vertex AI Search** instead of hardcoded JSON for the RAG step.
3. **A2A demo agent** — a tiny "SURA seguros" agent in a separate process, A2A-discovered, that returns an insurance quote.

### Skip for Monday (talking points, not built)
- Real Memory Bank (use fixture)
- Real Cloud Trace export (use screenshot)
- Veo / Imagen
- Model Armor (mention only)

---

## 8. Open questions for the user (confirm before Sunday 09:00)

1. **GCP project access:** Do we have working `gcloud auth` for a project with **Gemini 3.1 Pro preview** and **Live API** enabled? (vtxdemos? admin@altostrat?)
2. **Persona name:** Stick with **María González (pensionada, 58)** or pivot to a trabajador activo persona (debt consolidation reads better for trabajadores)?
3. **Stretch voice (Beat 6):** Yes/no? Adds 3-4 hours of build + 1 microphone-permission risk during the live demo. Recommend: **rehearse with it, but be ready to drop**.
4. **Reglamento corpus:** Can we get even 3-5 real PDFs (or marketing PDFs) from cajalosandes.cl to ground RAG? Otherwise we synthesize plausible content and label as illustrative.
5. **Liquidación sample:** OK to use a synthetic Chilean liquidación de pensión PDF? (Real one would have PII.)
6. **Demo language:** Pure Spanish, or Spanish UI with English narration to the room? (Affects agent system prompts.)
7. **Network:** Will the briefing room have reliable internet? If not, we need an offline-capable fallback (record video).
8. **Branding:** Confirm the right-side dark Inspector panel doesn't violate any visual guidance from the parallel frontend-fidelity workstream.
9. **Compliance disclaimer:** Should every product card carry a *"Simulación · no constituye oferta vinculante"* footer? (Recommend yes.)
10. **A2A partner agent (stretch):** Real partner relationship to namedrop (SURA, Consalud, BancoEstado), or generic "Partner Insurance Co."?

---

## Appendix — sources

- [Vertex AI Agent Builder](https://cloud.google.com/products/agent-builder)
- [ADK docs (adk.dev)](https://adk.dev/)
- [Live API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api)
- [Gemini 3 Pro](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro)
- [Agent Engine](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Memory Bank](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
- [RAG Engine](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- [Document AI processors](https://docs.cloud.google.com/document-ai/docs/processors-list)
- [A2A protocol](https://a2a-protocol.org/)
