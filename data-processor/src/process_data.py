#!/usr/bin/env python3
"""
Main entry point for the video data processor.
This module provides a command-line interface for processing video data.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Import the processor
from processors.video_data_processor import process_video_data

def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Video Data Processor')
    
    # Input options
    parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    
    # Output options
    parser.add_argument('--output-dir', '-o', default='processed_data', help='Directory to save processed data')
    
    # Processing options
    parser.add_argument('--no-clean', action='store_true', help='Skip data cleaning')
    parser.add_argument('--no-analyze', action='store_true', help='Skip data analysis')
    parser.add_argument('--formats', default='csv,json,gexf', help='Comma-separated list of export formats')
    
    # Logging options
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase verbosity')
    
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    
    setup_logging(log_level)
    logger = logging.getLogger('data_processor')
    
    # Parse export formats
    export_formats = [f.strip() for f in args.formats.split(',') if f.strip()] if args.formats else None
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process data
    logger.info(f"Processing data from {args.input}")
    
    results = process_video_data(
        input_path=args.input,
        output_dir=args.output_dir,
        clean=not args.no_clean,
        analyze=not args.no_analyze,
        export_formats=export_formats
    )
    
    # Print analysis results
    if results['success'] and results['analysis']:
        print("\nAnalysis Results:")
        print(json.dumps(results['analysis'], indent=2))
    
    # Print export paths
    if results['success'] and results['exports']:
        print("\nExported files:")
        for fmt, path in results['exports'].items():
            print(f"  {fmt}: {path}")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    sys.exit(main())
