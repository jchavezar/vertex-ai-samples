# Recipe: Modernización de Libertad Financiera (Demo 3 Actos)

Esta receta automatiza la preparación, ejecución paso a paso y desmontaje de la demostración de modernización de **Libertad Financiera** (`https://www.libertad.com.mx/`) en 3 actos progresivos de alto impacto para clientes y ejecutivos.

---

## 🎯 Los 3 Actos de la Demostración

| Acto | Objetivo Demostrable | Tecnología / Comando |
| :--- | :--- | :--- |
| **Acto 1: Clonado Fiel Tal Cual** | Replicación 100% idéntica del portal de producción (AEM monolítico) con activos locales, carrusel responsivo y tipografía corporativa en local. | `uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step1_clone.py` |
| **Acto 2: Modernización UI/UX** | Desaturación de barra superior monolítica y reemplazo por un Mega-Menú interactivo desplegable categorizado (*Créditos*, *Inversión & Cuentas*, *Seguros*, *Empresas*) con efecto *glassmorphism*. | `uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step2_ux.py` |
| **Acto 3: Feature de IA (Vertex AI + Gemini)** | Navegador Inteligente con *Search-As-You-Type* en paralelo: Pista A (&lt;10ms) autocompletado + Pista B búsqueda indexada con **Vertex AI Search** y síntesis ejecutiva ultra-rápida con **Gemini 3.5 Flash Lite** en una ventana dinámica auto-expansible (460px &rarr; 740px). | `uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step3_ai.py` |

---

## 🏛️ Arquitectura y Recursos

- **Ubicación del Código:** `semiautonomous-agents/app-modernization`
- **Servidor Local:** `serve_libertad.py` (Multi-threaded `ThreadingHTTPServer`, Puerto `8088`)
- **Herramienta de Inyección Modular:** `inject_feature.py` (Slots: `TOP_BAR`, `FLOATING_ASSISTANT`)
- **Motor de Búsqueda (GCP):**
  - Proyecto GCP: `vtxdemos` (Project Number: `254356041555`)
  - Engine ID: `libertad-search-navigator`
  - Data Store: `libertad-web-store` (Crawler del portal `libertad.com.mx/*`)
- **Modelo LLM de Síntesis:**
  - `gemini-3.5-flash-lite` (vía Vertex AI `us-central1` con fallback activo a `gemini-3.7-flash-lite`)
- **Navegación Continua (Smart 302 Redirect):**
  - Cualquier ruta relativa a páginas no clonadas (`/content/...`) es redirigida transparentemente a `https://www.libertad.com.mx/...` evitando errores 404.

---

## 🚀 Comandos Rápidos

### Preparar y Verificar Entorno
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/setup.py
```

### Ejecución de los Pasos
```bash
# Paso 1: Clon original idéntico
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step1_clone.py

# Paso 2: Inyección de UI/UX Moderna (Mega-Menú)
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step2_ux.py

# Paso 3: Activación y prueba del Navegador IA
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step3_ai.py
```

### Teardown / Limpieza
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/teardown.py
```
