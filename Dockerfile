# Use the official Python image.
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    ca-certificates \
    screen \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library if needed => too heavy and takes too long to build
# RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
#     tar -xzvf ta-lib-0.4.0-src.tar.gz && \
#     cd ta-lib && \
#     ./configure --prefix=/usr && \
#     make && \
#     make install && \
#     cd .. && \
#     rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your app runs on (if applicable)
# EXPOSE 8000

# Set the command to run main
# CMD ["python", "main.py"]

# Set the command to run strategies/depth.py
CMD ["python", "strategies/depth.py "]

