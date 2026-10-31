# SMARTLEAD AI - Production Container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Initialize DB, generate baseline data, and train ML model
RUN python scripts/init_db.py && \
    python scripts/generate_data.py --scale small && \
    python scripts/train_ml.py

EXPOSE 8000 8501

# Default startup script or command
CMD ["sh", "-c", "python scripts/run_backend.py & streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0"]
