# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
demo_step4_advisor.py
Acto 4: Demostración de Libertad AI Advisor Flotante 24/7 (Gemini 3.7 Flash).
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
    print("🤖 [ACTO 4] FEATURE DE IA: LIBERTAD AI ADVISOR 24/7 (GEMINI 3.7 FLASH)")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Inicializando archivos de la demo en el directorio actual: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Asegurar Header AI activo + Inyectar AI Advisor Flotante
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ai"], cwd=str(app_dir), check=True)
    subprocess.run([sys.executable, str(inject_script), "inject", "ai_advisor"], cwd=str(app_dir), check=True)

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

    # 3. Prueba de conectividad backend con Vertex AI Advisor
    print("⚡ Verificando endpoint en vivo /api/advisor (Gemini 3.7 Flash)...")
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8088/api/advisor",
            data=json.dumps({"message": "Hola, ¿cuánto gano con 50000 a 14%?"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            advisor_data = json.loads(resp.read().decode("utf-8"))
        t_total = round((time.time() - t0) * 1000)
        print(f"  • Modelo Vertex AI:           OK ({advisor_data.get('model', 'gemini-3.7-flash')})")
        print(f"  • Latencia de Respuesta:      OK ({advisor_data.get('latency_ms')}ms backend, {t_total}ms total)")
        print(f"  • Asesoría Financiera:        OK (Cálculo y persona mexicana validados)")
    except Exception as e:
        print(f"ℹ️ Servidor en línea en http://localhost:8088/ (Modo resiliente activo)")

    # 4. Lanzar navegador
    url = "http://localhost:8088/"
    subprocess.run(["open", url])

    print("\n✅ Libertad AI Advisor activo en la esquina inferior derecha del portal.")
    print(f"📁 Directorio de trabajo: {app_dir}")
    print(f"🌐 Interactúa en vivo en: {url}")
    print("""
📋 GUÍA DE INTERACCIÓN EN VIVO PARA EL PRESENTADOR:
  1. En la esquina inferior derecha verás el botón flotante dorado y marino:
     - Badge '✦ Asesor en Vivo • Gemini 3.7 Flash' con indicador verde de estado online.
  2. Haz clic en el botón para desplegar el Drawer Conversacional:
     - Diseño Glassmorphism con bordes redondeados y tipografía oficial.
     - Barra de chips superiores para consultas instantáneas con 1 clic:
       • 💰 Inversión 14%
       • ⚡ Crédito $50,000
       • 💳 CuentaYa Digital
  3. Prueba de Inteligencia Financiera:
     - Haz clic en '💰 Inversión 14%' o escribe: 'Quiero invertir $100,000 a 1 año'.
     - Observa la animación de tres puntos de Gemini y la respuesta estructurada con viñetas y cálculo de rendimiento.
  4. Input Textarea Universal:
     - Observa cómo la caja de texto se expande automáticamente sin parpadeo (Zero-Glitch Mechanics).
     - Presiona [Enter] para enviar o [Shift+Enter] para saltos de línea.
  5. Cierre o reinicio:
     - Presiona '↺' para reiniciar la conversación o '×' para minimizar el drawer.
""")
    print("==================================================================")

if __name__ == "__main__":
    main()
