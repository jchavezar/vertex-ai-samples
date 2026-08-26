# EBC Executive AI Transformation Showcase

> **Track 1: The EBC Executive AI Transformation Showcase**  
> Diseñado y optimizado para visualización de alto impacto en salas de juntas y pantallas directivas de **100 pulgadas**.

---

## 🏛️ Visión General & Propósito

El **EBC Executive AI Transformation Showcase** es una plataforma interactiva de demostración tecnológica de nivel C-Suite desarrollada para clientes empresariales de Google Cloud Vertex AI en Latinoamérica y el mundo.

Proporciona a Directores Generales (CEOs), Directores Financieros (CFOs), Directores de Tecnología (CTOs) y Consejeros de Administración una experiencia inmersiva, interactiva y cuantitativa sobre el poder transformador de la Inteligencia Artificial Generativa y los Enjambres de Agentes Autónomos.

---

## 🎨 Sistema de Diseño (Optimizado para Pantalla de 100")

- **Tema Claro Estricto (Strict Light Theme)**: Fondo blanco ártico cristalino (`#f8fafc`), superficies de cristal esmerilado con efecto glassmorphism (`rgba(255,255,255,0.92)`), bordes sutiles en `slate-200` y acentos ejecutivos en azul cobalto (`#1d4ed8`), verde esmeralda (`#059669`) e índigo (`#4338ca`). Sin estética oscura ni neón.
- **Tipografía de Alta Legibilidad C-Suite**:
  - Encabezados: 28px - 48px (`text-3xl` a `text-5xl`).
  - Textos de lectura: 16px - 20px (`text-base` a `text-xl`).
  - Tarjetas de Métricas Cuantitativas: 36px - 56px (`text-4xl` a `text-6xl`) para lectura nítida a 10 metros de distancia.
- **Idioma Unificado**: 100% en Español Ejecutivo (LatAm / Global).

---

## 🚀 3 Módulos Ejecutivos de Alto Impacto

### 🎙️ Módulo A: Asistente Ejecutivo de Voz en Tiempo Real
- **Interacción Bidireccional de Voz**: Micrófono interactivo con captura y transcripción en tiempo real de consultas verbales.
- **Visualizador Acústico Canvas**: Renderizado dinámico de ondas de sonido con gradientes de frecuencia activos durante la escucha y la locución.
- **Locución Ejecutiva en Español**: Síntesis de voz en tiempo real con guiones concisos y contundentes pensados para la toma de decisiones.
- **Escenarios Directivos Pre-Configurados**:
  - *ROI de automatización de atención a clientes con agentes multimodales*.
  - *Diseño y posicionamiento para productos de ultra alto patrimonio*.
  - *Impacto financiero, regulatorio y operativo de expansión regional*.
  - *Transformación y optimización de la cadena de suministro con IA*.
  - *Gobernanza corporativa y mitigación de riesgos bajo protocolo Zero-Leak*.
- **Cuadro de Mando Cuantitativo**: 4 métricas gigantes de ROI, reducción de OPEX, tiempo de amortización y precisión.

---

### 🎬 Módulo B: Estudio Creativo & Storyboards Cinemáticos
- **Generación de Campañas 360° en 1 Clic**: Transformación instantánea de cualquier iniciativa en una campaña publicitaria de clase mundial.
- **Concepto Rector & Slogan Ejecutivo**: Definición de narrativa de marca y slogan de alto impacto corporativo.
- **Storyboard Visual de 4 Paneles / Reels**:
  - *Panel 1: Gancho & Desafío* (El costo del statu quo).
  - *Panel 2: Innovación & Disrupción* (El salto cuántico tecnológico).
  - *Panel 3: Escala Global & Seguridad Blindada* (Validación de infraestructura).
  - *Panel 4: Cierre & Llamada a la Acción* (La decisión transformadora).
- **Reproductor de Reel Cinemático**: Modal interactivo a pantalla completa con avance automatizado de paneles, cuenta regresiva, y locución narrada en español.
- **Copy Multicanal**: Textos adaptados para LinkedIn C-Suite, Reels 9:16 verticales y Comunicados Oficiales de Prensa.
- **Proyección Financiera de Marketing**: Modelado de ROI publicitario, reducción de CAC y presupuesto sugerido.

---

### 🤖 Módulo C: Enjambre de Agentes Autónomos (4 Lanes Concurrentes)
- **Orquestación Multi-Agente en Tiempo Real**:
  1. 🎯 **Agente de Estrategia**: Modela la visión macro, posicionamiento de mercado y monetización.
  2. ✨ **Agente Creativo**: Diseña la experiencia de cliente, narrativa de marca y activos disruptivos.
  3. 📈 **Agente Financiero**: Proyecta CAPEX/OPEX, flujos descontados, ROI, VAN y TIR.
  4. 🛡️ **Agente Auditor & Cumplimiento**: Evalúa ciberseguridad, soberanía de datos, gobernanza y compliance bancario.
- **Transmisión en Vivo de Tokens de Razonamiento (SSE Stream)**: Visualización paso a paso del pensamiento analítico de cada agente mientras deliberan.
- **Dossier Ejecutivo Consolidado**: Tarjeta de síntesis final con Dictamen del Consejo de Administración, Presupuesto Aprobado, Payback y Plan de Acción Inmediato.

---

## 🛠️ Arquitectura & Stack Tecnológico

| Capa | Tecnología | Puerto | Descripción |
| :--- | :--- | :--- | :--- |
| **Backend** | Python 3.13 + FastAPI + `uv` | `8000` | APIs RESTful, SSE Streams, Google GenAI SDK con `vertexai=True` |
| **Modelos IA** | Gemini 3.7 / Gemini 2.5 Flash & Pro | Cloud | Razonamiento C-Suite, generación estructurada JSON con Pydantic |
| **Frontend** | React 19 + TypeScript + Vite | `5178` | UI de alta resolución con Tailwind CSS, Lucide Icons y Canvas Audio |
| **Seguridad** | Protocolo Zero-Leak | - | Sin secretos en código, variables centralizadas en `.env` |

---

## ⚡ Guía de Instalación y Ejecución

### 1. Requisitos Previos
- Python 3.13 con gestor `uv`.
- Node.js 20+ y `npm`.
- Credenciales activas de Google Cloud (`gcloud auth application-default login`).

### 2. Configuración de Entorno
Crea tu archivo `.env` en la raíz del proyecto (o utiliza el predeterminado):
```bash
PROJECT_ID=vtxdemos
REGION=us-central1
MODEL_NAME=gemini-2.5-flash
HOST=0.0.0.0
PORT=8000
FRONTEND_PORT=5178
```

### 3. Lanzamiento con 1 Solo Comando
Ejecuta el script unificado de arranque:
```bash
./start.sh
```

El script verificará y liberará automáticamente los puertos `8000` y `5178` si estaban ocupados, e iniciará backend y frontend concurrentemente:
- **Frontend UI**: [http://localhost:5178](http://localhost:5178)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
