FROM python:3.11-slim

# ---------------------------
# System-level dependencies
# ---------------------------
# Needed for psycopg2, Postgres, and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    make \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Python settings
# ---------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ---------------------------
# Install dependencies
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# Copy your entire project
# (after installing deps for caching)
# ---------------------------
COPY . .

# ---------------------------
# Expose FastAPI port
# ---------------------------
EXPOSE 8000

# ---------------------------
# Start the server
# ---------------------------
# NOTE: No --reload here → handled in docker-compose for DEV
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]