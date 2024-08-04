import os
import shutil


def collect_audio_files(source_dir, output_dir):
    """
    This method collects all audio files (.mp3) from a source directory and copies them to an output directory.

    :param source_dir: The directory containing the source audio files.
    :param output_dir: The directory where the audio files will be copied to.
    :return: None
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through files in the source directory
    for filename in os.listdir(source_dir):
        # Check if the file has the desired extension
        if filename.endswith('.mp3'):
            # Construct full file paths
            source_file = os.path.join(source_dir, filename)
            destination_file = os.path.join(output_dir, filename)
            # Copy file from source to destination
            shutil.copy(source_file, destination_file)
            print(f"Copied: {source_file} to {destination_file}")
