# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
demo_step2_ux.py
Acto 2: Modernización UI/UX del Header (Mega-Menú Desplegable con Glassmorphism).
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
    print("🎨 [ACTO 2] MODERNIZACIÓN UI/UX: MEGA-MENÚ DESPLEGABLE Y NAVEGACIÓN")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Inicializando archivos de la demo en el directorio actual: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # Inyectar modern_header_ux (Puro UI/UX)
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ux"], cwd=str(app_dir), check=True)

    # Asegurar servidor corriendo para este workspace
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

    url = "http://localhost:8088/"
    subprocess.run(["open", url])

    print("\n✅ Inyección modular UI/UX 'modern_header_ux' completada exitosamente.")
    print(f"📁 Directorio de trabajo: {app_dir}")
    print(f"🌐 Actualizado en navegador: {url}")
    print("""
📋 PUNTOS CLAVE PARA EL PRESENTADOR:
  1. Desaturación Cognitiva: Se eliminó el apiñamiento de más de 8 enlaces en la cabecera.
  2. Mega-Menú Categorizado: 4 accesos claros (Créditos, Inversión & Cuentas, Seguros, Empresas).
  3. Estética Glassmorphism: Fondo translúcido con blur (backdrop-filter) y sombras suaves.
  4. Reversibilidad Instantánea: Con un solo comando ('inject_feature.py reset') el sitio vuelve al original.
  5. Preparación para IA: Integra el dock de búsqueda Search-As-You-Type en la barra.
""")
    print("==================================================================")

if __name__ == "__main__":
    main()
