nohup .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8008 > backend.log 2>&1 &
