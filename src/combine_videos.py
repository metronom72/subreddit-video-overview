import os
import subprocess


def create_file_list(directory, file_list_path):
    """
    Creates a list of files in the given directory that have names ending with 'with_audio.mp4'.

    :param directory: The directory in which the files are located.
    :param file_list_path: The path to the file list that will be created.
    :return: None
    """
    with open(file_list_path, 'w') as file_list:
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('with_audio.mp4'):
                file_list.write(f"file '{filename}'\n")


def concatenate_videos(directory, output_file):
    """
    :param directory: The directory containing the videos to concatenate.
    :param output_file: The path and filename of the output concatenated video file.
    :return: None

    This method concatenates multiple videos located in the specified directory into a single video file. It uses FFmpeg to perform the concatenation with re-encoding to avoid any potential issues. The resulting video file will be saved at the specified output_file path.

    The method first creates a file_list.txt file in the directory to list the paths of the videos in the desired order of concatenation. It then builds an FFmpeg command with the necessary parameters to perform the concatenation, specifying the desired video and audio codecs, bitrates, and other settings.

    If the FFmpeg command executes successfully, it prints a success message indicating the output file location. If an error occurs during the concatenation process, it prints an error message. Finally, the method removes the temporary file_list.txt file after concatenation.

    Note: This method requires FFmpeg to be installed and available in the system's PATH.
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
