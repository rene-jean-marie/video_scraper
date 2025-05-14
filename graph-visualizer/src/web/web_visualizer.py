"""
Web-based visualization module for graph data.
This module provides functions to create interactive web visualizations.
"""

import os
import json
import networkx as nx
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WebVisualizer:
    """Class for creating interactive web-based visualizations of graph data."""
    
    def __init__(self, graph=None):
        """
        Initialize the web visualizer.
        
        Args:
            graph (networkx.Graph, optional): The graph to visualize.
        """
        self.graph = graph
        
        # HTML template for the visualization
        self.html_template = """<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #graph-container {
            width: 100%;
            height: 95vh;
            border: 1px solid lightgray;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }
        .controls {
            margin-bottom: 10px;
        }
        .node-info {
            position: fixed;
            right: 20px;
            top: 20px;
            background: white;
            border: 1px solid #ddd;
            padding: 10px;
            max-width: 300px;
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }
    </style>
</head>
<body>
    <div class="controls">
        <button onclick="zoomIn()">Zoom In</button>
        <button onclick="zoomOut()">Zoom Out</button>
        <button onclick="resetView()">Reset View</button>
        <input type="text" id="search" placeholder="Search nodes..." onkeyup="searchNodes()">
    </div>
    <div id="node-info" class="node-info"></div>
    <div id="graph-container"></div>
    
    <script type="text/javascript" src="graph_data.js"></script>
    <script type="text/javascript">
        // Create a network
        const container = document.getElementById('graph-container');
        
        // Options for the network
        const options = {
            nodes: {
                shape: 'dot',
                size: 10,
                font: {
                    size: 12
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                arrows: {
                    to: { enabled: true, scaleFactor: 0.5 }
                },
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: false,
                barnesHut: {
                    gravitationalConstant: -80000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true,
                hover: true
            }
        };
        
        // Create the network
        const network = new vis.Network(container, graph_data, options);
        
        // Node selection event
        network.on("click", function(params) {
            const nodeId = params.nodes[0];
            if (nodeId) {
                showNodeInfo(nodeId);
            } else {
                hideNodeInfo();
            }
        });
        
        // Show node information
        function showNodeInfo(nodeId) {
            const nodeInfo = document.getElementById('node-info');
            const node = graph_data.nodes.find(n => n.id === nodeId);
            
            if (node) {
                let html = `<h3>${node.label}</h3><ul>`;
                for (const [key, value] of Object.entries(node)) {
                    if (key !== 'id' && key !== 'label') {
                        html += `<li><strong>${key}:</strong> ${value}</li>`;
                    }
                }
                html += '</ul>';
                
                nodeInfo.innerHTML = html;
                nodeInfo.style.display = 'block';
            }
        }
        
        // Hide node information
        function hideNodeInfo() {
            document.getElementById('node-info').style.display = 'none';
        }
        
        // Zoom functions
        function zoomIn() {
            network.moveTo({ scale: network.getScale() * 1.2 });
        }
        
        function zoomOut() {
            network.moveTo({ scale: network.getScale() * 0.8 });
        }
        
        function resetView() {
            network.fit();
        }
        
        // Search function
        function searchNodes() {
            const searchText = document.getElementById('search').value.toLowerCase();
            
            if (searchText === '') {
                // Reset all nodes
                network.setData(graph_data);
                return;
            }
            
            const filteredNodes = graph_data.nodes.filter(node => {
                const label = node.label.toLowerCase();
                return label.includes(searchText);
            });
            
            const filteredNodeIds = filteredNodes.map(node => node.id);
            
            // Highlight the matching nodes
            network.setSelection({
                nodes: filteredNodeIds
            });
            
            if (filteredNodeIds.length > 0) {
                network.focus(filteredNodeIds[0], { scale: 1.2 });
            }
        }
        
        // Initial fit
        network.once('stabilizationIterationsDone', function() {
            network.fit();
        });
    </script>
</body>
</html>
"""
    
    def load_graph_from_file(self, file_path):
        """
        Load a graph from a file.
        
        Args:
            file_path (str): Path to the graph file.
            
        Returns:
            bool: True if the graph was loaded successfully, False otherwise.
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.gexf':
                self.graph = nx.read_gexf(file_path)
            elif file_ext == '.graphml':
                self.graph = nx.read_graphml(file_path)
            elif file_ext == '.json':
                self.graph = nx.readwrite.json_graph.node_link_graph(file_path)
            else:
                logger.error(f"Unsupported graph file format: {file_ext}")
                return False
            
            logger.info(f"Graph loaded with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            return True
        
        except Exception as e:
            logger.error(f"Error loading graph: {str(e)}")
            return False
    
    def convert_graph_to_json(self):
        """
        Convert the graph to JSON format for visualization.
        
        Returns:
            dict: The graph data in JSON format.
        """
        if not self.graph:
            logger.error("No graph loaded")
            return None
        
        # Prepare data for visualization
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_data = {
                "id": node_id,
                "label": attrs.get("title", node_id)[:30] if "title" in attrs else str(node_id)
            }
            
            # Add other attributes
            for key, value in attrs.items():
                if key not in ["id", "label"]:
                    # Convert values to strings for JSON serialization
                    if isinstance(value, (dict, list, tuple)):
                        node_data[key] = json.dumps(value)
                    else:
                        node_data[key] = str(value)
            
            nodes.append(node_data)
        
        edges = []
        for source, target, attrs in self.graph.edges(data=True):
            edge_data = {
                "from": source,
                "to": target
            }
            
            # Add edge attributes if any
            for key, value in attrs.items():
                if isinstance(value, (dict, list, tuple)):
                    edge_data[key] = json.dumps(value)
                else:
                    edge_data[key] = str(value)
                
            edges.append(edge_data)
        
        # Create JSON data
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def create_web_visualization(self, output_dir, title="Graph Visualization"):
        """
        Create an interactive web visualization of the graph.
        
        Args:
            output_dir (str): Directory to save the visualization files.
            title (str, optional): Title for the visualization.
            
        Returns:
            str: Path to the HTML file, or None if the visualization failed.
        """
        if not self.graph:
            logger.error("No graph loaded")
            return None
        
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Convert graph to JSON
            graph_data = self.convert_graph_to_json()
            
            if not graph_data:
                return None
            
            # Save graph data as JavaScript file
            js_file = os.path.join(output_dir, "graph_data.js")
            with open(js_file, "w", encoding="utf-8") as f:
                f.write(f"const graph_data = {json.dumps(graph_data, indent=2)};")
            
            # Create HTML file
            html_file = os.path.join(output_dir, "index.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(self.html_template.format(title=title))
            
            logger.info(f"Web visualization saved to {html_file}")
            return html_file
        
        except Exception as e:
            logger.error(f"Error creating web visualization: {str(e)}")
            return None


def create_web_visualization(input_file, output_dir="web_viz", title=None):
    """
    Create a web visualization from a graph file.
    
    Args:
        input_file (str): Path to the graph file.
        output_dir (str, optional): Directory to save the visualization files.
        title (str, optional): Title for the visualization.
        
    Returns:
        str: Path to the HTML file, or None if the visualization failed.
    """
    # Create visualizer
    visualizer = WebVisualizer()
    
    # Load graph
    if not visualizer.load_graph_from_file(input_file):
        return None
    
    # Set default title if not specified
    if not title:
        title = f"Graph Visualization: {os.path.basename(input_file)}"
    
    # Create web visualization
    return visualizer.create_web_visualization(output_dir, title)
