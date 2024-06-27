import os
import time
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor
from src.audio_generation.generate_audio import generate_audio_gtts, generate_audio_mozilla_tts
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


def fetch_comments():
    post_url = input('Enter the Reddit post URL (required): ')
    limit = int(input('Enter the number of top comments to fetch (required): '))

    # Fetch top comments from the subreddit post
    fetch_subreddit(post_url, limit)

    # List CSV files in the samples directory
    samples_dir = 'samples'
    csv_files = list_csv_files(samples_dir)

    if not csv_files:
        print("No CSV files found in the samples directory.")
        return None

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
    return pd.read_csv(csv_file)


def select_version(templates_dir):
    """Prompt the user to select a version from the available folders in the templates directory."""
    version_options = list_folders(templates_dir)

    if not version_options:
        print("No versions found in the templates directory.")
        return None

    print("Available versions:")
    for version in version_options:
        print(version)

    version = None
    while version not in version_options:
        version = input(f'Select a version ({", ".join(version_options)}): ')

    return version


def generate_audio_files(data, tts_library, output_dir):
    """Generate audio files for each comment in the data using the specified TTS library."""
    for index, row in data.iterrows():
        if tts_library == 'gtts':
            generate_audio_gtts(row['comment'], 'en', f'{output_dir}/comment_{index}.mp3')
        else:
            generate_audio_mozilla_tts(row['comment'], f'{output_dir}/comment_{index}.mp3')


def record_videos(data, version, output_dir):
    """Record videos for each comment in the data using the specified HTML template version."""
    for index, row in data.iterrows():
        record_mp4_task(index, row, output_dir, version)


def main():
    # Step 1: Prompt to use a default comment or fetch from Reddit
    use_default = input('Use default comment? (yes/no): ').strip().lower()

    if use_default == 'yes':
        # Default comment data
        data = pd.read_csv('samples/comments.csv')
    else:
        data = fetch_comments()
        if data is None:
            return

    # Print raw data for debugging
    print("Raw CSV Data:")
    print(data)

    # Prompt for TTS library selection
    tts_library = None
    while tts_library not in ['gtts', 'tts']:
        tts_library = input('Select TTS library (gtts/tts): ').strip().lower()

    # Setup the Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))

    # Step 3: Select HTML template version
    templates_dir = 'src/html_generation/templates'
    version = select_version(templates_dir)
    if version is None:
        return

    # Create a directory with the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = f'output_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)

    combined_mp4 = os.path.join(output_dir, f'output.mp4')

    # Generate audio files for comments
    generate_audio_files(data, tts_library, output_dir)

    # Record videos for comments
    record_videos(data, version, output_dir)

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
