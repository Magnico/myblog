# Base image
FROM python:3.9-slim-buster

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt update && apt install build-essential libpq-dev -y
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    musl-dev \
    libpq-dev \
    redis-server\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt



# Copy app code
COPY . .

RUN chmod +x /app/docker-entrypoint.sh

# Expose ports
EXPOSE 8000
EXPOSE 5432
EXPOSE 6379
