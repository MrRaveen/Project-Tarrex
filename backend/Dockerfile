# Dockerfile.api
# Builds a Docker image for the backend API service using Gunicorn
# FROM python:3.11-slim

# # Set workdir
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install gunicorn
# RUN pip install flower
# RUN pip install Flask-Caching

# # Copy the rest of the app
# COPY . .

# # Expose API port
# EXPOSE 8000

# # Start the API
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]


# Dockerfile.api
# Builds a Docker image for the backend API service using Gunicorn
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN pip install flower
RUN pip install Flask-Caching

# Copy the backend code
COPY backend/ .

# Set Python path
ENV PYTHONPATH=/app
ENV DB_NAME=tarrex

# Expose API port
EXPOSE 8000

# Start the API
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]

