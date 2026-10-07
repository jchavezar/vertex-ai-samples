# Guión de Demostración para Jetski: Modernización de Libertad Financiera

Este documento es el guión operativo paso a paso para ejecutar la demostración en vivo de las capacidades de **Jetski**. Con este guión podrás guiar a Jetski por órdenes de voz o texto para que construya la página web desde cero, valide visualmente el clon y agregue features de modernización e Inteligencia Artificial en tiempo real.

---

## 1. Análisis Exhaustivo de Modernización

### 1.1 Diagnóstico y Mejoras de UI/UX
* **Problema en el Header Actual**:
  - El header de Libertad Financiera presenta una barra de navegación saturada con más de 8 accesos directos horizontales con íconos dispersos (*Crédito, Inversión, CuentaYa, Seguros, etc.*), lo cual genera sobrecarga cognitiva y rompe la jerarquía en pantallas medianas.
* **Propuesta de Modernización**:
  - **Mega-Menú Desplegable Flotante (Glassmorphism)**: Agrupar la oferta de valor en 3 categorías maestras:
    1. **Financiamiento**: Crédito Personal, Crédito Automotriz, Crédito PYME.
    2. **Ahorro e Inversión**: LiberCuenta Digital, Inversión a Plazo Fijo con rendimientos garantizados.
    3. **Protección y Servicios**: Seguros de Vida, Asistencias Médicas y Pago de Servicios.
  - **Identidad Visual**: Conservar la paleta oficial (Azul `#0033a0` / `#002c72`, Amarillo `#fbba00`, Blanco `#ffffff`) pero con bordes redondeados (`rounded-xl`), micro-sombras suaves (`shadow-lg`), desenfoque de fondo (`backdrop-blur-md`) y transiciones de 200ms.

---

### 1.2 Features de Inteligencia Artificial para el Negocio
Para transformar la página web de un catálogo estático a un motor de generación de ingresos para Libertad Financiera:

1. **Libertad Copilot (Asesor Financiero 24/7)**:
   - Chatbot conversacional empático entrenado en productos de Libertad Financiera que asiste al cliente con lenguaje natural en español mexicano.
   - Detecta la intención del usuario (*"Necesito $20,000 para remodelar mi casa"*) y le sugiere el plazo y monto óptimos calculando el pago quincenal al instante.
2. **Simulador de Crédito con Pre-Aprobación Instantánea con IA**:
   - Evaluación crediticia predictiva en 60 segundos pidiendo mínimos datos (ingreso mensual estimado, plazo deseado).
   - Generación de un código QR / token para concluir el trámite en sucursal o en la app móvil.
3. **Onboarding Digital Asistido con Visión (OCR/KYC Multimodal)**:
   - Validación automática de INE y comprobante de domicilio usando capacidades multimodales de Gemini, reduciendo el abandono de solicitud digital de 65% a menos del 15%.
4. **Recomendador de Inversión Inteligente**:
   - Algoritmo que compara la inflación actual contra el rendimiento garantizado de Libertad Financiera, mostrando visualmente cuánto ganaría el usuario mes con mes.

---

### 1.3 Análisis Tecnológico: Del Monolito AEM a la Arquitectura AI-Native
* **Estado Actual (Adobe Experience Manager - AEM)**:
  - Arquitectura monolítica pesada basada en JCR/Clientlibs.
  - Dependencia de jQuery legado, más de 30 scripts de seguimiento que ralentizan la carga inicial (>3.8s en redes móviles).
  - Estilos embebidos con caracteres de escape CSS (`\2f `) que dificultan la extensibilidad ágil.
* **Arquitectura Moderna Propuesta**:
  - **Frontend Desacoplado**: React 19 + Vite o Next.js desplegado sobre Google Cloud Run / Edge CDN.
  - **Backend de IA Inteligente**: Google GenAI SDK con modelos `gemini-3.7-flash` para respuestas de baja latencia (<400ms) y streaming en vivo.
  - **Seguridad y Cero Fugas**: Cumplimiento regulatorio estricto (CNBV, CONDUSEF) con almacenamiento de secretos en Secret Manager y sin cookies de tracking invasivas.

---

## 2. Guión de la Demo en Vivo Paso a Paso

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           ESTRUCTURA DE LA DEMO                          │
├─────────┬──────────────────────────────────┬─────────────────────────────┤
│ FASE 1  │ Reconstrucción desde 0 (Clon)    │ Scraping & Render local     │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ FASE 2  │ Validación Visual con Browser    │ MCP CDP + Captura visual    │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ FASE 3  │ Modernización UI/UX (Header)     │ Inyección Mega-Menú         │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ FASE 4  │ Feature de Negocio IA (Copilot)  │ Inyección Chat Asesor IA    │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ FASE 5  │ Reversión Limpia                 │ Control de versión en vivo  │
└─────────┴──────────────────────────────────┴─────────────────────────────┘
```

---

### FASE 1: Construcción de la Página desde Cero (Pristine Clone)

> **Narrativa para el Presentador**:
> *"Jetski no solo escribe código desde cero, sino que tiene capacidades avanzadas de ingeniería inversa y clonado de alta fidelidad. Le pediré a Jetski que analice el portal en vivo de Libertad Financiera y extraiga una réplica 100% idéntica, incluyendo todas sus fuentes corporativas, estilos y assets gráficos."*

#### 💬 Prompt para darle a Jetski:
```text
Jetski, ejecuta la reconstrucción completa desde cero de la página web de Libertad Financiera (https://www.libertad.com.mx/) asegurando 100% de fidelidad tipográfica y de diseño, y levanta el portal en el servidor local.
```

#### ⚙️ Acciones que ejecuta Jetski de forma autónoma:
1. Ejecuta `uv run --with beautifulsoup4 python3 clone_libertad.py`
   - Descarga el HTML base.
   - Cosecha las 31 fuentes oficiales (`SourceSansPro`, `SourceSerifPro`, `StagSans`).
   - Extrae los banners desktop del carrusel con la pareja y la familia.
   - Normaliza URLs con caracteres especiales (`ñ`, tildes).
   - Elimina trackers lentos para carga local ultrarrápida.
2. Levanta el servidor local con `uv run python3 serve_libertad.py`.
3. Dispara `open http://localhost:8088/` para mostrar el sitio en pantalla.

---

### FASE 2: Evaluación Visual Automatizada con Browser MCP

> **Narrativa para el Presentador**:
> *"Para garantizar que la réplica no sea simplemente 'algo parecido', Jetski cuenta con visión por computadora e integración directa con el navegador para interactuar con la página y evaluar visualmente que cada elemento esté en su lugar exacto."*

#### 💬 Prompt para darle a Jetski:
```text
Jetski, realiza una evaluación visual interactiva del clon en http://localhost:8088/ utilizando el navegador MCP. Valida tanto el primer slide como el segundo slide del carrusel y confirma que no existan defectos visuales.
```

#### ⚙️ Acciones que ejecuta Jetski de forma autónoma:
1. Conecta con el navegador en modo depuración (puerto `9222`).
2. Selecciona la pestaña `http://localhost:8088/`.
3. Toma captura del Slide 1 (verificando la foto de la pareja con playera verde).
4. Ejecuta un clic programático con `browser_js_click` sobre el segundo indicador del carrusel.
5. Toma captura del Slide 2 (verificando la foto de la familia y el título de crédito en línea).
6. Analiza las imágenes con `view_file` y entrega el veredicto de fidelidad al 100%.

---

### FASE 3: Modernización de UI/UX - Mega-Menú Desplegable

> **Narrativa para el Presentador**:
> *"Ahora que tenemos la base idéntica, demostraremos cómo Jetski moderniza la interfaz. En el sitio actual, el menú superior satura al usuario con demasiados botones. Le ordenaremos a Jetski que rediseñe el Header y cree un menú desplegable moderno y profesional."*

#### 💬 Prompt para darle a Jetski:
```text
Jetski, moderniza el Header de la página de Libertad Financiera. Elimina la saturación horizontal de botones y agrega un menú desplegable moderno agrupado por categorías de productos.
```

#### ⚙️ Acciones que ejecuta Jetski de forma autónoma:
1. Ejecuta `uv run python3 inject_feature.py inject modern_header`.
2. Actualiza el Header para integrar un desplegable elegante con micro-animación al pasar el cursor o dar clic.
3. El usuario refresca el navegador en `http://localhost:8088/` y ve la interfaz desaturada y moderna.

---

### FASE 4: Inyección de Inteligencia Artificial - Libertad Copilot

> **Narrativa para el Presentador**:
> *"El mayor valor de Jetski es transformar aplicaciones tradicionales en experiencias nativas de IA. Ahora le pediremos que dote a Libertad Financiera de un Asistente Inteligente capaz de cotizar créditos en tiempo real con el cliente."*

#### 💬 Prompt para darle a Jetski:
```text
Jetski, integra en tiempo real el Asistente Financiero Inteligente (Libertad AI Copilot) con cotizador de crédito interactivo para los clientes.
```

#### ⚙️ Acciones que ejecuta Jetski de forma autónoma:
1. Ejecuta `uv run python3 inject_feature.py inject ai_assistant`.
2. Inyecta el widget flotante con branding de Libertad Financiera (`#0033a0`) en el slot semántico.
3. El usuario puede abrir el chat en el navegador, escribir *"Quiero un crédito de $30,000"* y ver la cotización interactiva en tiempo real.

---

### FASE 5: Reversión y Control en Vivo (Reset)

> **Narrativa para el Presentador**:
> *"Jetski mantiene el control absoluto del código, permitiéndonos iterar, probar hipótesis o regresar al clon base con un solo comando."*

#### 💬 Prompt para darle a Jetski:
```text
Jetski, restaura la página a su versión clonada base sin features inyectados.
```

#### ⚙️ Acciones que ejecuta Jetski de forma autónoma:
1. Ejecuta `uv run python3 inject_feature.py reset`.
2. Restaura `site/index.html` a su estado base original.

---

## 3. Hoja de Atajos de Comandos para el Operador

Si durante la demo deseas disparar los pasos directamente desde la terminal:

| Acción | Comando Terminal |
|--------|------------------|
| **Re-clonar desde cero** | `uv run --with beautifulsoup4 python3 clone_libertad.py` |
| **Levantar servidor** | `uv run python3 serve_libertad.py` |
| **Inyectar Header Moderno** | `uv run python3 inject_feature.py inject modern_header` |
| **Inyectar Asistente IA** | `uv run python3 inject_feature.py inject ai_assistant` |
| **Restaurar al Clon Base** | `uv run python3 inject_feature.py reset` |
| **Verificar puerto 8088** | `lsof -i :8088` |
