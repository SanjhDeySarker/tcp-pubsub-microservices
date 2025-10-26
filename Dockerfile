# Use minimal Python image
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pubsub/ ./pubsub/
COPY services/ ./services/
COPY run_broker.py .

# Expose broker port
EXPOSE 9000

# Run the broker
CMD ["python", "run_broker.py"]
