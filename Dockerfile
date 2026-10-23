FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install essential build and runtime libraries (including OpenMP & GLib for RapidOCR / ONNX Runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-verify RapidOCR loads without error and pre-warm models
RUN python -c "from rapidocr_onnxruntime import RapidOCR; RapidOCR()"

# Copy backend application source code
COPY backend/ /app/backend/
COPY build.sh /app/

WORKDIR /app/backend

# Collect static files during build
RUN python manage.py collectstatic --no-input

EXPOSE 8000

# Run migrations and start production WSGI server
CMD ["sh", "-c", "python manage.py migrate --no-input && gunicorn autocart_core.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
