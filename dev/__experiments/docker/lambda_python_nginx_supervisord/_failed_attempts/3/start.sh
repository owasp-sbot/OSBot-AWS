#!/bin/sh

# Start Flask app on port 5000
python3 flask_app.py &

# Start FastAPI app on port 8000
uvicorn fastapi_app:app --port 8000 &

# Start the Lambda adapter (the main process for AWS Lambda)
gunicorn -b :8080 -w 1 lambda_function:handler
