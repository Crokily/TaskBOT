# Use the official Python image as a base
FROM python:3.12.0-slim

# Set working directory
WORKDIR /app
# Copy application files to the container
COPY . /app

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

CMD ["python", "main.py"] 