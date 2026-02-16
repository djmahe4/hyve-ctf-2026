FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Create app directory
WORKDIR /app

# Waiting entrypoint script
COPY challenges/web/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8080

# Run entrypoint script
CMD ["/entrypoint.sh"]
