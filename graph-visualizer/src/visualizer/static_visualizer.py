"""
Static visualization module for graph data.
This module provides functions to create and save static visualizations.
"""

import networkx as nx
import matplotlib.pyplot as plt
import os
import logging

logger = logging.getLogger(__name__)

class StaticVisualizer:
    """Class for creating static visualizations of graph data."""
    
    def __init__(self, graph=None, figsize=(20, 20)):
        """
        Initialize the static visualizer.
        
        Args:
            graph (networkx.Graph, optional): The graph to visualize.
            figsize (tuple, optional): Figure size for the visualization.
        """
        self.graph = graph
        self.figsize = figsize
        self.pos = None
    
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
    
    def prepare_visualization(self):
        """
        Prepare the visualization data.
        
        Returns:
            tuple: A tuple containing node_sizes, node_labels, and layout position.
        """
        if not self.graph:
            logger.error("No graph loaded")
            return None, None, None
        
        # Get node attributes for visualization
        node_sizes = []
        node_labels = {}
        
        for node, attrs in self.graph.nodes(data=True):
            # Use views as node size if available, otherwise use default
            try:
                if 'views' in attrs:
                    views = attrs['views']
                    if isinstance(views, str):
                        views = views.replace('k', '000').replace('M', '000000').strip()
                        try:
                            size = float(views) / 10000  # Scale down for visualization
                        except ValueError:
                            size = 100
                    else:
                        size = 100
                else:
                    size = 100
            except:
                size = 100
                
            node_sizes.append(max(50, min(size, 1000)))  # Limit size range
            
            # Use title as label if available
            if 'title' in attrs:
                node_labels[node] = attrs['title'][:20] + '...' if len(attrs['title']) > 20 else attrs['title']
            else:
                node_labels[node] = node
        
        # Create layout if not already created
        if not self.pos:
            logger.info("Generating layout (this may take a while for large graphs)...")
            self.pos = nx.spring_layout(self.graph, k=0.3, iterations=50)
        
        return node_sizes, node_labels, self.pos
    
    def create_visualization(self, title=None, show=False):
        """
        Create a visualization of the graph.
        
        Args:
            title (str, optional): Title for the visualization.
            show (bool, optional): Whether to show the visualization.
            
        Returns:
            matplotlib.figure.Figure: The figure object.
        """
        if not self.graph:
            logger.error("No graph loaded")
            return None
        
        # Set up the figure
        plt.figure(figsize=self.figsize)
        
        # Prepare visualization data
        node_sizes, node_labels, pos = self.prepare_visualization()
        
        if not pos:
            return None
        
        # Draw the graph
        logger.info("Drawing graph...")
        nx.draw_networkx_nodes(self.graph, pos, node_size=node_sizes, alpha=0.7, 
                              node_color='lightblue', edgecolors='black')
        nx.draw_networkx_edges(self.graph, pos, width=0.5, alpha=0.5, arrows=True, 
                              arrowsize=10, edge_color='gray')
        
        # Draw labels with smaller font size
        nx.draw_networkx_labels(self.graph, pos, labels=node_labels, font_size=8)
        
        # Set title
        if title:
            plt.title(title)
        plt.axis('off')
        
        # Show the visualization if requested
        if show:
            plt.show()
        
        return plt.gcf()
    
    def save_visualization(self, output_file, dpi=300, title=None):
        """
        Save a visualization of the graph to a file.
        
        Args:
            output_file (str): Path to save the visualization.
            dpi (int, optional): DPI for the saved image.
            title (str, optional): Title for the visualization.
            
        Returns:
            bool: True if the visualization was saved successfully, False otherwise.
        """
        try:
            # Create visualization
            fig = self.create_visualization(title=title)
            
            if not fig:
                return False
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save the figure
            logger.info(f"Saving visualization to {output_file}")
            plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
            
            logger.info(f"Visualization saved to {output_file}")
            plt.close()
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving visualization: {str(e)}")
            return False


def visualize_graph_file(input_file, output_file=None, show=False, figsize=(20, 20), dpi=300):
    """
    Visualize a graph file and optionally save the visualization.
    
    Args:
        input_file (str): Path to the graph file.
        output_file (str, optional): Path to save the visualization.
        show (bool, optional): Whether to show the visualization.
        figsize (tuple, optional): Figure size for the visualization.
        dpi (int, optional): DPI for the saved image.
        
    Returns:
        bool: True if the visualization was successful, False otherwise.
    """
    # Create visualizer
    visualizer = StaticVisualizer(figsize=figsize)
    
    # Load graph
    if not visualizer.load_graph_from_file(input_file):
        return False
    
    # Default output file if not specified
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '_visualization.png'
    
    # Create and save visualization
    title = f"Graph Visualization: {os.path.basename(input_file)}"
    if output_file:
        success = visualizer.save_visualization(output_file, dpi=dpi, title=title)
    
    # Show visualization if requested
    if show:
        visualizer.create_visualization(title=title, show=True)
    
    return success if output_file else True
