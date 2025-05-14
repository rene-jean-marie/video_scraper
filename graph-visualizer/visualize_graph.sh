#!/bin/bash
# Script to run the graph visualizer

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the visualizer with the provided arguments
python src/visualize.py "$@"
