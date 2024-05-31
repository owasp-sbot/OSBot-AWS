# agent/Dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install --upgrade pip
RUN pip install prefect

# Set environment variables for Prefect
ENV PREFECT_API_URL="https://...."
ENV PREFECT_API_KEY="<your_api_key_here>"
ENV PREFECT_WORK_QUEUE_NAME="default"

# Expose necessary ports
EXPOSE 8080

# Start the Prefect worker
CMD ["prefect", "worker", "start", "--work-queue", "default"]
