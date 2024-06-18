import os
import time
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from src.audio_generation.generate_audio import generate_audio
from src.video_generation.combine_videos import concatenate_videos
from src.video_generation.record_html import record_mp4_task
from src.video_generation.store_metadata import store_metadata


def list_csv_files(directory):
    """List all CSV files in the given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.csv')]


def list_folders(directory):
    """List all folders in the given directory."""
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def main():
    # Step 1: List CSV files in the samples directory
    samples_dir = 'samples'
    if not os.path.exists(samples_dir):
        print(f"The directory '{samples_dir}' does not exist.")
        return

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

    # Step 2: List available versions (folders) in the templates directory
    templates_dir = 'src/html_generation/templates'
    if not os.path.exists(templates_dir):
        print(f"The directory '{templates_dir}' does not exist.")
        return

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
        generate_audio(row['comment'], 'en', f'{output_dir}/comment_{index}.mp3')
        record_mp4_task(index, row, output_dir, version)

    store_metadata(output_dir)

    # Concatenate all the MP4 files into one
    concatenate_videos(os.path.join(output_dir), combined_mp4)

    print(f"Images and video saved in {output_dir}")


if __name__ == "__main__":
    main()
