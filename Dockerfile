# Base image
FROM python:3.12-slim as base

# Set working directory
ENV APP_ROOT /app
WORKDIR ${APP_ROOT}

# Optimize layer caching for dependency installation
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Add non-root user for security
RUN useradd -r -s /bin/false appuser
USER appuser

# Set environment variables
ENV PYTHONPATH "${PYTHONPATH}:${APP_ROOT}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the application
ENTRYPOINT ["python", "main.py"]
