# Demo Libertad Financiera: Modernización en 3 Actos

Este flujo de trabajo permite orquestar y ejecutar de forma automatizada los 3 actos de la demostración de modernización de Libertad Financiera.

---

## ⚡ Preparación y Verificación de Entorno

// turbo
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/setup.py
```

---

## 🎬 Acto 1: Desplegar Clon Tal Cual (Baseline AEM)

Restablece el sitio al clon idéntico original de Libertad Financiera y lo visualiza en el navegador.

// turbo
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step1_clone.py
```

---

## 🎨 Acto 2: Inyectar Modernización UI/UX (Mega-Menú)

Transforma el header monolítico en un Mega-Menú interactivo categorizado con efecto glassmorphism.

// turbo
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step2_ux.py
```

---

## 🧠 Acto 3: Demostrar Navegador IA (Vertex AI + Gemini 3.5 Flash Lite)

Activa el Search-As-You-Type en paralelo con sugerencias (<10ms), ventana dinámica (460px -> 740px) y síntesis ejecutiva.

// turbo
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/demo_step3_ai.py
```

---

## 🧹 Limpieza (Teardown)

// turbo
```bash
uv run agy-recipes/libertad-financiera-modernization/scripts/teardown.py
```
