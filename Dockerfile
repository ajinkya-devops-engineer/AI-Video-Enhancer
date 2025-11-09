# ==========================
# Stage 1: Build environment
# ==========================
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /app/wheels


# ==========================
# Stage 2: Runtime image
# ==========================
FROM python:3.10-slim AS runtime

# Set working directory
WORKDIR /app

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels and install them
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application source
COPY . .

# Create necessary directories
RUN mkdir -p uploads output models

# Expose Streamlit default port
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Healthcheck to verify Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
