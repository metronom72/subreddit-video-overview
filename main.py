import os
from concurrent.futures import ThreadPoolExecutor

from src.cli.configuration import get_configuration
from src.cli.converters import convert_data_to_dataframe
from src.cli.inputs import generate_audio_files, record_videos, combine_video_audio_task, get_comments, \
    create_output_directory
from src.video.combine_videos import concatenate_videos
from src.video.store_metadata import store_metadata


def main():
    output_dir = create_output_directory()

    configuration = get_configuration('./config.toml', output_dir)

    data = get_comments(configuration)

    tts_library = configuration['audio_generation']['tts_library']

    version = configuration['html_generation']['version']

    combined_mp4 = None
    if configuration['combining']['enabled']:
        combined_mp4 = os.path.join(output_dir, f'output.mp4')

    # Generate audio files for comments
    if configuration['audio_generation']['enabled']:
        generate_audio_files(convert_data_to_dataframe(data), tts_library, output_dir)

    # Record videos for comments
    if configuration['video_generation']['enabled'] and configuration['html_generation']['enabled']:
        record_videos(convert_data_to_dataframe(data), version, output_dir)

    # Combine video and audio files in parallel
    if configuration['combining']['enabled'] and configuration['audio_generation']['enabled'] and \
            configuration['video_generation']['enabled']:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(combine_video_audio_task, index, row, output_dir) for index, row in
                       convert_data_to_dataframe(data).iterrows()]
            for future in futures:
                future.result()  # Wait for all futures to complete

    store_metadata(output_dir)

    # Concatenate all the MP4 files into one
    if combined_mp4 is not None and configuration['combining']['enabled'] and configuration['audio_generation'][
        'enabled'] and configuration['video_generation']['enabled']:
        concatenate_videos(os.path.join(output_dir), combined_mp4)

    print(f"Images and video saved in {output_dir}")


if __name__ == "__main__":
    main()
