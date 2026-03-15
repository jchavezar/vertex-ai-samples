import subprocess
import os

env = os.environ.copy()
env["PYTHONPATH"] = "."
p = subprocess.Popen(["python", "-m", "mcp_service.mcp_server"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    stdout, stderr = p.communicate(timeout=5)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
except Exception as e:
    p.kill()
    stdout, stderr = p.communicate()
    print("Timeout! STDOUT:", stdout)
    print("Timeout! STDERR:", stderr)
