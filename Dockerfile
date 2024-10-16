# Use the official Python image with GPU support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get install -y poppler-utils && \
    apt-get clean

# Create and set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api-fast-api-unificado-com-conversao:app", "--host", "0.0.0.0", "--port", "8000"]