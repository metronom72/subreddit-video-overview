import os

from moviepy.editor import VideoFileClip, AudioFileClip


def combine_video_audio(input_video, input_audio, output_video):
    """
    Combine the video and audio files into a single video file.

    :param input_video: The path to the input video file.
    :type input_video: str
    :param input_audio: The path to the input audio file.
    :type input_audio: str
    :param output_video: The path to save the output video file.
    :type output_video: str
    :return None

    :raises ValueError: if input_video or input_audio is not a valid file path

    """
    # Ensure input paths are strings and files exist
    if not isinstance(input_video, str) or not os.path.isfile(input_video):
        raise ValueError(f"Invalid video file path: {input_video}")
    if not isinstance(input_audio, str) or not os.path.isfile(input_audio):
        raise ValueError(f"Invalid audio file path: {input_audio}")

    # Load the video clip
    video_clip = VideoFileClip(input_video)

    # Load the audio clip
    audio_clip = AudioFileClip(input_audio)

    # Add a delay of 2 seconds to the audio
    delayed_audio_clip = audio_clip.set_start(2)

    # Set the audio of the video clip
    video_with_audio = video_clip.set_audio(delayed_audio_clip)

    # Write the result to a file
    video_with_audio.write_videofile(output_video, codec="libx264", audio_codec="aac")

    print(f"Video with audio saved to {output_video}")
