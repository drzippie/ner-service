# Spanish NER Service - Multi-stage Docker build
# Supports both spaCy and MITIE backends with configurable default

# Build stage for downloading models
FROM python:3.11-slim as model-downloader

# Install required tools for downloading
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /models

# Copy download script
COPY download_mitie_models.sh .
RUN chmod +x download_mitie_models.sh

# Download MITIE models
RUN ./download_mitie_models.sh

# Main application stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NER_BACKEND=mitie
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-mitie.txt ./

# Install Python dependencies
# Install both spaCy and MITIE dependencies for flexibility
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-mitie.txt

# Download spaCy models
RUN python -m spacy download es_core_news_md && \
    python -m spacy download es_core_news_sm

# Copy MITIE models from build stage
COPY --from=model-downloader /models/MITIE-models ./MITIE-models

# Copy application code
COPY src/ ./src/
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash ner-user && \
    chown -R ner-user:ner-user /app
USER ner-user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Default command - start web server
CMD ["python", "-m", "src.web_server"]