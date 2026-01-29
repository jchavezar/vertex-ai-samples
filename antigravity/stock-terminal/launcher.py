import subprocess

print("Starting services via shell...")

# Backend
# Note: we use nohup and & inside the shell command.
# We direct output to ../backend.log
backend_cmd = "nohup ./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &"
subprocess.Popen(backend_cmd, cwd="backend", shell=True, start_new_session=True)
print("Backend command issued.")

# Frontend
frontend_cmd = "nohup npm run dev > ../frontend.log 2>&1 &"
subprocess.Popen(frontend_cmd, cwd="frontend", shell=True, start_new_session=True)
print("Frontend command issued.")
