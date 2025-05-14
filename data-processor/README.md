# Data Processor

A standalone service for processing and analyzing video metadata and relationships.

## Features

- Process and transform video metadata from various sources
- Generate statistics and insights from video data
- Build and analyze video relationship networks
- Export data in various formats (JSON, CSV, GEXF)
- Scheduled data processing jobs
- Data validation and cleaning

## Requirements

- Python 3.8+
- Pandas
- NetworkX
- Scikit-learn (for advanced analytics)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
# Basic usage
python -m src.processor --input "video_data.json" --output "processed_data"

# Advanced usage
python -m src.processor \
  --input "video_data.json" \
  --output "processed_data" \
  --format "csv,json,gexf" \
  --analyze \
  --clean-data
```

## Configuration

Configuration can be modified in the `config/settings.py` file.

## Project Structure

```
data-processor/
├── config/              # Configuration files
├── docs/                # Documentation
├── src/                 # Source code
│   ├── processors/      # Data processing modules
│   ├── models/          # Data models
│   └── utils/           # Utility functions
└── tests/               # Test cases
```

## License

MIT
