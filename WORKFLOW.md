# Complete Workflow Guide

This guide demonstrates how to use all four components of the Video Projects suite together to create a powerful video scraping, downloading, analysis, and visualization pipeline.

## Step 1: Set up a Working Directory

First, create a shared working directory to store intermediate and final outputs:

```bash
mkdir -p ~/video-workflow/data
```

## Step 2: Use Video Spider to Scrape Video Data

Use the video-spider component to scrape videos from a website, build a relationship graph, and save the metadata:

```bash
cd ~/Windsurf/video-projects/video-spider

# Make sure Docker and Splash are running
docker info > /dev/null || sudo systemctl start docker
docker ps | grep -q "scrapinghub/splash" || docker run -d -p 8050:8050 scrapinghub/splash

# Run the spider with a starting URL, limiting to 50 videos and depth 2
./run_spider.sh --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
    --output-dir ~/video-workflow/data \
    --screenshots-dir ~/video-workflow/data/screenshots \
    --max-videos 50 \
    --max-depth 2
```

After running this command, you'll have:
- `~/video-workflow/data/video_relationships.gexf`: The video relationship graph
- Various metadata files in the data directory
- Screenshots in the screenshots directory

## Step 3: Use Video Downloader to Download Selected Videos

Use the video-downloader component to download the videos discovered by the spider:

```bash
cd ~/Windsurf/video-projects/video-downloader

# Extract video URLs from the graph or use a prepared list
grep -o "https://.*\"" ~/video-workflow/data/video_relationships.gexf | tr -d '"' > ~/video-workflow/data/video_urls.txt

# Download videos (limiting to 5 concurrent downloads)
./download_videos.sh --input-file ~/video-workflow/data/video_urls.txt \
    --output-dir ~/video-workflow/data/downloads \
    --max-concurrent 5 \
    --quality 720p
```

After this step, you'll have:
- Downloaded videos in `~/video-workflow/data/downloads/`
- Metadata JSON files for each video

## Step 4: Use Data Processor to Analyze the Data

Use the data-processor component to analyze the video metadata and relationships:

```bash
cd ~/Windsurf/video-projects/data-processor

# Process the graph data and any metadata files
./process_data.sh --input ~/video-workflow/data/ \
    --output-dir ~/video-workflow/data/processed \
    --formats csv,json,gexf
```

This command will:
- Load all data from the input directory
- Clean and normalize the data (e.g., standardize view counts and durations)
- Perform statistical analysis
- Generate processed outputs in multiple formats

After processing, you'll have:
- Statistical insights in the terminal output
- Cleaned and processed data files in CSV and JSON formats
- A potentially enhanced graph file in GEXF format

## Step 5: Use Graph Visualizer to Explore the Relationships

Visualize the processed graph data using the graph-visualizer component:

```bash
cd ~/Windsurf/video-projects/graph-visualizer

# Create both static and interactive web visualizations
./visualize_graph.sh --input ~/video-workflow/data/processed/video_graph_*.gexf \
    --output ~/video-workflow/data/visualizations \
    --type both \
    --show
```

This will:
- Create a static PNG visualization
- Generate an interactive web visualization
- Open the web visualization in your browser

## Additional Workflow Ideas

Here are some additional ways to combine these components:

### Extract Top Videos and Download Only Those

```bash
# Use data processor to identify most popular videos
cd ~/Windsurf/video-projects/data-processor
./process_data.sh --input ~/video-workflow/data/video_relationships.gexf \
    --output-dir ~/video-workflow/data/top_videos

# Extract URLs of top 10 videos (by views) from the processed data
python -c "import pandas as pd; df = pd.read_csv('~/video-workflow/data/top_videos/video_data_*.csv'); \
    df.sort_values('views_cleaned', ascending=False).head(10)[['url']].to_csv('~/video-workflow/data/top_urls.csv', index=False)"

# Download just those top videos
cd ~/Windsurf/video-projects/video-downloader
./download_videos.sh --input-file ~/video-workflow/data/top_urls.csv \
    --output-dir ~/video-workflow/data/top_downloads \
    --quality best
```

### Continuous Monitoring Workflow

You could set up a scheduled task to run this pipeline regularly:

```bash
# Create a workflow script
cat > ~/video-workflow/run_pipeline.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
WORK_DIR=~/video-workflow/runs/$DATE

mkdir -p $WORK_DIR

# Step 1: Scrape new data
cd ~/Windsurf/video-projects/video-spider
./run_spider.sh --url "https://example.com/trending" \
    --output-dir $WORK_DIR/spider_output

# Step 2: Process the data
cd ~/Windsurf/video-projects/data-processor
./process_data.sh --input $WORK_DIR/spider_output \
    --output-dir $WORK_DIR/processed

# Step 3: Visualize changes
cd ~/Windsurf/video-projects/graph-visualizer
./visualize_graph.sh --input $WORK_DIR/processed/*.gexf \
    --output $WORK_DIR/visualizations
EOF

chmod +x ~/video-workflow/run_pipeline.sh

# Set up cron job to run this daily
crontab -l | { cat; echo "0 0 * * * ~/video-workflow/run_pipeline.sh"; } | crontab -
```

## Benefits of This Modular Approach

This workflow demonstrates the key advantages of our refactoring:

1. **Flexibility**: You can use each component independently or combine them as needed.
2. **Reusability**: The output from one component is easily used as input to another.
3. **Maintainability**: Each component has a clear, specific responsibility.
4. **Scalability**: You can replace components or add new ones without disrupting the workflow.

The modular design allows you to adapt the workflow to your specific needs, whether you're focusing on data collection, video downloading, or visualization and analysis.

## Real-World Use Cases

### Content Analysis

Track video trends and analyze content characteristics across platforms:

```bash
# Scrape videos from multiple platforms
cd ~/Windsurf/video-projects/video-spider
./run_spider.sh --url "https://platform1.com/trending" --output-dir ~/video-workflow/platform1
./run_spider.sh --url "https://platform2.com/trending" --output-dir ~/video-workflow/platform2

# Process and analyze data from both platforms
cd ~/Windsurf/video-projects/data-processor
./process_data.sh --input ~/video-workflow/platform1 --output-dir ~/video-workflow/analysis/platform1
./process_data.sh --input ~/video-workflow/platform2 --output-dir ~/video-workflow/analysis/platform2

# Compare metrics between platforms
python -c "
import pandas as pd
p1 = pd.read_csv('~/video-workflow/analysis/platform1/video_data_*.csv')
p2 = pd.read_csv('~/video-workflow/analysis/platform2/video_data_*.csv')
print('Platform 1 avg views:', p1['views_cleaned'].mean())
print('Platform 2 avg views:', p2['views_cleaned'].mean())
"
```

### Educational Content Discovery

Find and download educational videos on specific topics:

```bash
# Scrape educational content
cd ~/Windsurf/video-projects/video-spider
./run_spider.sh --url "https://youtube.com/results?search_query=python+tutorial" \
    --output-dir ~/video-workflow/education/python

# Process and extract high-quality content
cd ~/Windsurf/video-projects/data-processor
./process_data.sh --input ~/video-workflow/education/python \
    --output-dir ~/video-workflow/education/processed

# Filter for long-form content (likely tutorials)
python -c "
import pandas as pd
df = pd.read_csv('~/video-workflow/education/processed/video_data_*.csv')
tutorials = df[df['duration_seconds'] > 600]  # Videos longer than 10 minutes
tutorials.sort_values('views_cleaned', ascending=False).to_csv('~/video-workflow/education/tutorials.csv')
"

# Download the top tutorials
cd ~/Windsurf/video-projects/video-downloader
python -c "
import pandas as pd
df = pd.read_csv('~/video-workflow/education/tutorials.csv')
top5 = df.head(5)
top5[['url']].to_csv('~/video-workflow/education/top5_tutorials.csv', index=False)
"
./download_videos.sh --input-file ~/video-workflow/education/top5_tutorials.csv \
    --output-dir ~/video-workflow/education/downloads \
    --quality 1080p
```
