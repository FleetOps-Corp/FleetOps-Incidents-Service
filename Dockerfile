# Multi-stage Dockerfile for Incidents Microservice.

# Builder stage: Compiles dependencies
# Runtime stage: Minimal production image with non-root user


# Stage 1: Builder
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-alpine

# Install runtime dependencies only
RUN apk add --no-cache \
    postgresql-client \
    libpq

# Create non-root user
RUN addgroup -g 1000 incidents && \
    adduser -D -u 1000 -G incidents incidents

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Install Python dependencies
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set ownership to non-root user
RUN chown -R incidents:incidents /app

# Switch to non-root user
USER incidents

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "incidents.wsgi:application"]
