import os
import time

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from src.audio_generation.generate_audio import generate_audio
from src.video_generation.combine_videos import concatenate_videos
from src.video_generation.record_html import record_mp4_task
from src.video_generation.store_metadata import store_metadata

# Step 1: Read CSV Data
csv_file = os.path.join('samples', 'comments.csv')  # Path to your CSV file
data = pd.read_csv(csv_file)

# Print raw data for debugging
print("Raw CSV Data:")
print(data)

# Setup the Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))

version = 'v2'

# Create a directory with the current timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")
output_dir = f'output_{timestamp}'
os.makedirs(output_dir, exist_ok=True)

combined_mp4 = os.path.join(output_dir, f'output.mp4')

for index, row in data.iterrows():
    generate_audio(row['comment'], 'en', f'{output_dir}/comment_{index}.mp3')
    record_mp4_task(index, row, output_dir, version)

store_metadata(output_dir)

# Concatenate all the MP4 files into one
concatenate_videos(os.path.join(output_dir), combined_mp4)

print(f"Images and video saved in {output_dir}")
