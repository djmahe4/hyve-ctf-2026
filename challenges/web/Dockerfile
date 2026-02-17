FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Create app directory
WORKDIR /app

# Copy application files
COPY challenges/web/ /app/
COPY utils/ /app/utils/

# Waiting entrypoint script
RUN apt-get update && apt-get install -y sed && \
    sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8080

# Run entrypoint script
CMD ["/app/entrypoint.sh"]
