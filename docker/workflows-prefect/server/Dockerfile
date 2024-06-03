# server/Dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install --upgrade pip
RUN pip install prefect

# Set environment variables for Prefect
ENV PREFECT_API_URL="http://0.0.0.0:4200/api"

# Expose necessary ports
EXPOSE 4200
EXPOSE 8080

# Start the Prefect server
CMD ["prefect", "server", "start"]
