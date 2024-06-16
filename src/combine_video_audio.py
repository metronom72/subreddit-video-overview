import os

from moviepy.editor import VideoFileClip, AudioFileClip


def combine_video_audio(input_video, input_audio, output_video):
    """
    Combine a video clip and an audio clip into a single video file.

    :param input_video: Path to the input video file.
    :param input_audio: Path to the input audio file.
    :param output_video: Path to the output video file.
    :raises ValueError: If either input_video or input_audio is not a valid file path.
    :return: None
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
