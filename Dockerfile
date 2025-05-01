FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (faiss-cpu might need gcc, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    python -c "import streamlit" && \
    echo "✅ Dependencies installed and verified"

# Copy rest of the app
COPY . .

RUN chmod -R 755 /app

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
