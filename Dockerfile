# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl needed for health check in run.sh)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set PYTHONPATH so imports resolve correctly
ENV PYTHONPATH="/app"

# Create a non-root user (HF Spaces runs as uid 1000)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app

# Ensure the entrypoint script is executable
RUN chmod +x run.sh

# Switch to non-root user
USER user

# Expose port 7860 (Streamlit HUD - publicly accessible on HF Spaces)
# and port 8000 (FastAPI API - internal backend)
EXPOSE 7860 8000

# Launch via the startup script
CMD ["./run.sh"]