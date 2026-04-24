FROM python:3.11-slim

# Install OS-level dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev libffi-dev git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install all dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

EXPOSE 8000

# Run the FastAPI app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
