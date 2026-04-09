FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and static files
COPY app/ ./app/
COPY static/ ./static/

# Expose port 80 for the web server
EXPOSE 80

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
