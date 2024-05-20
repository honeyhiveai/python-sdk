# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Update package list and install gcc and other necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app

RUN pip install --no-cache-dir -r tests/requirements.txt
RUN pip install --no-cache-dir -e .

CMD ["sh", "-c", "pytest -rA tests/api && pytest -rA tests/tracers && pytest -rA tests/test_hh_tracer.py"]
