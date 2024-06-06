# Use an official Python runtime as a parent image
FROM python:3.10-slim AS jsl

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt before other files to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Define the entry point for your application
ENTRYPOINT ["python", "jsl.py"]
