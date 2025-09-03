# Use Python 3.12
FROM python:3.12

# Set non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install corrected system dependencies needed for the powerful libraries
RUN apt-get update && apt-get install -y \
    # ---- Core Build & Utility Tools ----
    curl \
    nodejs \
    npm \
    # ---- Libraries for Python/JS Packages (e.g., lxml, pandas) ----
    build-essential \
    git \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set up the application directory
WORKDIR /app

# --- Install Python Dependencies ---
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Install Node.js Dependencies ---
COPY backend/package.json .
RUN npm install

# --- Copy Application Code ---
COPY frontend ./frontend/
COPY backend ./backend/

# Change ownership of the entire app to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set the final working directory to the backend
WORKDIR /app/backend

# Expose the port
EXPOSE 8080

# --- CORRECTED COMMAND ---
# Explicitly tell Gunicorn to add the parent directory to the Python path
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--pythonpath", "/app", "backend.app:app"]