# Use a Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV ARGOS_API_HOME /usr/src/app

# Set the working directory
WORKDIR $ARGOS_API_HOME

# Copy only the requirements file first to optimize caching
COPY requirements.txt .

# Install system dependencies (needed by Argos/NMT libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Gunicorn will listen on
EXPOSE 10000

# Command to run the application using Gunicorn
# This command automatically runs argos_core.py, which pre-loads the models.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "app:app"]