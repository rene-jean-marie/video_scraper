"""
Video downloader module for downloading videos from various platforms.
This module provides functions and classes to download videos with metadata.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import validators
from tqdm import tqdm

logger = logging.getLogger(__name__)

class VideoDownloader:
    """Class for downloading videos from various platforms."""
    
    def __init__(
        self,
        output_dir='downloads',
        max_retries=3,
        max_concurrent=5,
        quality='best',
        skip_existing=True
    ):
        """
        Initialize the video downloader.
        
        Args:
            output_dir (str): Directory to save downloaded videos
            max_retries (int): Maximum number of retries for failed downloads
            max_concurrent (int): Maximum number of concurrent downloads
            quality (str): Video quality to download ('best', '1080p', '720p', etc.)
            skip_existing (bool): Whether to skip existing files
        """
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        self.quality = quality
        self.skip_existing = skip_existing
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set for tracking downloaded URLs
        self.downloaded_urls = set()
        
        # Check if yt-dlp is installed
        self._check_ytdlp()
    
    def _check_ytdlp(self):
        """Check if yt-dlp is installed and accessible."""
        try:
            subprocess.run(
                ['yt-dlp', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("yt-dlp not found. Please install it first.")
            logger.info("You can install yt-dlp using: pip install yt-dlp")
            sys.exit(1)
    
    def download_video(self, url, custom_output_dir=None, custom_filename=None):
        """
        Download a video from a URL.
        
        Args:
            url (str): URL of the video to download
            custom_output_dir (str, optional): Custom output directory
            custom_filename (str, optional): Custom filename
        
        Returns:
            dict: Download result with metadata
        """
        # Validate URL
        if not validators.url(url):
            logger.error(f"Invalid URL: {url}")
            return {
                'url': url,
                'success': False,
                'error': 'Invalid URL'
            }
        
        # Check if URL was already downloaded
        if url in self.downloaded_urls:
            logger.warning(f"URL already downloaded: {url}")
            return {
                'url': url,
                'success': False,
                'error': 'Already downloaded'
            }
        
        # Determine output directory
        output_dir = custom_output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine output template
        if custom_filename:
            output_template = os.path.join(output_dir, custom_filename)
        else:
            output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        
        # Build yt-dlp command
        cmd = [
            'yt-dlp',
            '--ignore-errors',
            '--format', f'bestvideo[height<={self.quality}]+bestaudio/best' if self.quality.isdigit() else 'best',
            '--output', output_template,
            '--write-info-json',
            '--write-thumbnail',
            url
        ]
        
        if self.skip_existing:
            cmd.insert(1, '--skip-download')
            cmd.insert(1, '--rm-cache-dir')
        
        # Run the command
        logger.info(f"Downloading video: {url}")
        result = {
            'url': url,
            'success': False,
            'output_dir': output_dir
        }
        
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True
            )
            
            if process.returncode == 0:
                logger.info(f"Successfully downloaded: {url}")
                result['success'] = True
                
                # Find the info JSON file to extract metadata
                if custom_filename:
                    base_filename = os.path.splitext(custom_filename)[0]
                    info_file = os.path.join(output_dir, f"{base_filename}.info.json")
                else:
                    # Try to find the info JSON file based on the URL
                    info_files = [f for f in os.listdir(output_dir) if f.endswith('.info.json')]
                    info_file = None
                    
                    # Look for the most recent info file
                    if info_files:
                        info_file = max(
                            [os.path.join(output_dir, f) for f in info_files],
                            key=os.path.getmtime
                        )
                
                # Extract metadata from info file
                if info_file and os.path.exists(info_file):
                    try:
                        with open(info_file, 'r') as f:
                            metadata = json.load(f)
                            result['metadata'] = metadata
                    except Exception as e:
                        logger.warning(f"Error loading metadata: {str(e)}")
                
                # Add this URL to the downloaded set
                self.downloaded_urls.add(url)
            else:
                error_message = process.stderr or "Unknown error"
                logger.error(f"Error downloading {url}: {error_message}")
                result['error'] = error_message
        
        except Exception as e:
            logger.error(f"Exception downloading {url}: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def download_multiple_videos(self, urls, custom_output_dir=None, custom_filenames=None):
        """
        Download multiple videos concurrently.
        
        Args:
            urls (list): List of URLs to download
            custom_output_dir (str, optional): Custom output directory
            custom_filenames (dict, optional): Dictionary mapping URLs to custom filenames
        
        Returns:
            list: List of download results
        """
        results = []
        
        # Validate URLs
        valid_urls = [url for url in urls if validators.url(url)]
        if len(valid_urls) < len(urls):
            logger.warning(f"Skipping {len(urls) - len(valid_urls)} invalid URLs")
        
        # Create progress bar
        progress_bar = tqdm(total=len(valid_urls), desc="Downloading videos")
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_url = {}
            
            for url in valid_urls:
                filename = custom_filenames.get(url) if custom_filenames else None
                future = executor.submit(
                    self.download_video,
                    url,
                    custom_output_dir,
                    filename
                )
                future_to_url[future] = url
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Exception processing {url}: {str(e)}")
                    results.append({
                        'url': url,
                        'success': False,
                        'error': str(e)
                    })
                
                progress_bar.update(1)
        
        progress_bar.close()
        
        # Print summary
        successful = sum(1 for r in results if r.get('success', False))
        logger.info(f"Downloaded {successful} of {len(results)} videos")
        
        return results
    
    def extract_metadata_only(self, url):
        """
        Extract metadata from a video without downloading it.
        
        Args:
            url (str): URL of the video to extract metadata from
        
        Returns:
            dict: Video metadata or None if failed
        """
        # Validate URL
        if not validators.url(url):
            logger.error(f"Invalid URL: {url}")
            return None
        
        # Build yt-dlp command for metadata only
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print-json',
            url
        ]
        
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True
            )
            
            if process.returncode == 0 and process.stdout:
                try:
                    metadata = json.loads(process.stdout)
                    return metadata
                except json.JSONDecodeError:
                    logger.error(f"Error parsing metadata JSON for {url}")
            else:
                error_message = process.stderr or "Unknown error"
                logger.error(f"Error extracting metadata for {url}: {error_message}")
        
        except Exception as e:
            logger.error(f"Exception extracting metadata for {url}: {str(e)}")
        
        return None
    
    def download_from_file(self, input_file, custom_output_dir=None):
        """
        Download videos from a file containing URLs.
        
        Args:
            input_file (str): Path to the file containing URLs (one per line)
            custom_output_dir (str, optional): Custom output directory
        
        Returns:
            list: List of download results
        """
        try:
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            return self.download_multiple_videos(urls, custom_output_dir)
        
        except Exception as e:
            logger.error(f"Error loading URLs from file: {str(e)}")
            return []


def download_videos(
    urls=None,
    input_file=None,
    output_dir='downloads',
    max_retries=3,
    max_concurrent=5,
    quality='best',
    skip_existing=True
):
    """
    Download videos from URLs or a file.
    
    Args:
        urls (list, optional): List of URLs to download
        input_file (str, optional): Path to a file containing URLs
        output_dir (str): Directory to save downloaded videos
        max_retries (int): Maximum number of retries for failed downloads
        max_concurrent (int): Maximum number of concurrent downloads
        quality (str): Video quality to download ('best', '1080p', '720p', etc.)
        skip_existing (bool): Whether to skip existing files
    
    Returns:
        list: List of download results
    """
    # Initialize downloader
    downloader = VideoDownloader(
        output_dir=output_dir,
        max_retries=max_retries,
        max_concurrent=max_concurrent,
        quality=quality,
        skip_existing=skip_existing
    )
    
    # Download from URLs
    if urls:
        if isinstance(urls, str):
            urls = [urls]
        
        return downloader.download_multiple_videos(urls)
    
    # Download from file
    elif input_file:
        return downloader.download_from_file(input_file)
    
    else:
        logger.error("No URLs or input file provided")
        return []
