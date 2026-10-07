#!/usr/bin/env python3
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).parent / "demo_step4_advisor.py"), run_name="__main__")
