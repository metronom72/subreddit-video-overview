import os
from concurrent.futures import ThreadPoolExecutor
from src.cli.inputs import generate_audio_files, record_videos, combine_video_audio_task, get_comments, get_tts_library, get_version, create_output_directory
from src.video_generation.combine_videos import concatenate_videos
from src.video_generation.store_metadata import store_metadata


def main():
    data = get_comments()

    tts_library = get_tts_library()

    version = get_version()

    output_dir = create_output_directory()

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
