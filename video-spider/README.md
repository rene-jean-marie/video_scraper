# Video Spider

A standalone web scraping service for video websites built with Scrapy and Splash.

## Features

- Scrape videos from various video hosting websites
- Handle JavaScript-rendered content using Splash
- Extract video metadata (title, views, duration, etc.)
- Build relationship graphs between videos
- Support for pagination and category navigation
- Configurable selectors for different websites

## Requirements

- Python 3.8+
- Docker (for Splash JavaScript rendering)
- Scrapy
- NetworkX

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure Docker is installed and running
4. Start the Splash container:
   ```bash
   docker run -d -p 8050:8050 scrapinghub/splash
   ```

## Usage

```bash
# Basic usage
python -m src.run_spider --url "https://example.com/video" --max-videos 100

# Advanced usage with more options
python -m src.run_spider \
  --url "https://example.com/video" \
  --max-videos 100 \
  --max-depth 2 \
  --skip-categories \
  --output-file "video_graph.json"
```

## Configuration

Configuration can be modified in the `config/settings.py` file.

## Project Structure

```
video-spider/
├── config/              # Configuration files
├── docs/                # Documentation
├── src/                 # Source code
│   ├── spider/          # Spider implementation
│   ├── middlewares/     # Scrapy middlewares
│   ├── pipelines/       # Scrapy pipelines
│   ├── utils/           # Utility functions
│   └── lua_scripts/     # Splash Lua scripts
└── tests/               # Test cases
```

## License

MIT
