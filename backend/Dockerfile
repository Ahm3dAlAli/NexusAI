# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ .
COPY .env .
COPY nexusai/ ./nexusai

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]