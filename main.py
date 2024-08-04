import os
from concurrent.futures import ThreadPoolExecutor

from src.audio_generation.audio_collection import collect_audio_files
from src.cli.configuration import get_configuration
from src.cli.converters import convert_data_to_dataframe
from src.cli.inputs import generate_audio_files, record_videos, combine_video_audio_task, get_comments, \
    create_output_directory
from src.html.generate_html import generate_html
from src.video.combine_videos import concatenate_videos
from src.video.store_metadata import store_metadata


def main():
    output_dir = create_output_directory()

    configuration = get_configuration('./config.toml', output_dir)

    data = get_comments(configuration)

    extension = configuration['video_generation']['extension']
    tts_library = configuration['audio_generation']['tts_library']
    version = configuration['html_generation']['version']
    audio_collection_source = configuration['audio_collection']['source_folder']

    html_generation_enabled = configuration['html_generation']['enabled']
    video_generation_enabled = configuration['video_generation']['enabled']
    audio_generation_enabled = configuration['audio_generation']['enabled']
    combining_enabled = configuration['combining']['enabled']
    audio_collection_enabled = configuration['audio_collection']['enabled']

    combined_mp4 = None
    if combining_enabled:
        combined_mp4 = os.path.join(output_dir, f'output.{extension}')

    # Generate audio files for comments
    if audio_generation_enabled:
        generate_audio_files(convert_data_to_dataframe(data), tts_library, output_dir)
    elif audio_collection_enabled:
        collect_audio_files(audio_collection_source, output_dir)

    # Record videos for comments
    if video_generation_enabled and html_generation_enabled:
        record_videos(convert_data_to_dataframe(data), version, output_dir, extension)
    elif html_generation_enabled:
        for index, row in convert_data_to_dataframe(data).iterrows():
            html_file = os.path.join(output_dir, f'comment_{index}.html')
            generate_html(row, html_file, version)

    # Combine video and audio files in parallel
    if combining_enabled and audio_generation_enabled and video_generation_enabled:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(combine_video_audio_task, index, row, output_dir) for index, row in
                       convert_data_to_dataframe(data).iterrows()]
            for future in futures:
                future.result()  # Wait for all futures to complete

    store_metadata(output_dir)

    # Concatenate all the MP4 files into one
    if combined_mp4 is not None and combining_enabled and audio_generation_enabled and video_generation_enabled:
        concatenate_videos(os.path.join(output_dir), combined_mp4)

    print(f"Images and video saved in {output_dir}")


if __name__ == "__main__":
    main()
