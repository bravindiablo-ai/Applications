import requests, os, json
BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")
print("Using API_BASE:", BASE)
try:
    r = requests.get(BASE.replace("/api/v1","") + "/healthz", timeout=5)
    print("healthz:", r.status_code, r.text)
except Exception as e:
    print("healthz failed", e)
# Note: other endpoints require a running backend and auth token; run these locally after backend start.
