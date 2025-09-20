FROM python:3.12-slim

WORKDIR /app

# System deps (optional but good to have for CA roots & timezones)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

# Create dirs for state and creds
RUN mkdir -p /app/state /app/creds

ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
