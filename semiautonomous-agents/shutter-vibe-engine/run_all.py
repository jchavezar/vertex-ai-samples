"""Run every capability probe sequentially and tee output to findings/run.log."""
from __future__ import annotations

import importlib.util
import sys
import time
import traceback
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMOS_DIR = ROOT / "demos"
LOG_PATH = ROOT / "findings" / "run.log"
LOG_PATH.parent.mkdir(exist_ok=True)


class Tee(io_target := __import__("io").TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
        return len(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def run_demo(path: Path) -> tuple[bool, float]:
    sys.path.insert(0, str(DEMOS_DIR))
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    start = time.perf_counter()
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        module.main()
        return True, time.perf_counter() - start
    except Exception:
        traceback.print_exc()
        return False, time.perf_counter() - start


def main() -> None:
    demos = sorted(DEMOS_DIR.glob("[0-9][0-9]_*.py"))
    with LOG_PATH.open("w") as fh:
        tee = Tee(sys.stdout, fh)
        with redirect_stdout(tee):
            print(f"=== Shutter Vibe Engine — full run @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
            results = []
            for demo in demos:
                print(f"\n\n>>> Running {demo.name}")
                ok, dur = run_demo(demo)
                status = "OK" if ok else "FAIL"
                print(f"<<< {demo.name}: {status} ({dur:.1f}s)")
                results.append((demo.name, status, dur))

            print("\n=== Summary ===")
            for name, status, dur in results:
                print(f"  {status:<4} {dur:6.1f}s  {name}")
    print(f"\nLog written to {LOG_PATH}")


if __name__ == "__main__":
    main()
