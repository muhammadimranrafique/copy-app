# Dockerfile for Railway deployment of FastAPI backend
# This builds from the root of the monorepo and deploys the backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only backend requirements first for better Docker layer caching
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ ./

# Create directories for generated files
RUN mkdir -p /app/invoices /app/receipts

# Expose port (Railway provides PORT env var)
EXPOSE 8080

# Run the FastAPI application
# Railway sets the PORT environment variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

