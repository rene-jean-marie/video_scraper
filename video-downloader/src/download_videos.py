#!/usr/bin/env python3
"""
Main entry point for the video downloader.
This module provides a command-line interface for downloading videos.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Import the downloader
from downloader.video_downloader import download_videos

def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Video Downloader')
    
    # Input sources (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', help='URL of the video to download')
    input_group.add_argument('--urls', help='Comma-separated list of video URLs')
    input_group.add_argument('--input-file', help='File containing video URLs (one per line)')
    
    # Output options
    parser.add_argument('--output-dir', default='downloads', help='Directory to save downloaded videos')
    
    # Download options
    parser.add_argument('--quality', default='best', help='Video quality (best, 1080p, 720p, etc.)')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries for failed downloads')
    parser.add_argument('--max-concurrent', type=int, default=5, help='Maximum number of concurrent downloads')
    parser.add_argument('--no-skip-existing', action='store_true', help='Do not skip existing files')
    parser.add_argument('--metadata-only', action='store_true', help='Extract metadata without downloading')
    
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
    logger = logging.getLogger('video_downloader')
    
    # Prepare URLs list
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls:
        urls = [u.strip() for u in args.urls.split(',') if u.strip()]
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Download videos
    if urls or args.input_file:
        logger.info(f"Starting video download{'s' if len(urls) > 1 or args.input_file else ''}")
        
        results = download_videos(
            urls=urls,
            input_file=args.input_file,
            output_dir=args.output_dir,
            max_retries=args.max_retries,
            max_concurrent=args.max_concurrent,
            quality=args.quality,
            skip_existing=not args.no_skip_existing
        )
        
        # Print summary
        successful = sum(1 for r in results if r.get('success', False))
        logger.info(f"Download complete: {successful} of {len(results)} videos successful")
        
        return 0 if successful > 0 else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
