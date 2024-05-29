# Dockerfile for Python 3.12.3
FROM diniscruz/osbot_utils:latest

# Set working directory
WORKDIR /app

# Copy application code
COPY ./requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN pip install -e .

# Command to run your tests
CMD ["pytest", "tests"]
