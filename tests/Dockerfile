# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Update package list and install gcc and other necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libffi-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the test file
COPY __init__.py /app/

# Install honeyhive SDK from the tarball
COPY honeyhive.tar.gz /app/
RUN pip install honeyhive.tar.gz

# Install any additional requirements
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Run the test file
CMD ["python", "__init__.py"]
