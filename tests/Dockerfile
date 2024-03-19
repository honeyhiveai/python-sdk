# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app

RUN pip install --no-cache-dir -r tests/requirements.txt
RUN pip install --no-cache-dir -e .

CMD ["pytest", "-rA", "tests/"]
