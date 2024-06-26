import os
import time
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor
from src.audio_generation.generate_audio import generate_audio_gtts
from src.reddit.fetcn_subreddit import fetch_subreddit
from src.video_generation.combine_video_audio import combine_video_audio
from src.video_generation.combine_videos import concatenate_videos
from src.video_generation.record_html import record_mp4_task
from src.video_generation.store_metadata import store_metadata


def list_csv_files(directory):
    """List and sort all CSV files in the given directory by name."""
    return sorted([f for f in os.listdir(directory) if f.endswith('.csv')])


def list_folders(directory):
    """List all folders in the given directory."""
    return sorted([f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))])


def combine_video_audio_task(index, row, output_dir):
    mp3_file = os.path.join(output_dir, f'comment_{index}.mp3')
    mp4_file = os.path.join(output_dir, f'comment_{index}.mp4')
    with_audio_mp4_file = os.path.join(output_dir, f'comment_{index}_with_audio.mp4')

    # Check if the corresponding MP3 file exists
    if os.path.exists(mp3_file):
        combine_video_audio(mp4_file, mp3_file, with_audio_mp4_file)


def main():
    # Step 1: Prompt to use a default comment or fetch from Reddit
    use_default = input('Use default comment? (yes/no): ').strip().lower()

    if use_default == 'yes':
        # Default comment data
        data = pd.read_csv('samples/comments.csv')
    else:
        # Step 2: Prompt for Reddit post URL and comment limit
        post_url = input('Enter the Reddit post URL (required): ')
        limit = int(input('Enter the number of top comments to fetch (required): '))

        # Fetch top comments from the subreddit post
        fetch_subreddit(post_url, limit)

        # Step 3: List CSV files in the samples directory
        samples_dir = 'samples'
        csv_files = list_csv_files(samples_dir)

        if not csv_files:
            print("No CSV files found in the samples directory.")
            return

        # Display CSV file options to the user
        print("Select a CSV file:")
        for i, file in enumerate(csv_files):
            print(f"{i + 1}: {file}")

        # Prompt for CSV file selection
        csv_file_index = None
        while csv_file_index not in range(1, len(csv_files) + 1):
            try:
                csv_file_index = int(input(f"Enter the number corresponding to the CSV file (1-{len(csv_files)}): "))
            except ValueError:
                pass

        csv_file = os.path.join(samples_dir, csv_files[csv_file_index - 1])

        # Read CSV Data
        data = pd.read_csv(csv_file)

    # Print raw data for debugging
    print("Raw CSV Data:")
    print(data)

    # Setup the Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))

    # Step 3: List available versions (folders) in the templates directory
    templates_dir = 'src/html_generation/templates'
    version_options = list_folders(templates_dir)

    if not version_options:
        print("No versions found in the templates directory.")
        return

    print("Available versions:")
    for version in version_options:
        print(version)

    # Prompt for version selection
    version = None
    while version not in version_options:
        version = input(f'Select a version ({", ".join(version_options)}): ')

    # Create a directory with the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = f'output_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)

    combined_mp4 = os.path.join(output_dir, f'output.mp4')

    for index, row in data.iterrows():
        generate_audio_gtts(row['comment'], 'en', f'{output_dir}/comment_{index}.mp3')
        record_mp4_task(index, row, output_dir, version)

    # Combine video and audio files in parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(combine_video_audio_task, index, row, output_dir) for index, row in data.iterrows()]
        for future in futures:
            future.result()  # Wait for all futures to complete

    store_metadata(output_dir)

    # Concatenate all the MP4 files into one
    concatenate_videos(os.path.join(output_dir), combined_mp4)

    print(f"Images and video saved in {output_dir}")

if __name__ == "__main__":
    main()
