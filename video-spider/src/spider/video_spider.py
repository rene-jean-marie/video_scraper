"""
Core video spider implementation for crawling video websites.
This module provides the main spider class that handles crawling and data extraction.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import networkx as nx
import scrapy
from scrapy_splash import SplashRequest

from ..utils.selectors import DEFAULT_SELECTORS
from ..utils.lua_scripts import MAIN_SCRIPT

logger = logging.getLogger(__name__)


class VideoSpider(scrapy.Spider):
    """Spider for scraping video content using Splash for JavaScript rendering."""
    
    name = 'video_spider'
    
    def __init__(
        self,
        start_url=None,
        output_dir='output',
        screenshots_dir='screenshots',
        max_videos=100,
        max_depth=1,
        max_pages_per_category=3,
        skip_categories=False,
        *args,
        **kwargs
    ):
        """
        Initialize the video spider.
        
        Args:
            start_url (str): The URL to start crawling from
            output_dir (str): Directory to save output data
            screenshots_dir (str): Directory to save screenshots
            max_videos (int): Maximum number of videos to scrape
            max_depth (int): Maximum depth to crawl
            max_pages_per_category (int): Maximum pages to crawl per category
            skip_categories (bool): Whether to skip category pages
        """
        super(VideoSpider, self).__init__(*args, **kwargs)
        self.start_url = start_url
        if not self.start_url:
            raise ValueError('start_url is required')
        
        # Initialize tracking variables
        self.videos_scraped = 0
        self.current_depth = 0
        self.max_depth = max_depth
        self.crawled_urls = set()
        self.pages_crawled = {}
        self.max_pages_per_category = max_pages_per_category
        
        # Video relationship graph
        self.video_graph = nx.DiGraph()
        
        # Configuration
        self.max_videos = max_videos
        self.skip_categories = skip_categories
        
        # Directory setup
        self.output_dir = output_dir
        self.screenshots_dir = screenshots_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Set up graph file path
        self.graph_file = os.path.join(self.output_dir, 'video_relationships.gexf')
        
        # Set up selectors
        self.selectors = DEFAULT_SELECTORS.copy()
        
        logger.info(f'Starting spider with URL: {self.start_url}')
        logger.info(f'Output directory: {self.output_dir}')
        logger.info(f'Screenshots directory: {self.screenshots_dir}')
        logger.info(f'Max videos: {self.max_videos}, Max depth: {self.max_depth}')
    
    def start_requests(self):
        """Generate initial requests."""
        self.logger.info(f'Starting requests for URL: {self.start_url}')
        yield self.make_splash_request(self.start_url, self.parse, meta={'depth': 0})
    
    def make_splash_request(self, url, callback, meta=None):
        """Create a Splash request with the Lua script."""
        if meta is None:
            meta = {}
        
        # Add screenshot filename to meta
        if 'screenshot' not in meta:
            screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            meta['screenshot'] = os.path.join(self.screenshots_dir, screenshot_filename)
        
        # Set the default render timeout to 90 seconds
        splash_args = {
            'lua_source': MAIN_SCRIPT,
            'wait': 3,
            'timeout': 90,
            'images': 0,
            'resource_timeout': 15,
        }
        
        # Return the SplashRequest
        return SplashRequest(
            url=url,
            callback=callback,
            endpoint='execute',
            args=splash_args,
            meta=meta,
        )
    
    def determine_page_type(self, response):
        """Determine the type of page we're on."""
        # Check for video player (individual video page)
        if response.css(self.selectors['video_player']):
            return 'video'
        
        # Check for category grid (category listing page)
        elif response.css(self.selectors['category_grid']):
            return 'category'
        
        # Check for video grid (video listing page)
        elif response.css(self.selectors['video_grid']):
            return 'listing'
        
        return 'unknown'
    
    def parse(self, response):
        """Parse the response and extract data based on page type."""
        try:
            # Track the URL to avoid duplicates
            if response.url in self.crawled_urls:
                self.logger.info(f'Skipping already crawled URL: {response.url}')
                return
            
            self.crawled_urls.add(response.url)
            
            # Check if we've reached the maximum number of videos
            if self.videos_scraped >= self.max_videos:
                self.logger.info(f'Reached maximum number of videos: {self.max_videos}')
                return
            
            # Basic response validation
            content_type = response.headers.get('Content-Type', b'').decode()
            if not content_type.startswith('text/html'):
                self.logger.warning(f"Non-HTML response from {response.url}")
                return
            
            # Get current depth
            depth = response.meta.get('depth', 0)
            if depth > self.max_depth:
                self.logger.info(f'Reached maximum depth: {self.max_depth}')
                return
            
            # Determine page type
            page_type = self.determine_page_type(response)
            self.logger.info(f'Processing {page_type} page: {response.url} (depth: {depth})')
            
            # Handle different page types
            if page_type == 'video':
                yield from self.parse_video_page(response)
            elif page_type == 'category' and not self.skip_categories:
                yield from self.parse_category_page(response)
            elif page_type == 'listing':
                yield from self.parse_video_listing(response)
            else:
                self.logger.warning(f'Unknown page type for URL: {response.url}')
            
            # Save the graph periodically
            if self.videos_scraped % 10 == 0:
                self.save_graph()
        
        except Exception as e:
            self.logger.error(f'Error parsing response: {str(e)}')
    
    def parse_video_page(self, response):
        """Parse an individual video page."""
        self.logger.info(f'Parsing video page: {response.url}')
        
        try:
            # Extract video metadata
            video_id = self.extract_video_id_from_url(response.url)
            
            video_info = {
                'id': video_id,
                'url': response.url,
                'title': response.css('title::text').get(),
                'timestamp': datetime.now().isoformat(),
                'depth': response.meta.get('depth', 0),
            }
            
            # Update video count
            self.videos_scraped += 1
            
            # Add node to the graph
            self.video_graph.add_node(video_id, **video_info)
            
            # Extract related videos
            related_videos = response.css(self.selectors.get('related_videos', ''))
            if related_videos:
                for video in related_videos.css(self.selectors.get('related_video_item', '')):
                    related_url = video.css(self.selectors.get('related_video_url', '')).get()
                    if related_url:
                        related_url = response.urljoin(related_url)
                        related_id = self.extract_video_id_from_url(related_url)
                        related_title = video.css(self.selectors.get('related_video_title', '')).get()
                        
                        # Add edge to the graph
                        self.video_graph.add_edge(video_id, related_id)
                        
                        # Add related video to the graph
                        self.video_graph.add_node(related_id, title=related_title, url=related_url)
                        
                        # Only follow the link if we haven't reached max depth
                        new_depth = response.meta.get('depth', 0) + 1
                        if new_depth <= self.max_depth and self.videos_scraped < self.max_videos:
                            yield self.make_splash_request(
                                related_url,
                                self.parse,
                                meta={'depth': new_depth}
                            )
            
            yield video_info
        
        except Exception as e:
            self.logger.error(f'Error parsing video page: {str(e)}')
    
    def parse_category_page(self, response):
        """Parse a category page."""
        self.logger.info(f'Parsing category page: {response.url}')
        
        try:
            # Extract category metadata
            category_items = response.css(self.selectors.get('category_item', ''))
            
            for item in category_items:
                category_url = item.css(self.selectors.get('category_url', '')).get()
                if category_url:
                    category_url = response.urljoin(category_url)
                    category_title = item.css(self.selectors.get('category_title', '')).get()
                    
                    self.logger.info(f'Found category: {category_title} ({category_url})')
                    
                    # Only follow the link if we haven't reached max depth
                    new_depth = response.meta.get('depth', 0) + 1
                    if new_depth <= self.max_depth and self.videos_scraped < self.max_videos:
                        yield self.make_splash_request(
                            category_url,
                            self.parse,
                            meta={'depth': new_depth}
                        )
            
            # Check for pagination
            next_page = response.css(self.selectors.get('next_page', '')).get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                
                # Check if we've reached the max pages for this category
                current_base_url = response.url.split('?')[0]
                self.pages_crawled[current_base_url] = self.pages_crawled.get(current_base_url, 0) + 1
                
                if self.pages_crawled[current_base_url] < self.max_pages_per_category:
                    self.logger.info(f'Following next page {self.pages_crawled[current_base_url] + 1} for {current_base_url}')
                    
                    # Keep the same depth level for pagination
                    yield self.make_splash_request(
                        next_page_url,
                        self.parse,
                        meta={'depth': response.meta.get('depth', 0)}
                    )
                else:
                    self.logger.info(f'Reached maximum pages ({self.max_pages_per_category}) for {current_base_url}')
        
        except Exception as e:
            self.logger.error(f'Error parsing category page: {str(e)}')
    
    def parse_video_listing(self, response):
        """Parse a video listing page."""
        self.logger.info(f'Parsing video listing page: {response.url}')
        
        try:
            # Extract video items
            video_items = response.css(self.selectors.get('video_item', ''))
            
            for item in video_items:
                video_url = item.css(self.selectors.get('video_url', '')).get()
                if video_url:
                    video_url = response.urljoin(video_url)
                    video_title = item.css(self.selectors.get('video_title', '')).get()
                    video_thumbnail = item.css(self.selectors.get('video_thumbnail', '')).get()
                    video_duration = item.css(self.selectors.get('video_duration', '')).get()
                    video_views = item.css(self.selectors.get('video_views', '')).get()
                    
                    video_id = self.extract_video_id_from_url(video_url)
                    
                    # Add node to the graph
                    self.video_graph.add_node(
                        video_id,
                        title=video_title,
                        url=video_url,
                        thumbnail=video_thumbnail,
                        duration=video_duration,
                        views=video_views,
                        depth=response.meta.get('depth', 0)
                    )
                    
                    # Only follow the link if we haven't reached max depth
                    new_depth = response.meta.get('depth', 0) + 1
                    if new_depth <= self.max_depth and self.videos_scraped < self.max_videos:
                        yield self.make_splash_request(
                            video_url,
                            self.parse,
                            meta={'depth': new_depth}
                        )
            
            # Check for pagination
            next_page = response.css(self.selectors.get('next_page', '')).get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                
                # Check if we've reached the max pages for this listing
                current_base_url = response.url.split('?')[0]
                self.pages_crawled[current_base_url] = self.pages_crawled.get(current_base_url, 0) + 1
                
                if self.pages_crawled[current_base_url] < self.max_pages_per_category:
                    self.logger.info(f'Following next page {self.pages_crawled[current_base_url] + 1} for {current_base_url}')
                    
                    # Keep the same depth level for pagination
                    yield self.make_splash_request(
                        next_page_url,
                        self.parse,
                        meta={'depth': response.meta.get('depth', 0)}
                    )
                else:
                    self.logger.info(f'Reached maximum pages ({self.max_pages_per_category}) for {current_base_url}')
        
        except Exception as e:
            self.logger.error(f'Error parsing video listing page: {str(e)}')
    
    def extract_video_id_from_url(self, url):
        """Extract a unique ID from a video URL."""
        if not url:
            return None
        
        # Simple method: use the last part of the URL path
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else None
    
    def save_graph(self):
        """Save the video graph to a file."""
        try:
            if self.video_graph.number_of_nodes() > 0:
                self.logger.info(f'Saving graph with {self.video_graph.number_of_nodes()} nodes and {self.video_graph.number_of_edges()} edges')
                nx.write_gexf(self.video_graph, self.graph_file)
                self.logger.info(f'Graph saved to {self.graph_file}')
        except Exception as e:
            self.logger.error(f'Error saving graph: {str(e)}')
    
    def closed(self, reason):
        """Called when the spider is closed."""
        self.logger.info(f'Spider closed: {reason}')
        self.save_graph()
