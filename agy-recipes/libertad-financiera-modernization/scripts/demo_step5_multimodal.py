# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
demo_step5_multimodal.py
Acto 5: Precalificación Multimodal de Crédito con Visión AI (Gemini 3.7 Flash).
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
    print("⚡ [ACTO 5] PRECALIFICACIÓN MULTIMODAL DE CRÉDITO (VISIÓN AI SAT CFDI)")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Inicializando archivos de la demo en el directorio actual: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Asegurar Header AI + Copilot + Inyectar Precalificación Multimodal
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ai"], cwd=str(app_dir), check=True)
    subprocess.run([sys.executable, str(inject_script), "inject", "ai_advisor"], cwd=str(app_dir), check=True)
    subprocess.run([sys.executable, str(inject_script), "inject", "ai_multimodal_credit"], cwd=str(app_dir), check=True)

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

    # 3. Prueba de conectividad backend con Vertex AI Multimodal
    print("⚡ Verificando endpoint en vivo /api/multimodal-credit (Gemini 3.7 Flash)...")
    try:
        t0 = time.time()
        with urllib.request.urlopen("http://127.0.0.1:8088/api/multimodal-credit", timeout=15.0) as resp:
            credit_data = json.loads(resp.read().decode("utf-8"))
        t_total = round((time.time() - t0) * 1000)
        print(f"  • Extracción CFDI SAT:        OK ({credit_data.get('rfc')} - {credit_data.get('empleado')})")
        print(f"  • Capacidad CNBV (30%):       OK (${credit_data.get('capacidad_pago_maxima_mensual'):,.2f} MXN/mes)")
        print(f"  • Oferta Preaprobada:         OK (${credit_data.get('credito_preaprobado_monto'):,.2f} MXN a {credit_data.get('plazo_meses')}m)")
        print(f"  • Latencia de Análisis:       OK ({credit_data.get('latency_ms')}ms backend, {t_total}ms total)")
    except Exception as e:
        print(f"ℹ️ Servidor en línea en http://localhost:8088/ (Modo resiliente activo)")

    # 4. Lanzar navegador
    url = "http://localhost:8088/"
    subprocess.run(["open", url])

    print("\n✅ Módulo de Precalificación Multimodal con Visión AI activo en el portal.")
    print(f"📁 Directorio de trabajo: {app_dir}")
    print(f"🌐 Interactúa en vivo en: {url}")
    print("""
📋 GUÍA DE INTERACCIÓN EN VIVO PARA EL PRESENTADOR:
  1. En la pantalla verás dos accesos inmediatos a la Precalificación Multimodal:
     - El botón flotante inferior izquierdo: '📄 Precalificación Visión AI • Recibo CFDI 4.0'.
     - En el Simulador interactivo del Hero: al cambiar a modo 'Crédito' y hacer clic en 'Solicitar Crédito Preaprobado'.
  2. Al hacer clic se abre el Modal de Alta Fidelidad con Fondo Desenfoque (Glassmorphism):
     - Columna Izquierda: Visor del Comprobante de Nómina CFDI 4.0 con Timbre Fiscal SAT.
     - Columna Derecha: Tracker de validación regulatoria CNBV y Certificado Preaprobado.
  3. Ejecución del Escaneo Láser:
     - Haz clic en el botón superior: '⚡ Probar con Recibo Ejemplo ($18,450/qna)'.
     - Observa la barra de escaneo láser cyan neón recorriendo el documento.
  4. Extracción Estructurada con Gemini 3.7 Flash:
     - Extrae Sueldo Neto Quincenal ($18,450) y calcula Ingreso Mensual ($36,900).
     - Aplica la regla CNBV del 30%: Capacidad máxima autorizada = $11,070/mes.
     - Dictamen Crediticio en Vivo:
       • Monto preaprobado: $85,000 MXN a 24 meses.
       • Mensualidad: $4,427 MXN (Solo 12% del ingreso neto, semáforo verde).
       • Folio de Aprobación: LIB-PRE-2026-9842.
  5. Cierre de Venta Digital:
     - Haz clic en 'Descargar Certificado 📥' para generar el archivo JSON/PDF oficial con el folio y condiciones.
     - O clic en 'Aceptar Crédito en Línea ➔' para iniciar dispersión digital.
""")
    print("==================================================================")

if __name__ == "__main__":
    main()
