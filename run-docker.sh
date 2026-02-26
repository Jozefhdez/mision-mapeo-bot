#!/bin/bash

echo "Building Docker image"
docker build -t mision-mapeo-bot .

# Stop and remove existing container if running
echo "Stopping existing container..."
docker stop mision-mapeo-bot 2>/dev/null || true
docker rm mision-mapeo-bot 2>/dev/null || true

# Run container
echo "Starting container..."
docker run -d \
  --name mision-mapeo-bot \
  --restart unless-stopped \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  mision-mapeo-bot

echo "Container started!"
echo ""
echo "View logs: docker logs -f mision-mapeo-bot"
echo "Stop: docker stop mision-mapeo-bot"
echo "Restart: docker restart mision-mapeo-bot"
