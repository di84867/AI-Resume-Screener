# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - build-essential, python3-dev: for C-extensions
# - libgl1: for OpenCV/visualizations
# - libcairo2-dev, pkg-config: for reportlab/xhtml2pdf 
# - texlive-latex-base/extra, texlive-fonts-recommended: for LaTeX resume compilation
# - ffmpeg: for audio processing (SpeechRecognition/gTTS)
# - curl: for healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    ffmpeg \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# We use --no-cache-dir to keep the image size down
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download the spaCy model to ensure it's available offline in the container
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
# We disable CORS and XSRF protection to allow the container to be accessed externally
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
