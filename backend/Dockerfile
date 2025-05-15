# Use a stable Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variable
ENV PORT=8080

# Expose the port that Fly.io will route traffic to
EXPOSE 8080

# Start the Flask app and bind to 0.0.0.0 (important!)
CMD ["python", "app.py"]
