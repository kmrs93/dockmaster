# --- Stage 1: Build the Frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /build

COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./

# Override the outDir so it stays inside the build folder
RUN npx vite build --outDir dist

# --- Stage 2: Final Python Image ---
FROM python:3.12-slim

# Install system dependencies required for building psutil and running SSL
RUN apt-get update && apt-get install -y \
    ca-certificates \
    gcc \
    python3-dev \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (this includes your main.py)
COPY backend/ .

# Copy the COMPILED frontend into the static folder
COPY --from=frontend-build /build/dist ./static

EXPOSE 5555
# Replace: CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
