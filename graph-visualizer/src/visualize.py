#!/usr/bin/env python3
"""
Main entry point for the graph visualizer.
This module provides a command-line interface for creating graph visualizations.
"""

import os
import sys
import argparse
import logging
import webbrowser
from pathlib import Path

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import visualization modules
from visualizer.static_visualizer import visualize_graph_file
from web.web_visualizer import create_web_visualization

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Graph Visualizer')
    
    parser.add_argument('--input', '-i', required=True, help='Input graph file (GEXF, GraphML, JSON)')
    parser.add_argument('--output', '-o', help='Output file or directory (for static or web visualization)')
    parser.add_argument('--type', '-t', choices=['static', 'web', 'both'], default='both', help='Visualization type (static, web, or both)')
    parser.add_argument('--title', help='Title for the visualization')
    parser.add_argument('--show', '-s', action='store_true', help='Show the visualization')
    parser.add_argument('--web-port', type=int, default=8080, help='Port for the web server (for web visualization)')
    parser.add_argument('--figsize', default='20,20', help='Figure size for static visualization (width,height)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for static visualization')
    
    return parser.parse_args()

def start_web_server(html_path, port):
    """
    Start a simple web server to view the visualization.
    
    Args:
        html_path (str): Path to the HTML file.
        port (int): Port for the web server.
    """
    import http.server
    import socketserver
    import threading
    
    web_dir = os.path.dirname(html_path)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=web_dir, **kwargs)
        
        def log_message(self, format, *args):
            # Suppress log messages
            pass
    
    # Create server
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Web server started at http://localhost:{port}")
        print(f"Press Ctrl+C to stop the server")
        
        # Open the browser
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            # Start the server
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Web server stopped")

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger('graph_visualizer')
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Parse figsize
    try:
        figsize = tuple(map(int, args.figsize.split(',')))
    except:
        figsize = (20, 20)
    
    # Set default output paths
    input_basename = os.path.splitext(os.path.basename(args.input))[0]
    
    if args.output:
        static_output = args.output if args.type == 'static' else os.path.join(args.output, f"{input_basename}_visualization.png")
        web_output_dir = args.output if args.type == 'web' else os.path.join(args.output, 'web_viz')
    else:
        static_output = f"{input_basename}_visualization.png"
        web_output_dir = 'web_viz'
    
    # Create visualizations
    if args.type in ['static', 'both']:
        logger.info(f"Creating static visualization for {args.input}")
        title = args.title or f"Graph Visualization: {os.path.basename(args.input)}"
        
        success = visualize_graph_file(
            args.input,
            output_file=static_output,
            show=args.show,
            figsize=figsize,
            dpi=args.dpi
        )
        
        if success:
            logger.info(f"Static visualization saved to {static_output}")
        else:
            logger.error("Failed to create static visualization")
            return 1
    
    if args.type in ['web', 'both']:
        logger.info(f"Creating web visualization for {args.input}")
        title = args.title or f"Graph Visualization: {os.path.basename(args.input)}"
        
        html_path = create_web_visualization(
            args.input,
            output_dir=web_output_dir,
            title=title
        )
        
        if html_path:
            logger.info(f"Web visualization saved to {html_path}")
            
            if args.show:
                logger.info(f"Starting web server on port {args.web_port}")
                start_web_server(html_path, args.web_port)
        else:
            logger.error("Failed to create web visualization")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
