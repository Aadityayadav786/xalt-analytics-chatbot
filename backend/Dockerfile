# Use a stable Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port (Fly.io or Railway will use this)
EXPOSE 8080
ENV PORT=8080

# Start the Flask app
CMD ["python", "app.py"]
