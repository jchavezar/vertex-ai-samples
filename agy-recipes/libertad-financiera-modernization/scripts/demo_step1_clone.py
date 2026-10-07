# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
demo_step1_clone.py
Acto 1: Despliegue del Clon 100% fiel de Libertad Financiera tal cual (Baseline AEM).
"""

import sys
import socket
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_APP_DIR = REPO_ROOT / "semiautonomous-agents" / "app-modernization"
SCAFFOLD_SCRIPT = BASE_DIR / "scripts" / "scaffold_workspace.py"

def main():
    print("==================================================================")
    print("🎬 [ACTO 1] CLONADO TAL CUAL: BASELINE IDÉNTICO LIBERTAD FINANCIERA")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    # If cwd doesn't have inject_feature.py, scaffold it so files appear in explorer
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Inicializando archivos de la demo en el directorio actual: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Reset index.html to pristine original
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(app_dir), check=True)

    # 2. Ensure server is running for this specific workspace
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

    # 3. Launch browser to localhost:8088
    url = "http://localhost:8088/"
    subprocess.run(["open", url])

    print("\n✅ Portal restablecido a su clonado fiel tal cual (AEM legado).")
    print(f"📁 Directorio de trabajo: {app_dir}")
    print(f"🌐 Visualizando en navegador: {url}")
    print("""
📋 PUNTOS CLAVE PARA EL PRESENTADOR:
  1. Fidelidad Visual 100%: Replicación exacta del portal oficial de producción (libertad.com.mx).
  2. Arquitectura Monolítica Legada: AEM 6.x con jQuery y clientlibs pesadas.
  3. Diagnóstico UX: Barra de navegación saturada con más de 8 accesos horizontales apretados.
  4. Cero dependencias rotas: Carrusel funcional, tipografías y branding corporativo intactos.
""")
    print("==================================================================")

if __name__ == "__main__":
    main()
