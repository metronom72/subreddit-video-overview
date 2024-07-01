import os
import subprocess


def create_file_list(directory, file_list_path):
    """
    Create a file list of files with audio in a given directory.

    :param directory: The directory to search for files.
    :param file_list_path: The path to the output file list.
    :return None
    """
    with open(file_list_path, 'w') as file_list:
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('with_audio.mp4'):
                file_list.write(f"file '{filename}'\n")


def concatenate_videos(directory, output_file):
    """
    :param directory: The directory containing the videos to be concatenated.
    :param output_file: The path to the output file where the concatenated video will be saved.
    :return None

    This method concatenates multiple videos stored in the specified directory into a single video file. It uses FFmpeg to perform the concatenation with re-encoding to prevent any potential issues.

    First, a file list is created in the specified directory by calling the `create_file_list` method. This file list is used as an input to FFmpeg to indicate the order of videos to concatenate.

    The FFmpeg command is constructed with the necessary parameters for concatenation, video encoding, audio encoding, and output file path. The command is then executed using the `subprocess.run` method.

    If the concatenation is successful, a success message is printed to the console with the path to the output file. If an error occurs during concatenation, an error message is printed instead.

    After the concatenation, the file list is optionally removed using `os.remove`. This step can be skipped if you want to keep the file list for reference.
    """
    file_list_path = os.path.join(directory, 'file_list.txt')
    create_file_list(directory, file_list_path)

    # Use FFmpeg to concatenate the videos with re-encoding to avoid issues
    ffmpeg_command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', file_list_path,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac',
        '-b:a', '192k', output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Videos concatenated successfully into {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating videos: {e}")
    finally:
        # Optionally remove the file list after concatenation
        os.remove(file_list_path)
