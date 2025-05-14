#!/bin/bash
# Script to run the video spider

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Starting Docker..."
    sudo systemctl start docker
    sleep 5  # Wait for Docker to start
fi

# Check if Splash container is running
if ! docker ps | grep -q "scrapinghub/splash"; then
    echo "Splash container is not running. Starting Splash..."
    docker run -d -p 8050:8050 scrapinghub/splash
    sleep 5  # Wait for Splash to start
fi

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the spider with the provided arguments
python src/run_spider.py "$@"
