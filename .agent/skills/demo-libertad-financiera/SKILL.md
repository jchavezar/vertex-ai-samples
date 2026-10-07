---
name: demo-libertad-financiera
description: Sets the agent into complete cognitive context for the Libertad Financiera Modernization Demo and presents the 5 progressive demonstration options (Clonado tal cual, Mejora UX/UI, Navegador Vertex AI Search, Libertad AI Advisor Flotante 24/7, y Precalificación Multimodal de Crédito con Visión AI) without blindly auto-executing them as a script. Scaffolds files directly into the active workspace directory. Activate whenever the user mentions "demo libertad financiera", "libertad demo", "demo libertad", or asks about modernizing Libertad Financiera.
---

# Demo Libertad Financiera: Protocolo Cognitivo y Presentación en 5 Actos

Esta habilidad permite al agente adquirir de forma instantánea todo el contexto arquitectónico, técnico y de negocio de la modernización de **Libertad Financiera** (`https://www.libertad.com.mx/`), asegurando que **los archivos y la demo se generen y ejecuten directamente en el directorio/workspace que el usuario tenga abierto**, para que aparezcan visibles en el panel de archivos (*Explorer*).

---

## 🎯 Principio Fundamental: Trabajar en el Directorio Activo del Usuario (`cwd`)

> [!IMPORTANT]
> **REGLA DE DIRECTORIO ACTIVO**:
> Si el usuario abre un nuevo workspace o carpeta (por ejemplo, `tmp`, `~/demo`, o cualquier carpeta vacía), los archivos de la demo **NO deben quedarse escondidos en otra ruta externa**.
> 
> El agente debe:
> 1. Detectar el directorio de trabajo actual (`cwd`).
> 2. Si el directorio actual no contiene los archivos de la demo (`site/`, `serve_libertad.py`), ejecutar el andamiaje (`scaffold_workspace.py .`) para que los archivos del clon aparezcan de inmediato en el árbol del explorador a la izquierda del IDE.
> 3. Ejecutar el servidor y las inyecciones de código sobre el directorio actual abierto.

---

## 🧠 Base de Conocimiento Completa

1. **Master Repository Source**:
   - Ruta maestra: `/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/app-modernization/`
   - Receta y scripts: `/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/`

2. **Infraestructura y Servidor**:
   - Servidor: `serve_libertad.py` ejecutado con Python multihilo (`ThreadingHTTPServer`) en el puerto **`8088`**.
   - Endpoints activos:
     - `/api/suggest`: Autocompletado tipo Search-As-You-Type en <10ms.
     - `/api/search`: Grounding en Vertex AI Search + síntesis con `gemini-3.5-flash-lite`.
     - `/api/advisor`: Asesor financiero conversacional en vivo con `gemini-3.7-flash`.
     - `/api/multimodal-credit`: Extracción OCR de nómina SAT CFDI 4.0, cálculo regulatorio CNBV 30% y dictamen con `gemini-3.7-flash`.
   - Smart 302 Redirection: Intercepta rutas de páginas secundarias (`/content/...`) y redirige a `https://www.libertad.com.mx/...` para evitar errores 404.

3. **Inteligencia Artificial (Google Cloud)**:
   - Proyecto GCP: `vtxdemos` (Project Number: `254356041555`).
   - Motor de Búsqueda: Engine `libertad-search-navigator` en Data Store `libertad-web-store`.
   - Modelos Permitidos: **`gemini-3.7-flash`**, **`gemini-3.5-flash-lite`** (vía Vertex AI `us-central1`). NUNCA modelos obsoletos.

4. **Inyección Modular (`inject_feature.py`)**:
   - Controla en tiempo real los cambios sobre `./site/index.html` del directorio actual.
   - Modos disponibles:
     - `reset`: Restablece el clon tal cual (AEM legado).
     - `inject modern_header_ux`: Mega-menú + Hero 2026 + Simulador interactivo.
     - `inject modern_header_ai`: Todo lo de UX + Navegador inteligente Vertex AI Search.
     - `inject ai_advisor`: Libertad AI Advisor Flotante 24/7 en la esquina inferior derecha.
     - `inject ai_multimodal_credit`: Precalificación multimodal con escáner láser de CFDI y certificado digital.

---

## 🚫 Regla Estricta de Activación: CERO HERRAMIENTAS / CERO COMANDOS en el Turno 1

> [!CAUTION]
> **REGLA ABSOLUTA DE NO-AUTOEJECUCIÓN**:
> Cuando el usuario diga *"demo libertad financiera"*, el agente **NO DEBE EJECUTAR NINGÚN COMANDO NI MODIFICAR NINGÚN ARCHIVO**.
> 
> 1. **CERO HERRAMIENTAS**: Está estrictamente prohibido llamar a `run_command`, `write_to_file`, `replace_file_content` o cualquier herramienta en el turno inicial.
> 2. **SOLO DIÁLOGO**: El agente debe responder ÚNICAMENTE con el menú visual de las 5 opciones y esperar la instrucción explícita del usuario.
> 3. **PROHIBIDO ABRIR ARCHIVOS EN DIFF**: NUNCA uses `replace_file_content` sobre archivos en el editor del usuario; delega las inyecciones a los scripts de la receta.
> 4. **ANDAMIAJE BAJO DEMANDA**: Los archivos se copian al directorio actual (`scaffold_workspace.py`) **ÚNICAMENTE** cuando el usuario indique expresamente qué opción desea ejecutar.

---

## 📋 Protocolo de Respuesta al Solicitar "demo libertad financiera"

Cuando el usuario escriba *"demo libertad financiera"*, el agente responderá de inmediato en texto puro (sin herramientas) mostrando:

### 1. Presentar el Menú de las 5 Opciones

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │               DEMO LIBERTAD FINANCIERA: MENÚ DE 5 OPCIONES                  │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │                                                                             │
 │ [1] CLONADO DE PÁGINA TAL CUAL (Baseline AEM Monolítico)                    │
 │     • Replicación 100% fiel del portal de producción (libertad.com.mx).     │
 │     • Archivos clonados en este directorio (visibles en tu Explorer).       │
 │     • Carrusel, fuentes y activos locales en http://localhost:8088/.        │
 │     • Diagnóstico: cabecera monolítica saturada con >8 accesos apretados.   │
 │                                                                             │
 │ [2] MEJORA DE UX/UI (Modernización Modular del Header & Simulador)          │
 │     • Inyección de Mega-Menú interactivo desplegable con glassmorphism.     │
 │     • Hero Section Fintech 2026 con métricas clave y badges regulatorios.   │
 │     • Simulador financiero interactivo en tiempo real (Inversión vs Crédito)│
 │     • 4 categorías limpias (Créditos, Inversión & Cuentas, Seguros, Empresa)│
 │                                                                             │
 │ [3] FEATURE DE IA 1: NAVEGADOR INTELIGENTE (Vertex AI Search & Gemini)      │
 │     • Search-As-You-Type en paralelo: autocompletado instantáneo (<10ms).   │
 │     • Grounding en Vertex AI Search + síntesis con Gemini 3.5 Flash Lite.   │
 │     • Canvas dinámico auto-expansible (460px ──► 740px) y 0 errores 404.    │
 │                                                                             │
 │ [4] FEATURE DE IA 2: LIBERTAD AI COPILOT 24/7 (Gemini 3.7 Flash)            │
 │     • Drawer flotante conversacional como asesor financiero certificado.     │
 │     • Chips con preguntas rápidas (Inversión 14%, Créditos, CuentaYa).      │
 │     • Textarea universal de expansión automática (Zero-Glitch Mechanics).   │
 │     • Cálculos de inversión y crédito en lenguaje natural en tiempo real.   │
 │                                                                             │
 │ [5] FEATURE DE IA 3: PRECALIFICACIÓN MULTIMODAL DE CRÉDITO (Visión AI)      │
 │     • Escaneo láser de comprobante de nómina SAT (CFDI 4.0 con timbre).     │
 │     • Extracción con Gemini 3.7 Flash Vision de percepciones y retenciones. │
 │     • Regulación CNBV automática: tope del 30% sobre el ingreso neto.       │
 │     • Certificado digital de preaprobación con folio y cuota fija mensual.  │
 │                                                                             │
 └─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Preguntar al Usuario
Preguntar: **"¿Cuál de las 5 opciones deseas que preparemos o ejecutemos en este directorio?"**

---

## 🛠️ Ejecución por Opción en el Directorio Local (Solo cuando el usuario lo solicite)

Cuando el usuario te indique qué opción ejecutar (ej. *"ejecuta el paso 1"*, *"vamos con el paso 4"*, *"ejecuta la precalificación multimodal"*), el agente debe invocar el script correspondiente mediante `run_command`:

> 💡 **MÉTODO DIRECTO RECOMENDADO**:
> Cada script de la receta detecta automáticamente el directorio actual (`pwd`), andamia los archivos locales si aún no existen para que aparezcan en el Explorer, ejecuta los cambios, levanta el servidor y abre el navegador:
> - **Paso 1**: `uv run python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/demo_step1_clone.py`
> - **Paso 2**: `uv run python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/demo_step2_ux.py`
> - **Paso 3**: `uv run python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/demo_step3_ai.py`
> - **Paso 4**: `uv run python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/demo_step4_copilot.py`
> - **Paso 5**: `uv run python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/libertad-financiera-modernization/scripts/demo_step5_multimodal.py`

---

## 🎭 Detalle de la Narrativa de Presentación por Cada Paso:

### Paso 1: Clonado Tal Cual (Baseline AEM Monolítico)
1. **Andamiaje**: Si `./site` no existe en la carpeta actual, se copian `site/`, `serve_libertad.py` e `inject_feature.py` para que sean visibles en el Explorer.
2. **Estado**: Se asegura que `site/index.html` esté en su estado clonado original (sin inyecciones).
3. **Servidor**: Se inicia `serve_libertad.py` en el puerto `8088`.
4. **Navegador**: Se abre `http://localhost:8088/`.
5. **Narrativa**: Mostrar la fidelidad idéntica al portal de producción (`libertad.com.mx`), el monolito AEM 6.x y la saturación de 8 enlaces en el header.

### Paso 2: Mejora UI/UX (Mega-Menú, Hero 2026 y Simulador)
1. **Inyección**: Se inyecta el Mega-Menú glassmorphism, el Hero Section Fintech y el Simulador interactivo (`inject modern_header_ux`).
2. **Navegador**: Se actualiza `http://localhost:8088/`.
3. **Narrativa**: Mostrar la desaturación visual, las 4 categorías organizadas (Créditos, Inversión & Cuentas, Seguros, Empresa), el simulador en tiempo real ($5k a $300k con cálculo inmediato de 14% de ganancia o mensualidad) y las 4 tarjetas de productos destacados.

### Paso 3: Feature de IA 1 (Navegador Inteligente Vertex AI Search & Gemini)
1. **Inyección de IA**: Se incorpora el motor de búsqueda inteligente (`inject modern_header_ai`).
2. **Navegador**: Invitar al usuario a interactuar escribiendo *"crédito"* o *"inversión"*.
3. **Narrativa**: 
   - Autocompletado ultra-rápido (<10ms) en dock compacto (460px).
   - Animación de expansión dinámica fluida a 740px con shimmer skeleton.
   - Síntesis ejecutiva de Gemini 3.5 Flash Lite + tarjetas oficiales de Vertex AI Search sin errores 404 (Smart 302 Redirection).

### Paso 4: Feature de IA 2 (Libertad AI Advisor Flotante 24/7)
1. **Inyección**: Se activa el botón flotante y el drawer conversacional en la esquina inferior derecha (`inject ai_advisor`).
2. **Navegador**: Se abre `http://localhost:8088/`.
3. **Narrativa**: 
   - Botón flotante dorado/marino con status pill verde (En línea).
   - Drawer con diseño Glassmorphism, chips rápidos ("Inversión 14%", "Crédito $50,000", "CuentaYa").
   - Inteligencia financiera conversacional con Gemini 3.7 Flash, cálculos automáticos de rendimientos y asesoría en lenguaje natural.
   - Textarea universal auto-expansible (Zero-Glitch Mechanics).

### Paso 5: Feature de IA 3 (Precalificación Multimodal de Crédito con Visión AI)
1. **Inyección**: Se incorpora el modal de análisis de documentos y el botón de precalificación express (`inject ai_multimodal_credit`).
2. **Navegador**: Se abre `http://localhost:8088/`.
3. **Narrativa**: 
   - Lanzamiento desde el botón flotante inferior izquierdo o desde el Simulador del Hero al hacer clic en "Solicitar Crédito Preaprobado".
   - Escaneo láser animado de comprobante de nómina SAT (CFDI 4.0).
   - Lectura OCR con Gemini 3.7 Flash Vision: extracción de RFC, patrón, percepciones y deducciones.
   - Aplicación automática de la normativa CNBV (tope del 30% del ingreso mensual neto).
   - Emisión instantánea del Certificado Digital de Crédito Preaprobado ($85,000 MXN a 24 meses por $4,427/mes) con folio de autorización y opción de descarga.
