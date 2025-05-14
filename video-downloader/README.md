# Video Downloader

A standalone service for downloading videos from various hosting platforms with metadata extraction.

## Features

- Download videos from multiple video hosting platforms
- Extract video metadata (title, description, tags, etc.)
- Support for different video qualities
- Concurrent downloading capabilities
- Customizable download filters
- Retry mechanism for failed downloads
- Progress tracking and reporting

## Requirements

- Python 3.8+
- FFmpeg
- yt-dlp

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install FFmpeg:
   ```bash
   # For Debian/Ubuntu
   sudo apt-get install ffmpeg
   
   # For Arch Linux
   sudo pacman -S ffmpeg
   ```

## Usage

```bash
# Basic usage
python -m src.downloader --url "https://example.com/video" --output-dir "downloads"

# Advanced usage
python -m src.downloader \
  --url "https://example.com/video" \
  --output-dir "downloads" \
  --quality "best" \
  --max-retries 3 \
  --concurrent 5
```

## Configuration

Configuration can be modified in the `config/settings.py` file.

## Project Structure

```
video-downloader/
├── config/              # Configuration files
├── docs/                # Documentation
├── src/                 # Source code
│   ├── downloader/      # Downloader implementation
│   ├── processors/      # Post-processing modules
│   └── utils/           # Utility functions
└── tests/               # Test cases
```

## License

MIT
