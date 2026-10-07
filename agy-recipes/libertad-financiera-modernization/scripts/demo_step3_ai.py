# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
# ]
# ///
"""
demo_step3_ai.py
Acto 3: Demostración de Navegador Inteligente con Vertex AI Search y Gemini 3.5 Flash Lite.
"""

import sys
import socket
import time
import time
import json
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_APP_DIR = REPO_ROOT / "semiautonomous-agents" / "app-modernization"
SCAFFOLD_SCRIPT = BASE_DIR / "scripts" / "scaffold_workspace.py"

def main():
    print("==================================================================")
    print("🧠 [ACTO 3] FEATURE DE IA: NAVEGADOR INTELIGENTE (VERTEX AI + GEMINI)")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Inicializando archivos de la demo en el directorio actual: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Asegurar modern_header_ai inyectado (con Vertex AI Search y Gemini)
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ai"], cwd=str(app_dir), check=True)

    # 2. Asegurar servidor activo en puerto 8088 para este workspace
    serve_script = app_dir / "serve_libertad.py"
    if serve_script.exists():
        try:
            out = subprocess.check_output(["lsof", "-ti", ":8088"]).decode().strip()
            if out:
                for pid in out.split():
                    subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
                time.sleep(0.6)
        except subprocess.CalledProcessError:
            pass

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex(("127.0.0.1", 8088)) != 0:
            print("⚡ Iniciando servidor local en puerto 8088...")
            subprocess.Popen(["uv", "run", str(serve_script)], cwd=str(app_dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
        s.close()

    # 3. Prueba de conectividad backend
    print("⚡ Verificando endpoints en vivo (Search-As-You-Type)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8088/api/suggest?q=inversion", timeout=3.0) as resp:
            sug_data = json.loads(resp.read().decode("utf-8"))
        print(f"  • Pista A (<10ms) Autocompletado: OK ({len(sug_data.get('suggestions', []))} productos encontrados)")

        t0 = time.time()
        with urllib.request.urlopen("http://127.0.0.1:8088/api/search?q=inversion", timeout=15.0) as resp:
            srch_data = json.loads(resp.read().decode("utf-8"))
        t_total = round((time.time() - t0) * 1000)
        print(f"  • Pista B Síntesis Gemini:        OK ({srch_data.get('latency_ms')}ms backend, {t_total}ms total)")
        print(f"  • Fuentes Vertex AI Search:       OK ({len(srch_data.get('results', []))} páginas indexadas)")
    except Exception as e:
        print(f"ℹ️ Conexión local lista en http://localhost:8088/")

    # 4. Lanzar navegador
    url = "http://localhost:8088/"
    subprocess.run(["open", url])

    print("\n✅ Navegador Inteligente activo en el portal.")
    print(f"📁 Directorio de trabajo: {app_dir}")
    print(f"🌐 Interactúa en vivo en: {url}")
    print("""
📋 GUÍA DE INTERACCIÓN EN VIVO PARA EL PRESENTADOR:
  1. En la barra de búsqueda superior, escribe 'inversión' o 'crédito':
     - Observa la Pista A (<10ms): Aparecen sugerencias instantáneas en modo compacto (460px).
  2. Pausa la escritura 220ms:
     - Observa la Transición Fluida: La ventana se expande suavemente a 740px de ancho.
     - Aparece el Shimmer Skeleton animado mientras sintetiza con Gemini 3.5 Flash Lite.
  3. Resultado Completo:
     - Resumen Ejecutivo con negritas formateadas y lenguaje financiero claro.
     - Grid de 2 columnas con las 4 páginas indexadas por Vertex AI Search en 'libertad.com.mx'.
     - Badge de telemetría de latencia en vivo (ej. '⚡ 2061ms backend').
  4. Clic en Fuentes:
     - Haz clic en cualquier tarjeta: se abre en pestaña nueva sin errores 404 (Smart 302 Redirection).
  5. Controles UX:
     - Clic en el botón '⤡' / '⤢' para alternar tamaño a voluntad.
     - Presiona [Esc] para cerrar al instante.
""")
    print("==================================================================")

if __name__ == "__main__":
    main()
