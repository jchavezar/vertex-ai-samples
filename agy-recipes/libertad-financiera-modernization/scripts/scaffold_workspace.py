# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
scaffold_workspace.py
Scaffolds the Libertad Financiera demo files directly into the active workspace directory.
"""

import sys
import shutil
from pathlib import Path

MASTER_DIR = Path("/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/app-modernization")

def main():
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    print(f"📦 Scaffolding Libertad Financiera demo files into: {target_dir}")

    if not MASTER_DIR.exists():
        print(f"❌ Error: Master directory {MASTER_DIR} does not exist.")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy site folder
    target_site = target_dir / "site"
    master_site = MASTER_DIR / "site"
    if master_site.exists():
        if target_site.exists():
            shutil.rmtree(target_site)
        shutil.copytree(master_site, target_site)
        print("  • Copied site/ assets and HTML.")

    # 2. Copy serve_libertad.py
    shutil.copy2(MASTER_DIR / "serve_libertad.py", target_dir / "serve_libertad.py")
    print("  • Copied serve_libertad.py (ThreadingHTTPServer + Vertex Search API).")

    # 3. Copy inject_feature.py
    shutil.copy2(MASTER_DIR / "inject_feature.py", target_dir / "inject_feature.py")
    print("  • Copied inject_feature.py (Modular Feature Injector).")

    # 4. Ensure site starts in pristine baseline
    inject_script = target_dir / "inject_feature.py"
    if inject_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(target_dir), stdout=subprocess.DEVNULL)
        print("  • Initialized pristine clone baseline (index.html).")

    print(f"\n✅ All demo files successfully created in {target_dir}!")
    print("   Your Explorer sidebar is now populated with the project.")

if __name__ == "__main__":
    main()
