#!/usr/bin/env python3
"""
Main entry point for running the video spider.
This module provides a command-line interface for starting the spider.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

# Import the spider
from spider.video_spider import VideoSpider

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the video spider')
    
    parser.add_argument('--url', required=True, help='URL to start crawling from')
    parser.add_argument('--output-dir', default='output', help='Directory to save output data')
    parser.add_argument('--screenshots-dir', default='screenshots', help='Directory to save screenshots')
    parser.add_argument('--max-videos', type=int, default=100, help='Maximum number of videos to scrape')
    parser.add_argument('--max-depth', type=int, default=1, help='Maximum depth to crawl')
    parser.add_argument('--max-pages', type=int, default=3, help='Maximum pages per category')
    parser.add_argument('--skip-categories', action='store_true', help='Skip category pages')
    
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger('video_spider')
    
    # Get Scrapy settings
    from config.settings import SETTINGS
    settings = get_project_settings()
    settings.update(SETTINGS)
    
    # Set up directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.screenshots_dir, exist_ok=True)
    
    logger.info(f"Starting spider with URL: {args.url}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Screenshots directory: {args.screenshots_dir}")
    logger.info(f"Max videos: {args.max_videos}, Max depth: {args.max_depth}")
    
    # Configure Scrapy logging
    configure_logging(settings)
    
    # Create crawler
    runner = CrawlerRunner(settings)
    
    # Run spider
    d = runner.crawl(
        VideoSpider,
        start_url=args.url,
        output_dir=args.output_dir,
        screenshots_dir=args.screenshots_dir,
        max_videos=args.max_videos,
        max_depth=args.max_depth,
        max_pages_per_category=args.max_pages,
        skip_categories=args.skip_categories
    )
    
    # Add callback to stop the reactor
    d.addBoth(lambda _: reactor.stop())
    
    # Run the reactor
    reactor.run()
    
    logger.info("Spider finished")

if __name__ == "__main__":
    main()
