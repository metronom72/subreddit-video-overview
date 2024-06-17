import os
import json
import subprocess
import math


def format_size(size_bytes):
    """
    :param size_bytes: The size in bytes that needs to be formatted.
    :return: The formatted size in a human-readable format.

    This method takes a size in bytes and formats it into a human-readable format. It returns the formatted size as a string.

    The size is represented in the following units: B (bytes), KB (kilobytes), MB (megabytes), GB (gigabytes), TB (terabytes), PB (petabytes), EB (exabytes), ZB (zettabytes), YB (yottabytes).

    The method uses logarithmic calculations to determine the appropriate unit and then rounds the size to two decimal places before returning the result.

    Example:
    >>> format_size(1024)
    '1.00 KB'
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def format_duration(seconds):
    """
    Format Duration

    Format the given number of seconds into the following format: HH:MM:SS.

    :param seconds: The number of seconds to be formatted. (int)
    :return: The formatted duration in the format "HH:MM:SS". (str)

    Example:
        >>> format_duration(3661)
        '01:01:01'
    """
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def format_bitrate(bitrate):
    """
    Format the bitrate.

    :param bitrate: The bitrate to format.
    :type bitrate: float
    :return: The formatted bitrate.
    :rtype: str
    """
    if bitrate == 0:
        return "0 bps"
    bit_name = ("bps", "Kbps", "Mbps", "Gbps", "Tbps", "Pbps")
    i = int(math.floor(math.log(bitrate, 1000)))
    p = math.pow(1000, i)
    s = round(bitrate / p, 2)
    return f"{s} {bit_name[i]}"


def get_file_metadata(file_path):
    """
    :param file_path: the path of the file for which to retrieve metadata
    :return: a dictionary containing the file metadata
    """
    try:
        # Run ffprobe command to get file metadata
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries',
             'format=duration,bit_rate,size', '-show_streams', '-of', 'json', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        metadata = json.loads(result.stdout)

        # Extract required information
        format_info = metadata.get('format', {})
        streams_info = metadata.get('streams', [])

        file_metadata = {
            'filename': os.path.basename(file_path),
            'duration': format_duration(float(format_info.get('duration', 0))),
            'bitrate': format_bitrate(int(format_info.get('bit_rate', 0))),
            'size': format_size(int(format_info.get('size', 0))),
            'streams': []
        }

        for stream in streams_info:
            stream_metadata = {
                'codec_type': stream.get('codec_type'),
                'codec_name': stream.get('codec_name'),
                'width': stream.get('width'),
                'height': stream.get('height'),
                'bit_rate': format_bitrate(int(stream.get('bit_rate', 0))) if 'bit_rate' in stream else None,
            }
            file_metadata['streams'].append(stream_metadata)

        return file_metadata
    except Exception as e:
        print(f"Error retrieving metadata for {file_path}: {e}")
        return None


def store_metadata(folder_path):
    """
    Retrieve metadata from all the MP4 and MP3 files present in the given folder.

    :param folder_path: The path to the folder containing MP4 and MP3 files.
    :return: None

    This method reads all the MP4 and MP3 files in the specified folder, extracts their metadata using the `get_file_metadata` function, and stores the metadata in a list. The list is then saved as a JSON file named `metadata.json` in the current working directory.
    """
    metadata_list = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp4', '.mp3')):
                file_path = os.path.join(folder_path, file)
                metadata = get_file_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)

    # Sort metadata list by filename
    metadata_list.sort(key=lambda x: x['filename'])

    with open(os.path.join(folder_path, 'metadata.json'), 'w') as json_file:
        json.dump(metadata_list, json_file, indent=4)
