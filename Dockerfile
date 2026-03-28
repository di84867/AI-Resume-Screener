# Use an official Python runtime as a parent image
# Using bullseye instead of slim/trixie for more stable package names
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - build-essential, python3-dev, etc. for compiling C-extensions (pycairo)
# - libgl1 for OpenCV/visualizations
# - libcairo2-dev, pkg-config for reportlab/xhtml2pdf
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Health check to ensure the application is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
