#!/bin/sh
set -e

# If a run_backend.py exists and RUN_BACKEND is set to '1' or 'true', run it.
if [ -f "/app/run_backend.py" ]; then
  case "${RUN_BACKEND:-}" in
    1|true|TRUE|True)
      echo "Starting backend via run_backend.py"
      exec python /app/run_backend.py
      ;;
  esac
fi

# Default to uvicorn (app.main:app)
echo "Starting uvicorn: app.main:app"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
