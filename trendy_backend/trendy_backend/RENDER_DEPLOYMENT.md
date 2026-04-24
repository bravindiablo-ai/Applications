pip install --no-cache-dir -r requirements.txt
```

This command installs all dependencies listed in `requirements.txt` without using the pip cache, which prevents potential caching issues and ensures fresh package installation on each build.

## Start Configuration

The start command for Render is:

```
uvicorn app.main:app --host 0.0.0.0 --port 10000