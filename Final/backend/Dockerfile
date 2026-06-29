# ====================================================================
# RADIX Intelligence Backend Dockerfile
# Place in: Final/backend/Dockerfile
# ====================================================================

FROM python:3.13-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY . .

# Expose API and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Default command starts the FastAPI server
CMD ["python", "main.py"]
