# Video Projects

This repository contains a collection of standalone projects for video scraping, downloading, visualization, and data processing. It includes a unified workflow script that combines all components into a seamless pipeline.

## Project Structure

The repository is organized into the following standalone projects, each with its own specific functionality:

1. **video-spider**: Web scraping service for video websites.
2. **video-downloader**: Service for downloading videos from various hosting platforms.
3. **graph-visualizer**: Tool for visualizing network graphs from video relationships.
4. **data-processor**: Service for processing and analyzing video metadata and relationships.

## Project Descriptions

### 1. Video Spider

A standalone web scraping service for video websites built with Scrapy and Splash. It extracts video metadata and builds relationship graphs between videos.

**Key Features:**
- Scrape videos from various video hosting websites
- Handle JavaScript-rendered content using Splash
- Extract video metadata (title, views, duration, etc.)
- Build relationship graphs between videos

**Usage:**
```bash
cd video-spider
./run_spider.sh --url "https://example.com/video" --max-videos 100
```

### 2. Video Downloader

A standalone service for downloading videos from various hosting platforms with metadata extraction.

**Key Features:**
- Download videos from multiple video hosting platforms
- Extract video metadata (title, description, tags, etc.)
- Support for different video qualities
- Concurrent downloading capabilities

**Usage:**
```bash
cd video-downloader
./download_videos.sh --url "https://example.com/video" --output-dir "downloads"
```

### 3. Graph Visualizer

A standalone tool for visualizing network graphs from video relationships data.

**Key Features:**
- Interactive visualization of video relationship graphs
- Support for GEXF, JSON, and other graph formats
- Web-based UI with zoom, pan, and search capabilities
- Export visualizations as images or interactive HTML

**Usage:**
```bash
cd graph-visualizer
./visualize_graph.sh --input "video_relationships.gexf" --type web --show
```

### 4. Data Processor

A standalone service for processing and analyzing video metadata and relationships.

**Key Features:**
- Process and transform video metadata from various sources
- Generate statistics and insights from video data
- Build and analyze video relationship networks
- Export data in various formats (JSON, CSV, GEXF)

**Usage:**
```bash
cd data-processor
./process_data.sh --input "video_data.json" --formats csv,json,gexf
```

## Unified Workflow Script

A unified workflow script `genworkflow` is provided that combines all four components into a seamless pipeline. This script simplifies the process of running all steps in sequence with proper integration between components.

### Basic Usage

```bash
# Run the complete workflow
./genworkflow --url "https://example.com/video" --max-videos 20

# Skip specific steps (by name or number)
./genworkflow --skip-steps download,visualize
# OR
./genworkflow --skip-steps 2,4

# Get help
./genworkflow --help
```

### Advanced Options

The workflow script supports many configuration options:

```bash
./genworkflow \
  --url "https://example.com/video" \
  --workdir ~/video-data \
  --max-videos 50 \
  --max-depth 2 \
  --max-concurrent 5 \
  --quality 1080p \
  --visualization both
```

See `./genworkflow --help` for all available options.

## Manual Workflow Example

If you prefer to run each component separately, here's an example workflow:

1. **Scrape video data**:
   ```bash
   cd video-spider
   ./run_spider.sh --url "https://example.com/video" --output-dir "../data"
   ```

2. **Download the videos**:
   ```bash
   cd ../video-downloader
   ./download_videos.sh --input-file "../data/video_urls.txt" --output-dir "../downloads"
   ```

3. **Process the data**:
   ```bash
   cd ../data-processor
   ./process_data.sh --input "../data/video_relationships.gexf" --output-dir "../processed_data"
   ```

4. **Visualize the graph**:
   ```bash
   cd ../graph-visualizer
   ./visualize_graph.sh --input "../processed_data/video_graph.gexf" --show
   ```

## Requirements

Each project has its own specific requirements listed in its respective directory. In general, you'll need:

- Python 3.8+
- Docker (for Splash JavaScript rendering)
- FFmpeg (for video downloading)
- Various Python packages (specified in each project's requirements.txt)

## License

MIT
