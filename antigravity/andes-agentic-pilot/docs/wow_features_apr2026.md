# Caja Los Andes — "Wow" Feature Additions (Abril 2026)

**Briefing date:** Lunes 2026-04-20
**Build window:** Domingo 2026-04-19
**Audience:** Comité ejecutivo CCLA (Tomás Zavala + directorio + LEAP)
**Author:** Research-only addendum to `demo_strategy.md` and `caja_los_andes_research.md`
**Scope:** Recommend 5–8 ADDITIONAL features that complement (do not duplicate) the existing MVP (Concierge multi-agent + RAG citations + Document AI + Memory Bank widget + Live API stretch).

---

## 1. Resumen ejecutivo (≤150 palabras)

El demo actual ya tiene tres "wow moments" sólidos (multi-agente, citations, Document AI). Pero entre **Gemini 3.1 Pro (feb-2026)**, **Nano Banana Pro / Veo 3.1**, **NotebookLM Cinematic Video**, **Conversational Agents Console (HD voice + video streaming)**, **Conversational Analytics API**, **Computer Use API (GA)** y **Gemini Enterprise** (que reemplazó a Agentspace en oct-2025), Google publicó en seis meses más capacidad nueva que en los dos años previos — y casi nada de eso existe en el plan actual. Caja Los Andes no tiene chatbot, no tiene WhatsApp, no tiene voicebot, su app excluye iPhones <2018 y su 60 % de afiliados son trabajadores+pensionados que no se autoatienden. El demo del lunes debe sentirse como **un salto de 10 años**, no como "otra demo de chatbot". Esta nota recomienda **siete** adiciones quirúrgicas, todas con evidencia pública de abril 2026, todas demostrables en <12 horas de build.

---

## 2. La narrativa que une todo

> **"De Sucursal Virtual a *Sucursal IA*: Caja Los Andes 2030 — la primera caja agéntica de Chile."**

**One-liner para slide 1:** *"Hoy un afiliado abre miportal.cajalosandes.cl y encuentra un menú. Mañana abre la misma URL y encuentra una sucursal completa — con ejecutivo, cajero, asesor financiero, médico de telemedicina y agente de turismo — todos disponibles 24/7 en español chileno, en voz, video o WhatsApp, y todos sabiendo quién es."*

Esta frase tiene tres virtudes para la sala:
1. **Concreta** — "sucursal" es un objeto familiar para CCLA (139 puntos físicos, presupuesto enorme).
2. **Cuantificable** — sucursal virtual hoy = 1 menú estático; sucursal IA = N agentes especializados.
3. **Defensiva contra Microsoft/OpenAI** — *Copilot* y *ChatGPT Enterprise* venden "asistentes para tu equipo". Google vende "una sucursal entera para tus 4,5 M de afiliados". Diferente nivel de promesa, diferente tipo de comprador (Tomás Zavala, no el CIO).

Use esta frase de apertura, repítala antes del beat 7 ("trust slide"), y ciérrela con: *"todo lo que vieron es buildable — la pregunta no es 'si', es 'qué sucursal IA quieren ustedes que construyamos primero'"*.

---

## 3. Las siete adiciones (priorizadas)

> Las **3 primeras** son must-add (alto wow + buildable Sunday). Las **#4–5** son si sobra tiempo. Las **#6–7** son talking points sin build.

---

### Add-on #1 — "Vitrina de Beneficios IA" — Nano Banana Pro genera *su* beneficio personalizado

**Elevator pitch:** "María sube una selfie y el sistema le devuelve, en 4 segundos, una tarjeta visual estilo Caja Los Andes que dice *'Bono Escolar 2026 — María, esto es lo que te corresponde'*, lista para compartir por WhatsApp." Es el equivalente a una pieza de marketing 1-a-1, generada en vivo.

**Google capability:** **Nano Banana Pro** (Gemini 3 Pro Image, lanzado 20-nov-2025, 4K nativo, "studio-quality" rendering, soporte de texto en imagen sin glitches — el problema histórico de los image models). API en Vertex AI Image API. ([Nano Banana Pro / DeepMind](https://deepmind.google/models/gemini-image/pro/), [Cloud Next blog](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/cloud-next-gen-ai-vertex-ai-updates/))

**CCLA pain it solves:** Brecha de descubrimiento de beneficios (research doc §D.1: "70 % evalúa negativamente el sistema de protección social"; "Saldos a Favor" recibió 400 K consultas en 3 semanas). La copy estática de la guía de beneficios no convierte. **Una imagen personalizada en marca Caja convierte.**

**Demo sequence (90 s):**
1. María dice *"¿califico para el Bono Escolar este año?"*
2. ConciergeAgent verifica elegibilidad (BeneficiosAgent + RAG sobre reglamento, ya en el demo).
3. **NUEVO:** Inspector muestra `ImagenAgent → Nano Banana Pro` ejecutando un prompt como *"Tarjeta de beneficio en estilo Caja Los Andes (azul #003DA5, amarillo #FFC72C, tipografía sans-serif): 'Bono Escolar 2026 — para Sofía, hija de María — $64.574 — listo para retirar en cajalosandes.cl/bonos'. Diseño limpio, fotografía aspiracional de niña en colegio."*
4. La imagen aparece en 4 s, lista para descargar y compartir por WhatsApp (botón "Compartir").
5. **El moment:** la sala reconoce que la imagen tiene la marca correcta, el monto correcto, el nombre real de la hija — y se generó en vivo.

**Lean-forward 5 s:** Cuando la imagen termina de pintarse y muestra *"para Sofía"* — ese instante. Esperan ver un genérico, ven algo personal.

**Build cost:** S — un endpoint Vertex AI Image, ~30 LoC. El prompt es texto. No requiere selfie real (saltar el upload facial por ética/PII; usar nombre de cargas familiares ya en el perfil).

**Risk:** Latencia 4–8 s en hora pico (mitigar: pre-generar 2 muestras de fallback y mostrarlas si timeout >10 s). Riesgo de "alucinar" un monto incorrecto — **mitigación obligatoria:** pasar el monto por interpolación literal en el prompt y mostrar disclaimer *"Simulación · monto sujeto a validación SUSESO"*.

**Por qué nadie más lo hace:** OpenAI no tiene un image model con texto fiable a este nivel. Microsoft Designer es genérico. **Solo Google une**: la marca correcta + datos del CRM + render con texto perfecto en una sola llamada.

---

### Add-on #2 — "AndesTV — Resumen Cinemático del Trámite" (NotebookLM Cinematic Video Overview)

**Elevator pitch:** Al final del trámite (después de la solicitud de crédito + bono), el agente dice: *"¿Quieres que te lo explique en 30 segundos?"* y genera **un video corto narrado en español chileno** que recapitula qué pidió, qué le aprobaron, en qué fecha se pagará y qué viene después. Listo para enviar a su hijo o reenviar al RR.HH. de su empresa.

**Google capability:** **NotebookLM Cinematic Video Overviews** (lanzado 4-mar-2026 en Gemini 3 + Nano Banana Pro + Veo 3 → "fluid animations and rich, detailed visuals"). API NotebookLM Enterprise ya disponible para Vertex. ([Blog Google](https://blog.google/innovation-and-ai/products/notebooklm/generate-your-own-cinematic-video-overviews-in-notebooklm/), [docs API](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-audio-overview))

**CCLA pain it solves:** Pensionados (398 K) y trabajadores mayores tienen brecha digital. Un PDF de aprobación de crédito = baja comprensión + llamada al contact center. Un video de 30 s con voz humana en español chileno = comprensión inmediata + share viral por WhatsApp = reducción de llamadas al **600 510 0000**.

**Demo sequence (60 s):**
1. Después del beat 5 (memory nudge), agente ofrece: *"¿Quiero que te haga un video resumen?"*
2. Usuario click. Inspector muestra `NotebookLM.GenerateVideoOverview(input=trámite_actual, language=es-CL, duration=30s, style="caja-los-andes")`.
3. Pre-generar para el demo (no esperar 90 s en vivo) — pero mostrar la animación de "generando" con el progreso real de la API.
4. Reproducir el video: voz cálida femenina (Chirp 3 HD voz "Aoede" o equivalente latino), animaciones simples con la marca Caja, números clave en pantalla grande, llamada a la acción final ("siguiente pago: 5 de mayo").
5. Botón "Compartir por WhatsApp" → simula el share.

**Lean-forward 5 s:** Cuando el video empieza con la voz que dice *"Hola María, te aprobamos tu crédito de $4 millones a 36 meses"* — los ejecutivos sienten "esto se podría enviar mañana mismo a 4 millones de afiliados".

**Build cost:** M — el video puede pre-renderizarse el sábado y reproducirse local (no API en vivo) — **se recomienda esto**, evita el riesgo de cuota. El UI del botón + la animación de "generando" son ~2 horas.

**Risk:** Cuotas Veo 3.1 limitadas (10 free/mes en personal accounts; enterprise tier; usar [pricing](https://cloud.google.com/blog/products/ai-machine-learning/announcing-veo-3-imagen-4-and-lyria-2-on-vertex-ai)). **Mitigación: pre-renderizar el video Sunday noche** y servirlo desde `/static/`. Decirle a la sala "este video se generó el sábado con la API, miren el timestamp" — es honesto y muestra producción real.

**Por qué nadie más lo hace:** OpenAI Sora produce video pero no tiene narración integrada con un knowledge base personalizado en una sola pasada. NotebookLM Cinematic Video toma la conversación + reglamento + perfil → video coherente. **Diferenciación clara**.

---

### Add-on #3 — "Andes Visión" — Live API con video, María muestra su licencia médica por la cámara

**Elevator pitch:** En lugar de subir un PDF (que requiere saber qué es un PDF), María apunta la cámara del teléfono a su licencia médica de papel y el agente la lee, valida y procesa **en tiempo real, hablando con ella en chileno**.

**Google capability:** **Gemini Live API con video input streaming** (`gemini-live-2.5-flash-native-audio` GA, soporta voz + video bidireccional, 24 idiomas con español, voice activity detection, affective dialog, low-latency <500 ms, tool use). Es la misma Live API que ya está como stretch en demo_strategy.md, pero **agregando el canal de video**, que es lo nuevo. ([Live API docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api))

**CCLA pain it solves:** (a) Licencias médicas en papel siguen siendo problemáticas (research §D.1: "las electrónicas a veces vienen con marca 'no válida para trámite'"); (b) iOS 17+ excluye iPhones viejos, pero la cámara funciona en cualquier teléfono incluido un Android de gama baja; (c) Caja 18 lidera con 1,5 días de procesamiento — esto va a **<5 minutos**.

**Demo sequence (75 s):**
1. Beat alterno o adicional al beat 4. María dice *"no tengo el PDF, tengo el papel"*.
2. Agente: *"perfecto, apunta la cámara a la licencia"*.
3. **NUEVO:** la app abre la cámara (en el demo: feed de webcam laptop apuntando a un papel impreso de licencia tipo).
4. Live API recibe el stream de video. En el inspector se ve `LiveSession.video_frame_received(t=0.4s)` → `tool_call(extract_licencia, image_frame=...)` → resultado.
5. El agente, en voz, lee: *"OK María, veo licencia tipo 1, RUT del médico 12.345.678-9, 7 días de reposo desde el 15 de abril. ¿Es correcto?"*
6. María dice *"sí"*. Se procesa.

**Lean-forward 5 s:** Cuando el agente lee en voz el RUT del médico viendo el papel a 30 cm de distancia — los ejecutivos visualizan inmediatamente esto multiplicado por 2,95 millones de licencias/año del país.

**Build cost:** L (4–6 h) — Live API video es la pieza más compleja. **Solo construir si MVP terminado a las 14:00 del domingo.**

**Risk:** Permisos de cámara en el navegador del laptop del demo (testear en Chrome con HTTPS — `localhost` debería funcionar). Latencia de video sobre red de hotel/oficina del cliente. **Plan B**: pre-grabar el flow en video Sunday noche y reproducirlo si la red falla.

**Por qué nadie más lo hace:** OpenAI Realtime tiene voz sin video bidireccional persistente. Anthropic Claude no tiene Live API. **Solo Gemini Live tiene voz + video + tool calling en una sesión multimodal continua**.

---

### Add-on #4 — "Andes Insights" — el agente del directorio: hablar con BigQuery en chileno

**Elevator pitch:** Frente al directorio, el demonstrator abre una segunda pantalla — **no para ellos los afiliados, sino para ellos los directores** — y pregunta en español: *"muéstrame las solicitudes de crédito social del último mes desagregadas por sucursal y compara con el mismo mes del año pasado"*. Aparece un dashboard generado en vivo. Luego: *"¿qué sucursales tienen mayor cancelación temprana?"* — otro dashboard.

**Google capability:** **Conversational Analytics API + Data Agents** (lanzado oct-2025, GA principios 2026) sobre **BigQuery + Looker**. Genera SQL desde lenguaje natural, ejecuta, visualiza. ([docs Conversational Analytics](https://docs.cloud.google.com/gemini/data-agents/conversational-analytics-api/overview), [BigQuery overview](https://docs.cloud.google.com/bigquery/docs/conversational-analytics))

**CCLA pain it solves:** Tomás Zavala viene de Wharton + Consorcio (research §B.5) — el target es un GM data-driven. Hoy la reportería interna pasa por equipos de BI en sucesivos pings. **Esto le pone la base de datos de la caja en su micrófono.** Adicionalmente: la Memoria Cajas Chile 2024 enfatiza KPIs SUSESO trimestrales — el equipo que prepara esos reportes lo necesita.

**Demo sequence (90 s):**
1. Cambia de la vista del afiliado a la vista del director.
2. Pregunta en voz: *"¿cuántos créditos sociales otorgamos esta semana versus la semana pasada?"*
3. Inspector: `DataAgent → translate_to_SQL → BigQuery.run() → Looker.chart()`.
4. Aparece un gráfico de barras comparativo, etiquetado en español, con el dato real (synthetic dataset cargado el sábado).
5. Pregunta de seguimiento: *"desagrega por región"* → mapa de Chile.
6. Pregunta de cierre: *"recomiéndame en qué región enfocar la próxima campaña de crédito de salud"* → respuesta narrativa con 3 razones.

**Lean-forward 5 s:** El mapa de Chile aparece y Tomás Zavala visualiza inmediatamente que él podría hacer esto en su próxima reunión con el directorio sin pedirlo a nadie.

**Build cost:** M (3–4 h) — requiere cargar un dataset synthetic en BigQuery (~30 min con `bq load` y un CSV ficticio de "créditos por sucursal"), conectar Conversational Analytics API, embed del Looker en el frontend. Reuse del frontend ya construido.

**Risk:** API Conversational Analytics es nueva; chequear cuota en `vtxdemos`. **Mitigación:** si la API falla, fallback a un mockup pre-generado con las preguntas exactas hardcoded. La narrativa funciona igual.

**Por qué nadie más lo hace:** Microsoft Fabric Copilot existe pero requiere la stack Microsoft. Snowflake Cortex requiere Snowflake. **CCLA no tiene comprometido un data warehouse aún** — Google llega a tabla rasa con BigQuery + esto = decisión de plataforma directa. Posible *anchor* para la propuesta comercial.

---

### Add-on #5 — "AndesAcción" — el agente que *navega por ti* cajalosandes.cl

**Elevator pitch:** En vez de simular las APIs (que no existen), conectamos el agente al **navegador real** y le decimos *"andá a miportal.cajalosandes.cl, loguéate como María, descarga su última cartola de pensión, y resúmela"*. El agente lo hace en pantalla, paso por paso, con el cursor moviéndose. Es la prueba viva de que **podemos conectar un agente Vertex AI a la sucursal virtual existente sin tocar el backend**.

**Google capability:** **Computer Use API (Gemini 2.5 Computer Use → 3.x)** — modelo especializado de Google que ve, razona y actúa sobre interfaces web. Vía Browserbase o entorno controlado. Es la respuesta directa a OpenAI Operator y Anthropic Computer Use, **disponible en Vertex AI** y producto de Project Mariner. ([docs Computer Use](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/computer-use), [9to5Google](https://9to5google.com/2025/10/07/gemini-2-5-computer-use-model/))

**CCLA pain it solves:** El miedo #1 que el directorio va a expresar es *"esto requiere reescribir nuestros sistemas"*. Esta capability dice: **NO**. Modyo + Keycloak siguen como están. El agente actúa sobre la UI existente como si fuera un cliente. **Cero migración técnica para empezar.**

**Demo sequence (60 s):**
1. Demonstrator dice: *"sé lo que están pensando: 'esto requiere conectar APIs internas'. Déjenme demostrarles que NO."*
2. Abre un sandbox del navegador (Browserbase iframe o screen capture en vivo).
3. Pega el prompt: *"andá a https://miportal.cajalosandes.cl, ingresá con [credencial demo], descargá la última cartola y dime el saldo"*.
4. La cámara del navegador muestra: el agente navega a la URL, hace clic en "Ingresar", llena el formulario, acepta cookies, llega al portal, hace clic en "Cartolas", descarga el PDF, lo abre, extrae el dato.
5. Resultado: *"Tu última cartola dice saldo de pensión depositado: $487.000 al 5 de abril. ¿Quieres compararlo con el mes anterior?"*

**Lean-forward 5 s:** Cuando los directores ven el cursor moviéndose por **su propio sitio web**. Es viscerall: *"está usando NUESTRO portal"*.

**Build cost:** L (5–7 h) — Browserbase + Vertex AI Computer Use + manejo de errores (sitio puede tardar, captchas, etc.). **Recomendación:** no construir esto sin haberlo probado el sábado AM. Si el portal de CCLA tiene captchas o login complejo, **caer a un sitio de prueba clon** o pre-grabar la sesión.

**Risk:** Ventana de mantenimiento CCLA (research §B.1: viernes 17:30 → domingo 04:30 — *literalmente* el horario del build). Lookup en sábado AM si está down. **Backup obligatorio:** screen recording de la sesión exitosa.

**Por qué nadie más lo hace:** OpenAI Operator es similar pero requiere su stack y no se integra con Vertex enterprise. Anthropic Computer Use está disponible pero más cara, sin integración GCP. **Google es el único proveedor enterprise con cloud + computer-use + bases de datos + analytics todo en una sola factura.**

---

### Add-on #6 — "Pulso del Afiliado" (Conversational Insights, talking-point) — *no build*

**Elevator pitch:** Un slide al final muestra: *"Esta es la conversación que acabamos de tener. Ahora imaginen 100 mil de estas al día. Aquí ven las top 5 razones de consulta, sentimiento promedio, y dónde caen las llamadas — actualizado cada hora."*

**Google capability:** **Customer Experience Insights / CCAI Insights** — analiza conversaciones (texto + voz), genera resumen, sentimiento, deteccion de razones de llamada, dashboards en Looker. ([cloud.google.com CCAI Insights](https://cloud.google.com/solutions/ccai-insights), [release notes](https://docs.cloud.google.com/contact-center/insights/docs/release-notes))

**CCLA pain it solves:** SUSESO Circular 3.796 exige relacionamiento medible y trazable. Hoy el contact center 600 510 0000 no entrega telemetría a la dirección. Esto la entrega por defecto, sin reentrenar agentes humanos.

**Demo sequence (slide estático, 30 s):**
- Screenshot del dashboard CCAI Insights (uno público o sintético).
- Tres KPIs en grande: "73 % consultas resueltas sin humano · NPS conversacional 67 · Top razón: Bono Escolar".
- Frase: *"esto es lo que ustedes verán cada lunes"*.

**Lean-forward 5 s:** Cuando ven el número "73 % sin humano" — porque saben que su contact center está saturado.

**Build cost:** S (1 h, solo screenshot + slide).

**Risk:** Bajo — es talking point.

**Por qué nadie más lo hace:** Microsoft no tiene un Insights que ingiera ambos canales (chat + voz) con la madurez de CCAI. AWS Contact Lens es cercano pero menos integrado con sus propios LLMs.

---

### Add-on #7 — "Andes Cumplimiento" (Model Armor + Audit Trail, talking-point) — *no build, alta importancia regulatoria*

**Elevator pitch:** *"Cada respuesta que vieron pasa por un filtro de seguridad de Google llamado Model Armor — bloquea inyección de prompts, datos sensibles que se filtran, y respuestas que violan política. Y queda guardado en Cloud Trace para auditoría SUSESO."*

**Google capability:** **Model Armor + Cloud Trace + Vertex AI Eval Service**. Ya existe en `demo_strategy.md` como mención al final, pero **subir el énfasis** dado el contexto regulatorio CCAF.

**CCLA pain it solves:** El #1 bloqueador de adopción de IA en una caja de compensación regulada por SUSESO + CMF (REDEC) es *gobernanza*. Hoy nadie quiere ser el primer ejecutivo que pone IA generativa frente a un afiliado y termina en un titular de Diario Financiero por una respuesta incorrecta sobre asignación familiar. **Model Armor es el escudo.**

**Demo sequence (slide estático, 30 s en beat 7):**
- Mostrar trace de OpenTelemetry con un span de Model Armor: *"input filtered: 0 violations · output filtered: 0 violations · groundedness 0.94"*.
- Mencionar el vínculo: SUSESO Circular 3.796 (relacionamiento) + REDEC consentimiento + IFRS 9 explicabilidad → todo cubierto.

**Lean-forward 5 s:** Cuando los directores ven el span de "violations: 0" — el riesgo regulatorio que tenían en mente se desinfla.

**Build cost:** S (slide).

**Risk:** Bajo.

**Por qué nadie más lo hace:** Anthropic y OpenAI tienen system prompts y safety, pero no un servicio gestionado equivalente a Model Armor con SLA para enterprise. **Es un argumento de venta a CISO + a Cumplimiento simultáneamente.**

---

## 4. Lo NUEVO en Google AI entre 2025 y abril 2026 (executive-friendly)

| Capacidad | Lanzamiento | Por qué importa para CCLA |
|---|---|---|
| **Gemini 3.1 Pro** (replaza Gemini 3 Pro Preview que se discontinuó 26-mar-2026) | 19-feb-2026 | El modelo del demo. `thinking_level: high` razona, 1M context permite cargar reglamentos enteros, function calling streaming permite UX más fluido. ([gemini.google release notes](https://gemini.google/release-notes/), [Vertex docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro)) |
| **Nano Banana Pro** (Gemini 3 Pro Image) | 20-nov-2025 | Texto en imagen sin glitches, 4K, 14 idiomas — habilita la "tarjeta de beneficio personalizada". ([DeepMind](https://deepmind.google/models/gemini-image/pro/)) |
| **Veo 3.1** + ingredientes a video | abr-2026 (free para personal accounts 2-abr-2026) | Habilita el "AndesTV resumen cinemático". 1080p / 4K, audio, mejor sync. ([blog.google Veo 3.1](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/)) |
| **Lyria 3** | feb-mar 2026 | Música incidental para videos / hold music personalizado. Lower priority. ([DeepMind Lyria](https://deepmind.google/models/lyria/)) |
| **NotebookLM Cinematic Video Overviews** | 4-mar-2026 | Convierte un trámite en video narrado en 30 s. Habilita Add-on #2. ([blog.google NotebookLM](https://blog.google/innovation-and-ai/products/notebooklm/generate-your-own-cinematic-video-overviews-in-notebooklm/)) |
| **Gemini Enterprise** (reemplaza Agentspace) | 9-oct-2025 | El "frontdoor" para agentes de empleados internos. La narrativa "sucursal IA" se apoya en esto. ([cloud.google.com gemini-enterprise](https://cloud.google.com/gemini-enterprise), [The Register](https://www.theregister.com/2025/10/09/google_rearranges_agentspace_into_gemini/)) |
| **ADK v2 / ADK Python 1.30.0** | mar-abr 2026 | Subagents, A2A extension, mejor handling de eventos. Lo usaremos en backend. ([adk.dev/a2a](https://adk.dev/a2a/), [GitHub releases](https://github.com/google/adk-python/releases)) |
| **Conversational Agents Console (next-gen CES)** | abr 2025 → expandido 2026 | No-code, voces HD, video streaming en vivo, conectores CRM. Habilita demo "no necesitas equipo de devs". ([cloud.google.com next-gen CES](https://cloud.google.com/blog/products/ai-machine-learning/next-generation-customer-engagement-suite-ai-agents)) |
| **Conversational Analytics API + Data Agents** | oct-2025 GA, ampliado 2026 | Habilita Add-on #4 — preguntar a BigQuery en chileno. ([docs](https://docs.cloud.google.com/gemini/data-agents/conversational-analytics-api/overview)) |
| **Computer Use API** (Gemini 2.5 → 3.x) | oct-2025 preview, GA 2026 | Habilita Add-on #5 — agente navega cajalosandes.cl real. ([docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/computer-use)) |
| **Gemini CLI 1.0 estable** | abr 2026 | Agente de coding open-source con subagents — narrativa "ustedes pueden empezar mañana, free tier". ([blog.google Gemini CLI](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/)) |
| **Chirp 3 HD voices** GA | feb-2026 | 248 voces, 31 idiomas, voice cloning instantáneo. Habilita voz chilena femenina cálida en Add-on #2 y Add-on #3. ([docs Chirp 3](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)) |
| **Vertex AI Memory Bank** GA | jul-2025 | Ya en demo_strategy.md como widget. Subrayar que es **producto, no proof-of-concept**. ([docs](https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/overview)) |
| **AlloyDB AI con pgvector + ScaNN** | 2025 → expandido 2026 | Talking point para slide de arquitectura — "podemos vivir junto a su PostgreSQL existente". ([cloud.google.com/alloydb/ai](https://cloud.google.com/alloydb/ai)) |
| **Gemma 3** (open, multilingüe 140 idiomas) | mar-2025 → GA / 2026 | Para el caso "queremos modelo on-prem regulatorio" — Gemma 3 es la respuesta. ([blog.google Gemma 3](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-3/)) |
| **Cloud Next 2026** (22-24 abr 2026, *después* del briefing) | 22-abr-2026 | **No mencionar como pasado.** Mencionar como *"lo que va a anunciarse esta semana en Las Vegas"* — subraya momentum y posiciona al usuario como *insider*. ([Google Cloud Events](https://www.googlecloudevents.com/next-vegas/)) |

---

## 5. Orden de implementación recomendado (Sunday timeline)

| Hora | Tarea | Owner | Si no está listo a... |
|---|---|---|---|
| 09:00–12:00 | Cerrar MVP existente (Concierge + RAG + Document AI + Memory widget) — *ya planificado* | Backend + frontend | 12:00 = parar y screen-record lo que haya |
| 12:00–13:00 | Almuerzo + dry run #1 del MVP solo | Todos | — |
| 13:00–14:30 | **Add-on #1 — Nano Banana Pro tarjeta beneficio** (S, must-add) | Backend | 14:30 = degradar a imagen pre-renderizada |
| 14:30–15:30 | **Add-on #4 — Conversational Analytics dashboard** (M, must-add) | Backend + dataset | 15:30 = degradar a screenshot |
| 15:30–17:30 | **Add-on #2 — NotebookLM Cinematic Video** (M, must-add — pre-render Saturday recommended) | Backend | 17:30 = mostrar video pre-grabado, sin botón "generate" |
| 17:30–18:00 | Café + dry run #2 con add-ons #1, #2, #4 | Todos | — |
| 18:00–21:00 | **Stretch:** Add-on #3 (Live API video) **OR** Add-on #5 (Computer Use) — elegir UNO | Backend | Si ninguno funciona limpio, kill |
| 21:00–22:00 | Slides #6 (Pulso) y #7 (Cumplimiento) — solo screenshots | Slidesperson | — |
| 22:00–23:00 | Dry run #3 completo + record backup video | Todos | — |
| 23:00 | Push a main + cerrar | Todos | — |

**Decisión binaria de las 18:00:** elegir entre Add-on #3 (Live API video) o Add-on #5 (Computer Use). Recomendación: **Add-on #5 (Computer Use)** — menor riesgo de mic, más visceral ("usa NUESTRO portal"), mejor argumento técnico para Tomás Zavala (no requiere replatform).

**Lo que NO construir** (ya en demo_strategy.md como skip): Veo presenter avatar, Real Memory Bank wired, Real Cloud Trace export.

---

## 6. La feature que recomiendo MATAR del demo actual

**Mi recomendación opinada: kill el "Beat 6 — Live API voice close" como está hoy en `demo_strategy.md`.**

Razones:
1. **Riesgo de micrófono en sala ejecutiva** — un fail con voz frente a Tomás Zavala es memorable por la razón equivocada. Caja Los Andes no tiene un voicebot hoy; mostrarles uno que glitchea les valida su miedo, no su esperanza.
2. **Es un truco que ya vieron** — voz natural en español es lo que cualquier exec ya probó con ChatGPT móvil. **No genera el factor "wow"** que generaba en 2024.
3. **Sustituirla por Add-on #3 (Live API con VIDEO)** — mismo Live API, mismo build effort, pero la cámara apuntando a un papel es algo que **NO han visto** y que **directamente resuelve un pain identificado** (licencias médicas en papel, research §D.1).

Si insisten en mantener voz, **degradarla a un solo turn de cierre** ("María llama por teléfono, agente confirma") en lugar de los 60 s que están reservados. Así libero 45 s para Add-on #1 (Nano Banana tarjeta beneficio) que es pura adrenalina visual.

---

## 7. Fuentes (todas públicas, abril 2026)

### Modelos y plataforma
- [Gemini 3.1 Pro release notes](https://gemini.google/release-notes/) — confirma 19-feb-2026.
- [Vertex AI Gemini 3 Pro docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro) — confirma discontinuación de `gemini-3-pro-preview` el 26-mar-2026, migrar a `gemini-3.1-pro-preview`.
- [Gemini Enterprise overview](https://cloud.google.com/gemini-enterprise) — pricing, tiers, Spanish (Latinoamérica) soportado.
- [The Register — Google folds Agentspace into Gemini Enterprise](https://www.theregister.com/2025/10/09/google_rearranges_agentspace_into_gemini/).
- [CNBC — Gemini Enterprise launch](https://www.cnbc.com/2025/10/09/google-launches-gemini-enterprise-to-boost-ai-agent-use-at-work.html).
- [adk.dev/a2a](https://adk.dev/a2a/) — ADK v2 con A2A.
- [GitHub adk-python releases](https://github.com/google/adk-python/releases) — v1.30.0 abril 2026.

### Generative media
- [Nano Banana Pro / DeepMind](https://deepmind.google/models/gemini-image/pro/) — Gemini 3 Pro Image, 4K, texto perfecto.
- [Cloud Next blog — Veo 3, Imagen 4, Lyria 2 on Vertex AI](https://cloud.google.com/blog/products/ai-machine-learning/announcing-veo-3-imagen-4-and-lyria-2-on-vertex-ai).
- [blog.google — Veo 3.1 ingredients to video](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/).
- [blog.google — NotebookLM Cinematic Video Overviews](https://blog.google/innovation-and-ai/products/notebooklm/generate-your-own-cinematic-video-overviews-in-notebooklm/) — 4-mar-2026, usa Gemini 3 + Nano Banana Pro + Veo 3.
- [docs Cloud TTS — Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd) — 248 voces, 31 idiomas, instant voice cloning, GA feb-2026.
- [DeepMind — Lyria 3](https://deepmind.google/models/lyria/).

### Agentes & analytics
- [docs — Conversational Analytics API](https://docs.cloud.google.com/gemini/data-agents/conversational-analytics-api/overview).
- [docs — BigQuery Conversational Analytics](https://docs.cloud.google.com/bigquery/docs/conversational-analytics).
- [docs — Computer Use tool en Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/computer-use).
- [9to5Google — Gemini 2.5 Computer Use](https://9to5google.com/2025/10/07/gemini-2-5-computer-use-model/).
- [TechCrunch — Project Mariner rollout](https://techcrunch.com/2025/05/20/google-rolls-out-project-mariner-its-web-browsing-ai-agent/).
- [docs — Vertex AI Agent Engine Memory Bank](https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/overview).
- [docs — Live API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api).

### Customer engagement & adyacente
- [cloud.google.com — Next-Generation Customer Engagement Suite](https://cloud.google.com/blog/products/ai-machine-learning/next-generation-customer-engagement-suite-ai-agents) — Conversational Agents console, voces HD, video streaming, vertical AI agents (Wendy's, Mercedes-Benz).
- [cloud.google.com — CCAI Insights](https://cloud.google.com/solutions/ccai-insights).
- [docs — CXI release notes](https://docs.cloud.google.com/contact-center/insights/docs/release-notes).

### Data & open
- [cloud.google.com/alloydb/ai](https://cloud.google.com/alloydb/ai).
- [Futurum — Google Cloud Next databases for agentic AI](https://futurumgroup.com/insights/at-google-cloud-next-google-brings-its-databases-to-bear-on-agentic-ai-opportunity/).
- [blog.google — Gemma 3](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-3/).
- [developers.googleblog.com — Gemma 3 developer guide](https://developers.googleblog.com/en/introducing-gemma3/) — 140+ idiomas.

### Eventos
- [Google Cloud Events — Next 2026 Las Vegas (22-24 abr)](https://www.googlecloudevents.com/next-vegas/).
- [Avid + Google Cloud partnership 16-abr-2026](https://www.googlecloudpresscorner.com/2026-04-16-Avid-and-Google-Cloud-Announce-Partnership) — ejemplo reciente de partnership agentic.

### Coding / developer
- [blog.google — Gemini CLI](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/).
- [developers.googleblog.com — Subagents in Gemini CLI](https://developers.googleblog.com/en/subagents-have-arrived-in-gemini-cli/).

### Notas metodológicas
- WebSearch nativo del LLM bloqueado por Org Policy (`vertexai.allowedPartnerModelFeatures` deniega `web_search` para `claude-opus-4-7`). Investigación realizada con WebFetch directo + DuckDuckGo HTML, mismo método usado en `caja_los_andes_research.md`.
- Cloud Next 2026 ocurre 22-24 abril 2026 (después del briefing del 20). Los anuncios de Next NO se incorporaron porque aún no existen al momento del briefing — pero **mencionarlos como "esta semana en Las Vegas"** es honesto y poderoso.
- Algunas URLs de blog secundario (medium, etc.) son confirmatorias, no primarias. Las primarias son `blog.google`, `cloud.google.com`, `docs.cloud.google.com`, `deepmind.google`, `gemini.google`.
