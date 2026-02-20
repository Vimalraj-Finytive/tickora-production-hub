# Base image - lightweight and secure
FROM python:3.11-slim

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    systemd \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application code (FIXED: app.py to monitor.py)
COPY monitor.py .

# Streamlit port
EXPOSE 8501

# Run the application (FIXED: app.py to monitor.py)
CMD ["streamlit", "run", "monitor.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]