"""
Settings for the video spider project.
This module contains Scrapy settings and other configuration options.
"""

# Scrapy settings
SETTINGS = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'ROBOTSTXT_OBEY': False,
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_DELAY': 1.0,
    'COOKIES_ENABLED': True,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    'TELNETCONSOLE_ENABLED': False,
    'LOG_LEVEL': 'INFO',
    
    # Cache settings
    'HTTPCACHE_ENABLED': True,
    'HTTPCACHE_EXPIRATION_SECS': 86400,
    'HTTPCACHE_DIR': 'httpcache',
    'HTTPCACHE_IGNORE_HTTP_CODES': [503, 504, 505, 500, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409],
    'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
    
    # Retry middleware
    'RETRY_ENABLED': True,
    'RETRY_TIMES': 3,
    'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
    
    # Spider middleware
    'SPIDER_MIDDLEWARES': {
        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    },
    
    # Downloader middleware
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy_splash.SplashCookiesMiddleware': 723,
        'scrapy_splash.SplashMiddleware': 725,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    },
    
    # Splash settings
    'SPLASH_URL': 'http://localhost:8050',
    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
}

# Default paths
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_SCREENSHOTS_DIR = 'screenshots'

# Spider behavior settings
MAX_VIDEOS = 100
MAX_DEPTH = 1
MAX_PAGES_PER_CATEGORY = 3
SKIP_CATEGORIES = False
