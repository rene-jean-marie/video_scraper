#!/bin/bash
# Script to run the video downloader

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the downloader with the provided arguments
python src/download_videos.py "$@"
