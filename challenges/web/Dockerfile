FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Copy application files
COPY app.py .
COPY init_db.py .

# Initialize database
RUN python init_db.py

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "app.py"]
