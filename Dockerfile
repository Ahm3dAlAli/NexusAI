# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the package files
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Run the application
ENTRYPOINT ["paper-agent"]
CMD ["--interactive"]
