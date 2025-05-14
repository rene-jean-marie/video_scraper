# Graph Visualizer

A standalone tool for visualizing network graphs from video relationships data.

## Features

- Interactive visualization of video relationship graphs
- Support for GEXF, JSON, and other graph formats
- Web-based UI with zoom, pan, and search capabilities
- Node filtering and highlighting
- Community detection and graph analytics
- Export visualizations as images or interactive HTML

## Requirements

- Python 3.8+
- NetworkX
- Matplotlib
- Flask (for web interface)
- vis.js (included)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-line Interface

```bash
# Generate a static visualization
python -m src.visualizer --input "video_relationships.gexf" --output "visualization.png"

# Start the web interface
python -m src.web.app --input "video_relationships.gexf" --port 8080
```

### Python API

```python
from graph_visualizer import GraphVisualizer

# Create a visualizer
visualizer = GraphVisualizer("video_relationships.gexf")

# Generate a static visualization
visualizer.save_image("visualization.png")

# Generate an interactive HTML visualization
visualizer.save_html("visualization.html")
```

## Configuration

Configuration can be modified in the `config/settings.py` file.

## Project Structure

```
graph-visualizer/
├── config/              # Configuration files
├── docs/                # Documentation
├── src/                 # Source code
│   ├── visualizer/      # Core visualization logic
│   ├── web/             # Web interface
│   └── utils/           # Utility functions
└── tests/               # Test cases
```

## License

MIT
