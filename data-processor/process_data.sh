#!/bin/bash
# Script to run the data processor

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the processor with the provided arguments
python src/process_data.py "$@"
