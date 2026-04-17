# ============================================================================
# Ocean Sentinel V3.0 - Dockerfile ML Pipeline
# ============================================================================
# Agent IA & Scientifique - Pipeline Machine Learning
# LSTM + Isolation Forest + Formules UNESCO
# ============================================================================

FROM python:3.11-slim

LABEL maintainer="Ocean Sentinel Team"
LABEL version="3.0.0"
LABEL description="Pipeline ML pour prédiction et détection d'anomalies"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY requirements-ml.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements-ml.txt

# Copie des scripts
COPY scripts/ml_pipeline.py /app/
COPY scripts/__init__.py /app/ 2>/dev/null || echo "No __init__.py found"

# Création des répertoires
RUN mkdir -p /models /logs && \
    chmod 755 /models /logs

# Utilisateur non-root
RUN useradd -m -u 1000 oceansentinel && \
    chown -R oceansentinel:oceansentinel /app /models /logs

USER oceansentinel

# Healthcheck
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import tensorflow; import sklearn; print('OK')"

# Point d'entrée
ENTRYPOINT ["python", "/app/ml_pipeline.py"]

# Arguments par défaut
CMD ["--mode", "full"]
