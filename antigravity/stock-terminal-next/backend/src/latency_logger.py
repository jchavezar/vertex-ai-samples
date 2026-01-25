import datetime
import time
import json
import os

# Terminal Colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

class LatencyLogger:
    def __init__(self):
        self.start_times = {}
        self.last_mark = {}
        self.events = {} # key -> list of (message, step_elapsed, total_elapsed)

    def log(self, phase, message, level="INFO", color=BLUE):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        level_str = f"[{level}]"
        phase_str = f"[{phase.upper()}]"
        
        print(f"{BOLD}{CYAN}[{ts}]{RESET} {color}{BOLD}{phase_str}{RESET} {message}", flush=True)

    def start(self, key):
        self.start_times[key] = time.perf_counter()
        self.last_mark[key] = time.perf_counter()
        self.events[key] = []
        self.log("TIMER", f"Timer started for {key}", level="DEBUG", color=MAGENTA)

    def mark(self, key, message):
        if key not in self.start_times:
            self.start(key)
            return

        now = time.perf_counter()
        total_elapsed = (now - self.start_times[key]) * 1000
        step_elapsed = (now - self.last_mark[key]) * 1000
        self.last_mark[key] = now
        
        # Store event
        if key not in self.events: self.events[key] = []
        self.events[key].append((message, step_elapsed, total_elapsed))
        
        elapsed_str = f"{YELLOW}(+{step_elapsed:.1f}ms / {total_elapsed:.1f}ms total){RESET}"
        self.log(key, f"{message} {elapsed_str}", color=GREEN)

    def error(self, key, message):
        self.log(key, message, level="ERROR", color=RED)
        
    def dump_latency_summary(self, key):
        """Prints a structured summary block that can be parsed."""
        if key not in self.start_times or key not in self.events:
            return
            
        total_time = (time.perf_counter() - self.start_times[key])
        
        print(f"\n[LATENCY SUMMARY] {key}")
        print(f"TOTAL: {total_time:.3f}s")
        print("EVENTS:")
        for msg, step, total in self.events[key]:
            print(f"  - [{total/1000:.3f}s] {msg} (+{step:.1f}ms)")
        print("[/LATENCY SUMMARY]\n", flush=True)

# Global Instance
logger = LatencyLogger()
