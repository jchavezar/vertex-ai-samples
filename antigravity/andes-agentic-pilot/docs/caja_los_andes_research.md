# Caja Los Andes — Investigación Profunda para Briefing Ejecutivo

**Audiencia:** Ejecutivos de Caja de Compensación Los Andes (CCLA)
**Presentación:** Lunes 2026-04-20 — Google Cloud Vertex AI / Capacidades Agénticas
**Investigación realizada:** 2026-04-17 (sábado)
**Idioma de la audiencia:** Español (Chile)

---

## Resumen Ejecutivo (≤200 palabras)

Caja Los Andes (CCLA) es la **mayor caja de compensación de Chile**, con **4.046.785 trabajadores afiliados (59,8% del mercado), 398.171 pensionados, 55.441 empresas afiliadas (68,1% del mercado), 2.849 colaboradores y 139 puntos de atención**. En 2024 generó excedentes después de beneficios sociales por CLP 29.338 millones — y solo en el **1S25 ya igualó todos los excedentes de 2024 (CLP 58.991 MM, +207%)**, con NIM 17,8 % y rating **AA / Stable (Feller Rate, marzo 2025)**. Es el **#3 actor en créditos de consumo en Chile** (11,3 % de mercado, cartera bruta de **CLP 2,6 billones**), y su **tarjeta prepago Tapp superó 1,5 millones de clientes** con NPS líder y 4,9★ en App Store.

El **gerente general es Tomás Zavala Mujica** (Wharton MBA, ex Consorcio, asumió **4-nov-2024**); el equipo está en plena **diversificación de financiamiento internacional** (USD 100 MM con CAF junio 2025, USD 300 MM bonos sociales 144A/RegS) y empuja innovación abierta vía **LEAP (ex CLA Digital)** y el programa **TECLA Venture Client**. Su stack digital actual usa **Modyo (DXP), Keycloak SSO, Tapp como wallet/mini-banca móvil, y `mismetas.cajalosandes.cl` (SoyFocus) para inversiones**. **No tienen asistente conversacional público** — ni Gemini, ni Watson, ni Dialogflow, ni nada visible — lo cual constituye una **oportunidad blanca para Vertex AI agentic**: el ecosistema (4,4 M afiliados, 35 M+ transacciones de beneficios al año en la industria, 1,1 M de créditos sociales otorgados/año) es perfecto para *agents* multimodales y orquestación con Agent Builder.

---

## Tabla de Contenidos

- [Parte A — Quiénes son](#parte-a--quiénes-son)
- [Parte B — Estado actual de digital](#parte-b--estado-actual-de-digital)
- [Parte C — Contexto competitivo](#parte-c--contexto-competitivo)
- [Parte D — Pain points y oportunidades](#parte-d--pain-points-y-oportunidades)
- [Parte E — Features "WOW" para el demo](#parte-e--features-wow-para-el-demo)
- [Fuentes](#fuentes)

---

## Parte A — Quiénes son

### A.1 Identidad y misión

> **"Trabajamos en favor del bienestar social, entregamos herramientas para que las personas disfruten hoy la vida que sueñan."**
> — cajalosandes.cl, homepage

**Misión declarada (Earnings 2T25, p.20):**
> "Contribuir al desarrollo integral de sus afiliados y sus familias, promoviendo su bienestar de manera sostenible y mejorando su calidad de vida."

**Visión:**
> "Ser el referente líder en la creación de bienestar social en Chile."

**Estrategia:**
> "Ser reconocidos como pioneros en un nuevo modelo de seguridad social, enfocado en las personas y en ofrecer una experiencia de servicio excepcional."

### A.2 Historia

- Fundada en **1953** por la **Cámara Chilena de la Construcción (CChC)**, bajo el marco del **Decreto con Fuerza de Ley 245 / 1953** que creó el sistema de Cajas de Compensación de Asignación Familiar.
- En 2024 cumplió **70 años de operaciones** (Earnings 2T25, p.4).
- Pertenece al ecosistema CChC (que también controla AFP Habitat 27,26 %, Banco Internacional, Mutual de Seguridad, Red Salud, Confuturo, Vida Cámara, ILC).
- Mayo 2024: incorpora a la **Armada de Chile** (+23 mil beneficiarios). Junto al Ejército, Carabineros y PDI, ahora administra a las cuatro ramas FAOS.

### A.3 Marco legal

- Ley **18.833** — Estatuto General de las Cajas de Compensación de Asignación Familiar.
- Las CCAF son **instituciones privadas, sin fines de lucro, con patrimonio propio**, parte del sistema de protección social.
- Reguladas y fiscalizadas por la **Superintendencia de Seguridad Social (SUSESO)**.
- Funciones: administrar prestaciones sociales, pagar Asignaciones Familiares y Subsidio de Incapacidad Laboral por cuenta del Estado, otorgar **Crédito Social** y beneficios.
- 2025: la nueva **Reforma Previsional** habilita a las Cajas para asumir roles como **Administrador Previsional, Administrador de Fondos Previsionales o Administrador de Cuentas y Beneficios** — un *upside* regulatorio enorme.
- **REDEC (Ley 21.680)** — Registro de Deuda Consolidada CMF, semanal, exige consentimiento expreso del cliente. Caja Los Andes ya integra este flujo.

### A.4 Escala (cifras oficiales)

| Métrica | Valor | Fuente |
|---|---|---|
| **Trabajadores afiliados** | **4.046.785** (59,8 % del mercado CCAF) | Earnings 2T25 p.18 / Portal Empresas (4 M+) |
| **Pensionados afiliados** | **398.171** | Earnings 2T25 / Memoria Cajas Chile 2024 |
| **Empresas afiliadas** | **55.441** (68,1 % del mercado CCAF) | Earnings 2T25 p.18 |
| **Total afiliados (incl. pensionados)** | **4.465.373** (59,8 %) | Earnings 2T25 p.18 |
| **Tarjeta Tapp – clientes** | **1.507.840** (>1 M en nov-24) | Earnings 2T25 p.18 |
| **Colaboradores** | **2.849** (62 % mujeres, 43 % en liderazgo) | Memoria Cajas Chile 2024 |
| **Puntos de atención** | **139** (sucursales + puntos caja + oficinas móviles) | Earnings 2T25 p.18 |
| **Centros turísticos y recreacionales** | **17** (CLA Turismo: 18 hoteles/cabañas/parques) | Earnings 2T25; Memoria 2024 |
| **Reservas turismo 2024** | **48.000+** | Memoria Cajas Chile 2024 p.31 |
| **Beneficios sociales usados (personas)** | **3.117.544** en 2024 | Memoria Cajas Chile 2024 p.30 |
| **Créditos sociales otorgados 2024** | **1,1 millones** (CCLA) | Memoria Cajas Chile 2024 p.30 |
| **Cartera bruta créditos sociales** | **CLP 2.608.846 MM** (jun-25) | Earnings 2T25 p.10 |
| **Excedentes después de beneficios 1S25** | **CLP 58.991 MM** (= todo 2024) | Earnings 2T25 p.4 |
| **ROAA / ROAE / NIM / Eficiencia / CAR** | 3,1 % / 9,4 % / 17,8 % / 41,1 % / 40,7 % | Earnings 2T25 |
| **Rating Feller Rate** | **AA / Stable** (mar 2025; subió desde AA−) | Feller Rate 31-mar-2025 |

### A.5 Líneas de negocio

1. **Crédito Social** — eje de ingresos (88,4 % de los ingresos del 6M25).
   - Productos: Crédito Universal, Crédito de Salud, Crédito Consolidación de Deudas, Crédito Educación Superior. Simulador en línea.
   - Cartera diversificada por industria: Comercio 16,5 %, Pensionados 25,1 %, Sector Público 7,9 %, Construcción 6,8 %, etc.
2. **Beneficios sociales** — Asignación Familiar, SUF, subsidio cesantía, Bonos Profamilia (natalidad, escolaridad, nupcialidad, fallecimiento).
3. **Salud** — convenios farmacia, telemedicina, planes para pensionados, dental urgencia con copago $100 en RedSalud.
4. **Educación** — becas, Crédito Educación Superior, Caja Escolar Digital, Diplomados Comunidad Educativa, programa Siguecreciendo.
5. **Vivienda** — Ahorro Vivienda en plataforma Mis Metas/SoyFocus.
6. **Pensionados** — Plan Salud Pensionados, Recreación 50+, Centro Club, Universidad de la Experiencia, créditos especiales.
7. **Recreación / Turismo** — CLA Turismo (filial): 18 hoteles, cabañas y parques; convenios con JetSmart (25 %), FlixBus (20 %), Despegar (7 %), Amatista Travels.
8. **Tapp (filial Los Andes Tarjetas de Prepago S.A.)** — billetera digital, tarjeta prepago internacional sin comisión y 0 spread; #3 ranking prepago compras 2024 (CMF); +120 % YoY ventas; **NPS líder, 4,9★ App Store con 25.000+ valoraciones**; **crédito social digital de hasta 50 UF en 5 minutos**.
9. **Mis Metas / SoyFocus** — fondos mutuos, Ahorro Vivienda, APV, recomendación con tecnología "AI-driven" (sus palabras), reguladora CMF, 0,95 % comisión Serie B.
10. **Convenio Empresas (B2B)** — sucursal virtual empresas, integración PreVired, gestión de licencias, pago asignación, programas de bienestar, Fútbol 7×7 (>9.000 jugadores en 28 ciudades en 2024).

### A.6 Segmentos de cliente
- Trabajadores afiliados (4 M+).
- Pensionados (398 K).
- Empleadores / empresas (55 K+).
- Beneficiarios indirectos (cargas familiares).
- Ex-afiliados (portal dedicado).
- FAOS (Ejército, Armada, Carabineros, PDI).

### A.7 Canales

| Canal | Estado |
|---|---|
| **Sucursales físicas** | 139 puntos (sucursales + puntos caja + oficinas móviles) |
| **Sucursal virtual web** | `miportal.cajalosandes.cl` (Modyo + Keycloak SSO) |
| **App móvil "Caja Los Andes"** | Google Play `cajalosandes.cla`, **>1 M descargas, v6.2.1** |
| **App Tapp** | iOS / Android, 1,5 M clientes, 4,9★ |
| **Contact Center** | **600 510 0000** |
| **Portal pensionados** | `pensionados.cajalosandes.cl` |
| **Portal empresas** | `empresa.cajalosandes.cl` |
| **Mis Metas (SoyFocus)** | `mismetas.cajalosandes.cl` |
| **Redes sociales** | Instagram @cajalosandes, Facebook CajaLosAndesCL, X @CajaLosAndes, YouTube canalandes, LinkedIn cajalosandes |
| **WhatsApp** | **No publicado en sitio principal** — gap notable |
| **Chatbot / Asistente Virtual** | **No existe canal conversacional público** (verificación directa, abr 2026) |

---

## Parte B — Estado actual de digital

### B.1 Experiencia digital actual

- **Sitio público** (`cajalosandes.cl`) — informacional, con menú por audiencia. Maintenance window divulgado: viernes 17:30 → domingo 04:30 (operación legacy con ventana grande).
- **Portal autenticado** (`miportal.cajalosandes.cl`) usa **OIDC sobre Keycloak** (`sso.cajalosandes.cl/auth/realms/afiliados-ccla-prd`) con cliente `modyo-ccla` → portal sirvido por **Modyo DXP**.
- **App móvil** v6.2.1, iOS 17+ requerido (excluye iPhones más viejos — fricción).
- **Tapp** — la pieza más madura, mini-banca con onboarding mobile-first, crédito instantáneo 50 UF/5 min, gasto internacional.
- **Mis Metas / SoyFocus** — perfilamiento por cuestionario + recomendación de fondos ("tecnología AI-driven", según su propia copy) regulada por CMF.
- **CDN/Assets** servidos vía `cla.cdn.modyo.com` (Modyo).

### B.2 Stack y vendors identificados

| Capa | Vendor / Tecnología | Evidencia |
|---|---|---|
| **DXP / portal** | **Modyo** (Chile) | `client_id=modyo-ccla` en SSO; CDN `cla.cdn.modyo.com`; Caja Los Andes listada como cliente Modyo |
| **SSO / IAM** | **Keycloak** (realm `afiliados-ccla-prd`) | `sso.cajalosandes.cl/auth/realms/...` |
| **Wallet** | **Tapp** (filial CCLA, "Los Andes Tarjetas de Prepago S.A.") | Earnings 2T25 |
| **Inversiones** | **SoyFocus** (Mis Metas, regulada CMF) | mismetas.cajalosandes.cl |
| **Cobranza/payroll** | **PreVired** | Portal Empresas |
| **Innovación / Venture** | **LEAP** (ex CLA Digital), programa **TECLA** | Earnings 2T25 p.4; CLA Digital sitio |
| **Filial turismo** | **CLA Turismo S.p.A.** | Memoria 2024; sitio |
| **Productividad/colaboración interna** | **Tigabytes** (case study mencionado) | Búsqueda DDG |
| **Asistente conversacional / Chatbot** | **NINGUNO público** | Verificación directa de homepage abr 2026 |

### B.3 ¿Usan IA hoy?

- **No usan IA conversacional pública** (ni en web, ni en WhatsApp, ni en sucursal virtual). Verificado directo abr 2026.
- **SoyFocus** (Mis Metas) declara "tecnología *AI-driven*" para perfilar y recomendar fondos. Es lo más cercano a IA visible al cliente.
- Programa **TECLA / LEAP** (Venture Client) busca activamente tecnologías para "automatización de procesos, nuevos servicios y experiencias digitales personalizadas" — es la puerta de entrada natural para Vertex AI.
- Riesgo crediticio adoptó **IFRS 9** en 4T24 (Earnings 2T25 p.11), aumentando el índice de riesgo y la cobertura de morosidad — esto exige modelos de pérdida esperada (PD/LGD/EAD) más sofisticados → casos de uso de ML.

### B.4 Hitos recientes 2024-2025

| Fecha | Hito |
|---|---|
| Mayo 2024 | Afiliación de la Armada de Chile (+23 mil beneficiarios) |
| Nov 2024 | Tapp supera **1 millón** de clientes (#3 ranking prepago CMF) |
| **4-nov-2024** | **Tomás Zavala Mujica** asume como Gerente General Corporativo |
| 4T 2024 | Adopción metodológica **IFRS 9** |
| 2024 | Caja Los Andes en **Dow Jones Sustainability Index** percentil 98 (puntaje 71, +18 vs año anterior); SSIndex 79 % |
| 2024 | Bono social internacional **USD 300 MM 144A/RegS** — primer caja en historia. Premio "Debut FI Bond Deal of the Year" (Global Banking & Markets Latin America Awards) |
| Mar 2025 | **Feller Rate sube rating a AA / Stable** |
| Jun 2025 | **Préstamo USD 100 MM con CAF** — primer crédito multilateral. Para >100.000 afiliados nuevos vía crédito social |
| 2T 2025 | **8ª edición TECLA** — abre por primera vez a empresas no afiliadas. Programa Venture Client de LEAP |
| 2024-25 | Memoria Anual Integrada 2024 publicada (ES + EN); *upgrade* reportería bajo formato CMF unificado |

### B.5 Equipo y liderazgo

- **Presidente Directorio:** Ítalo Ozzano Cabezón
- **Gerente General Corporativo:** **Tomás Zavala Mujica** (MBA Wharton; ex Gerente Desarrollo Corporativo Grupo Consorcio; ex CSSA Consorcio; mentor Endeavor Chile; 2.200+ personas en rol previo)
- **Director(es):** Andrés Arriagada Laissle, Joaquín Cortés Huerta, Juan Pablo Portales Montes, Ximena Bravo Kemp, Claudia Castro Hruska, Marcela Andaur Rademacher
- **Head of LEAP / CLA Digital:** **Pedro Pablo Mir** (MBA MIT; ex Legria; ~80 startups apoyadas a la fecha)
- **Representante Legal:** Tomás Zavala Mujica
- **RUT:** 81.826.800-9 — **Casa Matriz:** General Calderón Nº121, Providencia, Santiago

### B.6 Subsidiarias / filiales relevantes

- **Tapp** — Los Andes Tarjetas de Prepago S.A. (wallet / mini-banca)
- **CLA Turismo S.p.A.** — 18 hoteles, parques, restaurantes "Raíces de los Andes"
- **CLA Digital → LEAP** (innovación abierta y CVC)

---

## Parte C — Contexto competitivo

### C.1 Mercado total CCAF en Chile (2024)

| KPI 2024 (industria) | Valor |
|---|---|
| Afiliados totales (4 cajas) | 7.298.892 (+3,4 %) |
| Trabajadores afiliados | 5.842.769 |
| Pensionados afiliados | 1.456.123 |
| Empresas afiliadas | 81.900 |
| Asignaciones Familiares pagadas | 7.792.662 (CLP 91.056 MM) |
| Beneficios sociales | 35,5 millones / CLP 59 mil MM |
| Créditos sociales otorgados | 1,78 millones / CLP 2.064 mil MM |
| Subsidios Incapacidad Laboral | 2.951.664 (60 % de licencias del país) |
| Sucursales totales (industria) | **+400** |

### C.2 Comparativo digital de cajas

| Caja | Afiliados | Cuota | Producto digital insignia | IA / Chatbot | Tech destacable |
|---|---|---|---|---|---|
| **Los Andes** | 4,5 M | 59,8 % | **Tapp + Mis Metas** | **No** chatbot público; SoyFocus AI-driven | Modyo DXP, Keycloak SSO, Bono 144A USD 300M, CAF USD 100M, **LEAP/TECLA Venture Client** |
| **Los Héroes** | 1,1 M | ~14,2 % cartera | App + Portal Héroes (100 % online), **Mediclic telemedicina**, **Héroes Prepago** | No chatbot público | 1° Premio Procalidad satisfacción 3 años seguidos; Red Chile Cuida; bonos sociales recurrentes |
| **La Araucana** | ~0,9 M | 11,1 % cartera | Modelo "Más Cerca" (7 sucursales rediseñadas), **Tu Salud Más Cerca** (telemedicina, 30k acciones preventivas, 4,8 M personas), **Crédito con Compromiso Verde** | No chatbot público | Premio OISS "Mejor Gestión y Herramienta Tecnológica"; lideró NASA Space Apps Challenge Chile; financiamiento BID Invest USD 70 MM; rating A+ |
| **18 (Caja 18)** | ~0,23 M | 6,7 % cartera | "Caja 18 Te Atiende" (gestión reclamos), tótems en sucursales | No chatbot público | 1° en gestión licencias médicas electrónicas (1,5 días promedio); IFC USD 45 MM |

**Cajas de Chile A.G.** (asociación gremial) lanzó en 2024 **Módulo de Consulta Saldos a Favor** (400 mil consultas en 3 semanas) y participa en mesa de **Finanzas Abiertas (Open Finance) CMF**.

### C.3 Posición competitiva única de CCLA

- **Mayor escala con margen amplio**: 59,8 % afiliados vs 11–14 % de cada competidor.
- **Único con bono internacional 144A/RegS** y línea CAF (USD 400 MM externos en total).
- **Único con ecosistema vertical completo**: Tapp (wallet), Mis Metas/SoyFocus (inversiones), CLA Turismo (hoteles), LEAP (innovación). Las otras cajas no tienen filiales de inversiones ni red turística propia tan grande.
- **Única con score DJSI percentil 98**.
- **Única con programa Venture Client formal** (TECLA/LEAP, 8 ediciones).
- **Pero**: Los Héroes les gana en *satisfacción de cliente* (3 años seguidos Premio Procalidad), La Araucana en *premios de tecnología social* (OISS), Caja 18 en *velocidad de licencias médicas* (1,5 días).

---

## Parte D — Pain points y oportunidades

### D.1 Voces del cliente / quejas comunes

- **Atención presencial inconsistente** — quejas en reclamos.cl referidas a "mala atención" en sucursales (ej. caja Providencia, mesa 4).
- **App móvil con barrera técnica** — requisito **iOS 17+** excluye iPhones de 2018 y anteriores; ventana de mantenimiento viernes-domingo amplia (interrumpe trámites de fin de semana, justo cuando pensionados disponen del tiempo).
- **No hay WhatsApp** publicado oficialmente — el canal que más usan los chilenos para servicio.
- **No hay chatbot/voicebot** — todo va a contact center (600 510 0000) o sucursal.
- **Procesos paper-heavy todavía:**
  - **Licencias médicas físicas** aún se entregan en papel a la sucursal o suben por sucursal virtual; las electrónicas a veces vienen con marca "no válida para trámite".
  - **Asignación Familiar** — actualización de tramos *pasó a ser no presencial en 2024* (vía SUSESO), pero todavía hay confusión sobre qué hacer.
- **Sub-utilización de beneficios** — 35 millones de prestaciones sociales se entregan/año en la industria, pero las CChC + Cajas de Chile reconocen el problema: *"debemos perseverar en aumentar el conocimiento sobre nuestra labor y los beneficios que otorgamos"* (Tomás Campero, Presidente Cajas de Chile, Memoria 2024). Estudio Cadem: **70 % evalúa negativamente el sistema de protección social** y **60 % se siente desprotegido**.
- **Brecha de descubrimiento (discovery gap)** — afiliados desconocen para qué califican (Bono Marzo, BPS, becas, descuentos, dental, telemedicina). El módulo "Saldos a Favor" de Cajas de Chile recibió 400 K consultas en 3 semanas — prueba de la hambre de auto-descubrimiento.

### D.2 Journeys lentos / fricción alta

| Journey | Fricción actual |
|---|---|
| Solicitar Crédito Social tradicional | Múltiples pasos web + documentación; en Tapp ya es 5 min para 50 UF, pero el resto de la cartera no |
| Reclamo / queja formal | Va a sucursal, contact center o web — sin trazabilidad para el cliente |
| Actualización tramo Asignación Familiar | Mejoró en 2024 con MDS, pero requiere consciencia del proceso |
| Becas / educación | Información dispersa, sin recomendador personalizado |
| Pensionados — uso de salud / recreación | Brecha digital, mucho trámite en sucursal |
| Empresas — onboarding y reportería | PreVired + portal — funcional pero sin asistente |
| Discovery de beneficios | "Guía de beneficios" estática; sin matching personalizado |

### D.3 Beneficios infrautilizados (típico problema de welfare)

- Bono escolar 2025 ($64.574) — requiere ser receptor de SUF / Asignación Familiar / Maternal con cargas al 31-dic-2024. Mucha gente no sabe que es elegible.
- Telemedicina y dental urgencia ($100 copago) — la mayoría de afiliados no conoce.
- Programa "Sana" (descuentos farmacia), Plan Salud Pensionados.
- Cine al Aire Libre (10.700 personas asistieron en 15 ciudades en 2024 — chico para 4 M).
- Universidad de la Experiencia (pensionados).
- Becas TECLA Talento Emprende.

---

## Parte E — Features "WOW" para el demo

> **Tono:** Spanish-friendly, audiencia chilena ejecutiva. Cada feature liga: pain → capability → "why they care".

### 1. **Andesia — Asistente Agéntico Multicanal (Web + WhatsApp + Voz)**
Un agente conversacional unificado, presente en sitio, app, WhatsApp y voicebot 600, capaz de **iniciar y completar trámites** (consulta saldo, simulación crédito, programación pago Asignación, estado licencia médica) sin pasar al humano. Habla chileno, conoce a cada afiliado por contexto OIDC.
- **Pain:** No tienen chatbot, contact center saturado, sin WhatsApp.
- **Vertex AI:** **Gemini 2.5 + Agent Builder + Live API (voice)** + integración Keycloak. Tool-use sobre APIs Modyo y Tapp.
- **Por qué les importa:** SUSESO Circular 3.796 exige relacionamiento medible y trazable con el afiliado — Andesia genera SLA, queue management, métricas. Cubre el gap WhatsApp con un solo build.

### 2. **MiBeneficio — Recomendador Personalizado de Beneficios ("Discover what you qualify for")**
Pantalla personalizada en sucursal virtual y app que cruza perfil del afiliado (cargas, edad, ingreso, comuna, pensión) con catálogo de 200+ beneficios y devuelve **"Hoy puedes pedir esto: Bono Escolar, dental urgencia, descuento Despegar"**, con CTA de un clic.
- **Pain:** Brecha de descubrimiento; 70 % evalúa mal el sistema de protección social; "saldos a favor" recibió 400K consultas en 3 semanas.
- **Vertex AI:** **Vector Search + Gemini** (RAG sobre la guía de beneficios completa) + **Recommendations AI** + segmentos en BigQuery.
- **Por qué les importa:** Eleva uso de beneficios → mejora NPS y posicionamiento DJSI/SSIndex. Posiciona a CCLA como "el que te conoce".

### 3. **Crédito 5 Minutos – Versión Universal con Decisión Asistida por IA**
Llevar la experiencia Tapp (50 UF en 5 min) a **toda la cartera** (Universal, Salud, Educación Superior, Consolidación) con un asistente que evalúa REDEC + IFRS 9 + capacidad de pago en tiempo real y muestra la mejor alternativa.
- **Pain:** Solo Tapp tiene 5-min experience; el resto del crédito social es web tradicional.
- **Vertex AI:** **Gemini para conversación + Document AI** (subir liquidaciones/cédula) + modelo PD/LGD en **Vertex AI Pipelines** + **explicabilidad con Vertex Explainable AI**.
- **Por qué les importa:** CCLA es **#3 actor en consumo Chile** con 11,3 % share. Una mejora marginal en *conversión + riesgo* impacta la línea de excedentes (CLP 59 mil MM 1S25, +207 %).

### 4. **Asistente del Pensionado — "AbuelApp" con Voz y Multimodal**
Voz natural (Live API), texto grande, capacidad de **subir foto del documento de licencia médica o boleta** y resolver dudas. Pensionados pueden preguntar "¿cuánto me queda en el plan salud?", "¿dónde está la sucursal más cercana?", "léeme mi cartola".
- **Pain:** 398K pensionados, brecha digital, dependencia presencial, requisito iOS 17+ excluye dispositivos antiguos.
- **Vertex AI:** **Live API multimodal (voz + visión) + Gemini** con prompts senior-first; OCR vía **Document AI**; síntesis de voz con **Chirp 3 HD**.
- **Por qué les importa:** Plan Salud Pensionados es producto estrella; Caja Los Héroes y La Araucana ya hacen esfuerzos en pensionados — esto les permite saltarse 2 años de ventaja.

### 5. **Inteligencia de Licencias Médicas — Procesamiento Automatizado e Inteligente**
**Document AI** ingesta licencias en papel y electrónicas, detecta inconsistencias y abuso (exactamente lo que el sector identifica como problema sistémico), prioriza casos a COMPIN. Caja 18 lidera con 1,5 días — CCLA puede ir a < 1 día.
- **Pain:** Las CCAF pagan ~60 % de licencias del país (2,95 M en 2024). El gasto crece "exponencialmente, más allá de la población y enfermedades, producto de malas prácticas" (Memoria Cajas Chile 2024 p.3).
- **Vertex AI:** **Document AI Custom Extractor + Gemini** para clasificación + **Vertex AI Vision** para validación de firmas/sellos + agente que coordina con COMPIN.
- **Por qué les importa:** Métricas SUSESO públicas — competir directamente con Caja 18 en velocidad. Reducción de fraude → menor SIL pagado indebidamente.

### 6. **Coach Financiero "Mis Metas+" — Conversational Wealth Assistant**
Sobre la base actual de SoyFocus (que ya dice ser "AI-driven"), un agente conversacional que **conversa en chileno** con el cliente sobre objetivos ("¿pa' la casa, pa' los cabros, pa' jubilarme?"), simula escenarios y rebalancea fondos APV / Vivienda / mutuos.
- **Pain:** Mis Metas hoy es cuestionario estático; baja conversión.
- **Vertex AI:** **Gemini + Vertex Forecasting + Agent Builder** con grounding sobre normativa CMF.
- **Por qué les importa:** Inclusión financiera es bandera estratégica; aumenta cross-sell APV; defendible ante CMF (todo conversational queda logueado).

### 7. **Onboarding Conversacional Empresas — Auto-afiliación Inteligente**
Para los 26 mil empleadores chilenos NO afiliados a CCLA, un agente que toma RUT empresa, infiere por SII / public data tamaño, sector y rotación, y **arma propuesta de valor + cotización de bienestar en una conversación**.
- **Pain:** CCLA tiene 68,1 % share pero el restante 32 % son empresas que no han elegido caja o están en competencia. Onboarding es proceso comercial caro.
- **Vertex AI:** **Gemini + Agent Builder + Connectors a SII / Modyo CMS** + generación de propuesta PDF dinámica.
- **Por qué les importa:** Mover 1 punto de share = ~27 K trabajadores nuevos. Reduce CAC del equipo comercial.

### 8. **Agente "Hospedaje CLA Turismo" — Reserva Conversacional con Vibe Search**
Para CLA Turismo (18 hoteles, 48K reservas), un agente que recibe "*quiero un finde con la familia, presupuesto 200 mil, cerca de Santiago, con piscina*" y arma itinerario, paga con Tapp y aplica descuentos de la guía de beneficios.
- **Pain:** Reservas hoy son web tradicional; competencia con Despegar/Booking.
- **Vertex AI:** **Vector Search (vibe-search sobre descripciones e imágenes con multimodal embeddings) + Gemini + Veo** para recap del viaje al volver.
- **Por qué les importa:** CLA Turismo en reestructuración (cerró 2 ubicaciones en 2T25). Necesita cada peso de ARPU. Valida narrativa de "ecosistema integrado".

### 9. **Centro de Contacto 360° con Copilot Agéntico para Ejecutivos**
Copiloto en tiempo real para los ejecutivos de sucursal y contact center: **transcribe, sugiere respuesta, recupera políticas SUSESO, completa formularios, escala a humano cuando hay riesgo regulatorio.**
- **Pain:** Atención presencial inconsistente (quejas reclamos.cl); SUSESO Circular 3.796 exige trazabilidad.
- **Vertex AI:** **Gemini + Speech-to-Text + Agent Assist + Vector Search** sobre normativa SUSESO/IFRS9/REDEC.
- **Por qué les importa:** 2.849 colaboradores; productividad y reducción de tiempos de espera (KPI directo del directorio según Memoria 2024). Calidad consistente entre sucursales.

### 10. **TECLA Discovery — Agente para Innovación Abierta (LEAP)**
Para el equipo de Pedro Pablo Mir: un agente que **escanea startups globales** (Crunchbase, papers, demos), las matchea con desafíos publicados internamente y arma scorecards de Venture Client.
- **Pain:** TECLA recibió 480+ aplicaciones en 2025; revisar manualmente es lento.
- **Vertex AI:** **Gemini Deep Research + Agent Builder + Vector Search** sobre portafolio LEAP + integración Notion/Slack.
- **Por qué les importa:** Posiciona a Vertex AI como **partner del partner** — el equipo LEAP es la puerta natural para escalar todo lo anterior. Da un "win" rápido al stakeholder más probable.

---

## Quick wins recomendados (ranking del autor)

1. **Andesia (Feature 1)** — máximo impacto visible, contesta el gap chatbot/WhatsApp directamente.
2. **MiBeneficio (Feature 2)** — quirúrgico al pain N°1 de la industria (uso de beneficios), demo visualmente impactante.
3. **Crédito 5 Minutos universal (Feature 3)** — toca la línea de ingresos más grande (88 % de revenue), valida ROI a CFO.

---

## Fuentes

### Sitios oficiales y documentos primarios
- [cajalosandes.cl — Homepage](https://www.cajalosandes.cl)
- [Centro de Ayuda](https://www.cajalosandes.cl/centro-de-ayuda)
- [Portal Empresas](https://empresa.cajalosandes.cl)
- [Portal Pensionados](https://pensionados.cajalosandes.cl)
- [Mi Portal (Sucursal Virtual)](https://miportal.cajalosandes.cl) — usa Modyo + Keycloak SSO `sso.cajalosandes.cl/auth/realms/afiliados-ccla-prd` (cliente `modyo-ccla`)
- [Mis Metas (SoyFocus)](https://mismetas.cajalosandes.cl)
- [Tapp](https://tapp.cl)
- [Somos Andes — Portal Corporativo](https://somosandes.cajalosandes.cl)
- [REDEC – Ley 21.680 explicación CCLA](https://www.cajalosandes.cl/redec)
- [Memoria Anual Cajas de Chile 2024 (PDF)](https://www.cajasdechile.cl/wp-content/uploads/2025/04/Memoria-Cajas-de-Chile-2024.pdf) — fuente primaria de cifras de industria, sección Caja Los Andes pp. 30-32.
- [Earnings Presentation 2T25 Caja Los Andes (PDF)](https://cla.cdn.modyo.com/uploads/ced4be73-c549-4f78-8475-27c32f2d6cc0/original/Earnings_Presentation_2T25_ESP_.pdf) — fuente primaria de cifras CCLA.
- [CLA Turismo Memoria Interactiva 2024 (PDF)](https://cla.cdn.modyo.com/uploads/c14c5df1-fb6d-453d-8be7-f7bd450bfaa4/original/CLA_Turismo_Memoria24_Interactiva_.pdf)

### Regulador / asociación
- [SUSESO – Superintendencia de Seguridad Social](https://www.suseso.gob.cl)
- [Cajas de Chile A.G.](https://www.cajasdechile.cl)

### Competencia
- [Caja Los Héroes](https://www.losheroes.cl)
- [Caja La Araucana — sección "El año de las Cajas" en Memoria Cajas Chile 2024](https://www.cajasdechile.cl) (sitio propio devolvió ECONNREFUSED durante la investigación)
- [Caja 18](https://www.caja18.cl)

### Vendors / stack identificado
- [Modyo — DXP usado por CCLA](https://www.modyo.com)
- [Modyo Customer Stories](https://www.modyo.com/resources/customer-stories) — CCLA aparece como cliente, no hay caso publicado.

### Wikipedia (contexto histórico)
- [Caja de Compensación de Asignación Familiar (Wikipedia)](https://es.wikipedia.org/wiki/Caja_de_compensaci%C3%B3n_de_asignaci%C3%B3n_familiar) — DFL 245/1953, evolución legal, listado de las 4 CCAF.
- [Cámara Chilena de la Construcción (Wikipedia)](https://es.wikipedia.org/wiki/C%C3%A1mara_Chilena_de_la_Construcci%C3%B3n) — ecosistema CChC.

### Rating y financiero
- Feller Rate — rating CCLA **AA / Stable** (subido de AA−), 31-mar-2025 (referencia indirecta vía búsqueda; reporte completo requiere registro en feller-rate.com).

### Liderazgo
- Tomás Zavala Mujica — Wharton, ex Consorcio (CSSA, Desarrollo Corporativo), asume GG Corporativo el **4-nov-2024** (Memoria Cajas Chile 2024 p.31).
- Pedro Pablo Mir — Head de LEAP (ex CLA Digital), MBA MIT, ex Legria.
- Ítalo Ozzano Cabezón — Presidente del Directorio CCLA (Memoria Cajas Chile 2024 p.8).

### Reclamos / sentimiento
- reclamos.cl — bloqueado HTTP 403 durante investigación. Una queja capturada: "caja los andes de providencia me tocó la mesa 4 mala atención". Recomendado revalidar con Apify/scraper antes del lunes.

### Notas metodológicas
- WebSearch nativo del modelo bloqueado por Org Policy (Vertex AI). Investigación realizada con WebFetch directo + DuckDuckGo HTML. Los PDFs financieros se descargaron (10MB+ excedidos en algunos) y se procesaron con `pdftotext`.
- No se logró acceder a `cajagabrielamistral.cl` (TLS cert inválido) — confirma que esa caja está disuelta/absorbida; quedan 4 CCAF activas.
- App Store / Google Play store pages devolvieron 404/403 — ratings de Tapp tomados de la propia memoria CCLA (4,9★ con 25K+ valoraciones).
