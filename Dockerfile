FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

RUN pip install -r requirements.txt

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/templates && \
    chown -R appuser:appuser /app

# Security: Remove shell access for appuser
RUN usermod -s /usr/sbin/nologin appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1


CMD ["python", "app.py"]