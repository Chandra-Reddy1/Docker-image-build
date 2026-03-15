# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY welcome.py .

# Expose port
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
