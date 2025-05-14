"""
Video data processor module for analyzing video metadata and relationships.
This module provides functions and classes to process video data.
"""

import os
import json
import logging
import pandas as pd
import networkx as nx
import numpy as np
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoDataProcessor:
    """Class for processing video metadata and relationships."""
    
    def __init__(self, input_dir=None, output_dir='processed_data'):
        """
        Initialize the video data processor.
        
        Args:
            input_dir (str, optional): Directory containing input data
            output_dir (str): Directory to save output data
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize data structures
        self.video_data = []
        self.video_df = None
        self.video_graph = None
    
    def load_data_from_file(self, file_path):
        """
        Load data from a file (JSON, CSV, GEXF).
        
        Args:
            file_path (str): Path to the data file
            
        Returns:
            bool: True if the data was loaded successfully, False otherwise
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    self.video_data = data
                elif isinstance(data, dict) and 'nodes' in data:
                    # This might be a network graph JSON
                    self.video_graph = nx.readwrite.json_graph.node_link_graph(data)
                    # Extract node data
                    self.video_data = [dict(id=n, **attrs) for n, attrs in self.video_graph.nodes(data=True)]
                else:
                    self.video_data = [data]  # Single video data
            
            elif file_ext == '.csv':
                self.video_df = pd.read_csv(file_path)
                self.video_data = self.video_df.to_dict('records')
            
            elif file_ext in ['.gexf', '.graphml']:
                if file_ext == '.gexf':
                    self.video_graph = nx.read_gexf(file_path)
                else:
                    self.video_graph = nx.read_graphml(file_path)
                    
                # Extract node data
                self.video_data = [dict(id=n, **attrs) for n, attrs in self.video_graph.nodes(data=True)]
            
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return False
            
            # Create DataFrame if not already created
            if self.video_df is None and self.video_data:
                self.video_df = pd.DataFrame(self.video_data)
            
            # Create graph if not already created
            if self.video_graph is None and self.video_data:
                self.video_graph = nx.DiGraph()
                for item in self.video_data:
                    if 'id' in item:
                        self.video_graph.add_node(item['id'], **{k: v for k, v in item.items() if k != 'id'})
                    elif 'url' in item:
                        self.video_graph.add_node(item['url'], **item)
                
                # Try to add edges if relationships exist
                for item in self.video_data:
                    if 'related_videos' in item and isinstance(item.get('related_videos'), list):
                        source = item.get('id', item.get('url'))
                        if source:
                            for related in item['related_videos']:
                                target = related.get('id', related.get('url'))
                                if target:
                                    self.video_graph.add_edge(source, target)
            
            logger.info(f"Loaded data from {file_path}")
            if self.video_graph:
                logger.info(f"Graph has {self.video_graph.number_of_nodes()} nodes and {self.video_graph.number_of_edges()} edges")
            if self.video_df is not None:
                logger.info(f"DataFrame has {len(self.video_df)} rows and {len(self.video_df.columns)} columns")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return False
    
    def load_data_from_directory(self, directory=None):
        """
        Load data from all supported files in a directory.
        
        Args:
            directory (str, optional): Directory to load data from (defaults to self.input_dir)
            
        Returns:
            bool: True if any data was loaded successfully, False otherwise
        """
        directory = directory or self.input_dir
        if not directory:
            logger.error("No input directory specified")
            return False
        
        success = False
        
        try:
            # Find all supported files
            supported_extensions = ['.json', '.csv', '.gexf', '.graphml']
            files = []
            
            for ext in supported_extensions:
                files.extend(Path(directory).glob(f'*{ext}'))
            
            if not files:
                logger.warning(f"No supported files found in {directory}")
                return False
            
            # Load data from each file
            for file_path in files:
                if self.load_data_from_file(str(file_path)):
                    success = True
            
            return success
        
        except Exception as e:
            logger.error(f"Error loading data from directory {directory}: {str(e)}")
            return False
    
    def clean_data(self):
        """
        Clean and preprocess the data.
        
        Returns:
            bool: True if the data was cleaned successfully, False otherwise
        """
        if self.video_df is None or self.video_df.empty:
            logger.error("No data to clean")
            return False
        
        try:
            # Make a copy to avoid modifying the original
            df = self.video_df.copy()
            
            # Handle missing values
            df = df.fillna({
                'title': 'Unknown',
                'views': 0,
                'duration': 0
            })
            
            # Clean and convert views (e.g., "1.5k" -> 1500)
            if 'views' in df.columns:
                def clean_views(views):
                    if pd.isna(views):
                        return 0
                    if isinstance(views, (int, float)):
                        return views
                    views_str = str(views).strip().lower()
                    views_str = views_str.replace(',', '')
                    
                    try:
                        if 'k' in views_str:
                            return float(views_str.replace('k', '')) * 1000
                        elif 'm' in views_str:
                            return float(views_str.replace('m', '')) * 1000000
                        else:
                            return float(views_str)
                    except:
                        return 0
                
                df['views_cleaned'] = df['views'].apply(clean_views)
            
            # Clean and convert duration (e.g., "5:30" -> 330 seconds)
            if 'duration' in df.columns:
                def clean_duration(duration):
                    if pd.isna(duration):
                        return 0
                    if isinstance(duration, (int, float)):
                        return duration
                    duration_str = str(duration).strip().lower()
                    
                    try:
                        # Format like "5:30"
                        if ':' in duration_str:
                            parts = duration_str.split(':')
                            if len(parts) == 2:
                                return int(parts[0]) * 60 + int(parts[1])
                            elif len(parts) == 3:
                                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        
                        # Format like "5min"
                        elif 'min' in duration_str:
                            return float(duration_str.replace('min', '')) * 60
                        
                        # Format like "1h30m"
                        elif 'h' in duration_str and 'm' in duration_str:
                            h_idx = duration_str.find('h')
                            m_idx = duration_str.find('m')
                            hours = float(duration_str[:h_idx])
                            minutes = float(duration_str[h_idx+1:m_idx])
                            return hours * 3600 + minutes * 60
                        
                        return float(duration_str)
                    except:
                        return 0
                
                df['duration_seconds'] = df['duration'].apply(clean_duration)
            
            # Update the DataFrame
            self.video_df = df
            
            logger.info("Data cleaning completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            return False
    
    def analyze_data(self):
        """
        Analyze the video data and generate statistics.
        
        Returns:
            dict: Dictionary containing analysis results
        """
        if self.video_df is None or self.video_df.empty:
            logger.error("No data to analyze")
            return {}
        
        try:
            results = {
                'total_videos': len(self.video_df)
            }
            
            # Check which columns are available for analysis
            if 'views_cleaned' in self.video_df.columns:
                results['total_views'] = self.video_df['views_cleaned'].sum()
                results['avg_views'] = self.video_df['views_cleaned'].mean()
                results['median_views'] = self.video_df['views_cleaned'].median()
                results['min_views'] = self.video_df['views_cleaned'].min()
                results['max_views'] = self.video_df['views_cleaned'].max()
            
            if 'duration_seconds' in self.video_df.columns:
                results['total_duration_seconds'] = self.video_df['duration_seconds'].sum()
                results['avg_duration_seconds'] = self.video_df['duration_seconds'].mean()
                results['median_duration_seconds'] = self.video_df['duration_seconds'].median()
                results['min_duration_seconds'] = self.video_df['duration_seconds'].min()
                results['max_duration_seconds'] = self.video_df['duration_seconds'].max()
            
            # Graph-based analysis
            if self.video_graph:
                results['graph_nodes'] = self.video_graph.number_of_nodes()
                results['graph_edges'] = self.video_graph.number_of_edges()
                
                # Calculate network metrics
                if results['graph_nodes'] > 0:
                    # Degree centrality
                    in_degree = dict(self.video_graph.in_degree())
                    out_degree = dict(self.video_graph.out_degree())
                    
                    if in_degree:
                        results['avg_in_degree'] = np.mean(list(in_degree.values()))
                        results['max_in_degree'] = max(in_degree.values())
                        results['max_in_degree_node'] = max(in_degree.items(), key=lambda x: x[1])[0]
                    
                    if out_degree:
                        results['avg_out_degree'] = np.mean(list(out_degree.values()))
                        results['max_out_degree'] = max(out_degree.values())
                        results['max_out_degree_node'] = max(out_degree.items(), key=lambda x: x[1])[0]
                    
                    # Try to detect communities
                    try:
                        import community as community_louvain
                        partition = community_louvain.best_partition(self.video_graph.to_undirected())
                        communities = {}
                        for node, community_id in partition.items():
                            if community_id not in communities:
                                communities[community_id] = []
                            communities[community_id].append(node)
                        
                        results['num_communities'] = len(communities)
                        results['community_sizes'] = [len(nodes) for nodes in communities.values()]
                    except:
                        # Community detection is optional
                        pass
            
            logger.info("Data analysis completed successfully")
            return results
        
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            return {}
    
    def export_data(self, formats=None):
        """
        Export processed data to various formats.
        
        Args:
            formats (list, optional): List of formats to export to ('csv', 'json', 'gexf')
                If not specified, exports to all available formats.
        
        Returns:
            dict: Dictionary mapping formats to output file paths
        """
        if not formats:
            formats = ['csv', 'json', 'gexf']
        
        if not self.output_dir:
            logger.error("No output directory specified")
            return {}
        
        output_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Export DataFrame
            if self.video_df is not None and 'csv' in formats:
                csv_file = os.path.join(self.output_dir, f'video_data_{timestamp}.csv')
                self.video_df.to_csv(csv_file, index=False)
                output_files['csv'] = csv_file
                logger.info(f"Exported data to CSV: {csv_file}")
            
            if self.video_df is not None and 'json' in formats:
                json_file = os.path.join(self.output_dir, f'video_data_{timestamp}.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.video_df.to_dict('records'), f, indent=2)
                output_files['json'] = json_file
                logger.info(f"Exported data to JSON: {json_file}")
            
            # Export graph
            if self.video_graph is not None and 'gexf' in formats:
                gexf_file = os.path.join(self.output_dir, f'video_graph_{timestamp}.gexf')
                nx.write_gexf(self.video_graph, gexf_file)
                output_files['gexf'] = gexf_file
                logger.info(f"Exported graph to GEXF: {gexf_file}")
            
            return output_files
        
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return output_files
    
    def process_data(self, input_path=None, clean=True, analyze=True, export_formats=None):
        """
        Process data from start to finish.
        
        Args:
            input_path (str, optional): Path to input file or directory
            clean (bool): Whether to clean the data
            analyze (bool): Whether to analyze the data
            export_formats (list, optional): List of formats to export to
        
        Returns:
            dict: Dictionary containing analysis results and export file paths
        """
        results = {
            'success': False,
            'analysis': {},
            'exports': {}
        }
        
        # Load data
        if input_path:
            if os.path.isfile(input_path):
                success = self.load_data_from_file(input_path)
            elif os.path.isdir(input_path):
                success = self.load_data_from_directory(input_path)
            else:
                logger.error(f"Input path not found: {input_path}")
                return results
        else:
            success = self.load_data_from_directory()
        
        if not success:
            logger.error("Failed to load data")
            return results
        
        # Clean data
        if clean:
            if not self.clean_data():
                logger.error("Failed to clean data")
                return results
        
        # Analyze data
        if analyze:
            results['analysis'] = self.analyze_data()
        
        # Export data
        if export_formats:
            results['exports'] = self.export_data(export_formats)
        
        results['success'] = True
        return results


def process_video_data(
    input_path=None,
    output_dir='processed_data',
    clean=True,
    analyze=True,
    export_formats=None
):
    """
    Process video data from start to finish.
    
    Args:
        input_path (str): Path to input file or directory
        output_dir (str): Directory to save output data
        clean (bool): Whether to clean the data
        analyze (bool): Whether to analyze the data
        export_formats (list, optional): List of formats to export to
        
    Returns:
        dict: Dictionary containing analysis results and export file paths
    """
    # Initialize processor
    processor = VideoDataProcessor(output_dir=output_dir)
    
    # Process data
    return processor.process_data(
        input_path=input_path,
        clean=clean,
        analyze=analyze,
        export_formats=export_formats
    )
