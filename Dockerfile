FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Set default port (can be overridden by environment variable from docker-compose.yml)
ENV NOTIFICATION_SERVICE_PORT=7000

# Run the application (using shell form to expand environment variable at runtime)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${NOTIFICATION_SERVICE_PORT:-7000}"]

