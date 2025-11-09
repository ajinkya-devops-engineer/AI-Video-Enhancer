# Docker Deployment Guide

This guide explains how to run the AI Video Enhancer application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the Docker image:**
   ```bash
   docker build -t video-enhancer:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name ai-video-enhancer \
     -p 8501:8501 \
     -v ./uploads:/app/uploads \
     -v ./output:/app/output \
     -v ./models:/app/models \
     video-enhancer:latest
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

4. **Stop the container:**
   ```bash
   docker stop ai-video-enhancer
   docker rm ai-video-enhancer
   ```

## GPU Support (NVIDIA)

If you have an NVIDIA GPU and want to use GPU acceleration:

1. **Install NVIDIA Container Toolkit:**
   Follow the instructions at: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

2. **Use the GPU-enabled Docker Compose configuration:**
   Uncomment the `deploy` section in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

3. **Or run with Docker CLI:**
   ```bash
   docker run -d \
     --name ai-video-enhancer \
     --gpus all \
     -p 8501:8501 \
     -v ./uploads:/app/uploads \
     -v ./output:/app/output \
     -v ./models:/app/models \
     video-enhancer:latest
   ```

## Volume Mounts

The container uses three volume mounts for persistent data:

- **./uploads** - Stores uploaded video files
- **./output** - Stores enhanced video files
- **./models** - Stores downloaded AI models (cached for faster startup)

## Container Management

### View logs:
```bash
docker-compose logs -f
# or
docker logs -f ai-video-enhancer
```

### Restart the container:
```bash
docker-compose restart
# or
docker restart ai-video-enhancer
```

### Rebuild after code changes:
```bash
docker-compose up -d --build
# or
docker build -t video-enhancer:latest . && docker restart ai-video-enhancer
```

## Environment Variables

You can customize the following environment variables in `docker-compose.yml`:

- `STREAMLIT_SERVER_PORT` - Port for Streamlit server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS` - Server address (default: 0.0.0.0)
- `STREAMLIT_SERVER_HEADLESS` - Run in headless mode (default: true)
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS` - Disable usage stats (default: false)

## Troubleshooting

### Container won't start:
```bash
docker-compose logs
```

### Out of memory:
Increase Docker's memory limit in Docker Desktop settings or add memory limits to docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

### Permission issues with volumes:
Ensure the mounted directories have proper permissions:
```bash
chmod -R 755 uploads output models
```

## Image Information

- **Base Image:** python:3.12-slim
- **Python Version:** 3.12
- **Exposed Port:** 8501
- **Working Directory:** /app

## Health Check

The container includes a health check that runs every 30 seconds to ensure the application is running properly.

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' ai-video-enhancer
```
